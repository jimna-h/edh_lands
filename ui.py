import tkinter as tk
from tkinter import filedialog
from Deck import Deck
import grab_from_archidekt as Arch
import threading
from Card import Card


# Handle file upload and submit
def upload_file():
    filepath = filedialog.askopenfilename()

    # Display the filepath on screen
    if filepath:
        file_label.config(text=filepath)
    else:
        file_label.config(text="")

# Process the uploaded file
def submit_file():

    # Set up the variables
    commander1 = commander1_entry.get()
    commander2 = commander2_entry.get() or None
    file_path = file_label.cget("text")

    # Create the Deck object
    if file_path:
        my_deck = Deck(commander1, commander2)
        my_deck.import_decklist_from_file(file_path)

        # Display stats
        update_stats_output(my_deck)
    else:
        update_stats("No file selected.")


# Handle username and deck name submit
def submit_username_deck():
    username = username_entry.get()
    deck_name = deck_name_entry.get()

    # Create the Deck object and display stats
    try:
        my_deck = Deck.import_decklist_from_archidekt(username, deck_name)
        update_stats_output(my_deck)
    except Exception as e:
        update_stats(f"Error loading deck: {e}")


# Handle URL submit
def submit_url():
    url = url_entry.get()

    try:
        # Grab the data from Archidekt
        my_decklist, commanders = Arch.get_archidekt_deck(Arch.extract_deck_id(url))

        # Create the Deck object and display stats
        my_deck = Deck(commanders[0], commanders[1])
        my_deck.import_decklist_from_text(Arch.archidekt_string(my_decklist))
        update_stats_output(my_deck)
    except Exception as e:
        update_stats(f"Error loading deck: {e}")


# Handle large list submit
def submit_large_list():
    commander1 = commander1_entry.get()
    commander2 = commander2_entry.get() or None
    large_list = list_text.get(1.0, tk.END).strip()

    # Create a Deck object and display stats
    if large_list:
        my_deck = Deck(commander1, commander2)
        my_deck.import_decklist_from_text(large_list)
        update_stats_output(my_deck)
    else:
        update_stats("No list provided.")


# Output stats the same, no matter what input method was used
def update_stats_output(my_deck):
    message = f"""Here are some stats for your deck:

Commanders: {my_deck.commander}
Color Identity: {my_deck.identity}
Average Mana Value: {my_deck.avg_manavalue}
Total Price: ${my_deck.total_price}
Current Land Count: {my_deck.land_count}
mdfc Land Count: {my_deck.mdfc_untapped}


{my_deck.comparison_statement}
    
You should play these basics: 
{my_deck.basics}
(I'll get to nonbasic lands later)
"""

    update_stats(message)


# Updates the stats display with new content
def update_stats(content):
    stats_text.config(state=tk.NORMAL) # Enable editing
    stats_text.delete(1.0, tk.END) # Clear content
    stats_text.insert(tk.END, content) # Add new content
    stats_text.config(state=tk.DISABLED) # Disable editing



# ---------- Placeholder handling for deck list input box ----------

# Clears the placeholder when user clicks inside text box
def on_focus_in(event):
    if list_text.get(1.0, tk.END).strip() == "Must use the format:\n1x CardName\n1x CardName":
        list_text.delete(1.0, tk.END)


# Restores the placeholder if text box is empty when user clicks away
def on_focus_out(event):
    if not list_text.get(1.0, tk.END).strip():
        list_text.insert(tk.END, "Must use the format:\n1x CardName\n1x CardName")


# ---------- Main GUI ----------

root = tk.Tk()
root.title("Commander & Deck Input Form")


# ---------- Frames Setup (Divide window into sections ----------

# Left Frame (Commanders, File, List)
left_frame = tk.Frame(root)
left_frame.grid(row=0, column=0, sticky="nsew")

# Middle Frame (Username, Deck_Name, URL)
middle_frame = tk.Frame(root)
middle_frame.grid(row=0, column=1, sticky="nsew")

# Right Frame (Stats Output)
right_frame = tk.Frame(root)
right_frame.grid(row=0, column=2, rowspan=2, sticky="nsew")


# ---------- Commander Section ----------

commander_frame = tk.Frame(left_frame)
commander_frame.pack(pady=10)

tk.Label(commander_frame, text="Commander 1:").pack()
commander1_entry = tk.Entry(commander_frame)
commander1_entry.pack(pady=5)

tk.Label(commander_frame, text="Commander 2:").pack()
commander2_entry = tk.Entry(commander_frame)
commander2_entry.pack(pady=5)


# ---------- File Upload Section ----------

file_frame = tk.Frame(left_frame)
file_frame.pack(pady=10)

tk.Label(file_frame, text="File Upload", font=("Helvetica", 14, "bold")).pack(pady=5)

file_label = tk.Label(file_frame, text="Select a txt file\nwith the same format as below")
file_label.pack()
tk.Button(file_frame, text="Upload File", command=upload_file).pack(pady=5)
tk.Button(file_frame, text="Submit File", command=submit_file).pack(pady=5)


# ---------- Large List Section ----------

list_frame = tk.Frame(left_frame)
list_frame.pack(pady=10)

tk.Label(list_frame, text="Enter Decklist", font=("Helvetica", 14, "bold")).pack(pady=5)

list_text = tk.Text(list_frame, height=10, width=30)
list_text.pack(pady=5)
list_text.insert(tk.END, "Must use the format:\n1x CardName\n1x CardName")
list_text.bind("<FocusIn>", on_focus_in)
list_text.bind("<FocusOut>", on_focus_out)

tk.Button(list_frame, text="Submit List", command=submit_large_list).pack(pady=5)


# ---------- Username & Deck_Name Section ----------

username_frame = tk.Frame(middle_frame)
username_frame.pack(pady=10)

tk.Label(username_frame, text="Archidekt\nUsername and Deck Name", font=("Helvetica", 14, "bold")).pack(pady=5)

tk.Label(username_frame, text="Username:").pack()
username_entry = tk.Entry(username_frame)
username_entry.pack(pady=5)

tk.Label(username_frame, text="Deck Name:").pack()
deck_name_entry = tk.Entry(username_frame)
deck_name_entry.pack(pady=5)

tk.Button(username_frame, text="Submit Username/Deck Name", command=submit_username_deck).pack(pady=10)


# ---------- URL Section ----------

url_frame = tk.Frame(middle_frame)
url_frame.pack(pady=10)

tk.Label(url_frame, text="Archidekt\nDeck URL", font=("Helvetica", 14, "bold")).pack(pady=5)

url_entry = tk.Entry(url_frame)
url_entry.pack(pady=5)

tk.Button(url_frame, text="Submit URL", command=submit_url).pack(pady=5)


# ----- New Data Gathering Button -----

def get_new_data():
    # Update label immediately
    get_data_status.config(text="Getting new data...\nThis will take a while...")

    # Start long task in background thread
    threading.Thread(target=run_long_task, daemon=True).start()

def run_long_task():
    try:
        Card.get_new_data()
        # Now update label back in GUI thread when done
        root.after(0, lambda: get_data_status.config(text="New data gathered!"))
    except Exception as e:
        root.after(0, lambda: get_data_status.config(text=f"Error: {e}"))

# ---------- Get New Data Section ----------

get_data_frame = tk.Frame(middle_frame)
get_data_frame.pack(pady=10)

tk.Label(get_data_frame, text="Update Card Database", font=("Helvetica", 14, "bold")).pack(pady=5)

# Label for showing status messages
get_data_status = tk.Label(get_data_frame, text="", font=("Helvetica", 10, "italic"))
get_data_status.pack(pady=5)

# Button to trigger the threaded data gathering
tk.Button(get_data_frame, text="Get New Data", command=get_new_data).pack(pady=5)



# ---------- Stats Output ----------

tk.Label(right_frame, text="Stats Output", font=("Helvetica", 14, "bold")).pack()

stats_text = tk.Text(right_frame, height=30, width=50, wrap=tk.WORD)
stats_text.pack(pady=10)
stats_text.config(state=tk.DISABLED)


# ---------- Grid Configuration ----------

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=2)
root.grid_rowconfigure(0, weight=1)

# ---------- Set fixed window size ----------

root.geometry("1000x600")
root.resizable(False, False)

# ---------- Start GUI ----------

root.mainloop()
