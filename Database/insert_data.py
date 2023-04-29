import pandas as pd
import sqlite3

def main(compiledEinsFilePath, compiledIbsFilePath):
    # Connect to the database
    eins_connection = sqlite3.connect('Eins.db')
    ibs_connection = sqlite3.connect('Ibs.db')

    # Read the Excel files
    eins_compiled = pd.read_excel(compiledEinsFilePath, sheet_name=None)
    ibs_compiled = pd.read_excel(compiledIbsFilePath, sheet_name=None)

    # Insert the data into the respective tables
    for table_name, table_data in eins_compiled.items():
        table_data.to_sql('_'.join(table_name.split(' ')), eins_connection, if_exists='replace', index=False)

    for table_name, table_data in ibs_compiled.items():
        table_data.to_sql('_'.join(table_name.split(' ')), ibs_connection, if_exists='replace', index=False)

    # Close the database connection
    eins_connection.close()
    ibs_connection.close()

if __name__ == "__main__":
    compiledEinsFilePath = '../Random_Generation/Outputs/compiled_EINS_reports.xlsx'
    compiledIbsFilePath = '../Random_Generation/Outputs/compiled_IBS_reports.xlsx'
    main(compiledEinsFilePath, compiledIbsFilePath)

