from Card import Card
import grab_from_archidekt as Arch

class Deck:

    """Create a deck object"""
    def __init__(self, commander1, commander2 = None, deck_size = 100):

        # Create a decklist object
        self.decklist = [None for _ in range(deck_size)]

        # Determine what the commanders are
        if commander2 is None:
            self.commander = [commander1]
            self.add_card(1, commander1)
        else:
            self.commander = [commander1, commander2]
            self.add_card(1, commander1)
            self.add_card(1, commander2)

        self.identity = self.det_color_identity()
        self.check_commanders()



        # We should also check to see if the commanders are legal
        # As well as the 99

    """Determine the color identity of the deck"""
    def det_color_identity(self):

        id = []

        # Add the color identities of all commanders
        for i in range(len(self.commander)):
            id += self.decklist[i].identity

        # Get each unique color in that identity and then put it in WUBRG order
        unique_letters = set(filter(lambda letter: letter in "WUBRG", id))
        return ''.join([letter for letter in "WUBRG" if letter in unique_letters])

    """Determine whether the commanders are legal"""
    def check_commanders(self):

        # Is it a Legendary Creature?
        for i in range(len(self.commander)):
            if "Legendary" in self.decklist[i].types and "Creature" in self.decklist[i].types:
                return

            print(f"{self.decklist[i].name} is not a legal commander according to our records.")
            print("This may mean it is a special kind of commander we haven't accounted for!")
            print("We will continue assuming this is the case :)")

    """Add a card to the deck in the next blank space given a quantity and the card's name"""
    def add_card(self, quantity, name):

        # Put the card in the next available None slot
        if None in self.decklist:
            for i in range(quantity):
                self.decklist[self.decklist.index(None)] = Card.get_card_by_name(name)
            return

        raise IndexError("There are no empty spaces left in the deck!")

    """Import a decklist given a txt file
       Format required: quantityx cardname"""
    def import_decklist_from_file(self, filename):

        # Open the file
        with open(filename, "r", encoding='utf-8') as file:
            for line in file:

                # Determine the quantity and card name depending on where 'quantityx' is
                quantity = int(line.split("x ")[0])
                name = "".join(line.split("x ", 1)[1:]).strip()

                # Add each card to the deck if it's not one of your commanders
                # (They were previously added)
                if name not in self.commander:
                    self.add_card(quantity, name)

        # Determine various important deck statistics
        self.det_stats()
        # Make sure each card fits within the commanders' color identity
        self.check_identity()

    """Same as above, except from a list pasted into a text box"""
    def import_decklist_from_text(self, text):

        for line in text.splitlines():
            quantity = int(line.split("x ")[0])
            name = "".join(line.split("x ", 1)[1:]).strip()

            if name not in self.commander:
                self.add_card(quantity, name)

        self.det_stats()
        self.check_identity()


    """Same as the above, except this searches for an Archidekt deck rather than using a txt file"""
    @staticmethod
    def import_decklist_from_archidekt(owner, deck_name):

        # Find the deck
        deck_url, deck_id = Arch.search_archidekt(owner, deck_name)

        # Grab the decklist, including which cards are the commanders
        my_decklist, commanders = Arch.get_archidekt_deck(deck_id)

        # Create a deck object with the appropriate commander(s)
        my_deck = Deck(commanders[0], commanders[1])

        # Determine the quantity and card name depending on where 'quantityx' is
        for item in my_decklist:
            quantity = int(item.split("x ")[0])
            name = "".join(item.split("x ", 1)[1:]).strip()

            # Add each card to the deck if it's not one of your commanders
            # (They were previously added)
            if name not in my_deck.commander:
                my_deck.add_card(quantity, name)

        # Determine various important deck statistics
        my_deck.det_stats()
        # Make sure each card fits within the commanders' color identity
        my_deck.check_identity()

        # Return the deck object
        return my_deck

    """Determine various statistics about the deck"""
    def det_stats(self):

        # Initialize several variables
        self.avg_manavalue = 0
        self.spell_count = 0
        self.land_count = 0
        self.total_price = 0
        self.pip_count = {"W": 0,
                          "U": 0,
                          "B": 0,
                          "R": 0,
                          "G": 0}
        self.mdfc_count = 0
        self.mdfc_tapped = 0
        self.mdfc_untapped = 0

        # This counts the number of cheap ramp and card draw in the deck
        self.count_cheap()

        # This counts the number of mdfc lands in the deck
        self.count_mdfc()

        for card in self.decklist:

            # Add the card price
            self.total_price += float(card.price)

            # Count the number of nonland cards
            # Account for their mana values and pips
            if "Land" not in card.types:
                self.spell_count += 1
                self.avg_manavalue += card.manavalue

                for i in card.pips:
                    self.pip_count[i] += card.pips[i]

            else:
                self.land_count += 1

        self.land_count -= self.mdfc_count

        # Using those numbers, determine the average mana value of the deck
        self.avg_manavalue /= self.spell_count
        self.avg_manavalue = round(self.avg_manavalue, 2)

        self.total_price = round(self.total_price, 2)

        # Figure out what lands the deck should play
        self.det_land_count() # How many
        self.compare_land_counts() # Compare that to how many currently in the deck
        self.rec_basics()     # Recommend that many basics, with ratios according to the pip count

    """Determine the number of lands recommended for the deck"""
    def det_land_count(self):

        # This uses Frank Karsten's formula, broken down into a few steps
        self.rec_land_count = (100 - len(self.commander))/60
        self.rec_land_count *= 19.59 + (1.9 * self.avg_manavalue) + 0.27
        self.rec_land_count -= (0.28 * self.cheap_count) - 1.35
        self.rec_land_count = round(self.rec_land_count, 2)

    """Compare current land count to the recommended number"""
    def compare_land_counts(self):
        current =  self.land_count + (self.mdfc_untapped * .74) + (self.mdfc_tapped * .38)
        diff = current - self.rec_land_count
        print()
        print()
        self.comparison_statement = ""
        if diff < 0:
            self.comparison_statement = f"You are playing {round(diff, 1) * -1} less lands in your deck than recommended"
        else: self.comparison_statement = f"You are playing {round(diff, 1)} more lands in your deck than recommended"

    """Check if each card is within the deck's color identity"""
    def check_identity(self):

        # Print each card not in the color identity
        for card in self.decklist:
            if not card.check_id(self.identity):
                print(f"{card.name} is not in the deck's identity")
                print(f"     {card.identity} not in {self.identity}")

    """Counts the number of cheap ramp/draw in the deck"""
    def count_cheap(self):

        self.cheap_count = 0

        for card in self.decklist:
            if card.is_cheap():
                self.cheap_count += 1

    """Counts the number of mdfc lands in the deck"""
    def count_mdfc(self):

        for card in self.decklist:

            det, kind = card.is_mdfc()
            if det:
                if kind == "tapped":
                    self.mdfc_tapped += 1
                if kind == "untapped":
                    self.mdfc_untapped += 1
                if kind == "dfc":
                    self.land_count -= 1
                self.mdfc_count += 1

    """Create a list of basic lands, evenly distributed for each color in the deck"""
    def rec_basics(self):

        # Determine the total number of colored pips in the deck
        pip_sum = 0
        for i in self.pip_count:
            pip_sum += self.pip_count[i]

        # Use the ratio of a type of pip to the total pips to determine the number of each basic
        plains_count = round(self.pip_count["W"] / pip_sum * self.rec_land_count)
        islands_count = round(self.pip_count["U"] / pip_sum * self.rec_land_count)
        swamps_count = round(self.pip_count["B"] / pip_sum * self.rec_land_count)
        mountains_count = round(self.pip_count["R"] / pip_sum * self.rec_land_count)
        forest_count = round(self.pip_count["G"] / pip_sum * self.rec_land_count)
        wastes_count = self.rec_land_count if plains_count == islands_count == swamps_count == mountains_count == forest_count == 0 else 0

        # Put it into a dictionary
        basic_counts = {"Plains": plains_count,
                        "Island": islands_count,
                        "Swamp": swamps_count,
                        "Mountain": mountains_count,
                        "Forest": forest_count,
                        "Wastes": wastes_count
                        }

        # Make sure it recommends the correct number of lands
        difference = round(self.rec_land_count) - sum(basic_counts.values())
        max_land = max(basic_counts, key=basic_counts.get)

        # If it doesn't, make the change on the most common basic type
        if difference > 0:
            basic_counts[max_land] += difference
        elif difference < 0:
            basic_counts[max_land] -= difference

        # Remove any basics where there are 0 recommended
        for key, value in list(basic_counts.items()):
            if value == 0:
                basic_counts.pop(key)

        # Store it
        self.basics = basic_counts

    """Replace some basics with the best nonbasic lands for the colors"""
    def rec_non_basics(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass





    """
    TO-DO:
    - Account for MDFCs in Archidekt
    - Create a list of recommended lands
        - Manually compile a list of the "best" nonbasics
        - Replace some basics with non-basics
        - Frank Karsten ratios
    - Add a budget option - it won't recommend lands over $X
    - str
    - repr
    """


