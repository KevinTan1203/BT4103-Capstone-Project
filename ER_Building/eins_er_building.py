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

        ENTITY_ID = data['Details of Company']['entity_id']
        NUM_OF_CHARGES = len(data['Charges']['charge_id'])
        data['Charges']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_OF_CHARGES)]).astype(str)

        NUM_OF_AUDITORS = len(data['Auditors']['auditor_name'])
        data['Auditors']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_OF_AUDITORS)]).astype(str)

        NUM_OFFICERS_AUTH_REP = len(data['Officers Auth. Rep']['employee_id'])
        data['Officers Auth. Rep']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_OFFICERS_AUTH_REP)]).astype(str)

        NUM_SHAREHOLDERS = len(data['Shareholders']['shareholder_id'])
        data['Shareholders']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_SHAREHOLDERS)]).astype(str)

        NUM_CAPITAL_STRUCTURE = len(data['Capital Structure']['issued_ordinary_no_of_shares'])
        data['Capital Structure']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_CAPITAL_STRUCTURE)]).astype(str)
        
        NUM_OF_COMPLIANCE_RECORDS = len(data['Compliance Record']['date_of_last_agm'])
        data['Compliance Record']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_OF_COMPLIANCE_RECORDS)]).astype(str)
        
        NUM_OF_FINANCIAL_DATA = len(data['Financial Data']['current_fye'])
        data['Financial Data']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_OF_FINANCIAL_DATA)]).astype(str)
        
        NUM_OF_KEY_RATIOS = len(data['Key Ratios']['current_fye'])
        data['Key Ratios']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_OF_KEY_RATIOS)]).astype(str)
        
        NUM_OF_ANALYSIS = len(data['Analysis']['fye'])
        data['Analysis']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_OF_ANALYSIS)]).astype(str)
        
        NUM_OF_WRIT_OF_SUMMONS = len(data['Writ of Sum. Org. Claim']['sn'])
        data['Writ of Sum. Org. Claim']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_OF_WRIT_OF_SUMMONS)]).astype(str)
        
        NUM_OF_WINDING_UP = len(data['Winding Up']['type'])
        data['Winding Up']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_OF_WINDING_UP)]).astype(str)
        
        NUM_OF_OS_OA_OP_OM = len(data['OS OA OP OM']['type'])
        data['OS OA OP OM']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_OF_OS_OA_OP_OM)]).astype(str)
        
        NUM_OF_ADD_EXP_PROP_INFO = len(data['Add Exp Prop. Info']['num_of_employee'])
        data['Add Exp Prop. Info']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_OF_ADD_EXP_PROP_INFO)]).astype(str)
        
        NUM_OF_ACCREDITATIONS = len(data['Accreditations']['award_name'])
        data['Accreditations']['entity_id'] = np.array([ENTITY_ID for i in range(NUM_OF_ACCREDITATIONS)]).astype(str)
        
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
    directory_path = base_dir + 'Random_Generation/EINS_Random_Output'
    files = os.listdir(directory_path)
    main(files, directory_path)
    print(f'Successfully Ammended {len(files) - 3} Data!')
