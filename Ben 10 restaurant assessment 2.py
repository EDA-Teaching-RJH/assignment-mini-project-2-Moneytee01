#======================================================================================================
#Restaurant Greeting and Menu System - XlR8 Speed Grill
#======================================================================================================
# This application allows a customer to:
#   1. Declare any food allergens thay have
#   2. Browse a themed menu filtered to safe food items for puchase
#   3. Place an order with allergen conflict checking
#   4. Save their order to a CSV (Comma-Seperated Values) File (file I/O)
#   5. Load the menu form a CSV file on start-up file (File I/O)

#
# Demonstrates: OOP (Object-Oriented Programming) With inheritance, regex input validation, file I/O,
# A custom utility library module and structured programiming flow.
#======================================================================================================


import csv
import os
import re
from decimal import Decimal

#------------------------------------------------------------------------------------------------------
# Custom utility library (inline module-style functions)
# In a full project these would live in a separate XLR8_utils.py file
# BE imported with: form XLR8_utils import validate_yes_no, validate_name
#------------------------------------------------------------------------------------------------------


def validate_yes_no(prompt):
    """
    Utility: Repeatedly prompts the user until they enter 'yes'
or 'no'
    Uses regex to accept flexible casing(Yes / YES / no / NO etc.)
    Returns the lowercased response string.
    """ 
    # The entire string is exactly "yes" or "no" according to the pattern.
    # case-insensitive.

    pattern = re.compile(r"^(yes|no)$", re.IGNORECASE) # For efficiency, compile the regex pattern once.
    while True:
        response = input(prompt).strip() # Request input from the user and eliminate leading and trailing whitespace
        if pattern.match(response):# check if the response matches the pattern
            return response.lower() # Return the response in lowercase for consistency
        print(" [!] please enter 'yes' or 'no'.") # Prompt the user to enter a valid response if they didn't match the pattern


def validate_name(prompt):
    """
    Utility: Validates that a customer name contains only letters and spaces.
    Uses regex to reject numeric or special-character input.
    Returns the stripped name string.
    """
    # Pattern: one or more letters or spaces, from start to end of the string. Case-insensitive.
    pattern = re.compile(r'^[A-Za-z\s]+$') #Compile the regex pattern once for efficiency
    while True:
        name = input(prompt).string.strip() # Ask the user for input and remove leading/trailing whitespace
        if pattern.match(name):
            return name
        print(" [!] Name must contain letters only (no numbers or symbols).")

def validate_loyalty_card(prompt):
    """
    Utility: Validates that the loyalty code in the format XXX000 (three uppercase letters followed by three digits), e.g XLR001.
    Uses regex for pattern matching.
    Returns the uppercsed code, or None if the user skips.
    """

    #pattern: exactly 3 uppercase letters followed by exactly 3 digits.
    pattern = re.compile(r"^[A-Z]{3}$") #Compile the regex pattern once for efficiency
    while True:
        code = input(prompt).strip().upper() #Ask the user for input, remove leading/trailing whitespace and convert to uppercase
        if code =="SKIP": #Allow the user to skip entering a loyalty code
            return None
        if pattern.matches(code): #Check if the code matches the pattern
            return code #Return the valid loyalty code
        print(" [!] Code must be 3 letters followed by 3 digits (e.g. XLR001).") #Prompt the user to enter a valid code if they didn't match the pattern
        print("   Type 'SKIP' to continue without a code.") #inform the user they can skip entering a code

#------------------------------------------------------------------------------------------------------
#OPP: Base class and subclass for Menu Items
#------------------------------------------------------------------------------------------------------

class MenuItemBase:
    """
    Abstract base class for all items that can appear on the menu.
    stores the common attributes shared by every menu item type.
    """

    def __init__(self, item_type, name, price, allergens=None):
        self.item_type = item_type # The catagory of the menu item (e.g. Starter, Main, Dessert, Drink)
        self.name = name # The name of the menu item (e.g. "Ben 10 Hero Burger")
        self.price = Decimal(str(price)) # The price of the menu item, stored as a Decimal for accurate currency repersentation
        self.allergens = allergens or [] #A list of allergens present in the menu item, defaulting to an empty list if not provided
    
    def is_safe_for(self, customer_allergns):
        """
        Returns True if not the item's allergens in the customer's declared allergens list, False otherwise.
        This method is inherited and available on all subclasses, allowing us to easily check if a menu item is safe for a customer based on their allergens.
        """
        for allergen in self.allergens:
            # Case-insensitive Substring check so partial matches are caught
            for ca in customer_allergns:
                if ca.lower() in allergen.lower() or allergen.lower() in ca.lower():
                    return False
        return True
    
    def display(self):
        """
        Returns a formatted one-line string representation of the menu item,"""
        allergen_str = ", ".join(self.allergens) if self.allergens else "None"
        return f" [{self.item_type}] {self.name:<35} £{self.price:.2f} Allergens: {allergen_str}"
    
    def to_csv_row(self):
        """
        Retuens a list suitable for writing as a CSVrow."""
        return [self.item_type, self.name, str(self.price), ";".join(self.allergens)]

class FoodItem(MenuItemBase):
    """
    Subclass of MenuItemBase repersenting food items (Starters, Mains, Desserts).
    Adds a 'cuisine_style' attribute to specific to food items.
    """

    def __init__(self, item_type, name, price, cuisine_style, allergens=None):
        # Call the parent class constructor or set the common attributes directly
        super().__init__(item_type, name, price, allergens) # Call the base class constructor to initialize common attributes
        self.cuisine_style = cuisine_style # The cuisine style of the food item (e.g. "American", "Italian", "Mexican" etc.)

    def display(self):
        """
        Override the base display to include cuisine style in the formatted string representation of the food item."""
        base_display = super().display() # Get the base display string from the parent class
        return f"{base_display} Cuisine: {self.cuisine_style}" # Append the cuisine style information to the base display string

class DrinkItem(MenuItemBase):
    """
    Subclass of MenuItemBase representing drink items.
    Inherits all attributes and methods from the base class.
    """

    def __init__(self, item_type, name, price, allergens=None):
        super().__init__(item_type, name, price, allergens)

#------------------------------------------------------------------------------------------------------
# File I/O: Menu CSV Helpers
#------------------------------------------------------------------------------------------------------


MENU_CSV = "menu.csv" # path to the menu CSV file
ORDER_CSV = "orders.csv" # path to the orders CSV file


def save_menu_to_csv(menu, filename=MENU_CSV):
    """
    Saves the Full menu to MENU_CSV so it can be loaded on future runs.
    Each row: item_type, name, price, allergens (pipe-seperated), Subclass_type
    """
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["item_type", "name", "price", "allergens", "subclass_type"]) #Write the header row
        for item in menu:
            subclass = "drink" if isinstance(item, DrinkItem) else "food"
            writer.writerow(item.to_csv_row() + [subclass]) #Write the item data along with its subclass type


def load_menu_form_csv(filepath):
    """
    Reads the menu form a CSV file and reconstructs the foodItem / DrinkItem objects.
    Returns a list of MenuItemBase subclass instances.
    If the file does not exist, returns an empty list.
    """
    items = []
    if not os.path.exists(filepath):
        return items #Returns an empty list if the file doesn't exist
    
    with open(filepath, "r", newline="", encoding="utf-8") as f
    reader = csv.DictReader(f)
    for row in reader:
        allergens = row["allergens"].split("|") if row["allergens"] else []
        if row["subclass"] == "drink":
            items.append(DrinkItem(row["item_type"], row["name"],
                                   row["price"], allergens))
        else:
            items.append(FoodItem(row["item_type"], row["name"],
                                     row["price"], "Unknown", allergens))
    return items

def save_order_to_csv(customer_name, lotalty_code, order_items, total):
    """
    Appends the customer's completed order to ORDERS_CSV.
    Each item in the order is written as a seperate row, with the customer name and order total repeated on each row for easy parsing.
    """
    file_exists = os.path.exists(ORDER_CSV)

    with open(ORDER_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write the header row if the file is being created for the first time
        if not file_exists:
            writer.writerow(["customer_name", "loyalty_code", "item_name", "item_price", "order_total"])
        for item in order_items:
            writer.writerow([customer_name, lotalty_code or "N/A",
                             item.name, item.price,
                             str(total)])



