import pandas as pd
import datetime
import numpy as np
import json
import itertools

#convert prices to integers
def price_to_float(price_series):
    for i in range(len(price_series)):
        price_series[i] = int(price_series[i][7:])
    return price_series


def main(combinedEINSFilePath, featureCalculationsFilePath, searchYear):
    # Read in feature calculations json file
    with open(featureCalculationsFilePath) as f:
        featureCalculationData = json.load(f)

    # Read the compiled reports and create each sheet as a dataframe
    req_criteria_df = pd.read_excel(combinedEINSFilePath, sheet_name='Request Criteria')
    search_rec_df = pd.read_excel(combinedEINSFilePath, sheet_name='Search Record')
    details_of_company_df = pd.read_excel(combinedEINSFilePath, sheet_name='Details of Company')
    capital_structure_df = pd.read_excel(combinedEINSFilePath, sheet_name='Capital Structure')
    charges_df = pd.read_excel(combinedEINSFilePath, sheet_name='Charges')
    auditors_df = pd.read_excel(combinedEINSFilePath, sheet_name='Auditors')
    officers_auth_rep_df = pd.read_excel(combinedEINSFilePath, sheet_name='Officers Auth. Rep')
    shareholders_df = pd.read_excel(combinedEINSFilePath, sheet_name='Shareholders')
    compliance_record_df = pd.read_excel(combinedEINSFilePath, sheet_name='Compliance Record')
    financial_data_df = pd.read_excel(combinedEINSFilePath, sheet_name='Financial Data')
    key_ratios_df = pd.read_excel(combinedEINSFilePath, sheet_name='Key Ratios')
    analysis_df = pd.read_excel(combinedEINSFilePath, sheet_name='Analysis')
    wos_oc_df = pd.read_excel(combinedEINSFilePath, sheet_name='Writ of Sum. Org. Claim')
    winding_up_df = pd.read_excel(combinedEINSFilePath, sheet_name='Winding Up')
    os_oa_op_om_df = pd.read_excel(combinedEINSFilePath, sheet_name='OS OA OP OM')
    add_exp_prop_info_df = pd.read_excel(combinedEINSFilePath,  sheet_name='Add Exp Prop. Info')
    accreditations_df = pd.read_excel(combinedEINSFilePath, sheet_name='Accreditations')
    fin_rel_search_count_df = pd.read_excel(combinedEINSFilePath, sheet_name='Financial Related Search Count')
    comm_rel_search_count_df = pd.read_excel(combinedEINSFilePath, sheet_name='Commercial Related Search Count')
    leg_rel_search_count_df = pd.read_excel(combinedEINSFilePath, sheet_name='Legal Related Search Count')

    # Convert price to float values
    wos_oc_df['amount'] = price_to_float(wos_oc_df['amount'])
    winding_up_df['amount'] = price_to_float(winding_up_df['amount'])
    os_oa_op_om_df['amount'] = price_to_float(os_oa_op_om_df['amount'])

    # Convert dates to datetime.date objects
    details_of_company_df["registration_date"] = pd.to_datetime(details_of_company_df["registration_date"]).dt.date
    details_of_company_df['date_of_name_change'] = pd.to_datetime(details_of_company_df['date_of_name_change']).dt.date
    officers_auth_rep_df['date_of_appointment'] = pd.to_datetime(officers_auth_rep_df['date_of_appointment']).dt.date
    charges_df['date_of_charge'] = pd.to_datetime(charges_df['date_of_charge']).dt.date
    wos_oc_df['date_of_filling'] = pd.to_datetime(wos_oc_df['date_of_filling']).dt.date
    winding_up_df['date_of_filling'] = pd.to_datetime(winding_up_df['date_of_filling']).dt.date
    os_oa_op_om_df['date_of_filling'] = pd.to_datetime(os_oa_op_om_df['date_of_filling']).dt.date

    # Calculate days since today
    wos_oc_df["months_since_filling"] = list(map(lambda x: (datetime.date.today().year - x.year)*12 + datetime.date.today().month - x.month, wos_oc_df["date_of_filling"]))
    winding_up_df["months_since_filling"] = list(map(lambda x: (datetime.date.today().year - x.year)*12 + datetime.date.today().month - x.month, winding_up_df["date_of_filling"]))
    os_oa_op_om_df["months_since_filling"] = list(map(lambda x: (datetime.date.today().year - x.year)*12 + datetime.date.today().month - x.month, os_oa_op_om_df["date_of_filling"]))

    # Initialise results dictionary
    results = {
        "entityNo":                                         [],
        "companyCreditHistoryDuration":                     [],
        "countryOrRegionOfIncorporationOrRegistration":     [],
        "daysSinceChangeOfNameOfCompany":                   [],
        "companyPrincipalActivitySubClass":                 [],
        "companyPrincipalActivityClass":                    [],
        "companyPrincipalActivityGroup":                    [],
        "companyPrincipalActivityDivision":                 [],
        "companyPrincipalActivitySection":                  [],
        "priceOfCompanyIssuedOrdinary":                     [],
        "totalShares":                                      [],
        "numSharesOwnedByShareholders":                     [],
        "numShareholders":                                  [],
        "numShareholdersWithMoreThan20PercentShares":       [],
        "amountOfRevenue":                                  [],
        "increasedRevenueFromPreviousYear":                 [],
        "amountOfProfitAfterTax":                           [],
        "increasedProfitFromPreviousYear":                  [],
        "amountOfShareholdersFund":                         [],
        "increasedShareholdersFundFromPreviousYear":        [],
        "companyProfitMargin":                              [],
        "increasedProfitMarginFromPreviousYear":            [],
        "companyLiquidity":                                 [],
        "increasedLiquidityFromPreviousYear":               [],
        "companyDebtRatio":                                 [],
        "increasedDebtRatioFromPreviousYear":               [],
        "companyReturnOnAssets":                            [],
        "companyReturnOnAssetsAgainstIndustryMedian":       [],
        "companyTotalAssetTurnover":                        [],
        "companyTotalAssetTurnoverAgainstIndustryMedian":   [],
        "companyNetProfitMarginAgainstIndustryMedian":      [],
        "companyRevenueGrowth":                             [],
        "companyRevenueGrowthAgainstIndustryMedian":        [],
        "numExistingLoans":                                 [],
        "lengthOfBankingRelationship":                      [],
        "auditor":                                          [],
        "officerNationality":                               [],
        "officerAppointmentDuration":                       [],
        "totalPendingWOSAmount":                            [],
        "totalConcludedWOSAmount":                          [],
        "totalPendingOCAmount":                             [],
        "totalConcludedOCAmount":                           [],
        "totalWOSAmount":                                   [],
        "totalOCAmount":                                    [],
        "totalWOSAndOCAmount":                              [],
        "totalWOSAmountAgainstRevenue":                     [],
        "totalOCAmountAgainstRevenue":                      [],
        "totalWOSAndOCAgainstRevenue":                      [],
        "totalConcludedWindingUpAmount":                    [],
        "totalPendingWindingUpAmount":                      [],
        "totalWindingUpAmount":                             [],
        "windingUpTotalAmountAgainstRevenue":               [],
        "totalPendingOSAmount":                             [],
        "totalConcludedOSAmount":                           [],
        "totalOSAmount":                                    [],
        "totalOSAmountAgainstRevenue":                      [],
        "totalPendingOAAmount":                             [],
        "totalConcludedOAAmount":                           [],
        "totalOAAmount":                                    [],
        "totalOAAmountAgainstRevenue":                      [],
        "totalPendingOPAmount":                             [],
        "totalConcludedOPAmount":                           [],
        "totalOPAmount":                                    [],
        "totalOPAmountAgainstRevenue":                      [],
        "totalPendingOMAmount":                             [],
        "totalConcludedOMAmount":                           [],
        "totalOMAmount":                                    [],
        "totalOMAmountAgainstRevenue":                      [],
        "totalPendingOSOAOPOMAmount":                       [],
        "totalConcludedOSOAOPOMAmount":                     [],
        "totalOSOAOPOMAmount":                              [],
        "totalOSOAOPOMAmountAgainstRevenue":                [],
        "recentYearFinancialSearchCount":                   [],
        "recentYearTradeInsuranceSearchCount":              [],
        "recentYearFinancialInstitutionSearchCount":        [],
        "recentYearHirePurchaseLeasingSearchCount":         [],
        "recentYearCommercialSearchCount":                  [],
        "recentYearCommercialRetailSearchCount":            [],
        "recentYearServicesSearchCount":                    [],
        "recentYearLegalSearchCount":                       [],
        "recentYearLitigationSearchCount":                  [],
        "recentYearConveyancingSearchCount":                [],
        "commercialPropertiesOwned":                        [],
        "employeeCount":                                    [],
        "revenuePerEmployee":                               [],
        "profitPerEmployee":                                []}
    

    COURTTYPE = featureCalculationData['WRIT_SUM_COURT_TYPE']
    TIMESPAN = featureCalculationData['TIMESPAN']
    STATUS = featureCalculationData['STATUS']
    CAUSE = featureCalculationData["CAUSE"]
    ORIGINATING_TYPE = ["ORIGINATING SUMMONS", "ORIGINATING APPLICATIONS", "ORIGINATING PETITIONS", "ORIGINATING MOTIONS"]


    for combinations in list(itertools.product(COURTTYPE, TIMESPAN, STATUS, CAUSE)):
        court_type, num_months, status, cause = combinations[0], combinations[1], combinations[2], combinations[3]
        results['totalAmountOf_{}_{}_WithinLast{}Months_DueTo{}'.format(status, court_type, num_months, cause)] = []
        results['numberOf_{}_{}_WithinLast{}Months_DueTo{}'.format(status, court_type, num_months, cause)] = []

    for combinations in list(itertools.product(TIMESPAN, STATUS)):
        num_months, status = combinations[0], combinations[1]
        results['totalAmountOf_{}_WindingUp_WithinLast{}Months'.format(status,num_months)] = []
        results['numberOf_{}_WindingUp_WithinLast{}Months'.format(status,num_months)] = []

    for combinations in list(itertools.product(ORIGINATING_TYPE, TIMESPAN, STATUS)):
        orig_type, num_months, status = combinations[0], combinations[1], combinations[2]
        results['totalAmountOf_{}_{}_WithinLast{}Months'.format(status,orig_type,num_months)] = []
        results['numberOf_{}_{}_WithinLast{}Months'.format(status,orig_type,num_months)] = []


    # Calculate features for each business
    for entity_no in req_criteria_df["requested_entity_id"]:

        print("Calculating EINS features for", entity_no)
        results["entityNo"].append(entity_no)


        # Obtain credit history duration, country, and days since change of name
        companyCreditHistoryDuration = ( datetime.date.today() - (details_of_company_df.loc[details_of_company_df["entity_id"]==entity_no, "registration_date"].values[0])).days
        countryOrRegionOfIncorporationOrRegistration = details_of_company_df[(details_of_company_df["entity_id"]==entity_no)]["country_or_region_of_incorporation_or_registration"].values[0]
        daysSinceChangeOfNameOfCompany = (datetime.date.today() - (details_of_company_df[(details_of_company_df['entity_id']==entity_no)]['date_of_name_change'].values[0])).days

        results["companyCreditHistoryDuration"].append(companyCreditHistoryDuration)
        results["countryOrRegionOfIncorporationOrRegistration"].append(countryOrRegionOfIncorporationOrRegistration)
        results["daysSinceChangeOfNameOfCompany"].append(daysSinceChangeOfNameOfCompany)


        # Retrieve principal activity of business
        ssic_mapper = pd.read_csv("../Dataset/ssic_data/ssic_mapping.csv", dtype=str)
        companyPrincipalActivitySubClassCode = details_of_company_df[(details_of_company_df["entity_id"]==entity_no)]["principal_activities"].values[0][-6:-1]
        ssic_lookup = ssic_mapper[ssic_mapper[ssic_mapper.columns[5]]==companyPrincipalActivitySubClassCode]

        if len(ssic_lookup) != 0:
            results["companyPrincipalActivitySubClass"].append(ssic_lookup["Sub-Class"].iloc[0])
            results["companyPrincipalActivityClass"].append(ssic_lookup["Class"].iloc[0])
            results["companyPrincipalActivityGroup"].append(ssic_lookup["Group"].iloc[0])
            results["companyPrincipalActivityDivision"].append(ssic_lookup["Division"].iloc[0])
            results["companyPrincipalActivitySection"].append(ssic_lookup["Section"].iloc[0])
        else:
            results["companyPrincipalActivitySubClass"].append(None)
            results["companyPrincipalActivityClass"].append(None)
            results["companyPrincipalActivityGroup"].append(None)
            results["companyPrincipalActivityDivision"].append(None)
            results["companyPrincipalActivitySection"].append(None)


        # Calculate price of shares and total shares
        priceOfCompanyIssuedOrdinary = capital_structure_df[(capital_structure_df["entity_id"]==entity_no)]["amount_of_issued_ordinary"].values[0] / capital_structure_df[(capital_structure_df["entity_id"]==entity_no)]["issued_ordinary_no_of_shares"].values[0]
        totalShares = capital_structure_df[(capital_structure_df['entity_id']==entity_no)]['issued_ordinary_no_of_shares'].values[0]

        results["priceOfCompanyIssuedOrdinary"].append(priceOfCompanyIssuedOrdinary)
        results["totalShares"].append(totalShares)


        # Calculate number of shares owned by shareholders, number of shareholders, and number of shareholders holding > 20% shares
        numSharesOwnedByShareholders = shareholders_df[(shareholders_df["entity_id"]==entity_no)]["no_of_shares"].sum()
        numShareholders = shareholders_df[(shareholders_df["entity_id"]==entity_no)]["shareholder_name"].count()
        numShareholdersWithMoreThan20PercentShares = len(shareholders_df[(shareholders_df["entity_id"]==entity_no) & (shareholders_df["no_of_shares"] >= 0.2*totalShares)])

        results["numSharesOwnedByShareholders"].append(numSharesOwnedByShareholders)
        results["numShareholders"].append(numShareholders)
        results["numShareholdersWithMoreThan20PercentShares"].append(numShareholdersWithMoreThan20PercentShares)


        # Calculate revenue, profit, shareholders fund, and their respective increment from the previous year
        amountOfRevenue = financial_data_df[financial_data_df["entity_id"]==entity_no]["current_fye_revenue"].values[0]
        increasedRevenueFromPreviousYear = amountOfRevenue - financial_data_df[financial_data_df["entity_id"]==entity_no]["previous_fye_revenue"].values[0]
        amountOfProfitAfterTax = financial_data_df[financial_data_df["entity_id"]==entity_no]["current_fye_profit_after_tax"].values[0]
        increasedProfitFromPreviousYear = amountOfProfitAfterTax -financial_data_df[financial_data_df["entity_id"]==entity_no]["previous_fye_profit_after_tax"].values[0]
        amountOfShareholdersFund = financial_data_df[financial_data_df["entity_id"]==entity_no]["current_fye_shareholders_fund"].values[0]
        increasedShareholdersFundFromPreviousYear = amountOfShareholdersFund - financial_data_df[financial_data_df["entity_id"]==entity_no]["previous_fye_shareholders_fund"].values[0]

        results["amountOfRevenue"].append(amountOfRevenue)
        results["increasedRevenueFromPreviousYear"].append(increasedRevenueFromPreviousYear)
        results["amountOfProfitAfterTax"].append(amountOfProfitAfterTax)
        results["increasedProfitFromPreviousYear"].append(increasedProfitFromPreviousYear)
        results["amountOfShareholdersFund"].append(amountOfShareholdersFund)
        results["increasedShareholdersFundFromPreviousYear"].append(increasedShareholdersFundFromPreviousYear)


        # Calculate profit margin, liquidity and debt ratio, and their respective increment from the previous year
        companyProfitMargin = float(key_ratios_df[key_ratios_df["entity_id"]==entity_no]["current_fye_profit_margin"].values[0].strip('%'))/100
        increasedProfitMarginFromPreviousYear = companyProfitMargin - float(key_ratios_df[key_ratios_df["entity_id"]==entity_no]["previous_fye_profit_margin"].values[0].strip('%'))/100

        companyLiquidity = key_ratios_df[key_ratios_df["entity_id"]==entity_no]["current_fye_liquidity_times"].values[0]
        increasedLiquidityFromPreviousYear = companyLiquidity - key_ratios_df[key_ratios_df["entity_id"]==entity_no]["previous_fye_liquidity_times"].values[0]

        companyDebtRatio = key_ratios_df[key_ratios_df["entity_id"]==entity_no]["current_fye_debt_times"].values[0]
        increasedDebtRatioFromPreviousYear = companyDebtRatio - key_ratios_df[key_ratios_df["entity_id"]==entity_no]["previous_fye_debt_times"].values[0]

        results["companyProfitMargin"].append(companyProfitMargin)
        results["increasedProfitMarginFromPreviousYear"].append(increasedProfitMarginFromPreviousYear)

        results["companyLiquidity"].append(companyLiquidity)
        results["increasedLiquidityFromPreviousYear"].append(increasedLiquidityFromPreviousYear)

        results["companyDebtRatio"].append(companyDebtRatio)
        results["increasedDebtRatioFromPreviousYear"].append(increasedDebtRatioFromPreviousYear)


        # Calculate return on assets, totl asset turnover, net profit margin and revenue growth, and their respective comparisons against the industry median
        companyReturnOnAssets = float(analysis_df[(analysis_df["entity_id"]==entity_no)]["company_level_return_on_assets"].values[0].strip('%'))/100
        companyReturnOnAssetsAgainstIndustryMedian = companyReturnOnAssets - float(analysis_df[(analysis_df["entity_id"]==entity_no)]["industry_median_return_on_assets"].values[0].strip('%'))/100

        companyTotalAssetTurnover = float(analysis_df[(analysis_df["entity_id"]==entity_no)]["company_level_total_asset_turnover"].values[0].strip('%'))/100
        companyTotalAssetTurnoverAgainstIndustryMedian = companyTotalAssetTurnover - float(analysis_df[(analysis_df["entity_id"]==entity_no)]["industry_median_total_asset_turnover"].str.strip('%'))

        companyNetProfitMarginAgainstIndustryMedian = companyProfitMargin - float(analysis_df[analysis_df["entity_id"]==entity_no]["industry_median_net_profit_margin"].values[0].strip('%'))/100

        companyRevenueGrowth = float(analysis_df[(analysis_df["entity_id"]==entity_no)]["company_level_revenue_growth"].values[0].strip('%'))/100
        companyRevenueGrowthAgainstIndustryMedian = companyRevenueGrowth - float(analysis_df[(analysis_df["entity_id"]==entity_no)]["industry_median_revenue_growth"].values[0].strip('%'))/100

        results["companyReturnOnAssets"].append(companyReturnOnAssets)
        results["companyReturnOnAssetsAgainstIndustryMedian"].append(companyReturnOnAssetsAgainstIndustryMedian)

        results["companyTotalAssetTurnover"].append(companyTotalAssetTurnover)
        results["companyTotalAssetTurnoverAgainstIndustryMedian"].append(companyTotalAssetTurnoverAgainstIndustryMedian)

        results["companyNetProfitMarginAgainstIndustryMedian"].append(companyNetProfitMarginAgainstIndustryMedian)

        results["companyRevenueGrowth"].append(companyRevenueGrowth)
        results["companyRevenueGrowthAgainstIndustryMedian"].append(companyRevenueGrowthAgainstIndustryMedian)


        # Calculate number of existing loans and length of banking relationship
        numExistingLoans = len(charges_df[(charges_df["entity_id"]==entity_no) &(charges_df["status"]!="COMPLETE")])
        lengthOfBankingRelationship = (datetime.date.today() - charges_df.loc[charges_df['entity_id']==entity_no, 'date_of_charge'].values[0]).days

        results["numExistingLoans"].append(numExistingLoans)
        results["lengthOfBankingRelationship"].append(lengthOfBankingRelationship)


        # Obtain the auditor
        auditor = auditors_df[(auditors_df["entity_id"]==entity_no)]["auditor_name"].values[0]
        results["auditor"].append(auditor)


        # Obtain the officer's nationality and current duration of appointment
        officerNationality = officers_auth_rep_df[(officers_auth_rep_df["entity_id"]==entity_no)]["nationality_or_citizenship"].values[0]
        officerAppointmentDuration = (datetime.date.today() - officers_auth_rep_df[officers_auth_rep_df['entity_id']==entity_no]['date_of_appointment'].values[0]).days

        results["officerNationality"].append(officerNationality)
        results["officerAppointmentDuration"].append(officerAppointmentDuration)


        # Calculate pending, concluded and total WOS and OC, as well as the totals against revenues

        totalPendingWOSAmount = wos_oc_df[
            (wos_oc_df["entity_id"]==entity_no) &
            ("WOS" in wos_oc_df["court_type"]) &
            (wos_oc_df["case_status"]=="PENDING")
            ]["amount"].sum()

        totalConcludedWOSAmount = wos_oc_df[
            (wos_oc_df["entity_id"]==entity_no) & 
            ("WOS" in wos_oc_df["court_type"]) &
            ("CONCLUDED" in wos_oc_df["case_status"])
            ]["amount"].sum()

        totalPendingOCAmount = wos_oc_df[
            (wos_oc_df["entity_id"]==entity_no) &
            ("OC" in wos_oc_df["court_type"]) &
            (wos_oc_df["case_status"]=="PENDING")
            ]["amount"].sum()

        totalConcludedOCAmount = wos_oc_df[
            (wos_oc_df["entity_id"]==entity_no) &
            ("OC" in wos_oc_df["court_type"]) &
            ("CONCLUDED" in wos_oc_df["case_status"])
            ]["amount"].sum()

        totalWOSAmount = wos_oc_df[
            (wos_oc_df["entity_id"]==entity_no) &
            ("WOS" in wos_oc_df["court_type"])
            ]["amount"].sum()

        totalOCAmount = wos_oc_df[
            (wos_oc_df["entity_id"]==entity_no) &
            ("WOS" in wos_oc_df["court_type"])
            ]["amount"].sum()

        totalWOSAndOCAmount = float(totalWOSAmount) + float(totalOCAmount)
        totalWOSAmountAgainstRevenue = float(totalWOSAmount) / float(amountOfRevenue)
        totalOCAmountAgainstRevenue = float(totalOCAmount) / float(amountOfRevenue)
        totalWOSAndOCAgainstRevenue = float(totalWOSAndOCAmount) / float(amountOfRevenue)


        results["totalPendingWOSAmount"].append(totalPendingWOSAmount)
        results["totalConcludedWOSAmount"].append(totalConcludedWOSAmount)

        results["totalPendingOCAmount"].append(totalPendingOCAmount)
        results["totalConcludedOCAmount"].append(totalConcludedOCAmount)

        results["totalWOSAmount"].append(totalWOSAmount)
        results["totalOCAmount"].append(totalOCAmount)
        results["totalWOSAndOCAmount"].append(totalWOSAndOCAmount)

        results["totalWOSAmountAgainstRevenue"].append(totalWOSAmountAgainstRevenue)
        results["totalOCAmountAgainstRevenue"].append(totalOCAmountAgainstRevenue)
        results["totalWOSAndOCAgainstRevenue"].append(totalWOSAndOCAgainstRevenue)


        # Calculate business litigation counts and amounts across court types, number of months, status, and cause

        for combinations in list(itertools.product(COURTTYPE, TIMESPAN, STATUS, CAUSE)):
            court_type, num_months, status, cause = combinations[0], combinations[1], combinations[2], combinations[3]
            results['totalAmountOf_{}_{}_WithinLast{}Months_DueTo{}'.format(status, court_type, num_months, cause)].append(
                wos_oc_df[
                    (wos_oc_df['entity_id'] == entity_no) &
                    (wos_oc_df["court_type"] == court_type) &
                    (wos_oc_df['months_since_filling']) &
                    (status in wos_oc_df["case_status_category"]) &
                    (cause in wos_oc_df["main_cause_category"]) 
                ]["amount"].sum()
            )
            results['numberOf_{}_{}_WithinLast{}Months_DueTo{}'.format(status, court_type, num_months, cause)].append(
                wos_oc_df[
                    (wos_oc_df['entity_id'] == entity_no) &
                    (wos_oc_df["court_type"] == court_type) &
                    (wos_oc_df['months_since_filling']) &
                    (status in wos_oc_df["case_status_category"]) &
                    (cause in wos_oc_df["main_cause_category"]) 
                ]["amount"].count()
            )


        # Calculate pending, concluded and total winding up, as well as the totals against revenues

        totalConcludedWindingUpAmount = winding_up_df[
            (winding_up_df["entity_id"]==entity_no) &
            (winding_up_df["type"]=="WINDING UP") &
            ("CONCLUDED" in winding_up_df["case_status"]) ]["amount"].sum()

        totalPendingWindingUpAmount = winding_up_df[
            (winding_up_df["entity_id"]==entity_no) &
            (winding_up_df["type"]=="WINDING UP") &
            ("PENDING" in winding_up_df["case_status"]) ]["amount"].sum()

        totalWindingUpAmount = winding_up_df[
            (winding_up_df["entity_id"]==entity_no) &
            (winding_up_df["type"]=="WINDING UP") ]["amount"].sum()

        windingUpTotalAmountAgainstRevenue = float(totalWindingUpAmount)/float(amountOfRevenue)

        results["totalConcludedWindingUpAmount"].append(totalConcludedWindingUpAmount)
        results["totalPendingWindingUpAmount"].append(totalPendingWindingUpAmount)
        results["totalWindingUpAmount"].append(totalWindingUpAmount)
        results["windingUpTotalAmountAgainstRevenue"].append(windingUpTotalAmountAgainstRevenue)


        # Calculate winding up counts and amounts across number of months, and status

        for combinations in list(itertools.product(TIMESPAN, STATUS)):
            num_months, status = combinations[0], combinations[1]
            results['totalAmountOf_{}_WindingUp_WithinLast{}Months'.format(status,num_months)].append(
                winding_up_df[
                    (winding_up_df['entity_id'] == entity_no) &
                    (winding_up_df['months_since_filling'] < num_months) &
                    (status in winding_up_df["case_status_category"])
                ]["amount"].sum()
            )
            results['numberOf_{}_WindingUp_WithinLast{}Months'.format(status,num_months)].append(
                winding_up_df[
                    (winding_up_df['entity_id'] == entity_no) &
                    (winding_up_df['months_since_filling'] < num_months) &
                    (status in winding_up_df["case_status_category"])
                ]["amount"].count()
            )


        # Calculate pending, concluded and total OS, OA, OP, and OM, as well as the totals against revenues

        totalPendingOSAmount = os_oa_op_om_df[
            (os_oa_op_om_df["entity_id"]==entity_no) &
            (os_oa_op_om_df["type"]=="ORIGINATING SUMMONS") &
            ("PENDING" in os_oa_op_om_df["case_status"])]["amount"].sum()

        totalConcludedOSAmount = os_oa_op_om_df[
            (os_oa_op_om_df["entity_id"]==entity_no) &
            (os_oa_op_om_df["type"]=="ORIGINATING SUMMONS") &
            ("CONCLUDED" in os_oa_op_om_df["case_status"])]["amount"].sum()

        totalOSAmount = os_oa_op_om_df[
            (os_oa_op_om_df["entity_id"]==entity_no) &
            (os_oa_op_om_df["type"]=="ORIGINATING SUMMONS")]["amount"].sum()

        totalOSAmountAgainstRevenue = float(totalOSAmount)/float(amountOfRevenue)


        totalPendingOAAmount = os_oa_op_om_df[
            (os_oa_op_om_df["entity_id"]==entity_no) &
            (os_oa_op_om_df["type"]=="ORIGINATING APPLICATIONS") &
            ("PENDING" in os_oa_op_om_df["case_status"])]["amount"].sum()

        totalConcludedOAAmount = os_oa_op_om_df[
            (os_oa_op_om_df["entity_id"]==entity_no) &
            (os_oa_op_om_df["type"]=="ORIGINATING APPLICATIONS") &
            ("CONCLUDED" in os_oa_op_om_df["case_status"])]["amount"].sum()

        totalOAAmount = os_oa_op_om_df[
            (os_oa_op_om_df["entity_id"]==entity_no) &
            (os_oa_op_om_df["type"]=="ORIGINATING APPLICATIONS")]["amount"].sum()

        totalOAAmountAgainstRevenue = float(totalOAAmount)/float(amountOfRevenue)


        totalPendingOPAmount = os_oa_op_om_df[
            (os_oa_op_om_df["entity_id"]==entity_no) &
            (os_oa_op_om_df["type"]=="ORIGINATING PETITIONS") &
            ("PENDING" in os_oa_op_om_df["case_status"])]["amount"].sum()

        totalConcludedOPAmount = os_oa_op_om_df[
            (os_oa_op_om_df["entity_id"]==entity_no) &
            (os_oa_op_om_df["type"]=="ORIGINATING PETITIONS") &
            ("CONCLUDED" in os_oa_op_om_df["case_status"])]["amount"].sum()

        totalOPAmount = os_oa_op_om_df[
            (os_oa_op_om_df["entity_id"]==entity_no) &
            (os_oa_op_om_df["type"]=="ORIGINATING PETITIONS")]["amount"].sum()

        totalOPAmountAgainstRevenue = float(totalOPAmount)/float(amountOfRevenue)


        totalPendingOMAmount = os_oa_op_om_df[
            (os_oa_op_om_df["entity_id"]==entity_no) &
            (os_oa_op_om_df["type"]=="ORIGINATING MOTIONS") &
            ("PENDING" in os_oa_op_om_df["case_status"])]["amount"].sum()

        totalConcludedOMAmount = os_oa_op_om_df[
            (os_oa_op_om_df["entity_id"]==entity_no) &
            (os_oa_op_om_df["type"]=="ORIGINATING MOTIONS") &
            ("CONCLUDED" in os_oa_op_om_df["case_status"])]["amount"].sum()

        totalOMAmount = os_oa_op_om_df[
            (os_oa_op_om_df["entity_id"]==entity_no) &
            (os_oa_op_om_df["type"]=="ORIGINATING MOTIONS")]["amount"].sum()

        totalOMAmountAgainstRevenue = float(totalOMAmount)/float(amountOfRevenue)


        totalPendingOSOAOPOMAmount = totalPendingOSAmount + totalPendingOAAmount + totalPendingOPAmount + totalPendingOMAmount

        totalConcludedOSOAOPOMAmount = totalConcludedOSAmount + totalConcludedOAAmount + totalConcludedOPAmount + totalConcludedOMAmount

        totalOSOAOPOMAmount = os_oa_op_om_df[
            (os_oa_op_om_df["entity_id"]==entity_no)]["amount"].sum()

        totalOSOAOPOMAmountAgainstRevenue = float(totalOSOAOPOMAmount)/ float(amountOfRevenue)


        results["totalPendingOSAmount"].append(totalPendingOSAmount)
        results["totalConcludedOSAmount"].append(totalConcludedOSAmount)
        results["totalOSAmount"].append(totalOSAmount)
        results["totalOSAmountAgainstRevenue"].append(totalOSAmountAgainstRevenue)

        results["totalPendingOAAmount"].append(totalPendingOAAmount)
        results["totalConcludedOAAmount"].append(totalConcludedOAAmount)
        results["totalOAAmount"].append(totalOAAmount)
        results["totalOAAmountAgainstRevenue"].append(totalOAAmountAgainstRevenue)

        results["totalPendingOPAmount"].append(totalPendingOPAmount)
        results["totalConcludedOPAmount"].append(totalConcludedOPAmount)
        results["totalOPAmount"].append(totalOPAmount)
        results["totalOPAmountAgainstRevenue"].append(totalOPAmountAgainstRevenue)

        results["totalPendingOMAmount"].append(totalPendingOMAmount)
        results["totalConcludedOMAmount"].append(totalConcludedOMAmount)
        results["totalOMAmount"].append(totalOMAmount)
        results["totalOMAmountAgainstRevenue"].append(totalOMAmountAgainstRevenue)

        results["totalPendingOSOAOPOMAmount"].append(totalPendingOSOAOPOMAmount)
        results["totalConcludedOSOAOPOMAmount"].append(totalConcludedOSOAOPOMAmount)
        results["totalOSOAOPOMAmount"].append(totalOSOAOPOMAmount)
        results["totalOSOAOPOMAmountAgainstRevenue"].append(totalOSOAOPOMAmountAgainstRevenue)


        # Calculate OS, OA, OP and OM counts and amounts across each type, number of months, and status

        for combinations in list(itertools.product(ORIGINATING_TYPE, TIMESPAN, STATUS)):
            orig_type, num_months, status = combinations[0], combinations[1], combinations[2]
            results['totalAmountOf_{}_{}_WithinLast{}Months'.format(status,orig_type,num_months)].append(
                    os_oa_op_om_df[
                        (os_oa_op_om_df['entity_id'] == entity_no) &
                        (os_oa_op_om_df["type"] == orig_type) &
                        (os_oa_op_om_df['months_since_filling'] < num_months) &
                        (status in os_oa_op_om_df["case_status_category"])
                    ]["amount"].sum()
            )
            results['numberOf_{}_{}_WithinLast{}Months'.format(status,orig_type,num_months)].append(
                    os_oa_op_om_df[
                        (os_oa_op_om_df['entity_id'] == entity_no) &
                        (os_oa_op_om_df["type"] == orig_type) &
                        (os_oa_op_om_df['months_since_filling'] < num_months) &
                        (status in os_oa_op_om_df["case_status_category"])
                    ]["amount"].count()
            )


        # Calculate recent year financial, commercial and legal search counts

        recentYearFinancialSearchCount = fin_rel_search_count_df[
            (fin_rel_search_count_df["entity_id"]==entity_no) &
            (fin_rel_search_count_df["year"]== searchYear-1)]["count"].sum()

        recentYearTradeInsuranceSearchCount = fin_rel_search_count_df[
            (fin_rel_search_count_df["entity_id"]==entity_no) &
            (fin_rel_search_count_df["year"]== searchYear-1) &
            (fin_rel_search_count_df["purpose"] == "Trade Insurance")]["count"].sum()

        recentYearFinancialInstitutionSearchCount = fin_rel_search_count_df[
            (fin_rel_search_count_df["entity_id"]==entity_no) &
            (fin_rel_search_count_df["year"]== searchYear-1) &
            (fin_rel_search_count_df["purpose"] == "Financial Institution")]["count"].sum()

        recentYearHirePurchaseLeasingSearchCount = fin_rel_search_count_df[
            (fin_rel_search_count_df["entity_id"]==entity_no) &
            (fin_rel_search_count_df["year"]== searchYear-1) &
            (fin_rel_search_count_df["purpose"] == "Hire Purchase / Leasing")]["count"].sum()

        recentYearCommercialSearchCount = comm_rel_search_count_df[
            (comm_rel_search_count_df["entity_id"]==entity_no) &
            (comm_rel_search_count_df["year"]== searchYear-1)]["count"].sum()

        recentYearCommercialRetailSearchCount = comm_rel_search_count_df[
            (comm_rel_search_count_df["entity_id"]==entity_no) &
            (comm_rel_search_count_df["year"]== searchYear-1) &
            (comm_rel_search_count_df["purpose"]=="Commercial-Retail")]["count"].sum()

        recentYearServicesSearchCount = comm_rel_search_count_df[
            (comm_rel_search_count_df["entity_id"]==entity_no) &
            (comm_rel_search_count_df["year"]== searchYear-1) &
            (comm_rel_search_count_df["purpose"]=="Service")]["count"].sum()

        recentYearLegalSearchCount = leg_rel_search_count_df[
            (leg_rel_search_count_df["entity_id"]==entity_no) &
            (leg_rel_search_count_df["year"]== searchYear-1)]["count"].sum()

        recentYearLitigationSearchCount = leg_rel_search_count_df[
            (leg_rel_search_count_df["entity_id"]==entity_no) &
            (leg_rel_search_count_df["year"]== searchYear-1) & 
            (leg_rel_search_count_df["purpose"] == "LITIGATION")]["count"].sum()

        recentYearConveyancingSearchCount = leg_rel_search_count_df[
            (leg_rel_search_count_df["entity_id"]==entity_no) &
            (leg_rel_search_count_df["year"]== searchYear-1) & 
            (leg_rel_search_count_df["purpose"] == "Conveyancing")]["count"].sum()

        results["recentYearFinancialSearchCount"].append(recentYearFinancialSearchCount)
        results["recentYearTradeInsuranceSearchCount"].append(recentYearTradeInsuranceSearchCount)
        results["recentYearFinancialInstitutionSearchCount"].append(recentYearFinancialInstitutionSearchCount)
        results["recentYearHirePurchaseLeasingSearchCount"].append(recentYearHirePurchaseLeasingSearchCount)

        results["recentYearCommercialSearchCount"].append(recentYearCommercialSearchCount)
        results["recentYearCommercialRetailSearchCount"].append(recentYearCommercialRetailSearchCount)
        results["recentYearServicesSearchCount"].append(recentYearServicesSearchCount)

        results["recentYearLegalSearchCount"].append(recentYearLegalSearchCount)
        results["recentYearLitigationSearchCount"].append(recentYearLitigationSearchCount)
        results["recentYearConveyancingSearchCount"].append(recentYearConveyancingSearchCount)


        # Obtain the number of commercial properties owned and employee count

        commercialPropertiesOwned = add_exp_prop_info_df[(add_exp_prop_info_df["entity_id"]==entity_no)]["num_of_commerical_properties_owned"].values[0]
        employeeCount = add_exp_prop_info_df[(add_exp_prop_info_df["entity_id"]==entity_no)]["num_of_employee"].values[0]

        results["commercialPropertiesOwned"].append(commercialPropertiesOwned)
        results["employeeCount"].append(employeeCount)


        # Calculate the revenue per employee and profit per employee

        revenuePerEmployee = float(amountOfRevenue) / float(employeeCount)
        profitPerEmployee = float(amountOfProfitAfterTax) / float(employeeCount)

        results["revenuePerEmployee"].append(revenuePerEmployee)
        results["profitPerEmployee"].append(profitPerEmployee)


    # Export results
    result_df = pd.DataFrame(results)
    result_df.to_csv("calculated_features/eins features.csv", index=False)


if __name__ == "__main__":
    featureCalculationsFilePath = "feature_calculations.json"
    file_name = "../Random_Generation/Outputs/compiled_EINS_reports.xlsx"
    main(file_name, featureCalculationsFilePath, 2023)
    print(f'====> EINS Feature Calculation Process Completed!')

