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