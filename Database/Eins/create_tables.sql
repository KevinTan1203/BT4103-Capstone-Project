CREATE TABLE Eins.Search_Record (
  entity_id INT NOT NULL,
  entity_name VARCHAR(100) NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Request_Criteria (
  request_id INT NOT NULL,
  request_date DATE NOT NULL,
  requestor_name char(50) NOT NULL,
  requested_entity_name VARCHAR(100) NOT NULL,
  requested_entity_id INT NOT NULL,
  PRIMARY KEY (request_id),
  FOREIGN KEY (requested_entity_id) REFERENCES Eins.Search_Record(entity_id)
);
CREATE TABLE Eins.Company_Details (
  entity_id INT NOT NULL,
  entity_name VARCHAR(100) NOT NULL,
  registration_date DATE NOT NULL,
  country_or_region_of_incorporation_or_registration VARCHAR(50) NOT NULL,
  date_of_name_change DATE,
  former_name VARCHAR(100),
  effective_date_of_former_name DATE,
  company_type VARCHAR(100) NOT NULL,
  registered_office_address VARCHAR(100) NOT NULL,
  date_of_address_change DATE,
  principal_activities VARCHAR(100) NOT NULL,
  status VARCHAR(50) NOT NULL,
  status_date DATE NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Key_Ratios_Current_FYE (
  entity_id INT NOT NULL,
  profit_margin DECIMAL NOT NULL,
  liquidity_times DECIMAL NOT NULL,
  debt_times DECIMAL NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Key_Ratios_Previous_FYE (
  entity_id INT NOT NULL,
  profit_margin DECIMAL NOT NULL,
  liquidity_times DECIMAL NOT NULL,
  debt_times DECIMAL NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Analysis_Net_Profit_Margin (
  entity_id INT NOT NULL,
  company_level DECIMAL NOT NULL,
  industry_median DECIMAL NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Analysis_Total_Asset_Turnover (
  entity_id INT NOT NULL,
  company_level DECIMAL NOT NULL,
  industry_median DECIMAL NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Analysis_Return_On_Assets (
  entity_id INT NOT NULL,
  company_level DECIMAL NOT NULL,
  industry_median DECIMAL NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Analysis_Revenue_Growth (
  entity_id INT NOT NULL,
  company_level DECIMAL NOT NULL,
  industry_median DECIMAL NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Writ_Of_Summons_Org_Claim (
  case_num INT NOT NULL,
  court_type VARCHAR(20) NOT NULL,
  year VARCHAR(10) NOT NULL,
  date_of_filing DATE NOT NULL,
  plaintiff_petitioner_claimant VARCHAR(20) NOT NULL,
  case_status_date_of_status_date_remarks VARCHAR(20) NOT NULL,
  plaintiff_claimant_status_date_of_status DATE,
  defendant_status_date_of_status DATE,
  amount FLOAT NOT NULL,
  date_of_last_update_in_experian_database DATE NOT NULL,
  main_cause VARCHAR(20) NOT NULL,
  entity_id INT NOT NULL,
  PRIMARY KEY (case_num),
  FOREIGN KEY (entity_id) REFERENCES Eins.Company_Details(entity_id)
);
CREATE TABLE Eins.Winding_Up (
  case_num INT NOT NULL,
  type VARCHAR(20) NOT NULL,
  year VARCHAR(10) NOT NULL,
  date_of_filing DATE NOT NULL,
  other_party_name VARCHAR(20) NOT NULL,
  case_status_date_of_status DATE NOT NULL,
  other_party_name_date_of_status DATE,
  defendant_status_date_of_status DATE,
  amount FLOAT NOT NULL,
  date_of_last_update_in_experian_database DATE NOT NULL,
  entity_id INT NOT NULL,
  PRIMARY KEY (case_num),
  FOREIGN KEY (entity_id) REFERENCES Eins.Company_Details(entity_id)
);
CREATE TABLE Eins.OS_OA_OP_OM (
  case_num INT NOT NULL,
  type VARCHAR(20) NOT NULL,
  year VARCHAR(10) NOT NULL,
  date_of_filing DATE NOT NULL,
  other_party_name VARCHAR(20) NOT NULL,
  case_status_date_of_status DATE NOT NULL,
  other_party_name_date_of_status DATE,
  defendant_status_date_of_status DATE,
  amount FLOAT NOT NULL,
  date_of_last_update_in_experian_database DATE NOT NULL,
  entity_id INT NOT NULL,
  PRIMARY KEY (case_num),
  FOREIGN KEY (entity_id) REFERENCES Eins.Company_Details(entity_id)
);
CREATE TABLE Eins.Additional_Experian_Prop_Info (
  entity_id INT NOT NULL,
  num_of_employees INT NOT NULL,
  num_of_commercial_properties_owned INT NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Acrreditations (
  entity_id INT NOT NULL,
  award_name VARCHAR(20) NOT NULL,
  year_of_award VARCHAR(10) NOT NULL,
  award_ranking INT NOT NULL,
  PRIMARY KEY (entity_id, award_name, year_of_award)
);
CREATE TABLE Eins.Financial_Search_Count (
  entity_id INT NOT NULL,
  financial_search_year INT NOT NULL,
  financial_search_total_count INT NOT NULL,
  financial_search_jan_count INT NOT NULL,
  financial_search_feb_count INT NOT NULL,
  financial_search_mar_count INT NOT NULL,
  financial_search_apr_count INT NOT NULL,
  financial_search_may_count INT NOT NULL,
  financial_search_jun_count INT NOT NULL,
  financial_search_jul_count INT NOT NULL,
  financial_search_aug_count INT NOT NULL,
  financial_search_sep_count INT NOT NULL,
  financial_search_oct_count INT NOT NULL,
  financial_search_nov_count INT NOT NULL,
  financial_search_dec_count INT NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Commercial_Search_Count (
  entity_id INT NOT NULL,
  commercial_search_year INT NOT NULL,
  commercial_search_total_count INT NOT NULL,
  commercial_search_jan_count INT NOT NULL,
  commercial_search_feb_count INT NOT NULL,
  commercial_search_mar_count INT NOT NULL,
  commercial_search_apr_count INT NOT NULL,
  commercial_search_may_count INT NOT NULL,
  commercial_search_jun_count INT NOT NULL,
  commercial_search_jul_count INT NOT NULL,
  commercial_search_aug_count INT NOT NULL,
  commercial_search_sep_count INT NOT NULL,
  commercial_search_oct_count INT NOT NULL,
  commercial_search_nov_count INT NOT NULL,
  commercial_search_dec_count INT NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Legal_Search_Count (
  entity_id INT NOT NULL,
  legal_search_year INT NOT NULL,
  legal_search_total_count INT NOT NULL,
  legal_search_jan_count INT NOT NULL,
  legal_search_feb_count INT NOT NULL,
  legal_search_mar_count INT NOT NULL,
  legal_search_apr_count INT NOT NULL,
  legal_search_may_count INT NOT NULL,
  legal_search_jun_count INT NOT NULL,
  legal_search_jul_count INT NOT NULL,
  legal_search_aug_count INT NOT NULL,
  legal_search_sep_count INT NOT NULL,
  legal_search_oct_count INT NOT NULL,
  legal_search_nov_count INT NOT NULL,
  legal_search_dec_count INT NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Capital_Structure_Issued_Ordinary (
  entity_id INT NOT NULL,
  no_of_shares INT NOT NULL,
  currency VARCHAR(50) NOT NULL,
  amount INT NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Capital_Structure_Paid_Up_Ordinary (
  entity_id INT NOT NULL,
  no_of_shares INT NOT NULL,
  currency VARCHAR(50) NOT NULL,
  amount INT NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Capital_Structure_Paid_Up_Reference (
  entity_id INT NOT NULL,
  no_of_shares INT NOT NULL,
  currency VARCHAR(50) NOT NULL,
  amount INT NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Capital_Structure_Paid_Up_Others (
  entity_id INT NOT NULL,
  no_of_shares INT NOT NULL,
  currency VARCHAR(50) NOT NULL,
  amount INT NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Charges (
  charge_id INT NOT NULL,
  date_of_charge DATE NOT NULL,
  chargees VARCHAR(100) NOT NULL,
  amount_secured_and_currency VARCHAR(75) NOT NULL,
  status VARCHAR(75) NOT NULL,
  entity_id INT NOT NULL,
  PRIMARY KEY (charge_id),
  FOREIGN KEY (entity_id) REFERENCES Eins.Company_Details(entity_id)
);
CREATE TABLE Eins.Auditors (
  auditor_id INT NOT NULL,
  auditor_name VARCHAR(100) NOT NULL,
  entity_id INT NOT NULL,
  date_of_appointment DATE NOT NULL,
  PRIMARY KEY (auditor_id),
  FOREIGN KEY (entity_id) REFERENCES Eins.Company_Details(entity_id)
);
CREATE TABLE Eins.Officers_Or_Authorised_Reps (
  employee_id INT NOT NULL,
  employee_name VARCHAR(100) NOT NULL,
  employee_address VARCHAR(100) NOT NULL,
  date_of_change_of_address DATE,
  nationality_or_citizenship VARCHAR(50) NOT NULL,
  date_of_appointment DATE NOT NULL,
  position_held VARCHAR(50) NOT NULL,
  entity_id INT NOT NULL,
  PRIMARY KEY (employee_id),
  FOREIGN KEY (entity_id) REFERENCES Eins.Company_Details(entity_id)
);
CREATE TABLE Eins.Shareholders (
  shareholder_id INT NOT NULL,
  shareholder_name VARCHAR(100) NOT NULL,
  shareholder_address VARCHAR(100) NOT NULL,
  date_of_change_of_address DATE,
  nationality_or_citizenship VARCHAR(50) NOT NULL,
  type_of_shares VARCHAR(50) NOT NULL,
  no_of_shares INT NOT NULL,
  currency VARCHAR(50) NOT NULL,
  entity_id INT NOT NULL,
  PRIMARY KEY (shareholder_id),
  FOREIGN KEY (entity_id) REFERENCES Eins.Company_Details(entity_id)
);
CREATE TABLE Eins.Compliance_Record (
  entity_id INT NOT NULL,
  date_of_last_agm DATE NOT NULL,
  date_of_last_ar DATE NOT NULL,
  date_of_ac_laid_at_last_agm DATE NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Financial_Data_Revenue (
  entity_id INT NOT NULL,
  currency VARCHAR(50) NOT NULL,
  previous_fye_amount INT NOT NULL,
  current_fye_amount INT NOT NULL,
  percentage_change DECIMAL NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Financial_Data_Profit_After_Tax (
  entity_id INT NOT NULL,
  currency VARCHAR(50) NOT NULL,
  previous_fye_amount INT NOT NULL,
  current_fye_amount INT NOT NULL,
  percentage_change DECIMAL NOT NULL,
  PRIMARY KEY (entity_id)
);
CREATE TABLE Eins.Financial_Data_Shareholders_Fund (
  entity_id INT NOT NULL,
  currency VARCHAR(50) NOT NULL,
  previous_fye_amount INT NOT NULL,
  current_fye_amount INT NOT NULL,
  percentage_change DECIMAL NOT NULL,
  PRIMARY KEY (entity_id)
);