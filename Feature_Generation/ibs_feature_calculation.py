# Import libraries
import pandas as pd
import datetime
import re
import json
import itertools

# Function to retrieve the business entity type from the UEN of the business
def entityTypeMapping(uen, mappingDF):
    """
    Maps a 9-character or 10-character UEN number to an entity-type 
    in accordance to https://www.uen.gov.sg/ueninternet/faces/pages/admin/aboutUEN.jspx
    """
    if len(uen) == 9: 
        # business registered with ACRA
        return "ACRA-registered Business"
    elif len(uen) == 10 and uen[3].isnumeric(): 
        # local company registered with ACRA
        return "ACRA-registered Local Company"
    elif len(uen) == 10 and not (uen[3].isnumeric()):
        # all other entities
        return mappingDF[mappingDF["Entity-Type Indicator"]==uen[3:5]]["Entity-Type"].iloc[0]
    else:
        return "Invalid UEN"
        

def main(compiledReportsFilePath, mappingfilePath, featureCalculationsFilePath, searchYear):
    # Read mapping file
    mappingDF = pd.read_csv(mappingfilePath)

    # Read in feature calculations json file
    with open(featureCalculationsFilePath) as f:
        featureCalculationData = json.load(f)

    # Read the compiled reports and create each sheet as a dataframe
    req_criteria_df = pd.read_excel(compiledReportsFilePath, sheet_name='Request Criteria')
    search_rec_df = pd.read_excel(compiledReportsFilePath, sheet_name='Search Record')
    current_business_df = pd.read_excel(compiledReportsFilePath,  sheet_name='Current Business')
    previous_business_df = pd.read_excel(compiledReportsFilePath, sheet_name='Previous Business')
    curr_business_lit_trace_df = pd.read_excel(compiledReportsFilePath, sheet_name='Current Business Lit Trace')
    business_lit_search_df = pd.read_excel(compiledReportsFilePath, sheet_name='Business Lit Search')
    bankruptcy_rec_df = pd.read_excel(compiledReportsFilePath, sheet_name='Bankruptcy Record')
    indv_lit_search_df = pd.read_excel(compiledReportsFilePath, sheet_name='Individual Lit Search')
    accreditation_df = pd.read_excel(compiledReportsFilePath, sheet_name='Accreditation')
    fin_rel_search_count_df = pd.read_excel(compiledReportsFilePath, sheet_name='Financial Related Search Count')
    comm_rel_search_count_df = pd.read_excel(compiledReportsFilePath, sheet_name='Commercial Related Search Count')
    leg_rel_search_count_df = pd.read_excel(compiledReportsFilePath, sheet_name='Legal Related Search Count')

    # Pre-processing of Business Litigation Search dataframe
    business_lit_search_df['amount'] = list(map(lambda x: re.findall(r'\d+', x), business_lit_search_df['amount']))
    business_lit_search_df['amount'] = list(map(lambda x: sum(list(map(lambda y: float(y), x))), business_lit_search_df['amount']))
    business_lit_search_df["filing_date"] = pd.to_datetime(business_lit_search_df["filing_date"])
    business_lit_search_df["months_since_filing"] = list(map(lambda x: (datetime.date.today().year - x.year)*12 + datetime.date.today().month - x.month, business_lit_search_df["filing_date"]))
    business_lit_search_df["entity_type"] = list(map(lambda x: 'Company' if 'LIMITED' in x else 'Individual', business_lit_search_df['plaintiff']))

    # Pre-processing of Bankruptcy Records dataframe
    bankruptcy_rec_df['amount'] = list(map(lambda x: re.findall(r'\d+', x), bankruptcy_rec_df['amount']))
    bankruptcy_rec_df['amount'] = list(map(lambda x: sum(list(map(lambda y: float(y), x))), bankruptcy_rec_df['amount']))
    bankruptcy_rec_df["filing_date"] = pd.to_datetime(bankruptcy_rec_df["filing_date"])
    bankruptcy_rec_df["months_since_filing"] = list(map(lambda x: (datetime.date.today().year - x.year)*12 + datetime.date.today().month - x.month, bankruptcy_rec_df["filing_date"]))
    bankruptcy_rec_df["entity_type"] = list(map(lambda x: 'Company' if 'LIMITED' in x else 'Individual', bankruptcy_rec_df['plaintiff'])) 
    
    # Pre-processing of Individual Litigation Search dataframe
    indv_lit_search_df['amount'] = list(map(lambda x: re.findall(r'\d+', x), indv_lit_search_df['amount']))
    indv_lit_search_df['amount'] = list(map(lambda x: sum(list(map(lambda y: float(y), x))), indv_lit_search_df['amount']))
    indv_lit_search_df["filing_date"] = pd.to_datetime(indv_lit_search_df["filing_date"])
    indv_lit_search_df["months_since_filing"] = list(map(lambda x: (datetime.date.today().year - x.year)*12 + datetime.date.today().month - x.month, indv_lit_search_df["filing_date"]))
    indv_lit_search_df["entity_type"] = list(map(lambda x: 'Company' if 'LIMITED' in x else 'Individual', indv_lit_search_df['plaintiff']))

    # Initialise results dictionary
    results = {
        "entityNo":                                                         [],
        "ownerID":                                                          [],
        "numCurrentLiveBusinesses":                                         [],
        "numCurrentLiquidatedBusinesses":                                   [],
        "numCurrentDissolvedBusinesses":                                    [],
        "numDirectors":                                                     [],
        "numAlternateDirectors":                                            [],
        "numShareholders":                                                  [],
        "numSecretaries":                                                   [],
        "numActiveCharges":                                                 [],
        "numSubsidiary":                                                    [],
        "numKeyPositions":                                                  [],
        "numDirectorsAgainstNumOtherBusinessDirectors":                     [],
        "numAlternateDirectorsAgainstNumOtherBusinessAlternateDirectors":   [],
        "numShareholdersAgainstNumOtherBusinessShareholders":               [],
        "numSecretariesAgainstNumOtherBusinessSecretaries":                 [],
        "numActiveChargesAgainstNumOtherBusinessActiveCharges":             [],
        "numSubsidiaryAgainstNumOtherBusinessSubsidiary":                   [],
        "numKeyPositionsAgainstNumOtherBusinessKeyPositions":               [],
        "isLongestAppointment":                                             [],
        "isMostRecentAppointment":                                          [],
        "entityType":                                                       [],
        "numPreviousTerminatedBusinesses":                                  [],
        "numPreviousCancelledBusinesses":                                   [],
        "numMCLitigation":                                                  [],
        "numDCLitigation":                                                  [],
        "numHCLitigation":                                                  [],
        "numWindingUpLitigation":                                           [],
        "numOSOAOPOMLitigation":                                            [],
        "numLitigationTraceBusinesses":                                     [],
        "avgNumMCLitigation":                                               [],
        "avgNumDCLitigation":                                               [],
        "avgNumHCLitigation":                                               [],
        "avgNumWindingUpLitigation":                                        [],
        "avgNumOSOAOPOMLitigation":                                         [],
        "recentYearIndividualFinancialSearchCount":                         [],
        "recentYearIndividualTradeInsuranceSearchCount":                    [],
        "recentYearIndividualFinancialInstitutionSearchCount":              [],
        "recentYearIndividualFinancialInstitutionSearchCount":              [],
        "recentYearIndividualHirePurchaseSearchCount":                      [],
        "recentYearIndividualCommercialSearchCount":                        [],
        "recentYearIndividualCommercialRetailSearchCount":                  [],
        "recentYearIndividualServicesSearchCount":                          [],
        "recentYearIndividualLegalSearchCount":                             [],
        "recentYearIndividualLitigationSearchCount":                        [],
        "recentYearIndividualConveyancingSearchCount":                      [],
    }

    COURTTYPE = featureCalculationData['WRIT_SUM_COURT_TYPE']
    TIMESPAN = featureCalculationData['TIMESPAN']
    ENTITYTYPE = featureCalculationData['ENTITY_TYPE']
    STATUS = featureCalculationData['STATUS']
    CAUSE = featureCalculationData['CAUSE']

    # Add on to results dictionary
    for combination in list(itertools.product(STATUS, COURTTYPE, TIMESPAN, ENTITYTYPE, CAUSE)):
        status, court_type, num_months, entity_type, cause = combination[0], combination[1], combination[2], combination[3], combination[4]
        results["totalamountOfBusinessLitigation_"+status+"_"+court_type+"_Within"+str(num_months)+"Months_"+entity_type+"plantiff_DueTo"+cause] = []
        results["numberOfBusinessLitigation_"+status+"_"+court_type+"_Within"+str(num_months)+"Months_"+entity_type+"plantiff_DueTo"+cause] = []
        results["totalamountOfIndividualLitigation_"+status+"_"+court_type+"_Within"+str(num_months)+"Months_"+entity_type+"plantiff_DueTo"+cause] = []
        results["numberOfIndividualLitigation_"+status+"_"+court_type+"_Within"+str(num_months)+"Months_"+entity_type+"plantiff_DueTo"+cause] = []  

    for combination in list(itertools.product(STATUS, TIMESPAN, ENTITYTYPE)):
        status, num_months, entity_type = combination[0], combination[1], combination[2]
        results["totalamountOfBankruptcyRecord_"+status+"_Within"+str(num_months)+"Months_"+entity_type+"plantiff"] = []
        results["numberOfBankruptcyRecord_"+status+"_Within"+str(num_months)+"Months_"+entity_type+"plantiff"] = []


    # Calculate features for each business owner
    for owner_id in current_business_df["entity_id"].unique():
        for entity_no in current_business_df[current_business_df["entity_id"]==owner_id]["registration_no"]:

            print("Calculating IBS features for", entity_no)
            results["entityNo"].append(entity_no)
            results["ownerID"].append(owner_id)


            # Replace N/A status with ""
            current_business_df["status"].fillna("", inplace=True)


            # Calculate number of current live, liquidated and dissolved businesses
            numCurrentLiveBusinesses = len(
                current_business_df[
                    (current_business_df["status"].str.contains("LIVE")) & (current_business_df["entity_id"]==owner_id)
                ]["status"]
            )

            numCurrentLiquidatedBusinesses = len(
                current_business_df[
                    (current_business_df["status"].str.contains("LIQUIDAT")) & (current_business_df["entity_id"]==owner_id)
                ]["status"]
            )

            numCurrentDissolvedBusinesses = len(
                current_business_df[
                    (current_business_df["status"].str.contains("DISSOLV")) & (current_business_df["entity_id"]==owner_id)
                ]["status"]
            )

            results["numCurrentLiveBusinesses"].append(numCurrentLiveBusinesses)
            results["numCurrentLiquidatedBusinesses"].append(numCurrentLiquidatedBusinesses)
            results["numCurrentDissolvedBusinesses"].append(numCurrentDissolvedBusinesses)


            # Calculate number of key positions, active charges and subsidiaries in the business
            numDirectors = current_business_df[current_business_df["registration_no"]==entity_no]["current_directors_todate_count"].values[0]
            numAlternateDirectors = current_business_df[current_business_df["registration_no"]==entity_no]["current_alternate_directors_todate_count"].values[0]
            numShareholders = current_business_df[current_business_df["registration_no"]==entity_no]["current_shareholders_todate_count"].values[0]
            numSecretaries = current_business_df[current_business_df["registration_no"]==entity_no]["current_secretaries_todate_count"].values[0]
            numActiveCharges = current_business_df[current_business_df["registration_no"]==entity_no]["active_charges_todate_count"].values[0]
            numSubsidiary = current_business_df[current_business_df["registration_no"]==entity_no]["subsidiary_todate_count"].values[0]
            numKeyPositions = numDirectors + numAlternateDirectors + numShareholders + numSecretaries

            results["numDirectors"].append(numDirectors)
            results["numAlternateDirectors"].append(numAlternateDirectors)
            results["numShareholders"].append(numShareholders)
            results["numSecretaries"].append(numSecretaries)
            results["numActiveCharges"].append(numActiveCharges)
            results["numSubsidiary"].append(numSubsidiary)
            results["numKeyPositions"].append(numKeyPositions)


            # Calculate number of current key positions, active charges and subsidiaries in the business compared to other businesses owned by the same owner 
            numDirectorsAgainstNumOtherBusinessDirectors = numDirectors - current_business_df[(current_business_df["registration_no"]!=entity_no) & (current_business_df["entity_id"]==owner_id)]["current_directors_todate_count"].sum()
            numAlternateDirectorsAgainstNumOtherBusinessAlternateDirectors = numAlternateDirectors - current_business_df[(current_business_df["registration_no"]!=entity_no) & (current_business_df["entity_id"]==owner_id)]["current_alternate_directors_todate_count"].sum()
            numShareholdersAgainstNumOtherBusinessShareholders = numShareholders - current_business_df[(current_business_df["registration_no"]!=entity_no) & (current_business_df["entity_id"]==owner_id)]["current_shareholders_todate_count"].sum()
            numSecretariesAgainstNumOtherBusinessSecretaries = numSecretaries - current_business_df[(current_business_df["registration_no"]!=entity_no) & (current_business_df["entity_id"]==owner_id)]["current_secretaries_todate_count"].sum()
            numActiveChargesAgainstNumOtherBusinessActiveCharges = numActiveCharges - current_business_df[(current_business_df["registration_no"]!=entity_no) & (current_business_df["entity_id"]==owner_id)]["active_charges_todate_count"].sum()
            numSubsidiaryAgainstNumOtherBusinessSubsidiary = numSubsidiary - current_business_df[(current_business_df["registration_no"]!=entity_no) & (current_business_df["entity_id"]==owner_id)]["subsidiary_todate_count"].sum()
            numKeyPositionsAgainstNumOtherBusinessKeyPositions = numDirectorsAgainstNumOtherBusinessDirectors + numAlternateDirectorsAgainstNumOtherBusinessAlternateDirectors + numShareholdersAgainstNumOtherBusinessShareholders + numSecretariesAgainstNumOtherBusinessSecretaries

            results["numDirectorsAgainstNumOtherBusinessDirectors"].append(numDirectorsAgainstNumOtherBusinessDirectors)
            results["numAlternateDirectorsAgainstNumOtherBusinessAlternateDirectors"].append(numAlternateDirectorsAgainstNumOtherBusinessAlternateDirectors)
            results["numShareholdersAgainstNumOtherBusinessShareholders"].append(numShareholdersAgainstNumOtherBusinessShareholders)
            results["numSecretariesAgainstNumOtherBusinessSecretaries"].append(numSecretariesAgainstNumOtherBusinessSecretaries)
            results["numActiveChargesAgainstNumOtherBusinessActiveCharges"].append(numActiveChargesAgainstNumOtherBusinessActiveCharges)
            results["numSubsidiaryAgainstNumOtherBusinessSubsidiary"].append(numSubsidiaryAgainstNumOtherBusinessSubsidiary)
            results["numKeyPositionsAgainstNumOtherBusinessKeyPositions"].append(numKeyPositionsAgainstNumOtherBusinessKeyPositions)


            # Calculate whether current appointment in the business is longest or most recent
            isLongestAppointment = current_business_df[(current_business_df["entity_id"]==owner_id)].sort_values(by='appointment_date', ascending=True).iloc[0]["registration_no"] == entity_no
            isMostRecentAppointment = current_business_df[(current_business_df["entity_id"]==owner_id)].sort_values(by='appointment_date', ascending=False).iloc[0]["registration_no"] == entity_no

            results["isLongestAppointment"].append(isLongestAppointment)
            results["isMostRecentAppointment"].append(isMostRecentAppointment)

            # Retrieve the business entity type from the UEN of the business 
            entityType = entityTypeMapping(entity_no, mappingDF)
            
            results["entityType"].append(entityType)


            # Calculate number of previously terminated and cancelled businesses
            numPreviousTerminatedBusinesses = len(previous_business_df[(previous_business_df["status"].str.contains("TERMINAT")) & (previous_business_df["entity_id"]==owner_id)])
            numPreviousCancelledBusinesses = len(previous_business_df[(previous_business_df["status"].str.contains("CANCEL")) & (previous_business_df["entity_id"]==owner_id)])

            results["numPreviousTerminatedBusinesses"].append(numPreviousTerminatedBusinesses)
            results["numPreviousCancelledBusinesses"].append(numPreviousCancelledBusinesses)


            # Calculate total number and proportion of each litigation type
            numMCLitigation = curr_business_lit_trace_df[
                (curr_business_lit_trace_df["entity_id"]==owner_id) &
                (curr_business_lit_trace_df["enquiries"]=="Litigation Trace: Magistrate Court\n(< $60,000)") &
                (curr_business_lit_trace_df["year"]==searchYear)
            ]["current_year_after_9_Jan"].sum()

            numDCLitigation = curr_business_lit_trace_df[
                (curr_business_lit_trace_df["entity_id"]==owner_id) &
                (curr_business_lit_trace_df["enquiries"]=="Litigation Trace: District Court\n($60,000 - $250,000)") & 
                (curr_business_lit_trace_df["year"]==searchYear)
            ]["current_year_after_9_Jan"].sum()

            numHCLitigation = curr_business_lit_trace_df[
                (curr_business_lit_trace_df["entity_id"]==owner_id) &
                (curr_business_lit_trace_df["enquiries"]=="Litigation Trace: High Court\n(> $250,000)") &
                (curr_business_lit_trace_df["year"]==searchYear)
            ]["current_year_after_9_Jan"].sum()

            numWindingUpLitigation = curr_business_lit_trace_df[
                (curr_business_lit_trace_df["entity_id"]==owner_id) &
                (curr_business_lit_trace_df["enquiries"]=="Winding Up Trace") &
                (curr_business_lit_trace_df["year"]==searchYear)
            ]["current_year_after_9_Jan"].sum()

            numOSOAOPOMLitigation = curr_business_lit_trace_df[
                (curr_business_lit_trace_df["entity_id"]==owner_id) &
                (curr_business_lit_trace_df["enquiries"]=="OS/OA/OP/OM Trace") &
                (curr_business_lit_trace_df["year"]==searchYear)
            ]["current_year_after_9_Jan"].sum()

            numLitigationTraceBusinesses = curr_business_lit_trace_df[
                (curr_business_lit_trace_df["entity_id"]==owner_id) &
                (curr_business_lit_trace_df["year"]==searchYear)
            ]["business_name"].nunique()

            if (numLitigationTraceBusinesses != 0):
                avgNumMCLitigation = numMCLitigation / numLitigationTraceBusinesses
                avgNumDCLitigation = numDCLitigation / numLitigationTraceBusinesses
                avgNumHCLitigation = numHCLitigation / numLitigationTraceBusinesses
                avgNumWindingUpLitigation = numWindingUpLitigation / numLitigationTraceBusinesses
                avgNumOSOAOPOMLitigation = numOSOAOPOMLitigation / numLitigationTraceBusinesses
            else:
                avgNumMCLitigation = 0
                avgNumDCLitigation = 0
                avgNumHCLitigation = 0
                avgNumWindingUpLitigation = 0
                avgNumOSOAOPOMLitigation = 0

            results["numMCLitigation"].append(numMCLitigation)
            results["numDCLitigation"].append(numDCLitigation)
            results["numHCLitigation"].append(numHCLitigation)
            results["numWindingUpLitigation"].append(numWindingUpLitigation)
            results["numOSOAOPOMLitigation"].append(numOSOAOPOMLitigation)
            results["numLitigationTraceBusinesses"].append(numLitigationTraceBusinesses)
            results["avgNumMCLitigation"].append(avgNumMCLitigation)
            results["avgNumDCLitigation"].append(avgNumDCLitigation)
            results["avgNumHCLitigation"].append(avgNumHCLitigation)
            results["avgNumWindingUpLitigation"].append(avgNumWindingUpLitigation)
            results["avgNumOSOAOPOMLitigation"].append(avgNumOSOAOPOMLitigation)


            # Calculate business litigation counts and amounts across court types, number of months, entity type, status, and cause
            for combination in list(itertools.product(COURTTYPE, TIMESPAN, ENTITYTYPE, STATUS, CAUSE)):
                court_type, num_months, entity_type, status, cause = combination[0], combination[1], combination[2], combination[3], combination[4]
                results["totalamountOfBusinessLitigation_"+status+"_"+court_type+"_Within"+str(num_months)+"Months_"+entity_type+"plantiff_DueTo"+cause].append(
                    business_lit_search_df[
                        (business_lit_search_df["entity_id"]==owner_id) &
                        (business_lit_search_df["court_type"] == court_type) &
                        (business_lit_search_df["months_since_filing"] < num_months) &
                        (business_lit_search_df["entity_type"] == entity_type) &
                        (business_lit_search_df["case_status_category"] == status) &
                        (business_lit_search_df["main_cause_category"] == cause)                             
                    ]["amount"].sum()
                )

                results["numberOfBusinessLitigation_"+status+"_"+court_type+"_Within"+str(num_months)+"Months_"+entity_type+"plantiff_DueTo"+cause].append(
                    business_lit_search_df[
                        (business_lit_search_df["entity_id"]==owner_id) &
                        (business_lit_search_df["court_type"] == court_type) &
                        (business_lit_search_df["months_since_filing"] < num_months) &
                        (business_lit_search_df["entity_type"] == entity_type) &
                        (business_lit_search_df["case_status_category"] == status) &
                        (business_lit_search_df["main_cause_category"] == cause) 
                    ]["amount"].count()
                )


            # Calculate bankruptcy record counts and amounts across number of months, entity type, and status
            for combinations in list(itertools.product(TIMESPAN, ENTITYTYPE, STATUS)):
                num_months, entity_type, status = combinations[0], combinations[1], combinations[2]
                results["totalamountOfBankruptcyRecord_"+status+"_Within"+str(num_months)+"Months_"+entity_type+"plantiff"].append(
                    bankruptcy_rec_df[
                        (bankruptcy_rec_df["entity_id"]==owner_id) &
                        (bankruptcy_rec_df["months_since_filing"] < num_months) &
                        (bankruptcy_rec_df["entity_type"] == entity_type) &
                        (bankruptcy_rec_df["case_status_category"] == status) 
                    ]["amount"].sum()
                )

                results["numberOfBankruptcyRecord_"+status+"_Within"+str(num_months)+"Months_"+entity_type+"plantiff"].append(
                    bankruptcy_rec_df[
                        (bankruptcy_rec_df["entity_id"]==owner_id) &
                        (bankruptcy_rec_df["months_since_filing"] < num_months) &
                        (bankruptcy_rec_df["entity_type"] == entity_type) &
                        (bankruptcy_rec_df["case_status_category"] == status) 
                    ]["amount"].count()
                )


            # Calculate individual litigation counts and amounts across court types, number of months, entity type, status, and cause
            for combinations in list(itertools.product(COURTTYPE, TIMESPAN, ENTITYTYPE, STATUS, CAUSE)):
                court_type, num_months, entity_type, status, cause = combinations[0], combinations[1], combinations[2], combinations[3], combinations[4]
                results["totalamountOfIndividualLitigation_"+status+"_"+court_type+"_Within"+str(num_months)+"Months_"+entity_type+"plantiff_DueTo"+cause].append(      
                    indv_lit_search_df[
                        (indv_lit_search_df["entity_id"]==owner_id) &
                        (indv_lit_search_df["court_type"] == court_type) &
                        (indv_lit_search_df["months_since_filing"] < num_months) &
                        (indv_lit_search_df["entity_type"] == entity_type) &
                        (indv_lit_search_df["case_status_category"] == status) &
                        (indv_lit_search_df["main_cause_category"] == cause) 
                    ]["amount"].sum()
                )

                results["numberOfIndividualLitigation_"+status+"_"+court_type+"_Within"+str(num_months)+"Months_"+entity_type+"plantiff_DueTo"+cause].append(      
                    indv_lit_search_df[
                        (indv_lit_search_df["entity_id"]==owner_id) &
                        (indv_lit_search_df["court_type"] == court_type) &
                        (indv_lit_search_df["months_since_filing"] < num_months) &
                        (indv_lit_search_df["entity_type"] == entity_type) &
                        (indv_lit_search_df["case_status_category"] == status) &
                        (indv_lit_search_df["main_cause_category"] == cause) 
                    ]["amount"].count()
                )


            # Calculate recent year financial, commercial and legal search counts
            recentYearIndividualFinancialSearchCount = fin_rel_search_count_df[
                (fin_rel_search_count_df["entity_id"]==owner_id) &
                (fin_rel_search_count_df["purpose"]=="All") &
                (fin_rel_search_count_df["year"]==searchYear-1) & 
                (fin_rel_search_count_df["month"]=="All")
            ]["count"].sum()

            recentYearIndividualTradeInsuranceSearchCount = fin_rel_search_count_df[
                (fin_rel_search_count_df["entity_id"]==owner_id) &
                (fin_rel_search_count_df["purpose"]=="Trade Insurance") &
                (fin_rel_search_count_df["year"]==searchYear-1) & 
                (fin_rel_search_count_df["month"]=="All")
            ]["count"].sum()

            recentYearIndividualFinancialInstitutionSearchCount = fin_rel_search_count_df[
                (fin_rel_search_count_df["entity_id"]==owner_id) &
                (fin_rel_search_count_df["purpose"]=="Financial Institution") &
                (fin_rel_search_count_df["year"]==searchYear-1) & 
                (fin_rel_search_count_df["month"]=="All")
            ]["count"].sum()

            recentYearIndividualHirePurchaseSearchCount = fin_rel_search_count_df[
                (fin_rel_search_count_df["entity_id"]==owner_id) &
                (fin_rel_search_count_df["purpose"]=="Hire Purchase / Leasing") &
                (fin_rel_search_count_df["year"]==searchYear-1) & 
                (fin_rel_search_count_df["month"]=="All")
            ]["count"].sum()

            recentYearIndividualCommercialSearchCount = comm_rel_search_count_df[
                (comm_rel_search_count_df["entity_id"]==owner_id) &
                (comm_rel_search_count_df["purpose"]=="All") &
                (comm_rel_search_count_df["year"]==searchYear-1) & 
                (comm_rel_search_count_df["month"]=="All")
            ]["count"].sum()

            recentYearIndividualCommercialRetailSearchCount = comm_rel_search_count_df[
                (comm_rel_search_count_df["entity_id"]==owner_id) &
                (comm_rel_search_count_df["purpose"]=="Commercial-Retail") &
                (comm_rel_search_count_df["year"]==searchYear-1) & 
                (comm_rel_search_count_df["month"]=="All")
            ]["count"].sum()

            recentYearIndividualServicesSearchCount = comm_rel_search_count_df[
                (comm_rel_search_count_df["entity_id"]==owner_id) &
                (comm_rel_search_count_df["purpose"]=="Services") &
                (comm_rel_search_count_df["year"]==searchYear-1) & 
                (comm_rel_search_count_df["month"]=="All")
            ]["count"].sum()

            recentYearIndividualLegalSearchCount = leg_rel_search_count_df[
                (leg_rel_search_count_df["entity_id"]==owner_id) &
                (leg_rel_search_count_df["purpose"]=="All") &
                (leg_rel_search_count_df["year"]==searchYear-1) & 
                (leg_rel_search_count_df["month"]=="All")
            ]["count"].sum()

            recentYearIndividualLitigationSearchCount = leg_rel_search_count_df[
                (leg_rel_search_count_df["entity_id"]==owner_id) &
                (leg_rel_search_count_df["purpose"]=="Litigation") &
                (leg_rel_search_count_df["year"]==searchYear-1) & 
                (leg_rel_search_count_df["month"]=="All")
            ]["count"].sum()

            recentYearIndividualConveyancingSearchCount = leg_rel_search_count_df[
                (leg_rel_search_count_df["entity_id"]==owner_id) &
                (leg_rel_search_count_df["purpose"]=="Conveyancing") &
                (leg_rel_search_count_df["year"]==searchYear-1) & 
                (leg_rel_search_count_df["month"]=="All")
            ]["count"].sum()

            results["recentYearIndividualFinancialSearchCount"].append(recentYearIndividualFinancialSearchCount)
            results["recentYearIndividualTradeInsuranceSearchCount"].append(recentYearIndividualTradeInsuranceSearchCount)
            results["recentYearIndividualFinancialInstitutionSearchCount"].append(recentYearIndividualFinancialInstitutionSearchCount)
            results["recentYearIndividualHirePurchaseSearchCount"].append(recentYearIndividualHirePurchaseSearchCount)
            results["recentYearIndividualCommercialSearchCount"].append(recentYearIndividualCommercialSearchCount)
            results["recentYearIndividualCommercialRetailSearchCount"].append(recentYearIndividualCommercialRetailSearchCount)
            results["recentYearIndividualServicesSearchCount"].append(recentYearIndividualServicesSearchCount)
            results["recentYearIndividualLegalSearchCount"].append(recentYearIndividualLegalSearchCount)
            results["recentYearIndividualLitigationSearchCount"].append(recentYearIndividualLitigationSearchCount)
            results["recentYearIndividualConveyancingSearchCount"].append(recentYearIndividualConveyancingSearchCount)


    # Export results
    result_df = pd.DataFrame(results)
    result_df.to_csv("calculated_features/ibs features.csv", index=False)



if __name__ == "__main__":
    mappingFilePath = "../Dataset/uen_data/UEN Mapping.csv"
    compiledReportsFilePath = "../Random_Generation/Outputs/compiled_IBS_reports.xlsx"
    featureCalculationsFilePath = "feature_calculations.json"
    main(compiledReportsFilePath, mappingFilePath, featureCalculationsFilePath, 2023)
    print(f'====> IBS Feature Calculation Process Completed!')









