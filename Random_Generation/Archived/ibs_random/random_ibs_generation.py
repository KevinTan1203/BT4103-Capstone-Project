import datetime
import pandas as pd
import json
import itertools
import random
import string
import numpy as np
import joblib
import sys

sys.path.append('../../../Litigation Clustering/')

from litigation_clustering import label_litigation_main_cause, label_litigation_case_status, label_litigation_party_status

from tqdm import tqdm


def randdate(start_date, end_date, update=True):
    if end_date == start_date:
        return end_date
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    if update:
        global randomDate
        randomDate = random_date
    return random_date

def randdates(num, start_date, end_date, update=True):
    random_dates = []
    for _ in range(num):
        random_date = randdate(start_date, end_date, update=False)
        random_dates.append(random_date)
    if update:
        global randomDates
        randomDates = random_dates
    return random_dates

def random_Related_Search_Count_Generation(purposes, entityId):
    # Generate the 'month' and 'year' column
    months = ['All', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_col = months * (len(purposes) + 3)
    year_col = ['20XX'] * len(month_col)

    # Generate the purpose column    
    purpose_col = ['All'] * 13 + list(itertools.chain(*[[ele] * 13 for ele in purposes])) + ['All'] * 26


    # Most recent 2 years section
    def random_row_generation():
        try:
            randomAll = random.randint(0, 5)
            num_of_splits = random.randint(0, randomAll)
            splits = []
            for i in range(num_of_splits - 1):
                split = random.randrange(1, randomAll - sum(splits))
                splits.append(split)
            splits.append(randomAll - sum(splits))

            # Create the data row
            row = [randomAll]
            monthsValue = [0] * (12 - len(splits)) + splits
            random.shuffle(monthsValue)
            row.extend(monthsValue)
            return row
        except ValueError:
            return [0] * 13

    randomRows = [random_row_generation() for i in range(len(purposes))]
    totalSum = [sum(row) for row in zip(*randomRows)]
    
    # Generate the count column
    count_col = totalSum + list(itertools.chain(*randomRows)) + random_row_generation() + random_row_generation()

    entity_col = [entityId for i in range(len(count_col))]

    # Creation of Dataframe
    dataframe = pd.DataFrame(data= {
        'entity_id': entity_col,
        'year': year_col, 
        'month': month_col, 
        'purpose': purpose_col, 
        'count': count_col
    }, columns=['entity_id', 'year', 'month', 'purpose', 'count'])

    return dataframe

def main():
    with open('../../ibs_variables.json') as f:
        data = json.load(f)

    # Intialise date variable
    global randomDate
    global randomDates
    req_date = randdate(datetime.datetime(2023, 1, 1), datetime.datetime.today())
    reg_date = randdate(datetime.datetime(2000, 1, 1), req_date)

    # Imported fields
    MAIN_CAUSE = list(pd.read_csv('../../../Dataset/litigation_data/litigation_main_cause.csv')['Main Cause'])
    CASE_STATUS = list(pd.read_csv('../../../Dataset/litigation_data/litigation_case_status.csv')['Case Status'])
    PARTY_STATUS = list(pd.read_csv('../../../Dataset/litigation_data/litigation_party_status.csv')['Party (Plaintiff/Defendant) Status'])
    ENTITY_TYPE_INDICATOR = list(pd.read_csv('../../../ibs/uen mapping/UEN Mapping.csv')['Entity-Type Indicator'])
    COY_STATUS = data['COY_STATUS']
    POSITION = data['POSITION']
    WRIT_SUM_COURT_TYPE = data['WRIT_SUM_COURT_TYPE']
    FINANCIAL_REL_SEARCH_COUNT_VAL = data['FINANCIAL_REL_SEARCH_COUNT_VAL']
    COMMERCIAL_REL_SEARCH_COUNT_VAL = data['COMMERCIAL_REL_SEARCH_COUNT_VAL']
    LEGAL_REL_SEARCH_COUNT_VAL = data['LEGAL_REL_SEARCH_COUNT_VAL']
    streetNameFirst = data['streetNameFirst']
    streetNameLast = data['streetNameLast']
    firstName = data['firstName']
    middleName = data['middleName']
    sector = data['sector']
    companyType = data['companyType']
    humanFirstName = data['humanFirstName']
    humanMiddleName = data['humanMiddleName']
    humanLastName = data['humanLastName']
    accreditationAwards = data['accreditationAwards']

    # Duplicated fields (Singular / Composite)
    ENTITY_ID = f'{random.choice(string.ascii_uppercase)}{random.randint(100, 999)}XXXX{random.choice(string.ascii_uppercase)}'

    # Multiple Occurence fields (variable according to each report)
    NUM_OF_CURR_BUSINESS_COUNT = random.randint(1, 5)
    NUM_OF_PREV_BUSINESSES_COUNT = random.randint(1, 5)
    ACRRED_COUNT = random.randint(1, 5)
    BANKRUPTCY_COUNT = random.randint(1, 5)
    INDV_LIT_SEARCH_COUNT = random.randint(1, 5)
    BUSINESS_LIT_SEARCH_COUNT = random.randint(1, 5) 

    # Predefined Fields
    INDIVIDUAL_NAME = [f'{random.choice(humanFirstName)}', f'{random.choice(humanMiddleName)} {random.choice(humanLastName)}']
    CURRBUSINESSES = [f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)} {random.choice(companyType)}' for i in range(NUM_OF_CURR_BUSINESS_COUNT)]
    PREVBUSINESSES = [f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)} {random.choice(companyType)}' for i in range(NUM_OF_PREV_BUSINESSES_COUNT)]
    
    # Initialise clustering models
    litigation_main_cause_clustering_model = joblib.load('../../../Litigation Clustering/litigation_main_cause_clustering.pkl')
    litigation_case_status_clustering_model = joblib.load('../../../Litigation Clustering/litigation_case_status_clustering.pkl')
    litigation_party_status_clustering_model = joblib.load('../../../Litigation Clustering/litigation_party_status_clustering.pkl')

    # Complex Field Function
    def nameOfPrivateTrusteesAppointed():
        random_name = f'{random.choice(humanFirstName)}', f'{random.choice(humanMiddleName)} {random.choice(humanLastName)}'
        random_address = f'{random.choice(streetNameFirst)} {random.choice(streetNameLast)} #{random.randint(1, 30)}-{random.randint(1, 50)} SINGAPORE {random.randint(100000, 999999)}'
        return ' '.join(list(random_name)) + ' ' + random_address


    random_params = {
        "Request Criteria": {
            'request_date':                             req_date.strftime('%Y/%m/%d'),
            'requestor_name':                           "SUBSCRIBER",
            'requested_individual_name':                ' '.join(INDIVIDUAL_NAME),
            'requested_id_no':                          ENTITY_ID,
            'request_id':                               "IBS SAMPLE",
        },
        "Search Record": {
            'individual_name':                          '\n'.join([f'{index + 1}) {" ".join(fullName)}' for index, fullName in enumerate(itertools.permutations(INDIVIDUAL_NAME, 2) )]),
            'individual_id':                            ENTITY_ID,
            'available_address':                        f'{random.choice(streetNameFirst)} {random.choice(streetNameLast)} #{random.randint(1, 30)}- {random.randint(1, 50)} SINGAPORE {random.randint(100000, 999999)}',
        },
        "Current Business": {
            'business_name':                            [f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)} {random.choice(companyType)}' for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
            'registration_no':                          [random.choice([
                                                            f'{"".join(random.choices(string.digits, k=8))}{random.choice(string.ascii_uppercase)}', 
                                                            f'{reg_date.year}{"".join(random.choices(string.digits, k=5))}{random.choice(string.ascii_uppercase)}', 
                                                            f'T{reg_date.year % 100:02}{random.choice(ENTITY_TYPE_INDICATOR)}{"".join(random.choices(string.digits, k=4))}{random.choice(string.ascii_uppercase)}', 
                                                        ]) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
            'status':                                   [random.choice(COY_STATUS) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
            'position':                                 ['\n'.join(random.sample(POSITION, random.randint(1, len(POSITION)))) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
            'appointment_date':                         [reg_date.strftime('%Y/%m/%d') for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
            'current_directors_todate_count':           [random.randint(0, 3) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
            'current_secretaries_todate_count':         [random.randint(0, 3) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
            'current_alternate_directors_todate_count': [random.randint(0, 3) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
            'active_charges_todate_count':              [random.randint(0, 3) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
            'current_shareholders_todate_count':        [random.randint(0, 3) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
            'subsidiary_todate_count':                  [random.randint(0, 3) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
        },
        "Previous Business": {
            'business_name':                            PREVBUSINESSES,
            'registration_no':                          [random.choice([
                                                            f'{"".join(random.choices(string.digits, k=8))}{random.choice(string.ascii_uppercase)}', 
                                                            f'{reg_date.year}{"".join(random.choices(string.digits, k=5))}{random.choice(string.ascii_uppercase)}', 
                                                            f'T{reg_date.year % 100}{random.choice(ENTITY_TYPE_INDICATOR)}{"".join(random.choices(string.digits, k=4))}{random.choice(string.ascii_uppercase)}', 
                                                        ]) for i in range(NUM_OF_PREV_BUSINESSES_COUNT)],
            'status':                                   [random.choice(COY_STATUS) for i in range(NUM_OF_PREV_BUSINESSES_COUNT)],
            'position':                                 [random.choice(POSITION) for i in range(NUM_OF_PREV_BUSINESSES_COUNT)],
            'cessation_date':                           [randdate(datetime.datetime(1900, 1, 1), reg_date).strftime('%Y/%m/%d') for i in range(NUM_OF_PREV_BUSINESSES_COUNT)],
        },
        "Current Business Lit Trace": {
            'business_name':                            list(itertools.chain(*[[biz] * 5 for biz in CURRBUSINESSES])),
            'year':                                     list(itertools.chain(*[[f'{req_date.year - 1}'] * 5 for _ in CURRBUSINESSES])),
            'enquiries':                                list(itertools.chain(*[['Litigation Trace: District Court\n($60,000 - $250,000)', 'Litigation Trace: High Court\n(> $250,000)', 'Litigation Trace: Magistrate Court\n(< $60,000)', 'OS/OA/OP/OM Trace', 'Winding Up Trace'] for biz in CURRBUSINESSES])),
            'current_year_after_9_Jan':                 [random.randint(0, 1) for _ in range(NUM_OF_CURR_BUSINESS_COUNT * 5)],
            'previous_year_before_9_Jan':               [random.randint(0, 1) for _ in range(NUM_OF_CURR_BUSINESS_COUNT * 5)],
        },
        "Business Lit Search": {
            'sn':                                       [i+1 for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'court_type':                               [random.choice(WRIT_SUM_COURT_TYPE) for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'case_no':                                  [random.randint(1000, 9999) for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'year':                                     [min(randomDates[i], randomDates[-i - 1]).year for i in range(len(randdates(2 * BUSINESS_LIT_SEARCH_COUNT, reg_date, req_date)) // 2)],
            'filing_date':                              [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'plaintiff':                                [f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)} {random.choice(companyType)}' for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'case_status':                              [random.choice(CASE_STATUS) for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'case_status_date':                         [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'case_status_remarks':                      [np.nan for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'plaintiff_status':                         [random.choice(PARTY_STATUS) for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'plaintiff_status_date':                    [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'defendant_status':                         [random.choice(PARTY_STATUS) for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'defendant_status_date':                    [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'amount':                                   [f'SGD {random.randint(10000, 90000)}' for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'last_update':                              [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(BUSINESS_LIT_SEARCH_COUNT)],
            'main_cause':                               [random.choice(MAIN_CAUSE) for i in range(BUSINESS_LIT_SEARCH_COUNT)],
        },
        "Bankruptcy Records": {
            'case_no':                                  [random.randint(100, 9999) for i in range(BANKRUPTCY_COUNT)],
            'year':                                     [min(randomDates[i], randomDates[-i - 1]).year for i in range(len(randdates(2 * BANKRUPTCY_COUNT, reg_date, req_date)) // 2)],
            'filing_date':                              [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(BANKRUPTCY_COUNT)],
            'plaintiff':                                [f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)} {random.choice(companyType)}' for i in range(BANKRUPTCY_COUNT)],
            'case_status':                              [random.choice(CASE_STATUS) for i in range(BANKRUPTCY_COUNT)],
            'case_status_date':                         [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(BANKRUPTCY_COUNT)],
            'case_status_remarks':                      [np.nan for i in range(BANKRUPTCY_COUNT)],
            'plaintiff_status':                         [random.choice(PARTY_STATUS) for i in range(BANKRUPTCY_COUNT)],
            'plaintiff_status_date':                    [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(BANKRUPTCY_COUNT)],
            'defendant_status':                         [random.choice(PARTY_STATUS) for i in range(BANKRUPTCY_COUNT)],
            'defendant_status_date':                    [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(BANKRUPTCY_COUNT)],
            'amount':                                   [f'SGD {random.randint(10000, 90000)}' for i in range(BANKRUPTCY_COUNT)],
            'last_update':                              [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(BANKRUPTCY_COUNT)],
            'name_of_private_trustees':                 [nameOfPrivateTrusteesAppointed() for i in range(BANKRUPTCY_COUNT)],
        },
        "Individual Lit Search": {
            'sn':                                       [i+1 for i in range(INDV_LIT_SEARCH_COUNT)],
            'court_type':                               [random.choice(WRIT_SUM_COURT_TYPE) for i in range(INDV_LIT_SEARCH_COUNT)],
            'case_no':                                  [random.randint(1000, 9999) for i in range(INDV_LIT_SEARCH_COUNT)],
            'year':                                     ['20XX' for i in range(INDV_LIT_SEARCH_COUNT)],
            'year':                                     [min(randomDates[i], randomDates[-i - 1]).year for i in range(len(randdates(2 * INDV_LIT_SEARCH_COUNT, reg_date, req_date)) // 2)],
            'filing_date':                              [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(INDV_LIT_SEARCH_COUNT)],
            'plaintiff':                                [f'{random.choice(humanFirstName)} {random.choice(humanMiddleName)} {random.choice(humanLastName)}' for i in range(INDV_LIT_SEARCH_COUNT)],
            'case_status':                              [random.choice(CASE_STATUS) for i in range(INDV_LIT_SEARCH_COUNT)],
            'case_status_date':                         [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(INDV_LIT_SEARCH_COUNT)],
            'case_status_remarks':                      [np.nan for i in range(INDV_LIT_SEARCH_COUNT)],
            'plaintiff_status':                         [random.choice(PARTY_STATUS) for i in range(INDV_LIT_SEARCH_COUNT)],
            'plaintiff_status_date':                    [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(INDV_LIT_SEARCH_COUNT)],
            'defendant_status':                         [random.choice(PARTY_STATUS) for i in range(INDV_LIT_SEARCH_COUNT)],
            'defendant_status_date':                    [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(INDV_LIT_SEARCH_COUNT)],
            'amount':                                   [f'SGD {random.randint(10000, 90000)}' for i in range(INDV_LIT_SEARCH_COUNT)],
            'last_update':                              [randdate(datetime.datetime(2000, 1, 1), datetime.datetime(2020, 1, 1)).strftime('%Y/%m/%d') for i in range(INDV_LIT_SEARCH_COUNT)],
            'main_cause':                               [random.choice(MAIN_CAUSE) for i in range(INDV_LIT_SEARCH_COUNT)],
        },
        "Accreditation": {
            'business':                                 [f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)}' for i in range(ACRRED_COUNT)],
            'award_name':                               [f'{random.choice(accreditationAwards)}' for i in range(ACRRED_COUNT)],
            'award_ranking':                            [f'{random.randint(2000, 2020)} Ranked {random.randint(1, 1000)}' for i in range(ACRRED_COUNT)],
        },
        "Financial Related Search Count": { 
            'individual_id':                            ENTITY_ID,
            'year':                                     f'20XX',
            'month':                                    None,
            'purpose':                                  list(random.sample(FINANCIAL_REL_SEARCH_COUNT_VAL, random.randint(1, len(FINANCIAL_REL_SEARCH_COUNT_VAL)))),
            'count':                                    None,
        },
        "Commercial Related Search Count": {
            'individual_id':                            ENTITY_ID,
            'year':                                     f'20XX',
            'month':                                    None,
            'purpose':                                  list(random.sample(COMMERCIAL_REL_SEARCH_COUNT_VAL, random.randint(1, len(COMMERCIAL_REL_SEARCH_COUNT_VAL)))),
            'count':                                    None,
        },
        "Legal Related Search Count": {
            'individual_id':                            ENTITY_ID,
            'year':                                     f'20XX',
            'month':                                    None,
            'purpose':                                  list(random.sample(LEGAL_REL_SEARCH_COUNT_VAL, random.randint(1, len(LEGAL_REL_SEARCH_COUNT_VAL)))),
            'count':                                    None,
        },
    }

    ################################################################################
    ############################### Table Generation ###############################
    ################################################################################

    # Table 1: Request Criteria
    random_req_criteria = pd.DataFrame(
        data=[list(random_params['Request Criteria'].values())], 
        columns=random_params['Request Criteria'].keys()
    )

    # Table 2: Search Record
    random_search_rec = pd.DataFrame(
        data=[list(random_params['Search Record'].values())], 
        columns=random_params['Search Record'].keys()
    )

    # Table 3: Table 3: Current Business
    random_current_business = pd.DataFrame(
        data=random_params['Current Business'], 
        columns=random_params['Current Business'].keys()
    )

    # Table 4: Previous Busines
    randon_previous_business = pd.DataFrame(
        data=random_params['Previous Business'], 
        columns=random_params['Previous Business'].keys()
    )

    # Table 5: Current Business Lit Trace
    randomm_curr_business_lit_trace = pd.DataFrame(
        data=random_params['Current Business Lit Trace'], 
        columns=random_params['Current Business Lit Trace'].keys()
    )

    # Table 6: Business Lit Search
    random_business_lit_search = pd.DataFrame(
        data=random_params['Business Lit Search'], 
        columns=random_params['Business Lit Search'].keys()
    )
    random_business_lit_search['main_cause_category'] = random_business_lit_search['main_cause'].apply(lambda x: label_litigation_main_cause(litigation_main_cause_clustering_model, x))
    random_business_lit_search['case_status_category'] = random_business_lit_search['case_status'].apply(lambda x: label_litigation_case_status(litigation_case_status_clustering_model, x))
    random_business_lit_search['plaintiff_status_category'] = random_business_lit_search['plaintiff_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))
    random_business_lit_search['defendant_status_category'] = random_business_lit_search['defendant_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))

    # Table 7: Bankruptcy Records
    random_bankruptcy_rec = pd.DataFrame(
        data=random_params['Bankruptcy Records'], 
        columns=random_params['Bankruptcy Records'].keys()
    )
    random_bankruptcy_rec['case_status_category'] = random_bankruptcy_rec['case_status'].apply(lambda x: label_litigation_case_status(litigation_case_status_clustering_model, x))
    random_bankruptcy_rec['plaintiff_status_category'] = random_bankruptcy_rec['plaintiff_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))
    random_bankruptcy_rec['defendant_status_category'] = random_bankruptcy_rec['defendant_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))

    # Table 8: Individual Lit Search
    random_indv_lit_search = pd.DataFrame(
        data=random_params['Individual Lit Search'], 
        columns=random_params['Individual Lit Search'].keys(),
    )
    random_indv_lit_search['main_cause_category'] = random_indv_lit_search['main_cause'].apply(lambda x: label_litigation_main_cause(litigation_main_cause_clustering_model, x))
    random_indv_lit_search['case_status_category'] = random_indv_lit_search['case_status'].apply(lambda x: label_litigation_case_status(litigation_case_status_clustering_model, x))
    random_indv_lit_search['plaintiff_status_category'] = random_indv_lit_search['plaintiff_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))
    random_indv_lit_search['defendant_status_category'] = random_indv_lit_search['defendant_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))

    # Table 9: Accreditation
    random_accreditation = pd.DataFrame(
        data=random_params['Accreditation'], 
        columns=random_params['Accreditation'].keys()
    )

    # Table 10: Financial Related Search Count  
    random_fin_rel_search_count = random_Related_Search_Count_Generation(
        random_params['Financial Related Search Count']['purpose'],
        random_params['Financial Related Search Count']['individual_id']
    )

    # Table 11: Commercial Related Search Count
    random_comm_rel_search_count = random_Related_Search_Count_Generation(
        random_params['Commercial Related Search Count']['purpose'],
        random_params['Commercial Related Search Count']['individual_id']
    )

    # Table 12: Legal Related Search Count 
    random_leg_rel_search_count = random_Related_Search_Count_Generation(
        random_params['Legal Related Search Count']['purpose'],
        random_params['Legal Related Search Count']['individual_id']
    )


    ################################################################################
    ############################### Export the data ################################
    ################################################################################
    # Output Data
    writer = pd.ExcelWriter(f'../../Outputs/IBS_Random_Output/{ENTITY_ID}.xlsx', engine='xlsxwriter')

    random_req_criteria.to_excel(writer, sheet_name='Request Criteria', index=False)
    random_search_rec.to_excel(writer, sheet_name='Search Record', index=False)
    random_current_business.to_excel(writer, sheet_name='Current Business', index=False)
    randon_previous_business.to_excel(writer, sheet_name='Previous Business', index=False)
    randomm_curr_business_lit_trace.to_excel(writer, sheet_name='Current Business Lit Trace', index=False)
    random_business_lit_search.to_excel(writer, sheet_name='Business Lit Search', index=False)
    random_bankruptcy_rec.to_excel(writer, sheet_name='Bankruptcy Record', index=False)
    random_indv_lit_search.to_excel(writer, sheet_name='Individual Lit Search', index=False)
    random_accreditation.to_excel(writer, sheet_name='Accreditation', index=False)
    random_fin_rel_search_count.to_excel(writer, sheet_name='Financial Related Search Count', index=False)
    random_comm_rel_search_count.to_excel(writer, sheet_name='Commercial Related Search Count', index=False)
    random_leg_rel_search_count.to_excel(writer, sheet_name='Legal Related Search Count', index=False)

    writer.close()


if __name__ == "__main__":
    numberOfRandomData = 20
    for i in tqdm(range(numberOfRandomData)):
        main()
    print(f'====> {numberOfRandomData} random generation(s) executed successfully!')
