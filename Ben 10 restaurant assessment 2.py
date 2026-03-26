# Ben 10 restaurant assessment 2.py
#======================================================================================================
#Restaurant Greeting and Menu System - XlR8 Speed Grill
#======================================================================================================
# This application allows a customer to:
#   1. Declare any food allergens thay have
#   2. Browse a themed menu filtered to safe food items for puchase
#   3. Place an order with allergen conflict checking
#   4. Save their order to a CSV (Comma-Seperated Values) File (file I/O)
#   5. Load the menu form a CSV file on start-up file (File I/O)
#   6. Save and load allergens using a loyalty code (new feature!)
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
        name = input(prompt).strip() # Ask the user for input and remove leading/trailing whitespace
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
    pattern = re.compile(r"^[A-Z]{3}\d{3}$") # Compile the regex pattern once for effieiency 
    while True:
        code = input(prompt).strip().upper() #Ask the user for input, remove leading/trailing whitespace and convert to uppercase
        if code =="SKIP": #Allow the user to skip entering a loyalty code
            return None
        if pattern.match(code): #Check if the code matches the pattern
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
    
    def is_safe_for(self, customer_allergens):
        """
        Returns True if not the item's allergens in the customer's declared allergens list, False otherwise.
        This method is inherited and available on all subclasses, allowing us to easily check if a menu item is safe for a customer based on their allergens.
        """
        for allergen in self.allergens:
            # Case-insensitive Substring check so partial matches are caught
            for ca in customer_allergens:
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
LOYALTY_CSV = "loyalty_customers.csv" # path to the loyalty customer data CSV file


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
    
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            allergens = row["allergens"].split(";") if row["allergens"] else []
            if row["subclass_type"] == "drink":
                items.append(DrinkItem(row["item_type"], row["name"],
                                       row["price"], allergens))
            else:
                items.append(FoodItem(row["item_type"], row["name"],
                                         row["price"], "Unknown", allergens))
    return items

def save_order_to_csv(customer_name, loyalty_code, order_items, total):
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
            writer.writerow([customer_name, loyalty_code or "N/A",
                             item.name, item.price,
                             str(total)])

def load_loyalty_customer_allergens(loyalty_code):
    """
    Loads saved allergens for a loyalty code from the loyalty customers CSV.
    Returns a list of allergens if found, None if the loyalty code has no saved data.
    """
    if not os.path.exists(LOYALTY_CSV):
        return None
    
    with open(LOYALTY_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["loyalty_code"] == loyalty_code:
                allergens = row["allergens"].split(";") if row["allergens"] else []
                return allergens
    return None

def save_loyalty_customer_allergens(loyalty_code, customer_name, allergens):
    """
    Saves or updates a customer's allergens in the loyalty customers CSV.
    If the loyalty code already exists, it updates the record. Otherwise, it creates a new one.
    """
    file_exists = os.path.exists(LOYALTY_CSV)
    existing_records = []
    code_exists = False
    
    # Read existing records if the file exists
    if file_exists:
        with open(LOYALTY_CSV, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["loyalty_code"] == loyalty_code:
                    code_exists = True
                    # Update the record with new allergen data
                    row["allergens"] = ";".join(allergens)
                    row["customer_name"] = customer_name
                existing_records.append(row)
    
    # If loyalty code doesn't exist, add a new record
    if not code_exists:
        existing_records.append({
            "loyalty_code": loyalty_code,
            "customer_name": customer_name,
            "allergens": ";".join(allergens)
        })
    
    # Write all records back to the file
    with open(LOYALTY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["loyalty_code", "customer_name", "allergens"])
        writer.writeheader()
        writer.writerows(existing_records)


#------------------------------------------------------------------------------------------------------
# Default Menu Data (used on first run before the menu.csv exists)
#------------------------------------------------------------------------------------------------------

DEFAULT_MENU = [
    FoodItem("Starter", "Gray Matter Mini Sliders", 6.00, "American", 
             ["Celerals containing gluten (Wheat, barley, rye, oats)", "Milk / Dairy"]),
    FoodItem("Starter", "Wildmutt Monster Bites", 5.50, "Fusion", 
             ["Gluten", "Milk / Dairy"]),
    FoodItem("Starter", "Four arms Spicy Wings", 9.00, "American", 
             ["allergen friendly"]),
    FoodItem("Main", "Ben 10 Hero Burger", 12.00, "American", 
             ["Gluten", "Milk / Dairy", "Eggs", "Sesame", "Mustard"]),
    FoodItem("Main", "Heatblast Fiery Pizza", 12.00, "Italian", 
             ["Gluten", "Milk / Dairy", "Eggs"]),
    FoodItem("Main", "Diamondhead crystal pasta salad", 8.50, "Italian", 
             ["Gluten", "Milk / Dairy", "Eggs"]),
    FoodItem("Main", "Upgrade Mac and Cheese", 10.00, "American", 
             ["Gluten", "Milk / Dairy"]),
    FoodItem("Dessert", "Big Chill Sundae", 10.00, "American", 
             ["Milk / Dairy", "Gluten"]),
    FoodItem("Dessert", "Omnitrix Donuts", 6.00, "American", 
             ["Gluten", "Milk / Dairy", "Eggs"]),
    FoodItem("Dessert", "Goop Jelly Cups", 3.00, "Fusion", 
             ["Gluten", "Milk / Dairy"]),
    FoodItem("Dessert", "Ben's Cosmic Cookies", 5.00, "American", 
             ["Gluten", "Milk / Dairy", "Eggs"]),
    DrinkItem("Drink", "XLR8 Speed Shake", 6.00, 
              ["Milk / Dairy"]),
    DrinkItem("Drink", "Omnitrix Energy Punch", 5.00, 
              ["allergen friendly"]),
    DrinkItem("Drink", "Kevin 11 Chaos Cola", 4.50, 
              ["allergen friendly"]),
    DrinkItem("Drink", "Gwen's Magic Berry Smoothie", 6.00, 
              ["Milk / Dairy", "contains yogurt"]),
]
# Full allergen reference list for customer information and menu item allergen tagging
ALLERGENS_LIST = [
    "Cereals contains gluten (wheat, barley, rye, oats)",
    "Milk / Dairy",
    "Eggs",
    "Peanuts",
    "Tree nuts (almonds, walnuts, cashews, etc.)",
    "Soybeans / Soy",
    "Fish",
    "Shellfish (shrimp, crab, lobster, etc.)",
    "Molluscs (clams, mussels, oysters, etc.)"
    "Sesame seeds",
    "Celery",
    "mustard",
    "Sulphur dioxide and sulphites",
    "Lupin",
]

# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

def main():
    # -- Greeting -----------------------------------------------------------
    print("=" * 65)
    print("       Welcome to XLR8 Speed Grill!")
    print("=" * 65)

    #Collect and validate customer name using regex utility
    customer_name = validate_name("May I take your name? ")
    print(f"\nGreat to have you with us, {customer_name}!\n")

    # Collect optional loyalty code using regex utility
    loyalty_code = validate_loyalty_card(
        "Do you have a loyalty code? (e.g. XLR001 - or type 'skip'): "
    )
    if loyalty_code:
        print(f"  Loyalty code {loyalty_code} noted - thank you\n")

    # -- Load menu (form CSV if it exists, otherwise use hardcoded default) - 
    menu = load_menu_form_csv(MENU_CSV)
    if not menu:
        # First run: use defaults and persist them to CSV for future runs
        menu = DEFAULT_MENU
        save_menu_to_csv(menu)
        print("  [info] Menu loaded form defaults and saved to menu.csv.\n")
    else:
        print("  [Info] Menu loaded form menu.csv.\n")

    # -- Allergen declaration -------------------------------------------------------
    customer_allergens = []
    
    # Check if loyalty code has saved allergens
    saved_allergens = None
    if loyalty_code:
        saved_allergens = load_loyalty_customer_allergens(loyalty_code)
        if saved_allergens:
            print(f"  We found saved allergies on your loyalty account: {', '.join(saved_allergens)}")
            use_saved = validate_yes_no("  Would you like to use these saved allergies? (yes/no): ")
            if use_saved == "yes":
                customer_allergens = saved_allergens
                print(f"  Allergies loaded from your loyalty account.\n")
            else:
                print("  You can enter new allergies instead.\n")
    
    # If no saved allergens were used, ask customer for allergen input
    if not customer_allergens:
        allergen_response = validate_yes_no(
            "Do you have any food allergies we should know about? (yes/no): "

        )

        if allergen_response == "no":
            print("\nUnderstood! If anything changes, just let us know.\n")
        else:
            print("\nThank you for letting us know. Here are the allergens present")
            print("in our kitchen - please tell us which apply to you:\n")
            for i, allergen in enumerate(ALLERGENS_LIST, start=1):
                print(f" {i:>2}. {allergen}")

            print("\nEnter your allergens one at a time.")
            print("Type 'done' when you have finished.\n")

            while True:
                entry = input(" Allergen: ").strip()
                if entry.lower() == "done":
                    break
                if entry:
                    # Check if the entered allergen is in the recognized list
                    if entry.lower() not in [allergen.lower() for allergen in ALLERGENS_LIST]:
                        print(f" [!] '{entry}' is not in our recognized allergens list. Please double-check the spelling or choose from the list above.")
                    customer_allergens.append(entry)
                    print(f" Added: {entry}")

    if customer_allergens:
        print(f"\n Recorded allergens: {', '.join(customer_allergens)}")
    print("\nWe will filter the menu to show only item that are safe for you.\n")

    # -- Display (filtered) menu --------------------------------------------
    see_menu = validate_yes_no("Would you like to see the meny? (yes/no): ")

    if see_menu == "no":
        print("\nNo problem! Come back any time - we hope to see you soon.")
        return

    print("\n" + "=" * 65)
    print("  OUR MENU")
    print("=" * 65)

    # Group items by catagory for a cleaner display 
    categories = ["Starter", "Main", "Dessert", "Drink"]
    safe_items = [] # Keep track of items the customer can safely order

    for category in categories:
        category_items = [item for item in menu if item.item_type == category]
        if not category_items:
            continue

        print(f"\n -- {category.upper()} --")
        for item in category_items:
            if item.is_safe_for(customer_allergens):
                print(item.display())
                safe_items.append(item)
            else:
                #show item but clearly flag it as unsafe
                print(f" [ALLERGEN WARNING] {item.name} - contains one or more of your allergens.")

    print("\n" +"=" *65)

    # -- Order taking -------------------------------------------------------------------

    order = []
    total = Decimal("0.00")


    print("\nplease enter the name of each item you would like to order.")
    print("Type 'done' when you have finished.\n")

    while True:
        choice = input("Item name: ").strip()
        if choice.lower() == "done":
            break

        if not choice:
            continue

        found = False 
        for item in menu:
            if item.name.lower() == choice.lower():
                found = True

                # Check allergen conflict before adding to order 

                if not item.is_safe_for(customer_allergens):
                    print(f" [!] Sorry - {item.name} contains allergens you declared.")
                    print("    Please choose a different item.")
                else:
                    order.append(item)
                    total += item.price
                    print(f"  ✓ {item.name} added to your order (£{item.price:.2f}).")
                break

        if not found:
            print(" [!] That item wasn't found. Please check the spelling and try again.")


    # -- Order summary ------------------------------------------------------

    print("\n" + "=" * 65)

    if not order:
        print(" No items were ordered. We hope to serve you next time!")

    else:
        print(" YOUR ORDER SUMMARY")
        print("=" * 65)
        for item in order:
            print(f" {item.name:<40} £{item.price:.2f}")
        print("-" * 65)
        print(f" {'TOTAL':<40} £{total:.2f}")
        print("=" * 65)

    # Save the order to CSV (File I/O - write)
    save_order_to_csv(customer_name, loyalty_code, order, total)
    print(f"\n Order saved to '{ORDER_CSV}'.")
    
    # Save loyalty customer allergen data if they have a loyalty code and allergens
    if loyalty_code and customer_allergens:
        save_loyalty_customer_allergens(loyalty_code, customer_name, customer_allergens)
        print(f" Allergies saved to your loyalty account for future visits.")
    
    print(f"\n Thank you for dining at XLR8 Speed Grill, {customer_name}!")
    print(" We hope to see you again soon!\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
 
if __name__ == "__main__":
    main()