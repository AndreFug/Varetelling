import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from PIL import Image, ImageTk
import csv
import os

# Define the CSV file name and headers
CSV_FILE = './Data/inventory.csv'
FIELDNAMES = ['ean', 'amount', 'name', 'popular']
Buttons = ['EAN', 'Antall', 'Navn', 'Populær']

class InventoryItem:
    """Represents a single inventory item."""
    def __init__(self, ean, amount, name, popular):
        self.ean = ean
        self.amount = int(amount)
        self.name = name
        self.popular = popular

class InventoryManager:
    """Manages inventory data loading and saving."""
    def __init__(self, filename):
        self.filename = filename
        self.items = []
        self.history = []
        self.load_inventory()

    def load_inventory(self):
        """Loads inventory data from the CSV file."""
        # Create the directory if it doesn't exist
        dir_name = os.path.dirname(self.filename)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

        # Create the file with headers if it doesn't exist
        if not os.path.isfile(self.filename):
            with open(self.filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                writer.writeheader()
        else:
            # Load existing data
            with open(self.filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                self.items = [
                    InventoryItem(row['ean'], row['amount'], row['name'], row['popular'])
                    for row in reader
                ]

    def save_inventory(self):
        """Saves inventory data to the CSV file."""
        with open(self.filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()
            for item in self.items:
                writer.writerow({
                    'ean': item.ean,
                    'amount': item.amount,
                    'name': item.name,
                    'popular': item.popular
                })

    def save_state(self):
        """Saves a snapshot of the current items for undo functionality."""
        # Deep copy the current state to avoid reference issues
        state = [InventoryItem(item.ean, item.amount, item.name, item.popular) for item in self.items]
        self.history.append(state)

    def undo(self):
        """Reverts to the last saved state, if available."""
        if not self.history:
            messagebox.showwarning("Angre", "Ingenting å angre")
            return

        # Restore the last saved state
        self.items = self.history.pop()
        self.save_inventory()


    def add_item(self, item):
        """Adds a new item to the inventory."""
        self.items.append(item)
        self.save_inventory()

    def update_item(self, index, item):
        """Updates an existing inventory item."""
        self.items[index] = item
        self.save_inventory()

    def delete_item(self, index):
        """Deletes an item from the inventory."""
        del self.items[index]
        self.save_inventory()

class InventoryGUI:
    """Creates the GUI for inventory management."""
    def __init__(self, root, manager):
        self.root = root
        self.manager = manager
        self.root.title("Bachus lagerbeholdning")
        logo_path = 'logo'  # Replace with your image file path
        self.logo_image = Image.open(logo_path)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)

        # Display the logo at the top of the window
        self.logo_label = tk.Label(self.root, image=self.logo_photo)
        self.logo_label.pack(pady=10)  # Adjust padding as needed
        self.create_widgets()
        self.load_items()

    def create_widgets(self):
        """Creates GUI widgets."""
        # Treeview for displaying inventory
        self.tree = ttk.Treeview(self.root, columns=Buttons, show='headings')
        for field in Buttons:
            self.tree.heading(field, text=field)
            self.tree.column(field, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Frame for action buttons
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.X)

        # Add, Edit, Delete, and Import buttons
        self.add_button = tk.Button(frame, text="Legg til linje", command=self.add_item)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.edit_button = tk.Button(frame, text="Rediger linje", command=self.edit_item)
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = tk.Button(frame, text="Slett linje", command=self.delete_item)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        # New Import CSV button
        self.import_button = tk.Button(frame, text="Importer endring", command=self.import_csv)
        self.import_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Undo button
        self.undo_button = tk.Button(frame, text="Angre" , command=self.undo)
        self.undo_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def load_items(self):
        """Loads items into the Treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Insert new items
        for idx, item in enumerate(self.manager.items):
            self.tree.insert('', 'end', iid=idx, values=(
                item.ean, item.amount, item.name, item.popular
            ))

    def add_item(self):
        """Opens a window to add a new item."""
        self.manager.save_state()
        self.item_window(None)
        


    def edit_item(self):
        selected = self.tree.selection()
        if selected:
            index = int(selected[0])
            item = self.manager.items[index]
            self.manager.save_state()
        else:
            ean = simpledialog.askstring("Endre linje", "Legg inn strekkoden til linjen du vil endre:")
            index = next((i for i, item in enumerate(self.manager.items) if item.ean == ean), None)
            if index is None:
                messagebox.showwarning("Feil EAN", f"Ingen linje med EAN {ean} er funnet i inventaret.")
                return
        self.item_window(index)

    def delete_item(self):
        selected = self.tree.selection()
        if selected:
            index = int(selected[0])
            item = self.manager.items[index]
            item_info = f"EAN: {item.ean}\nAntall: {item.amount}\nNavn: {item.name}\nPopulær: {item.popular}"
            self.manager.save_state()
            confirm = messagebox.askyesno("Er du sikker?", f"Sikker på at du vil slette denne linjen?\n\n{item_info}")
            if confirm:
                self.manager.delete_item(index)
                self.load_items()
        else:
            ean = simpledialog.askstring("Slett linje", "Legg inn strekkoden til linjen du vil slette:")
            if not ean:
                # messagebox.showwarning("Innlegg feil", "Legg inn korekt strekkode")
                return

            index = next((i for i, item in enumerate(self.manager.items) if item.ean == ean), None)
            if index is None:
                messagebox.showwarning("Feil EAN", f"Ingen linje med EAN {ean} er funnet i inventaret.")
            return

            item = self.manager.items[index]
            item_info = f"EAN: {item.ean}\nAntall: {item.amount}\nNavn: {item.name}\nPopulær: {item.popular}"
            self.manager.save_state()
            confirm = messagebox.askyesno("Er du sikker?", f"Sikker på at du vil slette denne linjen?\n\n{item_info}")
            if confirm:
                self.manager.delete_item(index)
                self.load_items()

    def undo(self):
        """Calls the undo function of the manager and refreshes the display."""
        self.manager.undo()
        self.load_items()

    def item_window(self, index):
        """Creates a window to add or edit an item."""
        if index is not None:
            item = self.manager.items[index]
        else:
            item = None
        win = tk.Toplevel(self.root)
        win.title("Legg til linje")

        # EAN field
        tk.Label(win, text="EAN").grid(row=0, column=0, padx=5, pady=5)
        ean_entry = tk.Entry(win)
        ean_entry.grid(row=0, column=1, padx=5, pady=5)
        if item:
            ean_entry.insert(0, item.ean)

        # Amount field
        tk.Label(win, text="Antall").grid(row=1, column=0, padx=5, pady=5)
        amount_entry = tk.Entry(win)
        amount_entry.grid(row=1, column=1, padx=5, pady=5)
        if item:
            amount_entry.insert(0, str(item.amount))

        # Name field
        tk.Label(win, text="Navn").grid(row=2, column=0, padx=5, pady=5)
        name_entry = tk.Entry(win)
        name_entry.grid(row=2, column=1, padx=5, pady=5)
        if item:
            name_entry.insert(0, item.name)

        # popular field
        tk.Label(win, text="Populær").grid(row=3, column=0, padx=5, pady=5)
        popular_entry = tk.Entry(win)
        popular_entry.grid(row=3, column=1, padx=5, pady=5)
        if item:
            popular_entry.insert(0, item.popular)

        def save_item():
            """Saves the new or edited item."""
            ean = ean_entry.get()
            amount = amount_entry.get()
            name = name_entry.get()
            popular = popular_entry.get()

            if not ean or not amount or not name or not popular:
                messagebox.showwarning("Innlegg feilet", "Fyll inn alle bokser.")
                return
            try:
                amount_int = int(amount)
            except ValueError:
                messagebox.showwarning("Innlegg feilet", "Må være et heltall.")
                return
            new_item = InventoryItem(ean, amount_int, name, popular)
            if index is not None:
                self.manager.update_item(index, new_item)
            else:
                self.manager.add_item(new_item)
            self.load_items()
            win.destroy()

        # Save button
        save_button = tk.Button(win, text="Save", command=save_item)
        save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def import_csv(self):
        """Imports items from a CSV file."""
        file_path = filedialog.askopenfilename(
            title="Velg filen for endring",
            filetypes=(("Excel filer", "*.xlsx"),("CSV Files", "*.csv"), ("All Files", "*.*"))
        )
        if not file_path:
            return  # User canceled the file dialog

        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                if reader.fieldnames != ['ean', 'amount', 'name']:
                    messagebox.showerror("Invalid CSV", "CSV file must have headers: ean, name, amount")
                    return

                for row in reader:
                    ean = row['ean']
                    amount = row['amount']
                    name = row['name']

                    try:
                        amount_int = int(amount)
                    except ValueError:
                        messagebox.showwarning("Invalid Data", f"Amount must be an integer for EAN {ean}. Skipping.")
                        continue

                    # Check if the item exists
                    existing_item = next((item for item in self.manager.items if item.ean == ean), None)
                    if existing_item:
                        # Adjust the amount of the existing item
                        new_amount = existing_item.amount + amount_int
                        if new_amount < 0:
                            messagebox.showwarning("Negative Inventory", f"Resulting amount for EAN {ean} would be negative. Setting amount to 0.")
                            existing_item.amount = 0
                        else:
                            existing_item.amount = new_amount
                    else:
                        if amount_int < 0:
                            messagebox.showwarning("Invalid Amount", f"Cannot add new item with negative amount for EAN {ean}. Skipping.")
                            continue
                        # Add new item with default popular value 'N'
                        new_item = InventoryItem(ean, amount_int, name, 'N')
                        self.manager.items.append(new_item)

                # Save changes and refresh display
                self.manager.save_inventory()
                self.load_items()
                messagebox.showinfo("Import Successful", "CSV file has been imported successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while importing the CSV file:\n{e}")

def main():
    root = tk.Tk()
    manager = InventoryManager(CSV_FILE)
    app = InventoryGUI(root, manager)
    root.mainloop()

if __name__ == '__main__':
    main()
