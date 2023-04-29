import pandas as pd
import numpy as np
import string
import os
from tqdm import tqdm
import shutil


def has_special_character(filename):
    # defining set of allowed characters
    allowed_chars = set(string.ascii_letters + string.digits + ' -_.')

    # Check if each character in the filename is an allowed character
    for char in filename:
        if char not in allowed_chars:
            return True
    return False


# def data_dict_preprocessing():
#     data = {}
#     file = 'compiled_IBS_reports.xlsx'
#     if os.path.isfile(file):
#         xl = pd.ExcelFile(file, engine='openpyxl')
#         for sheet_name in xl.sheet_names:
#             if sheet_name in data:
#                 data[sheet_name] = pd.concat(
#                     [data[sheet_name], xl.parse(sheet_name)], axis=0, ignore_index=True)
#             else:
#                 data[sheet_name] = xl.parse(sheet_name)
#     return data


def main(files, directory_path):
    # Create an empty list to store the Excel files
    excel_files = []

    # Loop through the files in the directory and append the Excel files to the list
    for filename in files:
        # Hidden files handler
        if filename in ['.DS_Store', '.gitkeep']:
            continue
        elif filename.endswith('.xlsx') and not has_special_character(filename):
            # new_filename = filename[0:-5] + '-compiled.xlsx'
            # old_filepath = os.path.join(directory_path, filename)
            # new_filepath = os.path.join(directory_path, new_filename)
            # shutil.move(old_filepath, new_filepath)
            excel_files.append(os.path.join(directory_path, filename))

    # Create and process dictionary to store the data from the Excel files
    # data = data_dict_preprocessing()


    # Loop through the Excel files and sheets and add the data to the dictionary
    for fileIndex in tqdm(range(len(excel_files))):
        file = excel_files[fileIndex]
        xl = pd.ExcelFile(file, engine='openpyxl')
        data = {}
        for sheet_name in xl.sheet_names:
            if sheet_name in data:
                data[sheet_name] = pd.concat(
                    [data[sheet_name], xl.parse(sheet_name)], axis=0, ignore_index=True)
            else:
                data[sheet_name] = xl.parse(sheet_name)

        ENTITY_ID = data["Request Criteria"]['requested_id_no']
        NUM_OF_CURRENT_BUSINESSES = len(data["Current Business"]["registration_no"])
        data["Current Business"]["individual_id"] = np.array([ENTITY_ID for i in range(NUM_OF_CURRENT_BUSINESSES)]).astype(str)

        NUM_OF_PREV_BUSINESSES = len(data["Previous Business"]["registration_no"])
        data["Previous Business"]["individual_id"] = np.array([ENTITY_ID for i in range(NUM_OF_PREV_BUSINESSES)]).astype(str)

        NUM_CURRENT_BUSINESS_LIT_TRACE = len(data['Current Business Lit Trace']['business_name'])
        data['Current Business Lit Trace']['individual_id'] = np.array([ENTITY_ID for i in range(NUM_CURRENT_BUSINESS_LIT_TRACE)]).astype(str)

        NUM_ACCREDITATION = len(data['Accreditation']['business'])
        data['Accreditation']['individual_id'] = np.array([ENTITY_ID for i in range(NUM_ACCREDITATION)]).astype(str)

        NUM_OF_BUSINESS_LIT_SEARCH = len(data["Business Lit Search"]["sn"])
        data["Business Lit Search"]["individual_id"] = np.array([ENTITY_ID for i in range(NUM_OF_BUSINESS_LIT_SEARCH)]).astype(str)
        
        NUM_OF_BANKRUPTCY_RECORDS = len(data["Bankruptcy Record"]["case_no"])
        data["Bankruptcy Record"]["individual_id"] = np.array([ENTITY_ID for i in range(NUM_OF_BANKRUPTCY_RECORDS)]).astype(str)
        
        NUM_OF_INDIV_LIT_SEARCH = len(data["Individual Lit Search"]["sn"])
        data["Individual Lit Search"]["individual_id"] = np.array([ENTITY_ID for i in range(NUM_OF_INDIV_LIT_SEARCH)]).astype(str)
        
        NUM_OF_FIN_REL_SEARCH_COUNT = len(data["Financial Related Search Count"]["year"])
        data["Financial Related Search Count"]["individual_id"] = np.array([ENTITY_ID for i in range(NUM_OF_FIN_REL_SEARCH_COUNT)]).astype(str)
        
        NUM_OF_COMM_REL_SEARCH_COUNT = len(data["Commercial Related Search Count"]["year"])
        data["Commercial Related Search Count"]["individual_id"] = np.array([ENTITY_ID for i in range(NUM_OF_COMM_REL_SEARCH_COUNT)]).astype(str)
        
        NUM_OF_LEGAL_REL_SEARCH_COUNT = len(data["Legal Related Search Count"]["year"])
        data["Legal Related Search Count"]["individual_id"] = np.array([ENTITY_ID for i in range(NUM_OF_LEGAL_REL_SEARCH_COUNT)]).astype(str)

        # Create a new Excel file with the merged data
        with pd.ExcelWriter(file) as writer:
            for sheet_name, sheet_data in data.items():
                sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # # Create a new Excel file with the merged data
    # with pd.ExcelWriter(base_dir + 'Random_Generation/compiled_IBS_reports.xlsx') as writer:
    #     for sheet_name, sheet_data in data.items():
    #         sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == "__main__":
    folders = os.getcwd().split("\\")
    base_dir = '../' * (len(folders) - folders.index('Capstone-Project') - 1)
    directory_path = base_dir + 'Random_Generation/IBS_Random_Output'
    files = os.listdir(directory_path)
    main(files, directory_path)
    print(f'Successfully Ammended {len(files) - 3} Data!')
