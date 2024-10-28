import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import csv
import os

# Define the CSV file name and headers
CSV_FILE = './Data/inventory.csv'
FIELDNAMES = ['ean', 'amount', 'name', 'popular']

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
        self.root.title("Inventory Management")
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
        self.tree = ttk.Treeview(self.root, columns=FIELDNAMES, show='headings')
        for field in FIELDNAMES:
            self.tree.heading(field, text=field)
            self.tree.column(field, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Frame for action buttons
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.X)

        # Add, Edit, Delete, and Import buttons
        self.add_button = tk.Button(frame, text="Add Item", command=self.add_item)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.edit_button = tk.Button(frame, text="Edit Item", command=self.edit_item)
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = tk.Button(frame, text="Delete Item", command=self.delete_item)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        # New Import CSV button
        self.import_button = tk.Button(frame, text="Import CSV", command=self.import_csv)
        self.import_button.pack(side=tk.LEFT, padx=5, pady=5)

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
        self.item_window(None)

    def edit_item(self):
        """Opens a window to edit the selected item."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an item to edit.")
            return
        index = int(selected[0])
        self.item_window(index)

    def delete_item(self):
        """Deletes the selected item after confirmation."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an item to delete.")
            return
        index = int(selected[0])
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?")
        if confirm:
            self.manager.delete_item(index)
            self.load_items()

    def item_window(self, index):
        """Creates a window to add or edit an item."""
        if index is not None:
            item = self.manager.items[index]
        else:
            item = None
        win = tk.Toplevel(self.root)
        win.title("Add/Edit Item")

        # EAN field
        tk.Label(win, text="EAN").grid(row=0, column=0, padx=5, pady=5)
        ean_entry = tk.Entry(win)
        ean_entry.grid(row=0, column=1, padx=5, pady=5)
        if item:
            ean_entry.insert(0, item.ean)

        # Amount field
        tk.Label(win, text="Amount").grid(row=1, column=0, padx=5, pady=5)
        amount_entry = tk.Entry(win)
        amount_entry.grid(row=1, column=1, padx=5, pady=5)
        if item:
            amount_entry.insert(0, str(item.amount))

        # Name field
        tk.Label(win, text="Name").grid(row=2, column=0, padx=5, pady=5)
        name_entry = tk.Entry(win)
        name_entry.grid(row=2, column=1, padx=5, pady=5)
        if item:
            name_entry.insert(0, item.name)

        # popular field
        tk.Label(win, text="popular (Y/N)").grid(row=3, column=0, padx=5, pady=5)
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
                messagebox.showwarning("Input Error", "Please fill all fields.")
                return
            try:
                amount_int = int(amount)
            except ValueError:
                messagebox.showwarning("Input Error", "Amount must be an integer.")
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
            title="Select CSV File",
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
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
