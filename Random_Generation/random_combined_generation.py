import datetime
import pandas as pd
import numpy as np
import json
import itertools
import random
import string
import os
import joblib
import sys
import re
from tqdm import tqdm

# run from combined_random folder
sys.path.append('../Litigation Clustering/')
sys.path.append('../Ssic Mapping/')

from ssic_mapping import ssic_mapping
from litigation_clustering import label_litigation_main_cause, label_litigation_case_status, label_litigation_party_status


# These two functions are used for generation of random dates between a start and end parameter
def randdate(start_date, end_date, update=True):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    if days_between_dates:
        random_number_of_days = random.randrange(days_between_dates)
    else:
        random_number_of_days = 0
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

# Complex Search Count Generation
def random_Related_Search_Count_Generation(purposes, entityId, year):
    # Generate the 'month' and 'year' column
    months = ['All', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_col = months * (len(purposes) + 3)
    year_col = [year] * len(months) * (len(purposes) + 1)
    year_col.extend([year-1] * len(months))
    year_col.extend([year-2] * len(months))

    # Generate the purpose column    
    purpose_col = ['All'] * 13 + list(itertools.chain(*[[ele] * 13 for ele in purposes])) + ['All'] * 26

    # Most recent 2 years section, where there may be more than one related search count purpose
    # For any given purpose, there will be a need for random generation to take place
    # and this inner function will handle it
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
    
    # Generate the Count Column
    count_col = totalSum + list(itertools.chain(*randomRows)) + random_row_generation() + random_row_generation()

    # Genrate the entity column
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
    with open('combined_variables.json') as f:
        data = json.load(f)

    # Intialise date variable
    global randomDate
    global randomDates
    req_date = randdate(datetime.datetime(2023, 1, 1), datetime.datetime.today())
    reg_date = randdate(datetime.datetime(2000, 1, 1), req_date)

    # Imported fields
    MAIN_CAUSE = list(pd.read_csv('../Dataset/litigation_data/litigation_main_cause.csv')['Main Cause'])
    CASE_STATUS = list(pd.read_csv('../Dataset/litigation_data/litigation_case_status.csv')['Case Status'])
    PARTY_STATUS = list(pd.read_csv('../Dataset/litigation_data/litigation_party_status.csv')['Party (Plaintiff/Defendant) Status'])
    ENTITY_TYPE_INDICATOR = list(pd.read_csv('../Dataset/uen_data/UEN Mapping.csv')['Entity-Type Indicator'])
    CHARGE_STATUS = data['CHARGE_STATUS']
    COUNTRY = data['COUNTRY']
    SHARE_TYPE = data['SHARE_TYPE']
    COY_TYPE = data['COY_TYPE']
    COY_STATUS = data['COY_STATUS']
    AUDITOR = data['AUDITOR']
    NATIONALITY = data['NATIONALITY']
    OFFICERS_POS_HELD = data['OFFICERS_POS_HELD']
    WRIT_SUM_COURT_TYPE = data['WRIT_SUM_COURT_TYPE']
    FINANCIAL_REL_SEARCH_COUNT_VAL = data['FINANCIAL_REL_SEARCH_COUNT_VAL']
    COMMERCIAL_REL_SEARCH_COUNT_VAL = data['COMMERCIAL_REL_SEARCH_COUNT_VAL']
    LEGAL_REL_SEARCH_COUNT_VAL = data['LEGAL_REL_SEARCH_COUNT_VAL']
    firstName = data['firstName']
    middleName = data['middleName']
    sector = data['sector']
    streetNameFirst = data['streetNameFirst']
    streetNameLast = data['streetNameLast']
    companyType = data['companyType']
    humanFirstName = data['humanFirstName']
    humanMiddleName = data['humanMiddleName']
    humanLastName = data['humanLastName']
    accreditationAwards = data['accreditationAwards']

    # Duplicated fields (Singular / Composite)
    ENTITY_ID = random.choice([
        f'{"".join(random.choices(string.digits, k=8))}{random.choice(string.ascii_uppercase)}', 
        f'{reg_date.year}{"".join(random.choices(string.digits, k=5))}{random.choice(string.ascii_uppercase)}', 
        f'T{reg_date.year % 100:02}{random.choice(ENTITY_TYPE_INDICATOR)}{"".join(random.choices(string.digits, k=4))}{random.choice(string.ascii_uppercase)}', 
    ])
    ENTITY_NAME = f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)} {random.choice(companyType)}'

    # Multiple Occurence fields (variable according to each report)
    NUM_OF_CHARGES = random.randint(1, 5)
    NUM_OF_SHAREHOLDERS = random.randint(1, 5)
    NUM_OF_OFFICERS_AUTH_REP = random.randint(1, 8)
    WRIT_SUM_ORGS_CLAIM_COUNT = random.randint(1, 3)
    WINDING_UP_COUNT = random.randint(1, 5)
    OSOAOPOM_COUNT = random.randint(1, 3)
    ACRRED_COUNT = random.randint(1, 5)

    # Predefined-fields
    CURR_FYE_REV = random.randint(10000000000, 90000000000)
    PAT_CURR_FYE = CURR_FYE_REV - random.randint(100000000, 999000000)
    SHAREHOLDERSFUND_CURR_FYE = CURR_FYE_REV - random.randint(900000000, 999000000)
    PREV_FYE_REV = random.randint(10000000000, 90000000000)
    PAT_PREV_FYE = PREV_FYE_REV - random.randint(100000000, 999000000)
    SHAREHOLDERSFUND_PREV_FYE = PREV_FYE_REV - random.randint(900000000, 999000000)

    # Initialise ssic mapping
    ssic_mapper = pd.read_csv('../Dataset/ssic_data/ssic_mapping.csv', dtype=str)
    
    # Initialise clustering models
    litigation_main_cause_clustering_model = joblib.load('../Litigation Clustering/litigation_main_cause_clustering.pkl')
    litigation_case_status_clustering_model = joblib.load('../Litigation Clustering/litigation_case_status_clustering.pkl')
    litigation_party_status_clustering_model = joblib.load('../Litigation Clustering/litigation_party_status_clustering.pkl')

    # Complex Field Function
    def nameOfPrivateTrusteesAppointed():
        random_name = f'{random.choice(humanFirstName)}', f'{random.choice(humanMiddleName)} {random.choice(humanLastName)}'
        random_address = f'{random.choice(streetNameFirst)} {random.choice(streetNameLast)} #{random.randint(1, 30)}-{random.randint(1, 50)} SINGAPORE {random.randint(100000, 999999)}'
        return ' '.join(list(random_name)) + ' ' + random_address


    # ---------------------------------------- EINS REPORT ---------------------------------------- #

    # Limits for each random attribute generated
    eins_random_params = {
        'Request Criteria': {
            'request_date':                                         req_date.strftime('%Y/%m/%d'),
            'requestor_name':                                       f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)} {random.choice(companyType)}', 
            'requested_entity_name':                                ENTITY_NAME,
            'requested_entity_id':                                  ENTITY_ID,
            'request_id':                                           'EINSG SAMPLE', 
        },
        'Search Record':{
            'entity_name':                                          ENTITY_NAME,
            'entity_id':                                            ENTITY_ID, 
        },
        'Details of Company':{
            'entity_name':                                          ENTITY_NAME,
            'entity_id':                                            ENTITY_ID,
            'registration_date':                                    reg_date.strftime('%Y/%m/%d'),
            'country_or_region_of_incorporation_or_registration':   random.choice(COUNTRY),
            'date_of_name_change':                                  randdate(reg_date, req_date).strftime('%Y/%m/%d'),
            'former_name':                                          f'{ENTITY_NAME}',
            'effective_date_of_former_name':                        randdate(reg_date, randomDate).strftime('%Y/%m/%d'),
            'company_type':                                         random.choice(COY_TYPE),
            'registered_office_address':                            f'{random.choice(streetNameFirst)} {random.choice(streetNameLast)} #{random.randint(1, 30)}-{random.randint(1, 50)} SINGAPORE {random.randint(100000, 999999)}',
            'date_of_address_change':                               randdate(reg_date, req_date).strftime('%Y/%m/%d'),
            'principal_activities':                                 random.choice(ssic_mapper['Sub-Class'] + ' ('+ ssic_mapper[ssic_mapper.columns[5]] + ')'),
            'status':                                               random.choice(COY_STATUS),
            'status_date':                                          randdate(reg_date, req_date).strftime('%Y/%m/%d'),  
        },
        'Capital Structure':{
            'entity_id':                                            ENTITY_ID,
            'issued_ordinary_no_of_shares':                         random.randint(10000, 10000000),
            'currency_of_issued_ordinary':                          'SINGAPORE, DOLLARS',
            'amount_of_issued_ordinary':                            random.randint(10000, 10000000),
            'paid_up_ordinary_no_of_shares':                        random.randint(10000, 10000000),
            'currency_of_paid_up_ordinary':                         'SINGAPORE, DOLLARS',
            'amount_of_paid_up_ordinary':                           random.randint(10000, 10000000),
            'paid_up_preference_no_of_shares':                      random.randint(10000, 10000000),
            'currency_of_paid_up_preference':                       'SINGAPORE, DOLLARS',
            'amount_of_paid_up_preference':                         random.randint(10000, 10000000),
            'paid_up_others_no_of_shares':                          random.randint(10000, 10000000), 
            'currency_of_paid_up_others':                           'SINGAPORE, DOLLARS', 
            'amount_of_paid_up_others':                             random.randint(10000, 10000000),
        },
        'Charges':{
            'charge_id':                                            [f'C{i.year}{"".join(random.choices(string.digits, k=5))}' for i in randdates(NUM_OF_CHARGES, reg_date, req_date)],
            'date_of_charge':                                       [randomDates[i].strftime('%Y/%m/%d') for i in range(NUM_OF_CHARGES)],
            'chargee':                                              ['BANK NAME' for _ in range(NUM_OF_CHARGES)],
            'amount_secured_and_currency':                          [f'{random.randint(10000, 100000000)} SINGAPORE, DOLLARS' for _ in range(NUM_OF_CHARGES)],
            'status':                                               [random.choice(CHARGE_STATUS) for i in range(NUM_OF_CHARGES)],
            'entity_id':                                            ENTITY_ID,
        },
        'Auditors':{
            'auditor_name':                                         random.choice(AUDITOR), 
            'date_of_appointment':                                  randdate(reg_date, req_date).strftime('%Y/%m/%d'),
            'entity_id':                                            ENTITY_ID,
        },
        'Officers Auth. Rep':{
            'employee_name':                                        [f'{random.choice(humanFirstName)} {random.choice(humanMiddleName)} {random.choice(humanLastName)}' for _ in range(NUM_OF_OFFICERS_AUTH_REP)],
            'employee_id':                                          [f'{random.choice(string.ascii_uppercase)}{random.randint(100, 999)}XXXX{random.choice(string.ascii_uppercase)}' for _ in range(NUM_OF_OFFICERS_AUTH_REP)],
            'employee_address':                                     [f'{random.choice(streetNameFirst)} {random.choice(streetNameLast)} #{random.randint(1, 30)}-{random.randint(1, 50)} {random.choice(NATIONALITY)} {random.randint(100000, 999999)}' for _ in range(NUM_OF_OFFICERS_AUTH_REP)],
            'date_of_change_of_address':                            [random.choice(['-', i.strftime('%Y/%m/%d')]) for i in randdates(NUM_OF_OFFICERS_AUTH_REP, reg_date, req_date)],
            'nationality_or_citizenship':                           [random.choice(NATIONALITY) for _ in range(NUM_OF_OFFICERS_AUTH_REP)],
            'date_of_appointment':                                  [i.strftime('%Y/%m/%d') for i in randdates(NUM_OF_OFFICERS_AUTH_REP, reg_date, req_date)],
            'position_held':                                        [random.choice(OFFICERS_POS_HELD) for _ in range(NUM_OF_OFFICERS_AUTH_REP)],
            'entity_id':                                            ENTITY_ID,
        },
        'Shareholders':{
            'shareholder_name':                                     [f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)} {random.choice(companyType)}' for _ in range(NUM_OF_SHAREHOLDERS)],
            'shareholder_id':                                       [''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) for _ in range(NUM_OF_SHAREHOLDERS)],
            'nationality_or_citizenship':                           [random.choice(NATIONALITY) for i in range(NUM_OF_SHAREHOLDERS)],
            'shareholder_address':                                  [f'{random.choice(streetNameFirst)} {random.choice(streetNameLast)} #{random.randint(1, 30)}-{random.randint(1, 50)} {random.choice(NATIONALITY)} {random.randint(100000, 999999)}' for _ in range(NUM_OF_SHAREHOLDERS)],
            'date_of_change_of_address':                            [random.choice(['-', i.strftime('%Y/%m/%d')]) for i in randdates(NUM_OF_SHAREHOLDERS, reg_date, req_date)],
            'type_of_shares':                                       [random.choice(SHARE_TYPE) for _ in range(NUM_OF_SHAREHOLDERS)],
            'no_of_shares':                                         [random.randint(10000, 100000000) for _ in range(NUM_OF_SHAREHOLDERS)],
            'currency':                                             ['SINGAPORE, DOLLARS' for _ in range(NUM_OF_SHAREHOLDERS)],
            'entity_id':                                            ENTITY_ID,
        },
        'Compliance Record':{
            'date_of_last_agm':                                     randdate(reg_date, req_date).strftime('%Y/%m/%d'),
            'date_of_last_ar':                                      randdate(reg_date, req_date).strftime('%Y/%m/%d'),
            'date_of_ac_laid_at_last_agm':                          randdate(reg_date, req_date).strftime('%Y/%m/%d'),
            'entity_id':                                            ENTITY_ID,
        },
        'Financial Data':{
            'entity_id':                                            ENTITY_ID,
            'current_fye':                                          f'31/12/{req_date.year - 1}',
            'previous_fye':                                         f'31/12/{req_date.year - 2}',
            'currency':                                             'SINGAPORE, DOLLARS',
            'current_fye_revenue':                                  CURR_FYE_REV,
            'previous_fye_revenue':                                 PREV_FYE_REV,
            'percentage_change_revenue':                            round((CURR_FYE_REV - PREV_FYE_REV) / PREV_FYE_REV * 100, 2),
            'current_fye_profit_after_tax':                         PAT_CURR_FYE,
            'previous_fye_profit_after_tax':                        PAT_PREV_FYE,
            'percentage_change_profit_after_tax':                   round((PAT_CURR_FYE - PAT_PREV_FYE) / PAT_PREV_FYE * 100, 2),
            'current_fye_shareholders_fund':                        SHAREHOLDERSFUND_CURR_FYE,
            'previous_fye_shareholders_fund':                       SHAREHOLDERSFUND_PREV_FYE,
            'percentage_change_shareholders_fund':                  round((SHAREHOLDERSFUND_CURR_FYE - SHAREHOLDERSFUND_PREV_FYE) / SHAREHOLDERSFUND_PREV_FYE * 100, 2),
        },
        'Key Ratios':{
            'entity_id':                                            ENTITY_ID,
            'current_fye':                                          f'31/12/{req_date.year - 1}',
            'previous_fye':                                         f'31/12/{req_date.year - 2}',
            'current_fye_profit_margin':                            f'{round(random.uniform(2.0, 5.0), 2)}%',
            'previous_fye_profit_margin':                           f'{round(random.uniform(2.0, 5.0), 2)}%',
            'current_fye_liquidity_times':                          round(random.uniform(0.0, 3.0), 2),
            'previous_fye_liquidity_times':                         round(random.uniform(0.0, 3.0), 2),
            'current_fye_debt_times':                               round(random.uniform(0.0, 3.0), 2),
            'previous_fye_debt_times':                              round(random.uniform(0.0, 3.0), 2),
        },
        'Analysis':{
            'entity_id':                                            ENTITY_ID,
            'fye':                                                  f'{req_date.year - 1}', 
            'company_level_revenue_growth':                         f'{round(random.uniform(5.0, 60.0), 2)}%',
            'industry_median_revenue_growth':                       f'{round(random.uniform(5.0, 30.0), 2)}%',
            'company_level_return_on_assets':                       f'{round(random.uniform(2.0, 5.0), 2)}%',
            'industry_median_return_on_assets':                     f'{round(random.uniform(2.0, 5.0), 2)}%',
            'company_level_total_asset_turnover':                   f'{round(random.uniform(2.0, 30.0), 2)}%',
            'industry_median_total_asset_turnover':                 f'{round(random.uniform(2.0, 15.0), 2)}%',
            'company_level_net_profit_margin':                      f'{round(random.uniform(2.0, 5.0), 2)}%',
            'industry_median_net_profit_margin':                    f'{round(random.uniform(2.0, 5.0), 2)}%',
        },
        'Writ of Sum. Org. Claim':{
            'sn':                                                   [i + 1 for i in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'court_type':                                           [random.choice(WRIT_SUM_COURT_TYPE) for _ in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'case_no':                                              [random.randint(1, 10000) for _ in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'year':                                                 [min(randomDates[i], randomDates[-i - 1]).year for i in range(len(randdates(2 * WRIT_SUM_ORGS_CLAIM_COUNT, reg_date, req_date)) // 2)], 
            'date_of_filling':                                      [min(randomDates[i], randomDates[-i - 1]).strftime('%Y/%m/%d') for i in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'plaintiff':                                            [f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)} {random.choice(companyType)}' for _ in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'case_status':                                          [random.choice(CASE_STATUS) for _ in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'date_of_case_status':                                  [randdate(min(randomDates[i], randomDates[-i - 1]), max(randomDates[i], randomDates[-i - 1])).strftime('%Y/%m/%d') for i in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'case_status_remarks':                                  [random.choice(CASE_STATUS) for _ in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'plaintiff_status':                                     [random.choice(PARTY_STATUS) for _ in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'date_of_plaitiff_status':                              [randdate(min(randomDates[i], randomDates[-i - 1]), max(randomDates[i], randomDates[-i - 1])).strftime('%Y/%m/%d') for i in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'defendant_status':                                     [random.choice(PARTY_STATUS) for _ in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'date_of_defendant_status':                             [randdate(min(randomDates[i], randomDates[-i - 1]), max(randomDates[i], randomDates[-i - 1])).strftime('%Y/%m/%d') for i in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'amount':                                               [f'1) SGD {random.randint(100, 50000)}000' for _ in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'last_updated':                                         [randdate(randomDates[i], req_date).strftime('%Y/%m/%d') for i in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'main_cause':                                           [random.choice(MAIN_CAUSE) for i in range(WRIT_SUM_ORGS_CLAIM_COUNT)],
            'entity_id':                                            ENTITY_ID,
        },
        'Winding Up':{
            'type':                                                 ['WINDING UP' for _ in range(WINDING_UP_COUNT)],
            'case_no':                                              [random.randint(1, 10000) for _ in range(WINDING_UP_COUNT)], 
            'year':                                                 [min(randomDates[i], randomDates[-i - 1]).year for i in range(len(randdates(2 * WINDING_UP_COUNT, reg_date, req_date)) // 2)], 
            'date_of_filling':                                      [min(randomDates[i], randomDates[-i - 1]).strftime('%Y/%m/%d') for i in range(WINDING_UP_COUNT)],
            'other_party_name':                                     [f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)} {random.choice(companyType)}' for _ in range(WINDING_UP_COUNT)],
            'case_status':                                          [random.choice(CASE_STATUS) for _ in range(WINDING_UP_COUNT)],
            'date_of_case_status':                                  [randdate(min(randomDates[i], randomDates[-i - 1]), max(randomDates[i], randomDates[-i - 1])).strftime('%Y/%m/%d') for i in range(WINDING_UP_COUNT)],
            'other_party_status':                                   [random.choice(PARTY_STATUS) for _ in range(WINDING_UP_COUNT)],
            'date_of_other_party_status':                           [randdate(min(randomDates[i], randomDates[-i - 1]), max(randomDates[i], randomDates[-i - 1])).strftime('%Y/%m/%d') for i in range(WINDING_UP_COUNT)],
            'defendant_status':                                     [random.choice(PARTY_STATUS) for _ in range(WINDING_UP_COUNT)],
            'date_of_defendant_status':                             [randdate(min(randomDates[i], randomDates[-i - 1]), max(randomDates[i], randomDates[-i - 1])).strftime('%Y/%m/%d') for i in range(WINDING_UP_COUNT)],
            'amount':                                               [f'1) SGD {random.randint(100000, 50000000)}' for _ in range(WINDING_UP_COUNT)],
            'last_updated':                                         [max(randomDates[i], randomDates[-i - 1]).strftime('%Y/%m/%d') for i in range(WINDING_UP_COUNT)],
            'entity_id':                                            ENTITY_ID,
        },
        'OS OA OP OM':{
            'type':                                                 ['ORIGINATING SUMMONS' for _ in range(OSOAOPOM_COUNT)],
            'case_no':                                              [random.randint(1, 10000) for _ in range(OSOAOPOM_COUNT)],
            'year':                                                 [min(randomDates[i], randomDates[-i - 1]).year for i in range(len(randdates(2 * OSOAOPOM_COUNT, reg_date, req_date)) // 2)], 
            'date_of_filling':                                      [min(randomDates[i], randomDates[-i - 1]).strftime('%Y/%m/%d') for i in range(OSOAOPOM_COUNT)],
            'other_party_name':                                     [f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)} {random.choice(companyType)}' for _ in range(OSOAOPOM_COUNT)],
            'case_status':                                          [random.choice(CASE_STATUS) for _ in range(OSOAOPOM_COUNT)],
            'date_of_case_status':                                  [randdate(min(randomDates[i], randomDates[-i - 1]), max(randomDates[i], randomDates[-i - 1])).strftime('%Y/%m/%d') for i in range(OSOAOPOM_COUNT)],
            'other_party_status':                                   [random.choice(PARTY_STATUS) for _ in range(OSOAOPOM_COUNT)],
            'date_of_other_party_status':                           [randdate(min(randomDates[i], randomDates[-i - 1]), max(randomDates[i], randomDates[-i - 1])).strftime('%Y/%m/%d') for i in range(OSOAOPOM_COUNT)],
            'defendant_status':                                     [random.choice(PARTY_STATUS) for _ in range(OSOAOPOM_COUNT)],
            'date_of_defendant_status':                             [randdate(min(randomDates[i], randomDates[-i - 1]), max(randomDates[i], randomDates[-i - 1])).strftime('%Y/%m/%d') for i in range(OSOAOPOM_COUNT)],
            'amount':                                               [f'1) SGD {random.randint(100000, 50000000)}' for _ in range(OSOAOPOM_COUNT)],
            'last_updated':                                         [max(randomDates[i], randomDates[-i - 1]).strftime('%Y/%m/%d') for i in range(OSOAOPOM_COUNT)],
            'entity_id':                                            ENTITY_ID,
        },
        'Add Exp Prop. Info':{
            'entity_id':                                            ENTITY_ID,
            'num_of_employee':                                      random.randint(10000, 50000), 
            'num_of_commerical_properties_owned':                   random.choice(['-', random.randint(1, 100)]),
        },
        'Accreditations':{
            'entity_id':                                            ENTITY_ID,
            'award_name':                                           ['SINGAPORE 1000 COMPANIES RANKED BY SALES/TURNOVER' for _ in range(ACRRED_COUNT)], 
            'year_of_award':                                        [i.year for i in randdates(ACRRED_COUNT, reg_date, req_date)], 
            'award_ranking':                                        ['-' for _ in range(ACRRED_COUNT)],
        },
        'Financial Related Search Count':{
            'entity_id':                                            ENTITY_ID,
            'year':                                                 f'20XX',
            'month':                                                None,
            'purpose':                                              list(random.sample(FINANCIAL_REL_SEARCH_COUNT_VAL, random.randint(1, len(FINANCIAL_REL_SEARCH_COUNT_VAL)))),
            'count':                                                None,
        },
        'Commercial Related Search Count':{
            'entity_id':                                            ENTITY_ID,
            'year':                                                 f'20XX',
            'month':                                                None,
            'purpose':                                              list(random.sample(COMMERCIAL_REL_SEARCH_COUNT_VAL, random.randint(1, len(COMMERCIAL_REL_SEARCH_COUNT_VAL)))),
            'count':                                                None,
        },
        'Legal Related Search Count':{
            'entity_id':                                            ENTITY_ID,
            'year':                                                 f'20XX',
            'month':                                                None,
            'purpose':                                              list(random.sample(LEGAL_REL_SEARCH_COUNT_VAL, random.randint(1, len(LEGAL_REL_SEARCH_COUNT_VAL)))),
            'count':                                                None,
        },
    }

    # Table 1: Request Criteria
    eins_random_req_criteria = pd.DataFrame(
        data=[list(eins_random_params['Request Criteria'].values())],
        columns=eins_random_params['Request Criteria'].keys()
    )

    # Table 2: Search Record
    eins_random_search_rec = pd.DataFrame(
        data=[list(eins_random_params['Search Record'].values())],
        columns=eins_random_params['Search Record'].keys()
    )

    # Table 3: Details of Company
    eins_random_details_of_comp = pd.DataFrame(
        data=[list(eins_random_params['Details of Company'].values())], 
        columns=eins_random_params['Details of Company'].keys()
    )
    principal_activities = eins_random_details_of_comp.loc[0, 'principal_activities']
    ssic_number = re.findall(r'\((\d+)\)', principal_activities)[0]
    eins_random_details_of_comp = pd.concat([eins_random_details_of_comp, ssic_mapping(ssic_number, ssic_mapper)], axis=1)

    # Table 4: Capital Structure
    eins_random_cap_struct = pd.DataFrame(
        data=[list(eins_random_params['Capital Structure'].values())],
        columns=eins_random_params['Capital Structure'].keys()
    )

    # Table 5: Charges
    eins_random_charges = pd.DataFrame(
        data=eins_random_params['Charges'],
        columns=eins_random_params['Charges'].keys()
    )

    # Table 6: Auditors
    eins_random_auditors = pd.DataFrame(
        data=[list(eins_random_params['Auditors'].values())],
        columns=eins_random_params['Auditors'].keys()
    )

    # Table 7: Officers Auth. Rep
    eins_random_off_Auth_Rep = pd.DataFrame(
        data=eins_random_params['Officers Auth. Rep'],
        columns=eins_random_params['Officers Auth. Rep'].keys()
    )

    # Table 8: Shareholders
    eins_random_shareholders = pd.DataFrame(
        data=eins_random_params['Shareholders'],
        columns=eins_random_params['Shareholders'].keys()
    )

    # Table 9: Compliance Record
    eins_random_compliance_rec = pd.DataFrame(
        data=[list(eins_random_params['Compliance Record'].values())],
        columns=eins_random_params['Compliance Record'].keys()
    )

    # Table 10: Financial Data
    eins_random_fin_Data = pd.DataFrame(
        data=[list(eins_random_params['Financial Data'].values())],
        columns=eins_random_params['Financial Data'].keys()
    )

    # Table 11 Key Ratios;
    eins_random_key_Ratio = pd.DataFrame(
        data=[list(eins_random_params['Key Ratios'].values())],
        columns=eins_random_params['Key Ratios'].keys()
    )

    # table 12: Analysis
    eins_random_analysis = pd.DataFrame(
        data=[list(eins_random_params['Analysis'].values())],
        columns=eins_random_params['Analysis'].keys()
    )

    # Table 13: Writ of Sum Org Claim
    eins_random_writ_SOC = pd.DataFrame(
        data=eins_random_params['Writ of Sum. Org. Claim'],
        columns=eins_random_params['Writ of Sum. Org. Claim'].keys()
    )
    eins_random_writ_SOC['main_cause_category'] = eins_random_writ_SOC['main_cause'].apply(lambda x: label_litigation_main_cause(litigation_main_cause_clustering_model, x))
    eins_random_writ_SOC['case_status_category'] = eins_random_writ_SOC['case_status'].apply(lambda x: label_litigation_case_status(litigation_case_status_clustering_model, x))
    eins_random_writ_SOC['plaintiff_status_category'] = eins_random_writ_SOC['plaintiff_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))
    eins_random_writ_SOC['defendant_status_category'] = eins_random_writ_SOC['defendant_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))

    # Table 14; Winding Up
    eins_random_winding_Up = pd.DataFrame(
        data=eins_random_params['Winding Up'],
        columns=eins_random_params['Winding Up'].keys()
    )
    eins_random_winding_Up['case_status_category'] = eins_random_winding_Up['case_status'].apply(lambda x: label_litigation_case_status(litigation_case_status_clustering_model, x))
    eins_random_winding_Up['other_party_status_category'] = eins_random_winding_Up['other_party_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))
    eins_random_winding_Up['defendant_status_category'] = eins_random_winding_Up['defendant_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))

    # Table 15; OS OA OP OM
    eins_random_osoaopom = pd.DataFrame(
        data=eins_random_params['OS OA OP OM'],
        columns=eins_random_params['OS OA OP OM'].keys()
    )
    eins_random_osoaopom['case_status_category'] = eins_random_osoaopom['case_status'].apply(lambda x: label_litigation_case_status(litigation_case_status_clustering_model, x))
    eins_random_osoaopom['other_party_status_category'] = eins_random_osoaopom['other_party_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))
    eins_random_osoaopom['defendant_status_category'] = eins_random_osoaopom['defendant_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))

    # Table 16: Asd Exp Prop Info
    eins_random_add_Exp_Prop_Info = pd.DataFrame(
        data=[list(eins_random_params['Add Exp Prop. Info'].values())],
        columns=eins_random_params['Add Exp Prop. Info'].keys()
    )

    # Table 17: Accreditations
    eins_random_accreditation = pd.DataFrame(
        data=eins_random_params['Accreditations'],
        columns=eins_random_params['Accreditations'].keys()
    )

    # Table 18: Financial Related Search Count
    eins_random_fin_search_count = random_Related_Search_Count_Generation(
        eins_random_params['Financial Related Search Count']['purpose'],
        eins_random_params['Financial Related Search Count']['entity_id'], 
        req_date.year-1
    )

    # Table 19: Commercial Related Search Count
    eins_random_comm_rel_search_count = random_Related_Search_Count_Generation(
        eins_random_params['Commercial Related Search Count']['purpose'],
        eins_random_params['Commercial Related Search Count']['entity_id'], 
        req_date.year-1
    )

    # Table 20: Legal Related Search Count
    eins_random_legal_rel_search_count = random_Related_Search_Count_Generation(
        eins_random_params['Legal Related Search Count']['purpose'],
        eins_random_params['Legal Related Search Count']['entity_id'], 
        req_date.year-1
    )

 
    # Output Data
    writer = pd.ExcelWriter(f'Outputs/EINS_Random_Output/Generated EINS Report - {ENTITY_ID}.xlsx', engine='xlsxwriter')

    eins_random_req_criteria.to_excel(writer, sheet_name='Request Criteria', index=False)
    eins_random_search_rec.to_excel(writer, sheet_name='Search Record', index=False)
    eins_random_details_of_comp.to_excel(writer, sheet_name='Details of Company', index=False)
    eins_random_cap_struct.to_excel(writer, sheet_name='Capital Structure', index=False)
    eins_random_charges.to_excel(writer, sheet_name='Charges', index=False)
    eins_random_auditors.to_excel(writer, sheet_name='Auditors', index=False)
    eins_random_off_Auth_Rep.to_excel(writer, sheet_name='Officers Auth. Rep', index=False)
    eins_random_shareholders.to_excel(writer, sheet_name='Shareholders', index=False)
    eins_random_compliance_rec.to_excel(writer, sheet_name='Compliance Record', index=False)
    eins_random_fin_Data.to_excel(writer, sheet_name='Financial Data', index=False)
    eins_random_key_Ratio.to_excel(writer, sheet_name='Key Ratios', index=False)
    eins_random_analysis.to_excel(writer, sheet_name='Analysis', index=False)
    eins_random_writ_SOC.to_excel(writer, sheet_name='Writ of Sum. Org. Claim', index=False)
    eins_random_winding_Up.to_excel(writer, sheet_name='Winding Up', index=False)
    eins_random_osoaopom.to_excel(writer, sheet_name='OS OA OP OM', index=False)
    eins_random_add_Exp_Prop_Info.to_excel(writer, sheet_name='Add Exp Prop. Info', index=False)
    eins_random_accreditation.to_excel(writer, sheet_name='Accreditations', index=False)
    eins_random_fin_search_count.to_excel(
        writer, sheet_name='Financial Related Search Count', index=False)
    eins_random_comm_rel_search_count.to_excel(
        writer, sheet_name='Commercial Related Search Count', index=False)
    eins_random_legal_rel_search_count.to_excel(
        writer, sheet_name='Legal Related Search Count', index=False)

    writer.close()


    # ---------------------------------------- IBS REPORT ---------------------------------------- #

    for x in range(len(eins_random_params['Officers Auth. Rep']['employee_name'])):
                   
        INDIVIDUAL_NAME = eins_random_params['Officers Auth. Rep']['employee_name'][x]
        INDIVIDUAL_ID = eins_random_params['Officers Auth. Rep']['employee_id'][x]
        INDIVIDUAL_POSITION = eins_random_params['Officers Auth. Rep']['position_held'][x]
        INDIVIDUAL_APPOINTMENT_DATE = eins_random_params['Officers Auth. Rep']['date_of_appointment'][x]
        
        # Multiple Occurence fields (variable according to each report)
        NUM_OF_CURR_BUSINESS_COUNT = random.randint(1, 5)
        NUM_OF_PREV_BUSINESSES_COUNT = random.randint(1, 5)
        ACRRED_COUNT = random.randint(1, 5)
        BANKRUPTCY_COUNT = random.randint(1, 5)
        INDV_LIT_SEARCH_COUNT = random.randint(1, 5)
        BUSINESS_LIT_SEARCH_COUNT = random.randint(1, 5) 

        # Predefined Fields
        CURRBUSINESSES = [eins_random_params['Request Criteria']['requested_entity_name'],] + [f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)} {random.choice(companyType)}' for i in range(NUM_OF_CURR_BUSINESS_COUNT-1)]
        PREVBUSINESSES = [f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)} {random.choice(companyType)}' for i in range(NUM_OF_PREV_BUSINESSES_COUNT)]

        ibs_random_params = {
            "Request Criteria": {
                'request_date':                             req_date.strftime('%Y/%m/%d'),
                'requestor_name':                           "SUBSCRIBER",
                'requested_individual_name':                INDIVIDUAL_NAME,
                'requested_id_no':                          INDIVIDUAL_ID,
                'request_id':                               "IBS SAMPLE",
            },
            "Search Record": {
                'individual_name':                          ' \n'.join([f'{index + 1}) {" ".join(fullName)}' for index, fullName in enumerate(itertools.permutations(INDIVIDUAL_NAME, 2) )]),
                'individual_id':                            INDIVIDUAL_ID,
                'available_address':                        f'{random.choice(streetNameFirst)} {random.choice(streetNameLast)} #{random.randint(1, 30)}-{random.randint(1, 50)} SINGAPORE {random.randint(100000, 999999)}',
            },
            "Current Business": {
                'entity_id':                                INDIVIDUAL_ID,
                'business_name':                            CURRBUSINESSES,
                'registration_no':                          [eins_random_params['Request Criteria']['requested_entity_id'],] + [random.choice([
                                                                f'{"".join(random.choices(string.digits, k=8))}{random.choice(string.ascii_uppercase)}', 
                                                                f'{reg_date.year}{"".join(random.choices(string.digits, k=5))}{random.choice(string.ascii_uppercase)}', 
                                                                f'T{reg_date.year % 100:02}{random.choice(ENTITY_TYPE_INDICATOR)}{"".join(random.choices(string.digits, k=4))}{random.choice(string.ascii_uppercase)}', 
                                                            ]) for i in range(NUM_OF_CURR_BUSINESS_COUNT-1)],
                'status':                                   [eins_random_params['Details of Company']['status'],] + [random.choice(COY_STATUS) for i in range(NUM_OF_CURR_BUSINESS_COUNT-1)],
                'position':                                 [INDIVIDUAL_POSITION,] + [' \n'.join(random.sample(OFFICERS_POS_HELD, random.randint(1, len(OFFICERS_POS_HELD)))) for i in range(NUM_OF_CURR_BUSINESS_COUNT-1)],
                'appointment_date':                         [INDIVIDUAL_APPOINTMENT_DATE,] + [i.strftime('%Y/%m/%d') for i in randdates(NUM_OF_CURR_BUSINESS_COUNT-1, reg_date, req_date)],
                'current_directors_todate_count':           [random.randint(0, 3) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
                'current_secretaries_todate_count':         [random.randint(0, 3) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
                'current_alternate_directors_todate_count': [random.randint(0, 3) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
                'active_charges_todate_count':              [random.randint(0, 3) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
                'current_shareholders_todate_count':        [random.randint(0, 3) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
                'subsidiary_todate_count':                  [random.randint(0, 3) for i in range(NUM_OF_CURR_BUSINESS_COUNT)],
            },                        
            "Previous Business": {
                'entity_id':                                INDIVIDUAL_ID,
                'business_name':                            PREVBUSINESSES,
                'registration_no':                          [random.choice([
                                                                f'{"".join(random.choices(string.digits, k=8))}{random.choice(string.ascii_uppercase)}', 
                                                                f'{reg_date.year}{"".join(random.choices(string.digits, k=5))}{random.choice(string.ascii_uppercase)}', 
                                                                f'T{reg_date.year % 100}{random.choice(ENTITY_TYPE_INDICATOR)}{"".join(random.choices(string.digits, k=4))}{random.choice(string.ascii_uppercase)}', 
                                                            ]) for i in range(NUM_OF_PREV_BUSINESSES_COUNT)],
                'status':                                   [random.choice(COY_STATUS) for i in range(NUM_OF_PREV_BUSINESSES_COUNT)],
                'position':                                 [random.choice(OFFICERS_POS_HELD) for i in range(NUM_OF_PREV_BUSINESSES_COUNT)],
                'cessation_date':                           [randdate(datetime.datetime(1900, 1, 1), reg_date).strftime('%Y/%m/%d') for i in range(NUM_OF_PREV_BUSINESSES_COUNT)],
            },
            "Current Business Lit Trace": {
                'entity_id':                                INDIVIDUAL_ID,
                'business_name':                            list(itertools.chain(*[[biz] * 5 for biz in CURRBUSINESSES])),
                'year':                                     list(itertools.chain(*[[f'{req_date.year - 1}'] * 5 for _ in CURRBUSINESSES])),
                'enquiries':                                list(itertools.chain(*[['Litigation Trace: District Court \n($60,000 - $250,000)', 'Litigation Trace: High Court \n(> $250,000)', 'Litigation Trace: Magistrate Court \n(< $60,000)', 'OS/OA/OP/OM Trace', 'Winding Up Trace'] for biz in CURRBUSINESSES])),
                'current_year_after_9_Jan':                 [random.randint(0, 1) for _ in range(NUM_OF_CURR_BUSINESS_COUNT * 5)],
                'previous_year_before_9_Jan':               [random.randint(0, 1) for _ in range(NUM_OF_CURR_BUSINESS_COUNT * 5)],
            },
            "Business Lit Search": {
                'entity_id':                                INDIVIDUAL_ID,
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
                'individual_id':                            INDIVIDUAL_ID,
            },
            "Bankruptcy Records": {
                'entity_id':                                INDIVIDUAL_ID,
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
                'entity_id':                                INDIVIDUAL_ID,
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
                'entity_id':                                INDIVIDUAL_ID,
                'business':                                 [f'{random.choice(firstName)} {random.choice(middleName)} {random.choice(sector)}' for i in range(ACRRED_COUNT)],
                'award_name':                               [f'{random.choice(accreditationAwards)}' for i in range(ACRRED_COUNT)],
                'award_ranking':                            [f'{random.randint(2000, 2020)} Ranked {random.randint(1, 1000)}' for i in range(ACRRED_COUNT)],
            },
            "Financial Related Search Count": { 
                'entity_id':                                INDIVIDUAL_ID,
                'year':                                     f'20XX',
                'month':                                    None,
                'purpose':                                  list(random.sample(FINANCIAL_REL_SEARCH_COUNT_VAL, random.randint(1, len(FINANCIAL_REL_SEARCH_COUNT_VAL)))),
                'count':                                    None,
            },
            "Commercial Related Search Count": {
                'entity_id':                                INDIVIDUAL_ID,
                'year':                                     f'20XX',
                'month':                                    None,
                'purpose':                                  list(random.sample(COMMERCIAL_REL_SEARCH_COUNT_VAL, random.randint(1, len(COMMERCIAL_REL_SEARCH_COUNT_VAL)))),
                'count':                                    None,
            },
            "Legal Related Search Count": {
                'entity_id':                                INDIVIDUAL_ID,
                'year':                                     f'20XX',
                'month':                                    None,
                'purpose':                                  list(random.sample(LEGAL_REL_SEARCH_COUNT_VAL, random.randint(1, len(LEGAL_REL_SEARCH_COUNT_VAL)))),
                'count':                                    None,
            },
        }

        # Table 1: Request Criteria
        ibs_random_req_criteria = pd.DataFrame(
            data=[list(ibs_random_params['Request Criteria'].values())], 
            columns=ibs_random_params['Request Criteria'].keys()
        )

        # Table 2: Search Record
        ibs_random_search_rec = pd.DataFrame(
            data=[list(ibs_random_params['Search Record'].values())], 
            columns=ibs_random_params['Search Record'].keys()
        )

        # Table 3: Table 3: Current Business
        ibs_random_current_business = pd.DataFrame(
            data=ibs_random_params['Current Business'], 
            columns=ibs_random_params['Current Business'].keys()
        )

        # Table 4: Previous Busines
        ibs_random_previous_business = pd.DataFrame(
            data=ibs_random_params['Previous Business'], 
            columns=ibs_random_params['Previous Business'].keys()
        )

        # Table 5: Current Business Lit Trace
        ibs_random_curr_business_lit_trace = pd.DataFrame(
            data=ibs_random_params['Current Business Lit Trace'], 
            columns=ibs_random_params['Current Business Lit Trace'].keys()
        )

        # Table 6: Business Lit Search
        ibs_random_business_lit_search = pd.DataFrame(
            data=ibs_random_params['Business Lit Search'], 
            columns=ibs_random_params['Business Lit Search'].keys()
        )
        ibs_random_business_lit_search['main_cause_category'] = ibs_random_business_lit_search['main_cause'].apply(lambda x: label_litigation_main_cause(litigation_main_cause_clustering_model, x))
        ibs_random_business_lit_search['case_status_category'] = ibs_random_business_lit_search['case_status'].apply(lambda x: label_litigation_case_status(litigation_case_status_clustering_model, x))
        ibs_random_business_lit_search['plaintiff_status_category'] = ibs_random_business_lit_search['plaintiff_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))
        ibs_random_business_lit_search['defendant_status_category'] = ibs_random_business_lit_search['defendant_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))

        # Table 7: Bankruptcy Records
        ibs_random_bankruptcy_rec = pd.DataFrame(
            data=ibs_random_params['Bankruptcy Records'], 
            columns=ibs_random_params['Bankruptcy Records'].keys()
        )
        ibs_random_bankruptcy_rec['case_status_category'] = ibs_random_bankruptcy_rec['case_status'].apply(lambda x: label_litigation_case_status(litigation_case_status_clustering_model, x))
        ibs_random_bankruptcy_rec['plaintiff_status_category'] = ibs_random_bankruptcy_rec['plaintiff_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))
        ibs_random_bankruptcy_rec['defendant_status_category'] = ibs_random_bankruptcy_rec['defendant_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))

        # Table 8: Individual Lit Search
        ibs_random_indv_lit_search = pd.DataFrame(
            data=ibs_random_params['Individual Lit Search'], 
            columns=ibs_random_params['Individual Lit Search'].keys(),
        )
        ibs_random_indv_lit_search['main_cause_category'] = ibs_random_indv_lit_search['main_cause'].apply(lambda x: label_litigation_main_cause(litigation_main_cause_clustering_model, x))
        ibs_random_indv_lit_search['case_status_category'] = ibs_random_indv_lit_search['case_status'].apply(lambda x: label_litigation_case_status(litigation_case_status_clustering_model, x))
        ibs_random_indv_lit_search['plaintiff_status_category'] = ibs_random_indv_lit_search['plaintiff_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))
        ibs_random_indv_lit_search['defendant_status_category'] = ibs_random_indv_lit_search['defendant_status'].apply(lambda x: label_litigation_party_status(litigation_party_status_clustering_model, x))

        # Table 9: Accreditation
        ibs_random_accreditation = pd.DataFrame(
            data=ibs_random_params['Accreditation'], 
            columns=ibs_random_params['Accreditation'].keys()
        )

        # Table 10: Financial Related Search Count  
        ibs_random_fin_rel_search_count = random_Related_Search_Count_Generation(
            ibs_random_params['Financial Related Search Count']['purpose'],
            ibs_random_params['Financial Related Search Count']['entity_id'],
            req_date.year-1
        )

        # Table 11: Commercial Related Search Count
        ibs_random_comm_rel_search_count = random_Related_Search_Count_Generation(
            ibs_random_params['Commercial Related Search Count']['purpose'],
            ibs_random_params['Commercial Related Search Count']['entity_id'],
            req_date.year-1
        )

        # Table 12: Legal Related Search Count 
        ibs_random_leg_rel_search_count = random_Related_Search_Count_Generation(
            ibs_random_params['Legal Related Search Count']['purpose'],
            ibs_random_params['Legal Related Search Count']['entity_id'],
            req_date.year-1
        )

        # Output Data
        writer = pd.ExcelWriter(f'Outputs/IBS_Random_Output/Generated IBS Report - {INDIVIDUAL_ID}.xlsx', 
                                engine='xlsxwriter')   

        ibs_random_req_criteria.to_excel(writer, sheet_name='Request Criteria', index=False)
        ibs_random_search_rec.to_excel(writer, sheet_name='Search Record', index=False)
        ibs_random_current_business.to_excel(writer, sheet_name='Current Business', index=False)
        ibs_random_previous_business.to_excel(writer, sheet_name='Previous Business', index=False)
        ibs_random_curr_business_lit_trace.to_excel(writer, sheet_name='Current Business Lit Trace', index=False)
        ibs_random_business_lit_search.to_excel(writer, sheet_name='Business Lit Search', index=False)
        ibs_random_bankruptcy_rec.to_excel(writer, sheet_name='Bankruptcy Record', index=False)
        ibs_random_indv_lit_search.to_excel(writer, sheet_name='Individual Lit Search', index=False)
        ibs_random_accreditation.to_excel(writer, sheet_name='Accreditation', index=False)
        ibs_random_fin_rel_search_count.to_excel(writer, sheet_name='Financial Related Search Count', index=False)
        ibs_random_comm_rel_search_count.to_excel(writer, sheet_name='Commercial Related Search Count', index=False)
        ibs_random_leg_rel_search_count.to_excel(writer, sheet_name='Legal Related Search Count', index=False)

        writer.close()

if __name__ == "__main__":
    numberOfRandomData = 250
    for i in tqdm(range(numberOfRandomData)):
        main()
    print(f'====> {numberOfRandomData} random generation(s) executed successfully!')

