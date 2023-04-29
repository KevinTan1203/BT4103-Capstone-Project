import pdfplumber
import pandas as pd
import numpy as np
import itertools
import re
import os

def main(directory, infile, outfile):
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
        'REQUEST CRITERIA':                              [],
        'SEARCH RECORD':                                 [],
        'Details of Company':                            [],
        'Capital Structure':                             [],
        'Charge(s)':                                     [],
        'Auditor(s)':                                    [],
        'Officer(s) / Authorised Representative(s)':     [],
        'SHAREHOLDER(S)':                                [],
        'Compliance Record':                             [],
        'Financial Data':                                [],
        'Key Ratios':                                    [],
        'ANALYSIS':                                      [],
        '1) WRIT OF SUMMONS/ ORIGINATING CLAIM':         [],
        '2) WINDING UP':                                 [],
        '3) OS/OA/OP/OM':                                [],
        'ADDITIONAL EXPERIAN PROPRIETARY INFORMATION':   [],
        'ACCREDITATIONS':                                [],
        'FINANCIAL RELATED SEARCH COUNT':                [],
        'COMMERCIAL RELATED SEARCH COUNT':               [],
        'LEGAL RELATED SEARCH COUNT':                    [],
    }

    ########################################################################################
    # Section 3: Table population
    # Parse the rows into each of the respective table
    ########################################################################################
    compiledList = [ele for rowData in dataExtraction for ele in rowData]
    tableList = []
    currentKey = None
    for rowData in compiledList[:-1]:
        # If there are no data or element present in the given row, we will simply continue
        if len(rowData) == 0:
            continue
        # If we hit an element that is one of the headers in our table dictionary, that would signal the
        # start of the respective table, and hence would need to compile the data that we have accumulated in tableList
        # and append the result in the preceding table
        elif rowData[0] in list(tablesDict.keys()):
            # Assigns the current table name to the currentKey variable 
            currentTable = currentKey
            currentKey = rowData[0]
            if len(tableList) > 0:
                tablesDict[currentTable] = tableList
                tableList = [] 
        else:
            # If none of the previous conditions are met, the rowData is a row 
            # of data that belongs to the current table being processed
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
        'Requested Entity Name',
        'Requested Entity Number',
        'File Reference Number', 
    ]
    for actual, expected in itertools.zip_longest(REQUESTCRITERIA.columns, columnNames):
        assert actual == expected, f'REQUEST CRITERIA has column {actual} but should be {expected}'
    # --------------------------
    
    # Table 2: SEARCH RECORD
    # Collect the data in the array, Our data should only have a length of 2
    searchRecordArr = np.array(tablesDict['SEARCH RECORD'][:2])
    searchRecordHeaders = [h.replace(':', '').replace('*','') for h in searchRecordArr[:,0]]
    searchRecordData = searchRecordArr[:,1]
    SEARCHRECORD = pd.DataFrame([searchRecordData], columns=searchRecordHeaders)

    # ----- Assertion Test -----
    columnNames = [
        'Entity Name', 
        'Entity Number', 
    ]
    for actual, expected in itertools.zip_longest(SEARCHRECORD.columns, columnNames):
        assert actual == expected, f'SEARCH RECORD has column {actual} but should be {expected}'
    # --------------------------    

    # Table 3: DETAILS OF COMPANY
    DetailsOfCompanyArr = np.array(tablesDict['Details of Company'])
    DetailsOfCompanyHeaders = [h.replace(':', '').replace('*','') for h in DetailsOfCompanyArr[:,0]]
    DetailsOfCompanyData = DetailsOfCompanyArr[:,1]
    DETAILSOFCOMPANY = pd.DataFrame([DetailsOfCompanyData], columns=DetailsOfCompanyHeaders)
    if 'Former Name (Effective Date)' in DETAILSOFCOMPANY.columns:
        columnIndex = DETAILSOFCOMPANY.columns.get_loc('Former Name (Effective Date)')
        DETAILSOFCOMPANY.insert(columnIndex, 'Former Name', None)
        DETAILSOFCOMPANY.insert(columnIndex + 1, 'Effective Date', None)
        DETAILSOFCOMPANY['Former Name'] = DETAILSOFCOMPANY['Former Name (Effective Date)'].str.extract('(.*) \(')
        DETAILSOFCOMPANY['Effective Date'] = DETAILSOFCOMPANY['Former Name (Effective Date)'].str.extract('\((.*)\)')
        DETAILSOFCOMPANY.drop(columns='Former Name (Effective Date)', inplace=True)
   
    # ----- Assertion Test -----
    columnNames = [
        'Entity Name', 
        'Entity Number', 
        'Date of Registration (dd/mm/yyyy)',
        'Country/Region of Incorporation/Registration',
        'Date of Change of Name', 
        'Former Name', 
        'Effective Date',
        'Type of Company', 
        'Registered Office Address',
        'Date of Change of Address', 
        'Principal Activity / Activities',
        'Status', 
        'Status Date', 
    ]
    for actual, expected in itertools.zip_longest(DETAILSOFCOMPANY.columns, columnNames):
        assert actual == expected, f'DETAILS OF COMPANY has column {actual} but should be {expected}'
    # --------------------------    
    
    # Table 4: CAPITAL STRUCTURE
    # Retrieve the data for Capital Structure
    capStructureArr = np.array(tablesDict['Capital Structure'])
    capStructureHeaders = [h.replace(':', '').replace('*','') for h in capStructureArr[0,:]]
    capStructureData = capStructureArr[1:,:]
    CAPITALSTRUCTURE = pd.DataFrame(capStructureData, columns=capStructureHeaders)

    # Conversion from long to wide format with new features added
    capStructureData = {}
    capStructureHeaders = tablesDict['Capital Structure'][0]
    for data in tablesDict['Capital Structure'][1:]:
        for index in range(1, len(data)):
            capStructureData[f'{data[0]} {capStructureHeaders[index]}'] = [data[index]]
    CAPITALSTRUCTURE = pd.DataFrame(capStructureData)

    # ----- Assertion Test -----
    columnNames = [
        'ISSUED ORDINARY No. of Shares', 
        'ISSUED ORDINARY Currency',
        'ISSUED ORDINARY Amount', 
        'PAID-UP ORDINARY No. of Shares',
        'PAID-UP ORDINARY Currency', 
        'PAID-UP ORDINARY Amount',
        'PAID-UP PREFERENCE No. of Shares', 
        'PAID-UP PREFERENCE Currency',
        'PAID-UP PREFERENCE Amount', 
        'PAID-UP OTHERS No. of Shares',
        'PAID-UP OTHERS Currency', 
        'PAID-UP OTHERS Amount', 
    ]
    for actual, expected in itertools.zip_longest(CAPITALSTRUCTURE.columns, columnNames):
        assert actual == expected, f'CAPITAL STRUCTURE has column {actual} but should be {expected}'
    # -------------------------- 

    # Table 5: CHARGES
    chargesData = {}
    for data in tablesDict['Charge(s)']:
        for index, value in enumerate(data):
            if index % 2:
                if columnName in chargesData:
                    chargesData[columnName].append(value)
                else:
                    chargesData[columnName] = [value]
            else:
                columnName = value
    CHARGES = pd.DataFrame.from_dict(chargesData)
    CHARGES.columns = [h.replace(':', '').replace('*','') for h in CHARGES.columns]

    # ----- Assertion Test -----
    columnNames = [
        'Charge No', 
        'Date of Charge', 
        'Chargee(s)',
        'Amount Secured and Currency', 
        'Status', 
    ]
    for actual, expected in itertools.zip_longest(CHARGES.columns, columnNames):
        assert actual == expected, f'CHARGES has column {actual} but should be {expected}'
    # -------------------------- 
    
    # Table 6: AUDITORS
    auditorsArr = np.array(tablesDict['Auditor(s)'])
    auditorsHeader = auditorsArr[0,:]
    auditorsData = auditorsArr[1:,:]
    AUDITORS = pd.DataFrame(data=auditorsData, columns=auditorsHeader)
    
    # ----- Assertion Test -----
    columnNames = [
        'Name', 
        'Date of Appointment', 
    ]
    for actual, expected in itertools.zip_longest(AUDITORS.columns, columnNames):
        assert actual == expected, f'AUDITORS has column {actual} but should be {expected}'
    # -------------------------- 

    # Table 7: OFFICERS / AUTHORISED REPRESENTATIVES
    officersAuthRepArr = np.array(tablesDict['Officer(s) / Authorised Representative(s)'])
    officersAuthRepHeaders = [h.replace(':', '').replace('*','') for h in officersAuthRepArr[0,:]]
    officersAuthRepData = officersAuthRepArr[1:,:]
    OFFICERSAUTHREPRESENTATIVE = pd.DataFrame(officersAuthRepData, columns=officersAuthRepHeaders)
    for columnName in ('Name\nID', 'Address\nDate of Change of Address', 'Date of Appointment/\nPosition Held'):
        if columnName in OFFICERSAUTHREPRESENTATIVE.columns:
            columnIndex = OFFICERSAUTHREPRESENTATIVE.columns.get_loc(columnName)
            splitNames = re.split('(/\n|\n)', columnName, maxsplit=1)[::2]
            for index, splitName in enumerate(splitNames):
                OFFICERSAUTHREPRESENTATIVE.insert(columnIndex + index, splitName, None)
            OFFICERSAUTHREPRESENTATIVE[splitNames] = OFFICERSAUTHREPRESENTATIVE[columnName].str.rsplit('\n', n=1, expand=True)
            OFFICERSAUTHREPRESENTATIVE.drop(columns=columnName, inplace=True)

    # ----- Assertion Test -----
    columnNames = [
        'Name', 
        'ID', 
        'Address', 
        'Date of Change of Address',
        'Nationality/Citizenship', 
        'Date of Appointment', 
        'Position Held', 
    ]
    for actual, expected in itertools.zip_longest(OFFICERSAUTHREPRESENTATIVE.columns, columnNames):
        assert actual == expected, f'OFFICERS / AUTH REPRESENTATIVE has column {actual} but should be {expected}'
    # -------------------------- 


    # Table 8: SHAREHOLDERS
    shareholderData = {}
    for index, data in enumerate(tablesDict['SHAREHOLDER(S)']):
        if index % 2:
            for column, value in zip(columns, data):
                if column in shareholderData:
                    shareholderData[column].append(value)
                else:
                    shareholderData[column] = [value]
        else:
            columns = data
    SHAREHOLDERS = pd.DataFrame.from_dict(shareholderData)
    SHAREHOLDERS.columns = [h.replace(':', '').replace('*','') for h in SHAREHOLDERS.columns]
    for columnName in ('Name\nID', 'Address\nDate of Change of Address'):
        if columnName in SHAREHOLDERS.columns:
            columnIndex = SHAREHOLDERS.columns.get_loc(columnName)
            splitNames = re.split('(/\n|\n)', columnName, maxsplit=1)[::2]
            for index, splitName in enumerate(splitNames):
                SHAREHOLDERS.insert(columnIndex + index, splitName, None)
            SHAREHOLDERS[splitNames] = SHAREHOLDERS[columnName].str.rsplit('\n', n=1, expand=True)
            SHAREHOLDERS.drop(columns=columnName, inplace=True)

    # ----- Assertion Test -----
    columnNames = [
        'Name', 
        'ID', 
        'Nationality/Citizenship', 
        'Address',
        'Date of Change of Address', 
        'Type', 
        'No Of Shares', 
        'Currency', 
    ]
    for actual, expected in itertools.zip_longest(SHAREHOLDERS.columns, columnNames):
        assert actual == expected, f'SHAREHOLDERS has column {actual} but should be {expected}'
    # -------------------------- 
        

    # Table 9: COMPLIANCE RECORD
    complianceRecordArr = np.array(tablesDict['Compliance Record'])
    complianceRecordHeaders = [h.replace(':', '').replace('*','') for h in complianceRecordArr[:,0]]
    complianceRecordData = complianceRecordArr[:,1:]
    COMPLIANCERECORD = pd.DataFrame(data=complianceRecordData.T, columns=complianceRecordHeaders)

    # ----- Assertion Test -----
    columnNames = [
        'Date of Last AGM', 
        'Date of Last AR', 
        'Date of A/C Laid at Last AGM', 
    ]
    for actual, expected in itertools.zip_longest(COMPLIANCERECORD.columns, columnNames):
        assert actual == expected, f'COMPLIANCE RECORD has column {actual} but should be {expected}'
    # -------------------------- 


    # Table 10: FINANCIAL DATA
    financialData = {
        f"Current {tablesDict['Financial Data'][1][0]}": [tablesDict['Financial Data'][1][1]], 
        f"Previous {tablesDict['Financial Data'][1][0]}": [tablesDict['Financial Data'][1][3]], 
        tablesDict['Financial Data'][2][0]: [tablesDict['Financial Data'][2][1]], 
    }
    for data in tablesDict['Financial Data'][3:]:
        financialData[f'Current {data[0]}'] = [data[1]]
        financialData[f'Previous {data[0]}'] = [data[3]]
        financialData[f"{data[0]} ({tablesDict['Financial Data'][1][2]})"] = [data[2]]
    FINANCIALDATA = pd.DataFrame(financialData)
    FINANCIALDATA.columns = [h.replace(':', '').replace('*','') for h in FINANCIALDATA.columns]

    # ----- Assertion Test -----
    columnNames = [
        'Current FYE',
        'Previous FYE',
        'CURRENCY',
        'Current Revenue',
        'Previous Revenue',
        'Revenue (% CHANGE)', 
        'Current Profit after tax',
        'Previous Profit after tax', 
        'Profit after tax (% CHANGE)',
        "Current Shareholders' fund", 
        "Previous Shareholders' fund",
        "Shareholders' fund (% CHANGE)", 
    ]
    for actual, expected in itertools.zip_longest(FINANCIALDATA.columns, columnNames):
        assert actual == expected, f'FINANCIAL DATA has column {actual} but should be {expected}'
    # -------------------------- 


    # Table 11: KEY RATIOS
    keyRatiosArr = np.array(tablesDict['Key Ratios'])
    keyRatiosHeaders = [h.replace(':', '').replace('*','') for h in keyRatiosArr[:,0]]
    keyRatiosData = keyRatiosArr[:,1:]
    KEYRATIOS = pd.DataFrame(data=keyRatiosData.T, columns=keyRatiosHeaders)
    keyRatiosData = {
        f"Current {tablesDict['Key Ratios'][0][0]}": [tablesDict['Key Ratios'][0][1]], 
        f"Previous {tablesDict['Key Ratios'][0][0]}": [tablesDict['Key Ratios'][0][2]], 
    }
    for data in tablesDict['Key Ratios'][1:]:
        keyRatiosData[f'Current {data[0]}'] = [data[1]]
        keyRatiosData[f'Previous {data[0]}'] = [data[2]]
    KEYRATIOS = pd.DataFrame(keyRatiosData)
    KEYRATIOS.columns = [h.replace(':', '').replace('*','') for h in KEYRATIOS.columns]

    # ----- Assertion Test -----
    columnNames = [
        'Current FYE', 
        'Previous FYE', 
        'Current Profit Margin',
        'Previous Profit Margin', 
        'Current Liquidity [times]',
        'Previous Liquidity [times]', 
        'Current Debt [times]',
        'Previous Debt [times]', 
    ]
    for actual, expected in itertools.zip_longest(KEYRATIOS.columns, columnNames):
        assert actual == expected, f'KEY RATIOS has column {actual} but should be {expected}'
    # --------------------------
    
    # Table 12: ANALYSIS
    split = re.search(r'(.*) \((.*)\)(.*)', tablesDict['ANALYSIS'][1][1])
    analysisData = {
        split.group(2).split()[0]: split.group(2).split()[1],
    }
    for data in tablesDict['ANALYSIS'][2:6]:
        analysisData[f'{split.group(1)} {data[0]}'] = [data[1]]
        analysisData[f"{tablesDict['ANALYSIS'][1][2]} {data[0]}"] = [data[2]]
    ANALYSIS = pd.DataFrame(analysisData)
    ANALYSIS.columns = [h.replace(':', '').replace('*','') for h in ANALYSIS.columns]

    # ----- Assertion Test -----
    columnNames = [
        'FYE', 
        'COMPANY LEVEL Revenue Growth', 
        'INDUSTRY MEDIAN Revenue Growth',
        'COMPANY LEVEL Return on Assets', 
        'INDUSTRY MEDIAN Return on Assets',
        'COMPANY LEVEL Total Asset Turnover',
        'INDUSTRY MEDIAN Total Asset Turnover',
        'COMPANY LEVEL Net Profit Margin', 
        'INDUSTRY MEDIAN Net Profit Margin'
    ]
    for actual, expected in itertools.zip_longest(ANALYSIS.columns, columnNames):
        assert actual == expected, f'ANALYSIS has column {actual} but should be {expected}'
    # --------------------------

    # Table 13: LITGATION SEARCH (WRIT OF SUMMONS / ORIGINATING CLAIM)
    # The first 3 rows are information on the dataset, which we would not require in our table construction
    # Likewise, the last row in the array is irrelevant
    writOfSummsArr = tablesDict['1) WRIT OF SUMMONS/ ORIGINATING CLAIM'][4:-1]
    writeOfSummmonsOriginatingClaimHeaders = [
        'SN', 
        'Court/Type', 
        'Case \nNo.', 
        'Year', 
        'Filing \nDate', 
        'Plaintiff / \nPetitioner / \nClaimant', 
        'Case Status / \nStatus Date/ \nRemarks', 
        'Plaintiff / \nClaimant \nStatus / \nStatus Date', 
        'Defendant \nStatus*/ \n \nStatus Date', 
        'A mount(s)', 
        'Last Updated \nin Experian \nDatabase',
        'Main Cause'
    ]
    # Creating the table for WRIT OF SUMMONS / ORIGINATING CLAIM
    WRITOFSUMMONSORGINATINGCLAIM = pd.DataFrame(columns=[h.replace('\n', '').replace('*','').replace('A mount(s)', 'Amount(s)') for h in writeOfSummmonsOriginatingClaimHeaders])

    # Concat and append the data to the table
    for rowIndex in range(len(writOfSummsArr) // 2):
        dataList = writOfSummsArr[2*rowIndex]
        dataList.extend([writOfSummsArr[2*rowIndex+1][1]])
        WRITOFSUMMONSORGINATINGCLAIM = WRITOFSUMMONSORGINATINGCLAIM.append(pd.DataFrame([dataList], 
            columns=list(WRITOFSUMMONSORGINATINGCLAIM.columns)), ignore_index=True)

    WRITOFSUMMONSORGINATINGCLAIM[['Case Status', 'Case Status Date', 'Case Status Remarks']] = WRITOFSUMMONSORGINATINGCLAIM['Case Status / Status Date/ Remarks'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:3]) #split Case Status, Date and Remarks into separate columns
    WRITOFSUMMONSORGINATINGCLAIM[['Plaintiff / Claimant Status', 'Plaintiff / Claimant Status Date']] = WRITOFSUMMONSORGINATINGCLAIM['Plaintiff / Claimant Status / Status Date'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:2]) #split Plaintiff / Claimant Status and Date into separate columns
    WRITOFSUMMONSORGINATINGCLAIM[['Defendant Status', 'Defendant Status Date']] = WRITOFSUMMONSORGINATINGCLAIM['Defendant Status/  Status Date'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:2]) #split Defendant Status and Date into separate columns
    WRITOFSUMMONSORGINATINGCLAIM = WRITOFSUMMONSORGINATINGCLAIM[[
        'SN', 
        'Court/Type', 
        'Case No.', 
        'Year', 
        'Filing Date',
        'Plaintiff / Petitioner / Claimant',
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
        'Court/Type', 
        'Case No.', 
        'Year', 
        'Filing Date',
        'Plaintiff / Petitioner / Claimant', 
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
    for actual, expected in itertools.zip_longest(WRITOFSUMMONSORGINATINGCLAIM.columns, columnNames):
        assert actual == expected, f'WRIT OF SUMMONS ORGINATING CLAIM has column {actual} but should be {expected}'
    # --------------------------

    # Table 14: LITGATION SEARCH (WINDING UP)
    windingUpArr = tablesDict['2) WINDING UP'][1:-1]

    # Creating the table for WRIT OF SUMMONS / ORIGINATING CLAIM
    WINDINGUP = pd.DataFrame(columns=[h.replace('\n', ' ').replace('*','') for h in windingUpArr[0]])

    for row in windingUpArr[1:]:
        WINDINGUP = WINDINGUP.append(pd.DataFrame([row], 
            columns=list(WINDINGUP.columns)), ignore_index=True)

    WINDINGUP[['Case Status', 'Case Status Date']] = WINDINGUP['Case Status / Status Date'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:2]) #split Case Status and Date into separate columns
    WINDINGUP[['Other Party Status', 'Other Party Status Date']] = WINDINGUP['Other Party Status/ Status Date'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:2]) #split Other Party Status and Date into separate columns
    WINDINGUP[['Defendant Status', 'Defendant Status Date']] = WINDINGUP['Defendant Status/ Status Date'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:2]) #split Defendant Status and Date into separate columns
    WINDINGUP = WINDINGUP[[
        'Type',
        'Case No.',
        'Year',
        'Filing Date',
        'Other Party Name',
        'Case Status', 
        'Case Status Date',
        'Other Party Status',
        'Other Party Status Date',
        'Defendant Status',
        'Defendant Status Date',
        'Amount(s)',
        'Last Updated in Experian Database'
    ]]

    # ----- Assertion Test -----
    columnNames = [
        'Type', 
        'Case No.', 
        'Year', 
        'Filing Date', 
        'Other Party Name',
        'Case Status', 
        'Case Status Date', 
        'Other Party Status',
        'Other Party Status Date', 
        'Defendant Status', 
        'Defendant Status Date',
        'Amount(s)', 
        'Last Updated in Experian Database', 
    ]
    for actual, expected in itertools.zip_longest(WINDINGUP.columns, columnNames):
        assert actual == expected, f'WINDING UP has column {actual} but should be {expected}'
    # --------------------------

    # Table 15: LITIGATION SEARCH (OS/OA/OP/OM)
    # The first 2 rows are irrelevant to our table construction, likewise for the last row in the dataset
    OSOAOPOMArr = tablesDict['3) OS/OA/OP/OM'][2:-1]

    # Initialise the table
    OSOAOPOM = pd.DataFrame(columns=[h.replace('\n', ' ').replace('*','') for h in OSOAOPOMArr[0]])
    for rowData in OSOAOPOMArr[1:]:
        OSOAOPOM = OSOAOPOM.append(pd.DataFrame([rowData], 
            columns=list(OSOAOPOM.columns)), ignore_index=True)

    OSOAOPOM[['Case Status', 'Case Status Date']] = OSOAOPOM['Case Status / Status Date'].apply(lambda x: pd.Series(re.split('(../...)', str(x).replace('\n', ''), 1))[:2]) #split Case Status and Date into separate columns
    OSOAOPOM[['Other Party Status', 'Other Party Status Date']] = OSOAOPOM['Other Party Status/ Status Date'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:2]) #split Other Party Status and Date into separate columns
    OSOAOPOM[['Defendant Status', 'Defendant Status Date']] = OSOAOPOM['Defendant Status/ Status Date'].apply(lambda x: pd.Series(re.split('(../....)', str(x).replace('\n', ''), 1))[:2]) #split Defendant Status and Date into separate columns
    OSOAOPOM = OSOAOPOM[[
        'Type',
        'Case No.',
        'Year',
        'Filing Date',
        'Other Party Name',
        'Case Status', 
        'Case Status Date',
        'Other Party Status',
        'Other Party Status Date',
        'Defendant Status',
        'Defendant Status Date',
        'Amount(s)',
        'Last Updated in Experian Database'
    ]]

    # ----- Assertion Test -----
    columnNames = [
        'Type',
        'Case No.',
        'Year',
        'Filing Date',
        'Other Party Name',
        'Case Status', 
        'Case Status Date', 
        'Other Party Status',
        'Other Party Status Date', 
        'Defendant Status', 
        'Defendant Status Date',
        'Amount(s)', 
        'Last Updated in Experian Database', 
    ]
    for actual, expected in itertools.zip_longest(OSOAOPOM.columns, columnNames):
        assert actual == expected, f'OSOAOPOM has column {actual} but should be {expected}'
    # --------------------------

    # Table 16: ADDITIONAL EXPERIAN PROPRIETARY INFORMATION
    addExpPropInfoArr = np.array(tablesDict['ADDITIONAL EXPERIAN PROPRIETARY INFORMATION'])
    addExpPropInfoHeaders = [h.replace(":", "").replace("*","") for h in addExpPropInfoArr[:,0]]
    addExpPropInfoData = addExpPropInfoArr[:,1:]
    ADDEXPPROPINFO = pd.DataFrame(addExpPropInfoData.T, columns=addExpPropInfoHeaders)

    # ----- Assertion Test -----
    columnNames = [
        'No. of Employees', 
        'Commercial Properties Owned', 
    ]
    for actual, expected in itertools.zip_longest(ADDEXPPROPINFO.columns, columnNames):
        assert actual == expected, f'ADD EXP PROP INFO has column {actual} but should be {expected}'
    # --------------------------

    # Table 17: ACCREDITATIONS
    accreditationsArr = np.array(tablesDict['ACCREDITATIONS'])
    accreditationsArrHeaders = [h.replace(":", "").replace("*","") for h in accreditationsArr[0]]
    accreditationsArrData = accreditationsArr[1:]

    ACCREDITATIONS = pd.DataFrame(accreditationsArrData, columns=accreditationsArrHeaders)

    # ----- Assertion Test -----
    columnNames = [
        'Award', 
        'Year', 
        'Ranking', 
    ]
    for actual, expected in itertools.zip_longest(ACCREDITATIONS.columns, columnNames):
        assert actual == expected, f'ACCREDITATIONS has column {actual} but should be {expected}'
    # --------------------------

    # Table 18: FINANCIAL RELATED SEARCH COUNT
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


    # ----- Assertion Test -----

    # --------------------------

    # Table 19: COMMERCIAL RELATED SEARCH COUNT
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

    # ----- Assertion Test -----

    # --------------------------
        
    # Table 20: LEGAL RELATED SEARCH COUNT
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

    for data in tablesDict['LEGAL RELATED SEARCH COUNT'][2:]:
        if len(data) == 14:
            year = data[0]
            add(year, 'All', 'All', data[1])
            for index in range(2, 14):
                add(year, tablesDict['LEGAL RELATED SEARCH COUNT'][1][index], 'All', data[index])
        else:
            for index in range(1, 13):
                add(year, tablesDict['LEGAL RELATED SEARCH COUNT'][1][index], data[0], data[index])
    LEGRELSEARCHCOUNT = pd.DataFrame(legalRelatedSearchCountData)

    # ----- Assertion Test -----

    # --------------------------

    ########################################################################################
    # Section 5: Column Renaming
    # Column headers for the respective tables will be renamed for ease of management in
    # downstream applications such as database querying
    ########################################################################################
    REQUESTCRITERIA.columns = [
        'request_date', 
        'requestor_name', 
        'requested_entity_name', 
        'requested_entity_id', 
        'request_id', 
    ]

    SEARCHRECORD.columns = [
        'entity_name', 
        'entity_id', 
    ]
    
    DETAILSOFCOMPANY.columns = [
        'entity_name', 
        'entity_id', 
        'registration_date', 
        'country_or_region_of_incorporation_or_registration', 
        'date_of_name_change', 
        'former_name', 
        'effective_date_of_former_name', 
        'company_type', 
        'registered_office_address', 
        'date_of_address_change', 
        'principal_activities', 
        'status', 
        'status_date', 
    ]
    
    CAPITALSTRUCTURE.columns = [
        'issued_ordinary_no_of_shares', 
        'currency_of_issued_ordinary', 
        'amount_of_issued_ordinary', 
        'paid_up_ordinary_no_of_shares',  
        'currency_of_paid_up_ordinary', 
        'amount_of_paid_up_ordinary', 
        'paid_up_preference_no_of_shares', 
        'currency_of_paid_up_preference', 
        'amount_of_paid_up_preference', 
        'paid_up_others_no_of_shares', 
        'currency_of_paid_up_others', 
        'amount_of_paid_up_others', 
    ]

    CHARGES.columns = [
        'charge_id', 
        'date_of_charge', 
        'chargee', 
        'amount_secured_and_currency', 
        'status', 
    ]

    AUDITORS.columns = [
        'auditor_name', 
        'date_of_appointment', 
    ]

    OFFICERSAUTHREPRESENTATIVE.columns = [
        'employee_name', 
        'employee_id', 
        'employee_address', 
        'date_of_change_of_address', 
        'nationality_or_citizenship', 
        'date_of_appointment', 
        'position_held', 
    ]

    SHAREHOLDERS.columns = [
        'shareholder_name', 
        'shareholder_id', 
        'nationality_or_citizenship', 
        'shareholder_address', 
        'date_of_change_of_address', 
        'type_of_shares', 
        'no_of_shares', 
        'currency', 
    ]

    COMPLIANCERECORD.columns = [
        'date_of_last_agm', 
        'date_of_last_ar', 
        'date_of_ac_laid_at_last_agm', 
    ]

    FINANCIALDATA.columns = [
        'current_fye', 
        'previous_fye', 
        'currency', 
        'current_fye_revenue', 
        'previous_fye_revenue', 
        'percentage_change_revenue', 
        'current_fye_profit_after_tax', 
        'previous_fye_profit_after_tax', 
        'percentage_change_profit_after_tax', 
        'current_fye_shareholders_fund', 
        'previous_fye_shareholders_fund', 
        'percentage_change_shareholders_fund', 
    ]

    KEYRATIOS.columns = [
        'current_fye', 
        'previous_fye', 
        'current_fye_profit_margin', 
        'previous_fye_profit_margin', 
        'current_fye_liquidity_times', 
        'previous_fye_liquidity_times', 
        'current_fye_debt_times', 
        'previous_fye_debt_times', 
    ]

    ANALYSIS.columns = [
        'fye', 
        'company_level_revenue_growth', 
        'industry_median_revenue_growth', 
        'company_level_return_on_assets', 
        'industry_median_return_on_assets', 
        'company_level_total_asset_turnover', 
        'industry_median_total_asset_turnover', 
        'company_level_net_profit_margin',
        'industry_median_net_profit_margin' 
    ]

    WRITOFSUMMONSORGINATINGCLAIM.columns = [
        'sn', 
        'court_type', 
        'case_no', 
        'year', 
        'date_of_filling', 
        'plaintiff', 
        'case_status', 
        'date_of_case_status', 
        'case_status_remarks', 
        'plaintiff_status', 
        'date_of_plaitiff_status', 
        'defendant_status', 
        'date_of_defendant_status', 
        'amount', 
        'last_updated', 
        'main_cause', 
    ]

    WINDINGUP.columns = [
        'type', 
        'case_no', 
        'year', 
        'date_of_filling', 
        'other_party_name', 
        'case_status', 
        'date_of_case_status', 
        'other_party_status', 
        'date_of_other_party_status', 
        'defendant_status', 
        'date_of_defendant_status', 
        'amount', 
        'last_updated'
    ]

    OSOAOPOM.columns = [
        'type', 
        'case_no', 
        'year', 
        'date_of_filing', 
        'other_party_name', 
        'case_status', 
        'date_of_case_status', 
        'other_party_status', 
        'date_of_other_party_status', 
        'defendant_status', 
        'date_of_defendant_status', 
        'amount', 
        'last_updated'
    ]

    ADDEXPPROPINFO.columns = [
        'num_of_employee', 
        'num_of_commerical_properties_owned', 
    ]
    
    ACCREDITATIONS.columns = [
        'award_name', 
        'year_of_award', 
        'award_ranking', 
    ]


    ########################################################################################
    # Section 6: Data export
    # Export all tables into an excel file for downstream application
    ########################################################################################

    # Output File Name will be according to entity number of requested company
    outputFilename = f"{REQUESTCRITERIA.requested_entity_id[0]}.xlsx"

    writer = pd.ExcelWriter(f'Output/{outputFilename}', engine='xlsxwriter')
    REQUESTCRITERIA.to_excel(writer, sheet_name='Request Criteria')
    SEARCHRECORD.to_excel(writer, sheet_name='Search Record')
    DETAILSOFCOMPANY.to_excel(writer, sheet_name='Details of Company')
    CAPITALSTRUCTURE.to_excel(writer, sheet_name='Capital Structure')
    CHARGES.to_excel(writer, sheet_name='Charges')
    AUDITORS.to_excel(writer, sheet_name='Auditors')
    OFFICERSAUTHREPRESENTATIVE.to_excel(writer, sheet_name='Officers Auth. Rep')
    SHAREHOLDERS.to_excel(writer, sheet_name='Shareholders')
    COMPLIANCERECORD.to_excel(writer, sheet_name='Compliance Record')
    FINANCIALDATA.to_excel(writer, sheet_name='Financial Data')
    KEYRATIOS.to_excel(writer, sheet_name='Key Ratios')
    ANALYSIS.to_excel(writer, sheet_name='Analysis')
    WRITOFSUMMONSORGINATINGCLAIM.to_excel(writer, sheet_name='Writ of Sum. Org. Claim')
    WINDINGUP.to_excel(writer, sheet_name='Winding Up')
    OSOAOPOM.to_excel(writer, sheet_name='OS OA OP OM')
    ADDEXPPROPINFO.to_excel(writer, sheet_name='Add Exp Prop. Info')
    ACCREDITATIONS.to_excel(writer, sheet_name='Accreditations')
    FINRELSEARCHCOUNT.to_excel(writer, sheet_name='Financial Related Search Count')
    COMRELSEARCHCOUNT.to_excel(writer, sheet_name='Commercial Related Search Count')
    LEGRELSEARCHCOUNT.to_excel(writer, sheet_name='Legal Related Search Count')
    writer.close()
    print(f'Exported as {REQUESTCRITERIA.requested_entity_id[0]} to subdirectory Output/')
    

if __name__ == "__main__":
    inputOutput = []
    directory = "../Dataset/eins_data"

    # Scans the current folder for all available PDF reports to be scrape
    for (dir_path, dir_names, file_names) in os.walk(directory):
        for fileName in file_names:
            inputOutput.append(
                [fileName, f"{fileName.split('.')[0]}.xlsx"]
            )
    for infile, outfile in inputOutput:
        main(directory, infile, outfile)

    print(f'====> {len(inputOutput)} PDF(s) successfully scraped!')