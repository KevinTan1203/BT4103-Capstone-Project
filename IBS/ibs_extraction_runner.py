import pdfplumber
import pandas as pd
import numpy as np
import re
import os
import itertools

def main(directory, infile):
    ########################################################################################
    # Section 1: Parsing through the PDF
    # Open the PDF files using pdfplumber and read all lines into a single list for each pdf
    ########################################################################################
    dataExtraction = []
    x_tolereance = 8
    print(f'Reading file: {infile}')
    with pdfplumber.open(f'{directory}/{infile}') as pdf:
        for page in range(len(pdf.pages)):
            page_section = pdf.pages[page].find_tables()
            tableCount = 0
            while True:
                # Scans the current page for multiple tables
                # If a new table is detected, extract the data from that table, else proceed 
                # on to the next page
                try:
                    table_content = page_section[tableCount].extract(x_tolerance = x_tolereance)
                    dataExtraction.append(
                        [[ele for ele in table_content_data if ele not in [None, '']] for \
                            table_content_data in table_content]
                    )
                    tableCount += 1
                except IndexError:
                    break

    ########################################################################################
    # Section 2: Initialising the table dictionary
    # Predefine the table headers for each table present in the report
    ########################################################################################
    tablesDict = {
        'REQUEST CRITERIA':                                                                          [],
        'SEARCH RECORD':                                                                             [],
        'CURRENT BUSINESS':                                                                          [],
        'PREVIOUS BUSINESS':                                                                         [],
        'CURRENT BUSINESS LITIGATION TRACE\nNote: Available Information As Per Experian Database':   [],
        'BUSINESS LITIGATION SEARCH – WRIT OF SUMMONS/ ORIGINATING CLAIM':                           [],
        'BANKRUPTCY RECORD(S)':                                                                      [],
        'INDIVIDUAL LITIGATION SEARCH – WRIT OF SUMMONS/ ORIGINATING CLAIM':                         [],
        'ACCREDITATIONS – CURRENT BUSINESS':                                                         [],
        'FINANCIAL RELATED SEARCH COUNT':                                                            [],
        'COMMERCIAL RELATED SEARCH COUNT':                                                           [],
        'LEGAL RELATED SEARCH COUNT':                                                                [],
    }

    ########################################################################################
    # Section 3: Table population
    # Parse the rows into each of the respective table
    ########################################################################################
    compiledList = [ele for rowData in dataExtraction for ele in rowData]
    tableList = []
    currentKey = None

    # Iterating through each element in the singular list that we have compiled into
    for rowData in compiledList[:-1]:

        # If there are no data or element present in the given row, we will simply continue
        if len(rowData) == 0:
            continue

        # If we hit an element that is one of the headers in our table dictionary, that would signal the
        # start of the respective table, and hence would need to compile the data that we have accumulated in tableList
        # and append the result in the preceding table
        elif rowData[0] in list(tablesDict.keys()):
            currentTable = currentKey
            currentKey = rowData[0]

            # If there are elements in tableList, we will append the entire result to the previous table 
            # and reinitialise the tableList
            if len(tableList) > 0:
                tablesDict[currentTable] = tableList
                tableList = []

        # If none of the previous 2 conditions were met, we would simply append the data rows into the tableList
        else:
            tableList.append(rowData)

    # Add the last table to the tablesList
    tablesDict['LEGAL RELATED SEARCH COUNT'] = tableList

    ########################################################################################
    # Section 4: Table Construction
    # Create the respective tables in each of the report
    ########################################################################################

    # Table 1: REQUEST CRITERIA
    # Remove the information row, which is simply the first element in the array
    requestCriteriaArr = np.array(tablesDict['REQUEST CRITERIA'][1:])
    requestCriteriaHeaders = [h.replace(':', '').replace('*','') for h in requestCriteriaArr[:,0]]
    requestCriteriaData = requestCriteriaArr[:,1]
    REQUESTCRITERIA = pd.DataFrame([requestCriteriaData], columns=requestCriteriaHeaders)

    # ----- Assertion Test -----
    columnNames = [
        'Date of Request', 
        'Name of Requestor', 
        'Requested Individual Name', 
        'Requested ID Number', 
        'File Reference Number', 
    ]
    for actual, expected in itertools.zip_longest(REQUESTCRITERIA.columns, columnNames):
        assert actual == expected, f'REQUEST CRITERIA has column {actual} but should be {expected}'
    # --------------------------

    # Table 2: SEARCH RECORD
    # Collect the data in the first 3 rows of the array
    searchRecordArr = np.array(tablesDict['SEARCH RECORD'][:3])
    searchRecordHeaders = [h.replace(':', '').replace('\n','') for h in searchRecordArr[:,0]]
    searchRecordData = searchRecordArr[:,1]
    SEARCHRECORD = pd.DataFrame([searchRecordData], columns=searchRecordHeaders)

    # ----- Assertion Test -----
    columnNames = [
        'Individual Name(As per Experian database)', 
        'ID Number', 
        'Available Address(As per Experian database)', 
    ]
    for actual, expected in itertools.zip_longest(SEARCHRECORD.columns, columnNames):
        assert actual == expected, f'SEARCH RECORD has column {actual} but should be {expected}'
    # --------------------------

    # Table 3: CURRENT BUSINESS
    currentBusinessData = {}
    index = 0
    while index < len(tablesDict['CURRENT BUSINESS']):
        if tablesDict['CURRENT BUSINESS'][index] == ['No.', 'Name', 'Registration Number', 'Status', 'Position', 'Appointment Date']:
            for column, value in zip(tablesDict['CURRENT BUSINESS'][index][1:], tablesDict['CURRENT BUSINESS'][index + 1][1:]):
                if column in currentBusinessData:
                    currentBusinessData[column].append(value)
                else:
                    currentBusinessData[column] = [value]
            for i in range(4, 7):
                for j in range(2):
                    column = tablesDict['CURRENT BUSINESS'][index + i][2 * j]
                    if column in currentBusinessData:
                        currentBusinessData[column].append(tablesDict['CURRENT BUSINESS'][index + i][2 * j + 1])
                    else:
                        currentBusinessData[column] = [tablesDict['CURRENT BUSINESS'][index + i][2 * j + 1]]
            index += 6
        index += 1
    CURRENTBUSINESS = pd.DataFrame(currentBusinessData)

    # ----- Assertion Test -----
    columnNames = [
        'Name', 
        'Registration Number', 
        'Status', 
        'Position',
        'Appointment Date',
        'Current Directors', 
        'Current Secretaries',
        'Current Alternate Directors', 
        'Active Charges',
        'Current Shareholders / Owners', 
        'Subsidiary/Associates', 
    ]
    for actual, expected in itertools.zip_longest(CURRENTBUSINESS.columns, columnNames):
        assert actual == expected, f'CURRENT BUSINESS has column {actual} but should be {expected}'
    # --------------------------


    # Table 4: Previous Business
    previousBusinessArr = np.array(tablesDict['PREVIOUS BUSINESS'])
    previousBusinessHeaders = previousBusinessArr[0][1:]
    previousBusinessData = [row[1:] for row in previousBusinessArr[1:]]
    PREVIOUSBUSINESS = pd.DataFrame(previousBusinessData, columns=previousBusinessHeaders)

    # ----- Assertion Test -----
    columnNames = [
        'Name', 
        'Registration Number', 
        'Status', 
        'Position', 
        'Cessation Date', 
    ]
    for actual, expected in itertools.zip_longest(PREVIOUSBUSINESS.columns, columnNames):
        assert actual == expected, f'PREVIOUS BUSINESS has column {actual} but should be {expected}'
    # --------------------------


    # Table 5: CURRENT BUSINESS LITIGATION TRACE \nNote: Available Information As Per Experian Database
    currentBusLitTraceData = {'Name': [], 'Year': []}
    currentBusLitTraceArr = tablesDict['CURRENT BUSINESS LITIGATION TRACE\nNote: Available Information As Per Experian Database']
    # Observation tells us that each business should have a total of 7 rows of data
    for index in range(0, len(currentBusLitTraceArr), 7):
        for i in range(2, 7):
            currentBusLitTraceData['Name'].append(currentBusLitTraceArr[index][1])
            columnNames = [columnName.split('\n')[0] for columnName in currentBusLitTraceArr[index + 1]]
            currentBusLitTraceData['Year'].append(currentBusLitTraceArr[index + 1][1].split('\n')[1])
            for j in range(3):
                if columnNames[j] in currentBusLitTraceData:
                    currentBusLitTraceData[columnNames[j]].append(currentBusLitTraceArr[index + i][j])
                else:
                    currentBusLitTraceData[columnNames[j]] = [currentBusLitTraceArr[index + i][j]]
    CURRENTBUSINESSLITIGATIONTRACE = pd.DataFrame(currentBusLitTraceData)

    # ----- Assertion Test -----
    columnNames = [
        'Name', 
        'Year', 
        'Enquiries', 
        'Current Year On/After 9 Jan',
        'Previous Year Before 9 Jan', 
    ]
    for actual, expected in itertools.zip_longest(CURRENTBUSINESSLITIGATIONTRACE.columns, columnNames):
        assert actual == expected, f'CURRENT BUSINESS LITIGATIONTRACE has column {actual} but should be {expected}'
    # --------------------------


    # Table 6: BUSINESS LITIGATION SEARCH – WRIT OF SUMMONS/ ORIGINATING CLAIM
    # The first 6 rows are information on the dataset, which we would not require in our table construction
    # Likewise, the last row in the array is irrelevant
    businessLitigationSearchArr = tablesDict['BUSINESS LITIGATION SEARCH – WRIT OF SUMMONS/ ORIGINATING CLAIM'][6:-1]

    businessLitigationSearchHeaders = [
        'SN', 
        'Court/Type', 
        'Case No.', 
        'Year', 
        'Filing Date', 
        'Plaintiff / \nPetitioner\n/Claimant', 
        'Case Status / \nStatus Date/ \nRemarks', 
        'Plaintiff/ \nClaimant \nStatus/ \nStatus Date', 
        'Defendant \nStatus*/ \nStatus Date', 
        'Amount(s)', 
        'Last Updated in \nExperian \nDatabase',
        'Main Cause'
    ]

    # Initialise the dataframe 'Business Litigation Search'
    BUSINESSLITIGATIONSEARCH = pd.DataFrame(columns=[h.replace('\n', '').replace('*','') for h in businessLitigationSearchHeaders])

    # Concatenate the data and append them to the dataframe
    businessLitigationSearchData = businessLitigationSearchArr[1:]
    for rowIndex in range(0, len(businessLitigationSearchData), 2):
        rowData = businessLitigationSearchData[rowIndex]
        rowData.append(businessLitigationSearchData[rowIndex+1][-1])
    
        BUSINESSLITIGATIONSEARCH = BUSINESSLITIGATIONSEARCH.append(
                pd.DataFrame([rowData], columns=list(BUSINESSLITIGATIONSEARCH.columns)), ignore_index=True)

    # Split Case Status, Date and Remarks into separate columns
    BUSINESSLITIGATIONSEARCH[['Case Status', 'Case Status Date', 'Case Status Remarks']] = BUSINESSLITIGATIONSEARCH['Case Status / Status Date/ Remarks'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:3])

    # Split Plaintiff / Claimant Status and Date into separate columns
    BUSINESSLITIGATIONSEARCH[['Plaintiff / Claimant Status', 'Plaintiff / Claimant Status Date']] = BUSINESSLITIGATIONSEARCH['Plaintiff/ Claimant Status/ Status Date'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:2])

    # Split Defendant Status and Date into separate columns
    BUSINESSLITIGATIONSEARCH[['Defendant Status', 'Defendant Status Date']] = BUSINESSLITIGATIONSEARCH['Defendant Status/ Status Date'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:2])
    BUSINESSLITIGATIONSEARCH = BUSINESSLITIGATIONSEARCH[[
        'SN', 
        'Court/Type', 
        'Case No.', 
        'Year', 
        'Filing Date', 
        'Plaintiff / Petitioner/Claimant', 
        'Case Status',
        'Case Status Date', 
        'Case Status Remarks',
        'Plaintiff / Claimant Status', 
        'Plaintiff / Claimant Status Date',
        'Defendant Status', 
        'Defendant Status Date',
        'Amount(s)', 
        'Last Updated in Experian Database',
        'Main Cause'
    ]]

     # ----- Assertion Test -----
    columnNames = [
        'SN', 
        'Court/Type', 
        'Case No.', 
        'Year', 
        'Filing Date',
        'Plaintiff / Petitioner/Claimant', 
        'Case Status', 
        'Case Status Date',
        'Case Status Remarks', 
        'Plaintiff / Claimant Status',
        'Plaintiff / Claimant Status Date', 
        'Defendant Status',
        'Defendant Status Date', 
        'Amount(s)',
        'Last Updated in Experian Database', 
        'Main Cause', 
    ]
    for actual, expected in itertools.zip_longest(BUSINESSLITIGATIONSEARCH.columns, columnNames):
        assert actual == expected, f'BUSINESS LITIGATION SEARCH has column {actual} but should be {expected}'
    # --------------------------

    # Table 7: BANKRUPTCY RECORDS
    # We can ignore the last row of the array, as the information is irrelevant
    # The first row in the array are the headers for the table, hence the main data only starts from row 2 onwards
    bankruptcyRecordsArr = tablesDict['BANKRUPTCY RECORD(S)'][2:-1]

    bankruptcyRecordsHeaders = [
        'Case No.', 
        'Year', 
        'Filing Date', 
        'Plaintiff / \nPetitioner/ \nClaimant', 
        'Case Status/ \nStatus Date/ \nRemark', 
        'Plaintiff/ \nClaimant \nStatus/ \nStatus Date', 
        'Defendant \nStatus*/ \nStatus Date', 
        'Amount(s)', 
        'Last Updated \nin Experian \nDatabase',
        'Name of Private Trustees \nAppointed (As per \nExperian Database)',
    ]

    # Initialise the dataframe 'Bankruptcy Records'
    BANKRUPTCYRECORDS = pd.DataFrame(columns=[h.replace('\n', '').replace(':','') for h in bankruptcyRecordsHeaders])

    # Concat the data and append them to the dataframe
    bankruptcyRecordsData = bankruptcyRecordsArr[1:]
    for rowIndex in range(0, len(bankruptcyRecordsData), 2):
        rowData = bankruptcyRecordsData[rowIndex]
        rowData.append(bankruptcyRecordsData[rowIndex+1][-1])
        BANKRUPTCYRECORDS = BANKRUPTCYRECORDS.append(
                pd.DataFrame([rowData], columns=list(BANKRUPTCYRECORDS.columns)), ignore_index=True)

    # Split Case Status, Date and Remarks into separate columns
    BANKRUPTCYRECORDS[['Case Status', 'Case Status Date', 'Case Status Remarks']] = BANKRUPTCYRECORDS['Case Status/ Status Date/ Remark'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:3])

    # Split Plaintiff / Claimant Status and Date into separate columns
    BANKRUPTCYRECORDS[['Plaintiff / Claimant Status', 'Plaintiff / Claimant Status Date']] = BANKRUPTCYRECORDS['Plaintiff/ Claimant Status/ Status Date'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:2])

    # Split Defendant Status and Date into separate columns
    BANKRUPTCYRECORDS[['Defendant Status', 'Defendant Status Date']] = BANKRUPTCYRECORDS['Defendant Status*/ Status Date'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:2])
    BANKRUPTCYRECORDS = BANKRUPTCYRECORDS[[
        'Case No.', 
        'Year', 
        'Filing Date', 
        'Plaintiff / Petitioner/ Claimant',
        'Case Status',
        'Case Status Date', 
        'Case Status Remarks',
        'Plaintiff / Claimant Status', 
        'Plaintiff / Claimant Status Date',
        'Defendant Status', 
        'Defendant Status Date',
        'Amount(s)', 
        'Last Updated in Experian Database',
        'Name of Private Trustees Appointed (As per Experian Database)'
    ]]

    # ----- Assertion Test -----
    columnNames = [
        'Case No.', 
        'Year', 
        'Filing Date', 
        'Plaintiff / Petitioner/ Claimant',
        'Case Status', 
        'Case Status Date', 
        'Case Status Remarks',
        'Plaintiff / Claimant Status', 
        'Plaintiff / Claimant Status Date',
        'Defendant Status', 
        'Defendant Status Date', 
        'Amount(s)',
        'Last Updated in Experian Database',
        'Name of Private Trustees Appointed (As per Experian Database)', 
    ]
    for actual, expected in itertools.zip_longest(BANKRUPTCYRECORDS.columns, columnNames):
        assert actual == expected, f'BANKRUPTCY RECORDS SEARCH has column {actual} but should be {expected}'
    # --------------------------

    # Table 8: INDIVIDUAL LITIGATION SEARCH – WRIT OF SUMMONS/ ORIGINATING CLAIM
    # Rows 1 to 5 are information related to table details. Hence, we can exclude them from the table construction
    # Likewise, the last row is irrelevant
    indvLitigationSearchArr = tablesDict['INDIVIDUAL LITIGATION SEARCH – WRIT OF SUMMONS/ ORIGINATING CLAIM'][5:-1]

    indvLitigationSearchHeaders = [
        'SN', 
        'Court/ Type', 
        'Case \nNo.', 
        'Year', 
        'Filing \nDate', 
        'Plaintiff/ \nPetitioner\n/Claimant', 
        'Case Status / \nStatus Date \nRemarks', 
        'Plaintiff/ \nClaimant \nStatus/ \nStatus Date',
        'Defendant \nStatus*/ \n \nStatus Date', 
        'Amount(s)', 
        'Last Updated \nin Experian \nDatabase',
        'Main Cause',
    ]

    # Initialise the dataframe
    INDIVIDUALLITIGATIONSEARCH = pd.DataFrame(columns=[h.replace('\n', '').replace(':','') for h in indvLitigationSearchHeaders])

    # Concat the data and append them to the dataframe
    indvLitigationSearchData = indvLitigationSearchArr[1:]
    for rowIndex in range(0, len(indvLitigationSearchData), 2):
        # Each data set has 2 rows
        rowData = indvLitigationSearchData[rowIndex]
        rowData.append(indvLitigationSearchData[rowIndex+1][-1])
        INDIVIDUALLITIGATIONSEARCH = INDIVIDUALLITIGATIONSEARCH.append(
            pd.DataFrame([rowData], columns=list(INDIVIDUALLITIGATIONSEARCH.columns)), ignore_index=True)

    # Split Case Status, Date and Remarks into separate columns
    INDIVIDUALLITIGATIONSEARCH[['Case Status', 'Case Status Date', 'Case Status Remarks']] = INDIVIDUALLITIGATIONSEARCH['Case Status / Status Date Remarks'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:3])

    # Split Plaintiff / Claimant Status and Date into separate columns
    INDIVIDUALLITIGATIONSEARCH[['Plaintiff / Claimant Status', 'Plaintiff / Claimant Status Date']] = INDIVIDUALLITIGATIONSEARCH['Plaintiff/ Claimant Status/ Status Date'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:2])

    # Split Defendant Status and Date into separate columns
    INDIVIDUALLITIGATIONSEARCH[['Defendant Status', 'Defendant Status Date']] = INDIVIDUALLITIGATIONSEARCH['Defendant Status*/  Status Date'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:2])

    INDIVIDUALLITIGATIONSEARCH = INDIVIDUALLITIGATIONSEARCH[[
        'SN', 
        'Court/ Type', 
        'Case No.', 
        'Year', 
        'Filing Date', 
        'Plaintiff/ Petitioner/Claimant', 
        'Case Status',
        'Case Status Date', 
        'Case Status Remarks',
        'Plaintiff / Claimant Status', 
        'Plaintiff / Claimant Status Date',
        'Defendant Status', 
        'Defendant Status Date',
        'Amount(s)', 
        'Last Updated in Experian Database',
        'Main Cause',
    ]]

    # ----- Assertion Test -----
    columnNames = [
        'SN', 
        'Court/ Type', 
        'Case No.', 
        'Year', 
        'Filing Date',
        'Plaintiff/ Petitioner/Claimant', 
        'Case Status', 
        'Case Status Date',
        'Case Status Remarks', 
        'Plaintiff / Claimant Status',
        'Plaintiff / Claimant Status Date', 
        'Defendant Status',
        'Defendant Status Date', 
        'Amount(s)',
        'Last Updated in Experian Database', 
        'Main Cause',
    ]
    for actual, expected in itertools.zip_longest(INDIVIDUALLITIGATIONSEARCH.columns, columnNames):
        assert actual == expected, f'INDIVIDUAL LITIGATION SEARCH has column {actual} but should be {expected}'
    # --------------------------

    # Table 9: ACCREDITATIONS – CURRENT BUSINESS
    # Initialise the dataframe
    ACCREDITATIONS = pd.DataFrame(columns=[
        'Business',
        'Ranking Source',
        'Ranks',
    ])
    accreditationsData = tablesDict['ACCREDITATIONS – CURRENT BUSINESS']

    # Concat the data and append them to the dataframe
    for rowIndex in range(0, len(accreditationsData), 2):
        rowData = accreditationsData[rowIndex]
        rowData.extend(accreditationsData[rowIndex+1])
        ACCREDITATIONS = ACCREDITATIONS.append(
                pd.DataFrame([rowData], columns=list(ACCREDITATIONS.columns)), ignore_index=True)

    # ----- Assertion Test -----
    columnNames = [
        'Business', 
        'Ranking Source', 
        'Ranks', 
    ]
    for actual, expected in itertools.zip_longest(ACCREDITATIONS.columns, columnNames):
        assert actual == expected, f'ACCREDITATIONS has column {actual} but should be {expected}'
    # --------------------------

    # Table 10: FINANCIAL RELATED SEARCH COUNT
    financialRelatedSearchCountData = {
        'year': [], 
        'month': [], 
        'purpose': [], 
        'count': [], 
    }

    def add(year, month, purpose, count):
        financialRelatedSearchCountData['year'].append(year)
        financialRelatedSearchCountData['month'].append(month)
        financialRelatedSearchCountData['purpose'].append(purpose)
        financialRelatedSearchCountData['count'].append(count)

    for data in tablesDict['FINANCIAL RELATED SEARCH COUNT'][2:]:
        if len(data) == 14:
            year = data[0]
            add(year, 'All', 'All', data[1])
            for index in range(2, 14):
                add(year, tablesDict['FINANCIAL RELATED SEARCH COUNT'][1][index], 'All', data[index])
        else:
            for index in range(1, 13):
                add(year, tablesDict['FINANCIAL RELATED SEARCH COUNT'][1][index], data[0], data[index])
    FINRELSEARCHCOUNT = pd.DataFrame(financialRelatedSearchCountData)


    # Table 11: COMMERCIAL RELATED SEARCH COUNT
    commercialRelatedSearchCountData = {
        'year': [], 
        'month': [], 
        'purpose': [], 
        'count': [], 
    }

    def add(year, month, purpose, count):
        commercialRelatedSearchCountData['year'].append(year)
        commercialRelatedSearchCountData['month'].append(month)
        commercialRelatedSearchCountData['purpose'].append(purpose)
        commercialRelatedSearchCountData['count'].append(count)

    for data in tablesDict['COMMERCIAL RELATED SEARCH COUNT'][2:]:
        if len(data) == 14:
            year = data[0]
            add(year, 'All', 'All', data[1])
            for index in range(2, 14):
                add(year, tablesDict['COMMERCIAL RELATED SEARCH COUNT'][1][index], 'All', data[index])
        else:
            for index in range(1, 13):
                add(year, tablesDict['COMMERCIAL RELATED SEARCH COUNT'][1][index], data[0], data[index])
    COMRELSEARCHCOUNT = pd.DataFrame(commercialRelatedSearchCountData)


    # Table 12: LEGAL RELATED SEARCH COUNT
    legalRelatedSearchCountData = {
        'year': [], 
        'month': [], 
        'purpose': [], 
        'count': [], 
    }

    def add(year, month, purpose, count):
        legalRelatedSearchCountData['year'].append(year)
        legalRelatedSearchCountData['month'].append(month)
        legalRelatedSearchCountData['purpose'].append(purpose)
        legalRelatedSearchCountData['count'].append(count)

    for data in tablesDict['LEGAL RELATED SEARCH COUNT'][2:-5]:
        if len(data) == 14:
            year = data[0]
            add(year, 'All', 'All', data[1])
            for index in range(2, 14):
                add(year, tablesDict['LEGAL RELATED SEARCH COUNT'][1][index], 'All', data[index])
        else:
            for index in range(1, len(data)):
                add(year, tablesDict['LEGAL RELATED SEARCH COUNT'][1][index], data[0], data[index])
    LEGRELSEARCHCOUNT = pd.DataFrame(legalRelatedSearchCountData)
        
    ########################################################################################
    # Section 5: Column Renaming
    # Column headers for the respective tables will be renamed for ease of management in
    # downstream applications such as database querying
    ########################################################################################
    REQUESTCRITERIA.columns = [
        'request_date', 
        'requestor_name', 
        'requested_individual_name', 
        'requested_id_no', 
        'request_id', 
    ]

    SEARCHRECORD.columns = [
        'individual_name', 
        'individual_id', 
        'available_address', 
    ]
    
    CURRENTBUSINESS.columns = [
        'business_name', 
        'registration_no', 
        'status', 
        'position', 
        'appointment_date', 
        'current_directors_todate_count', 
        'current_secretaries_todate_count', 
        'current_alternate_directors_todate_count', 
        'active_charges_todate_count', 
        'current_shareholders_todate_count', 
        'subsidiary_todate_count', 
    ]
    
    PREVIOUSBUSINESS.columns = [
        'business_name', 
        'registration_no', 
        'status', 
        'position', 
        'cessation_date', 
    ]
    
    CURRENTBUSINESSLITIGATIONTRACE.columns = [
        'business_name', 
        'year', 
        'enquiries', 
        'current_year_after_9_Jan', 
        'previous_year_before_9_Jan'
    ]
    
    BUSINESSLITIGATIONSEARCH.columns = [
        'sn', 
        'court_type', 
        'case_no', 
        'year', 
        'filing_date', 
        'plaintiff', 
        'case_status', 
        'case_status_date', 
        'case_status_remarks', 
        'plaintiff_status', 
        'plaintiff_status_date', 
        'defendant_status', 
        'defendant_status_date', 
        'amount', 
        'last_update', 
        'main_cause', 
    ]

    BANKRUPTCYRECORDS.columns = [
        'case_no', 
        'year', 
        'filing_date', 
        'plaintiff', 
        'case_status', 
        'case_status_date', 
        'case_status_remarks', 
        'plaintiff_status', 
        'plaintiff_status_date', 
        'defendant_status', 
        'defendant_status_date', 
        'amount', 
        'last_update', 
        'name_of_private_trustees', 
    ]

    INDIVIDUALLITIGATIONSEARCH.columns = [
        'sn', 
        'type', 
        'case_no', 
        'year', 
        'filing_date', 
        'plaintiff', 
        'case_status', 
        'case_status_date', 
        'case_status_remarks', 
        'plaintiff_status', 
        'plaintiff_status_date', 
        'defendant_status', 
        'defendant_status_date', 
        'amount', 
        'last_update', 
        'main_cause', 
    ]
    
    ACCREDITATIONS.columns = [
        'business', 
        'award_name', 
        'award_ranking', 
    ]


    ########################################################################################
    # Section 6: Data export
    # Export all tables into an excel file for downstream application
    ########################################################################################
    # Output Data
    outfileID = list(REQUESTCRITERIA['requested_id_no'])[0]
    
    writer = pd.ExcelWriter(f'Output/{outfileID}.xlsx', engine='xlsxwriter')
    REQUESTCRITERIA.to_excel(writer, sheet_name='Request Criteria')
    SEARCHRECORD.to_excel(writer, sheet_name='Search Record')
    CURRENTBUSINESS.to_excel(writer, sheet_name='Current Business')
    PREVIOUSBUSINESS.to_excel(writer, sheet_name='Previous Business')
    CURRENTBUSINESSLITIGATIONTRACE.to_excel(writer, sheet_name='Current Business Lit Trace')
    BUSINESSLITIGATIONSEARCH.to_excel(writer, sheet_name='Business Lit Search')
    BANKRUPTCYRECORDS.to_excel(writer, sheet_name='Bankruptcy Records')
    INDIVIDUALLITIGATIONSEARCH.to_excel(writer, sheet_name='Individual Lit Search')
    ACCREDITATIONS.to_excel(writer, sheet_name='Accreditation')
    FINRELSEARCHCOUNT.to_excel(writer, sheet_name='Financial Related Search Count')
    COMRELSEARCHCOUNT.to_excel(writer, sheet_name='Commercial Related Search Count')
    LEGRELSEARCHCOUNT.to_excel(writer, sheet_name='Legal Related Search Count')
    writer.close()
    print(f'Exported as {outfileID}.xlsx to subdirectory Output/')


if __name__ == "__main__":
    inputOutput = []
    directory = "../Dataset/ibs_data"

    # Scans the current folder for all available PDF reports to be scrape
    for (dir_path, dir_names, file_names) in os.walk(directory):
        for fileName in file_names:
            inputOutput.append(
                [fileName, f"{fileName.split('.')[0]}.xlsx"]
            )
    for infile, outfile in inputOutput:
        main(directory, infile)

    print(f'====> {len(inputOutput)} PDF(s) successfully scraped!')