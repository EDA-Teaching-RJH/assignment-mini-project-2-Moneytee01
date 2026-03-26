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
       return Name
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
        if patterns.matches(code): #Check if the code matches the pattern
            return code #Return the valid loyalty code
        print(" [!] Code must be 3 letters followed by 3 digits (e.g. XLR001).") #Prompt the user to enter a valid code if they didn't match the pattern
        print("   Type 'SKIP' to continue without a code.") #inform the user they can skip entering a code

        