import pandas as pd
from typing import List, Dict, Union, Any
import os
import pprint # Used for pretty printing the results during testing

# --- Part 1: Data Loading and Preparation ---

def load_hsn_data(file_path: str) -> Dict[str, str]:
    """
    Loads HSN data from an Excel file into an efficient in-memory dictionary.
    This function should be called once when the application starts.

    Args:
        file_path (str): The path to the HSN_Master_Data.xlsx file.

    Returns:
        Dict[str, str]: A dictionary mapping HSN codes to their descriptions.
                        Returns an empty dictionary if the file is not found or is invalid.
    """
    print(f"Attempting to load HSN data from: {file_path}")
    if not os.path.exists(file_path):
        print(f"--- CRITICAL ERROR: File not found at '{file_path}'. ---")
        return {}

    try:
        # Read the Excel file, ensuring HSNCode is treated as a string
        # to preserve leading zeros (e.g., '01').
        df = pd.read_excel(file_path, dtype={'HSNCode': str})

        # --- Data Cleaning and Validation of the Master File ---
        # Ensure required columns exist
        if 'HSNCode' not in df.columns or 'Description' not in df.columns:
            print("--- CRITICAL ERROR: Excel file must contain 'HSNCode' and 'Description' columns. ---")
            return {}
            
        # Drop rows where HSNCode is missing
        df.dropna(subset=['HSNCode'], inplace=True)
        
        # Clean the HSN codes: remove leading/trailing whitespace
        df['HSNCode'] = df['HSNCode'].str.strip()

        # Convert the cleaned DataFrame into a dictionary for fast lookups.
        # This is the most efficient structure for our validation task.
        hsn_map = pd.Series(df.Description.values, index=df.HSNCode).to_dict()
        
        print(f"--- Successfully loaded {len(hsn_map)} HSN codes into memory. ---")
        return hsn_map

    except Exception as e:
        print(f"--- CRITICAL ERROR: An error occurred while loading the Excel file: {e} ---")
        return {}


# --- Part 2: The Main Validation Function (The "Tool") ---

def validate_hsn_codes(
    hsn_inputs: Union[str, List[str]], 
    hsn_data_map: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Validates one or more HSN codes against the pre-loaded HSN data map.

    Args:
        hsn_inputs (Union[str, List[str]]): A single HSN code as a string, or a list of HSN codes.
        hsn_data_map (Dict[str, str]): The in-memory dictionary of HSN codes and descriptions.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing the validation result
                               for a single HSN code.
    """
    # --- Input Normalization ---
    if isinstance(hsn_inputs, str):
        codes_to_validate = [hsn_inputs]
    elif isinstance(hsn_inputs, list):
        codes_to_validate = hsn_inputs
    else:
        # Handle invalid input type
        return [{
            "input_hsn": str(hsn_inputs),
            "is_valid": False,
            "reason_code": "INVALID_INPUT_TYPE",
            "message": "Error: Input must be a string or a list of strings."
        }]

    if not codes_to_validate:
        return []

    results = []
    for code in codes_to_validate:
        # Ensure the item in the list is a string
        if not isinstance(code, str):
            results.append({
                "input_hsn": str(code),
                "is_valid": False,
                "reason_code": "INVALID_ITEM_TYPE",
                "message": "Error: All items in the list must be strings."
            })
            continue

        clean_code = code.strip()

        # --- Logic 1: Format Validation ---
        # HSN codes in India are typically 2, 4, 6, or 8 digits.
        if not clean_code.isdigit() or len(clean_code) not in [2, 4, 6, 8]:
            results.append({
                "input_hsn": code,
                "is_valid": False,
                "reason_code": "INVALID_FORMAT",
                "message": "Invalid format. HSN code must be 2, 4, 6, or 8 digits."
            })
            continue

        # --- Logic 2: Existence Validation ---
        # Use .get() for a safe dictionary lookup that won't raise an error.
        description = hsn_data_map.get(clean_code)

        if description is not None:
            results.append({
                "input_hsn": code,
                "is_valid": True,
                "description": description,
                "message": "HSN code is valid."
            })
        else:
            results.append({
                "input_hsn": code,
                "is_valid": False,
                "reason_code": "NOT_FOUND",
                "message": "HSN code not found in the master data."
            })

    return results

# --- Part 3: Testing the Function ---

if __name__ == "__main__":
    # This block runs only when you execute the script directly.
    # It will not run when the functions are imported by another script (like an agent).

    # Define the path to your Excel file
    HSN_FILE_PATH = "HSN_SAC.xlsx"

    # Load the data ONCE
    hsn_master_data = load_hsn_data(HSN_FILE_PATH)

    # Proceed only if data was loaded successfully
    if not hsn_master_data:
        print("\nHalting tests due to data loading failure.")
    else:
        print("\n" + "="*50)
        print("               RUNNING VALIDATION TESTS")
        print("="*50 + "\n")

        # 1. Test a single valid HSN code
        print("--- Test 1: Single Valid Code ---")
        test_1 = validate_hsn_codes("0101", hsn_master_data)
        pprint.pprint(test_1)
        print("\n")

        # 2. Test a code that does not exist
        print("--- Test 2: Code Not Found ---")
        test_2 = validate_hsn_codes("99999999", hsn_master_data)
        pprint.pprint(test_2)
        print("\n")

        # 3. Test a code with invalid format (wrong length)
        print("--- Test 3: Invalid Format (Length) ---")
        test_3 = validate_hsn_codes("12345", hsn_master_data)
        pprint.pprint(test_3)
        print("\n")

        # 4. Test a code with invalid format (non-numeric)
        print("--- Test 4: Invalid Format (Non-Numeric) ---")
        test_4 = validate_hsn_codes("010A", hsn_master_data)
        pprint.pprint(test_4)
        print("\n")

        # 5. Test a list with a mix of valid and invalid codes
        print("--- Test 5: Mixed List of Codes ---")
        mixed_codes = ["01", "01011010", "123", "ABC", "01012100", "98765432"]
        test_5 = validate_hsn_codes(mixed_codes, hsn_master_data)
        pprint.pprint(test_5)
        print("\n")

        # 6. Test a code with leading/trailing whitespace
        print("--- Test 6: Code with Whitespace ---")
        test_6 = validate_hsn_codes("  010121  ", hsn_master_data)
        pprint.pprint(test_6)
        print("\n")
        
        # 7. Test invalid input types
        print("--- Test 7: Invalid Input Type ---")
        test_7 = validate_hsn_codes(12345, hsn_master_data)
        pprint.pprint(test_7)
        print("\n")