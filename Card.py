import requests
import time
import json

# Index bulk data
with open("scryfall_all.json", 'r') as bulkfile:
    bulkdata = json.load(bulkfile)
card_index = {card['name']: card for card in bulkdata}

# Index data of the cheap ramp/draw
with open("cheap_list.json", 'r') as cheapfile:
    cheap_list = json.load(cheapfile)
cheap_index = {card['name']: card for card in cheap_list}

# Index tapped mdfc data
with open("mdfc_tapped.json", 'r') as tappedfile:
    tapped_list = json.load(tappedfile)
tapped_index = {card['name']: card for card in tapped_list}

# Index untapped mdfc data
with open("mdfc_untapped.json", 'r') as UNtappedfile:
    UNtapped_list = json.load(UNtappedfile)
UNtapped_index = {card['name']: card for card in UNtapped_list}

# Index dfc data
with open("dfc.json", 'r') as dfcfile:
    dfc_list = json.load(dfcfile)
dfc_index = {card['name']: card for card in dfc_list}







class Card:

    """Create a Card object"""
    def __init__(self, name, cost, manavalue, identity, price, types):
        self.name = name
        self.cost = cost
        self.manavalue = manavalue
        self.identity = identity
        self.pips = {"W": 0,
                     "U": 0,
                     "B": 0,
                     "R": 0,
                     "G": 0}
        self.det_pips()
        self.price = price
        self.types = types

    """Count the number of each colored pip in a card"""
    def det_pips(self):

        for symbol in self.cost:
            if symbol in self.pips:
                self.pips[symbol] += 1

    """Check if a card falls within a certain color identity"""
    def check_id(self, given):
        for symbol in self.identity:
            if symbol not in given:
                return False
        return True

    """Check to see if the card is cheap ramp/draw"""
    def is_cheap(self):
        if cheap_index.get(self.name) is None:
            return False
        return True

    """Check to see if the card is an mdfc land"""
    def is_mdfc(self):
        if tapped_index.get(self.name) is not None:
            return True, "tapped"
        if UNtapped_index.get(self.name) is not None:
            return True, "untapped"
        if dfc_index.get(self.name) is not None:
            return True, "dfc"
        return False, None

    """Given a card name, create a Card object
    First search data downloaded to the pc,
    Then search Scryfall if not found"""
    @staticmethod
    def get_card_by_name(name):

        card = card_index.get(name)

        # If the card isn't in our data, grab it online
        if card is None:
            print(f"{name} not found in our dataset, searching Scryfall...")
            card = Card.search_card(name)

        # If we still don't have the card's data, give up
        if card is None:
            print(f"{name} not found on Scryfall.")
            return

        # Extract relevant data
        name = card['name']
        cost = card.get('mana_cost', 'N/A')
        mana_value = card.get('cmc', 0)
        identity = card.get('color_identity', [])
        price = card['prices'].get('usd', 'Price not available')
        types = card.get('type_line', 'Unknown type')

        # Create and return the Card object
        return Card(name, cost, mana_value, identity, price, types)

    "Search for a card on Scryfall"
    @staticmethod
    def search_card(name):

        query = f'!"{name}" cheapest:usd'
        card_data = Card.search_scryfall(query)
        if len(card_data) == 0:
            raise ValueError(f"No card found for {name}")
        card = card_data[0]

        return card

    "Search scryfall with a query"
    @staticmethod
    def search_scryfall(query):
        # Define headers as required by Scryfall
        headers = {
            "User-Agent": "MyMTGProject/1.0",
            "Accept": "application/json"
        }

        # Base API search
        url = f"https://api.scryfall.com/cards/search?q={query}"

        all_cards = []
        while url:
            response = requests.get(url, headers=headers)

            # Check for rate limit error (429) and retry after some delay
            if response.status_code == 429:
                print("Rate limited! Waiting 1 second before retrying...")
                time.sleep(1)  # Wait before retrying
                continue  # Retry the same request

            data = response.json()

            # Confirm data type
            if data.get("object") != "list":
                print(f"Scryfall returned an error: {data.get('details', 'Unknown error')}")
                break

            # Add cards from this page
            all_cards.extend(data["data"])

            # Check if more pages exist
            url = data.get("next_page", None)

            # Respect Scryfall’s rate limit (100ms delay)
            time.sleep(0.1)

        return all_cards

    """Download all relevant data"""
    @staticmethod
    def get_new_data():
        print("Getting new data...")
        print("This will take a while...")
        Card.download_bulk_data()
        Card.download_cheap_data()
        Card.download_mdfc_tapped_data()
        Card.download_mdfc_untapped_data()
        Card.download_dfc_data()

    """Download bulk data for the cheapest version of every commander legal card"""
    @staticmethod
    def download_bulk_data():
        """Downloads Scryfall's full card database and saves only the cheapest version of each card."""

        # Define headers as required by Scryfall
        headers = {
            "User-Agent": "MyMTGProject/1.0",
            "Accept": "application/json"
        }

        # Get the URL for the bulk card data
        bulk_url = "https://api.scryfall.com/bulk-data"
        response = requests.get(bulk_url, headers=headers)
        bulk_data = response.json()

        # Find the default bulk data (all cards)
        all_cards_url = None
        for item in bulk_data["data"]:
            if item["type"] == "default_cards":  # This contains all non-digital cards
                all_cards_url = item["download_uri"]
                break

        if not all_cards_url:
            print("Failed to find bulk card data.")
            return

        print(f"Downloading bulk card data from {all_cards_url}...")

        # Download the full card database
        response = requests.get(all_cards_url)
        all_cards = response.json()

        # Dictionary to store only the cheapest version of each card
        cheapest_cards = {}

        for card in all_cards:
            name = card["name"]
            price = card["prices"].get("usd")

            # Ignore cards with no listed USD price
            if price is None:
                continue

            price = float(price)

            # If the card isn't stored yet OR if this version is cheaper, update it
            if name not in cheapest_cards or price < float(cheapest_cards[name]["prices"]["usd"]):
                cheapest_cards[name] = card

        # Convert dictionary to a list for saving
        cheapest_card_list = list(cheapest_cards.values())

        # Save to a local JSON file
        with open("scryfall_all.json", "w", encoding="utf-8") as file:
            json.dump(cheapest_card_list, file, indent=2)

        print(f"Saved {len(cheapest_card_list)} cheapest card versions to 'scryfall_all.json'.")

    """Download data for the cheapest version for all draw/ramp cards less than 4 mana"""
    @staticmethod
    def download_cheap_data():

        print("Downloading data on cheap draw and ramp from Scryfall...")

        cheap_list = Card.search_scryfall("f:edh cheapest:usd (function:ramp or function:draw) -mana:x cmc<4 -t:sticker -t:attraction")

        file_path = "cheap_list.json"

        with open(file_path, 'w') as json_file:
            json.dump(cheap_list, json_file, indent=4)

        print(f"Saved {len(cheap_list)} cheap ramp/draw cards saved to '{file_path}'")

    """Download data for all mdfc lands that DON'T enter untapped"""
    @staticmethod
    def download_mdfc_tapped_data():

        print("Downloading data on tapped mdfc lands from Scryfall...")

        mdfc_tapped = Card.search_scryfall(r'f:edh cheapest:usd -t:/^[^\/]*Land/ t:Land is:mdfc -o:"As this land enters, you may pay 3 life. If you don’t, it enters tapped."')

        file_path = "mdfc_tapped.json"

        with open(file_path, 'w') as json_file:
            json.dump(mdfc_tapped, json_file, indent=4)

        print(f"Saved {len(mdfc_tapped)} tapped mdfc lands saved to '{file_path}'")

    """Download data for all mdfc lands that CAN enter untapped"""
    @staticmethod
    def download_mdfc_untapped_data():

        print("Downloading data on untapped mdfc lands from Scryfall...")

        mdfc_untapped = Card.search_scryfall(r'f:edh cheapest:usd -t:/^[^\/]*Land/ t:Land is:mdfc o:"As this land enters, you may pay 3 life. If you don’t, it enters tapped."')

        file_path = "mdfc_untapped.json"

        with open(file_path, 'w') as json_file:
            json.dump(mdfc_untapped, json_file, indent=4)

        print(f"Saved {len(mdfc_untapped)} untapped mdfc lands saved to '{file_path}'")

    """Download data for all dfc lands that are NOT mdfcs"""
    @staticmethod
    def download_dfc_data():

        print("Downloading data on dfc lands from Scryfall...")

        dfc = Card.search_scryfall(r'f:edh cheapest:usd -t:/^[^\/]*Land/ t:Land -is:mdfc')

        file_path = "dfc.json"

        with open(file_path, 'w') as json_file:
            json.dump(dfc, json_file, indent=4)

        print(f"Saved {len(dfc)} dfc lands saved to '{file_path}'")












    """Load previously downloaded card data.
       This has been copied to the top of the page
       so this function doesn't currently get called"""

    """
    @staticmethod
    def load_card_data(filename):
        with open(filename, 'r') as file:
            data = json.load(file)

        # Create an index dictionary to map card names to their data
        card_index = {card['name']: card for card in data}
        return card_index
    """

    """Gives the most essential data for the card"""
    def __str__(self):
        return f"name: {self.name}\ncost: {self.cost}\nprice: {self.price}\n"

    """This is not what a repr function should do and I know that"""
    def __repr__(self):
        return f"{self.name}"







