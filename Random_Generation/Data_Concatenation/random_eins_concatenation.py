import pandas as pd
import string
import os
from tqdm import tqdm
import shutil


def has_special_character(filename):
    # Defining set of allowed characters
    allowed_chars = set(string.ascii_letters + string.digits + ' -_.')

    # Check if each character in the filename is an allowed character
    for char in filename:
        if char not in allowed_chars:
            return True
    return False

def data_dict_preprocessing():
    data = {}
    file = 'compiled_EINS_reports.xlsx'
    if os.path.isfile(file):
        xl = pd.ExcelFile(file, engine='openpyxl')
        for sheet_name in xl.sheet_names:
            if sheet_name in data:
                data[sheet_name] = pd.concat(
                    [data[sheet_name], xl.parse(sheet_name)], axis=0, ignore_index=True)
            else:
                data[sheet_name] = xl.parse(sheet_name)
    return data

def main(files, directory_path):
    # Create an empty list to store the Excel files
    excel_files = []

    # Loop through the files in the directory and append the Excel files to the list
    for filename in files:
        # Hidden files handler
        if filename in ['.DS_Store', '.gitkeep']:
            continue
        elif filename.endswith('.xlsx') and not has_special_character(filename):
            new_filename = filename[0:-5] + '-compiled.xlsx'
            old_filepath = os.path.join(directory_path, filename)
            new_filepath = os.path.join(directory_path, new_filename)
            shutil.move(old_filepath, new_filepath)
            excel_files.append(os.path.join(directory_path, new_filename))

    # Create and process dictionary to store the data from the Excel files
    data = data_dict_preprocessing()

    # Loop through the Excel files and sheets and add the data to the dictionary
    for fileIndex in tqdm(range(len(excel_files))):
        file = excel_files[fileIndex]
        xl = pd.ExcelFile(file, engine='openpyxl')
        for sheet_name in xl.sheet_names:
            if sheet_name in data:
                data[sheet_name] = pd.concat(
                    [data[sheet_name], xl.parse(sheet_name)], axis=0, ignore_index=True)
            else:
                data[sheet_name] = xl.parse(sheet_name)

    # Create a new Excel file with the merged data
    with pd.ExcelWriter('../Outputs/compiled_EINS_reports.xlsx') as writer:
        for sheet_name, sheet_data in data.items():
            sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == "__main__":
    # Run from Data_Concatenation folder
    directory_path = '../Outputs/EINS_Random_Output'
    files = os.listdir(directory_path)
    main(files, directory_path)
    print(f'Successfully Compiled {len(files) - 2} EINS Data Reports!')
