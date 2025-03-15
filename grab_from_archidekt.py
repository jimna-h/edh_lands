from bs4 import BeautifulSoup
from requests import get
from re import search

headers = {
    "User-Agent": "Mozilla/5.0"
}

"""Given a username and a deck name, this function returns the deck's url and id"""
def search_archidekt(owner_username, deck_name):

    # Build the search url
    deck_name_for_url = deck_name.replace(" ", "_")
    search_url = f"https://archidekt.com/search/decks?name={deck_name_for_url}&orderBy=-updatedAt&ownerUsername={owner_username}"

    # Make the search
    response = get(search_url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch:", response.status_code)
        return None, None

    # Parse the html into soup (whatever that means)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the url for the first deck (and by consequence, id)
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.startswith('/decks/'):
            deck_url = "https://archidekt.com" + href
            deck_id = extract_deck_id(deck_url)
            print("Found deck URL:", deck_url)
            print("Deck ID:", deck_id)
            return deck_url, deck_id

    print("Deck URL not found.")
    return None, None

"""Given a deck's url, this function returns the deck's id"""
def extract_deck_id(deck_url):
    match = search(r'/decks/(\d+)', deck_url)
    if match:
        return int(match.group(1))
    return None

"""Given a deck's id, this function returns a decklist and a list of commanders"""
def get_archidekt_deck(deck_id):

    # Open the provided deck
    url = f"https://archidekt.com/api/decks/{deck_id}/"
    response = get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    # Extract cards from the deck
    cards = []
    commanders = []
    for card in data['cards']:
        card_name = card['card']['oracleCard']['name']
        quantity = card['quantity']
        cards.append(f"{quantity}x {card_name}")
        if "Commander" in card.get('categories', []):
            commanders += [card['card']['oracleCard']['name']]

    if len(commanders) == 1:
        commanders += [None]
    return cards, commanders


"""Given a decklist in list form, return it as strings"""
def archidekt_string(decklist):
    ret = ""
    for card in decklist:
        ret += card + "\n"

    return ret

