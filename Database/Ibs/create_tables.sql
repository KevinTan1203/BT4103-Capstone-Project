CREATE TABLE Ibs.Individual (
    individual_id INT NOT NULL,
    individual_name VARCHAR(100) NOT NULL,
    available_address VARCHAR(100) NOT NULL,
    PRIMARY KEY (individual_id)
);
CREATE TABLE Ibs.Request_Info (
    file_reference_no INT NOT NULL,
    requestor_name VARCHAR(100) NOT NULL,
    requested_indvidual_name VARCHAR(100) NOT NULL,
    requested_id_no INT NOT NULL,
    requested_id INT NOT NULL,
    PRIMARY KEY (file_reference_no),
    FOREIGN KEY (requested_id_no) REFERENCES Ibs.Individual(individual_id)
);
CREATE TABLE Ibs.Business_Litigation (
    case_no INT NOT NULL,
    last_update DATE NOT NULL,
    court_type VARCHAR(20) NOT NULL,
    year VARCHAR(10) NOT NULL,
    filing_date DATE NOT NULL,
    plaintiff VARCHAR(20) NOT NULL,
    case_status VARCHAR(20) NOT NULL,
    case_status_date DATE NOT NULL,
    case_status_remarks VARCHAR(100) NOT NULL,
    plaintiff_status VARCHAR(20) NOT NULL,
    plaintiff_status_date DATE NOT NULL,
    defendant_status VARCHAR(20) NOT NULL,
    amount INT NOT NULL,
    main_cause VARCHAR(100) NOT NULL,
    individual_id INT NOT NULL,
    PRIMARY KEY (case_no, last_update),
    FOREIGN KEY (individual_id) REFERENCES Ibs.Individual(individual_id)
);
CREATE TABLE Ibs.Individual_Litigation (
    case_no INT NOT NULL,
    last_update DATE NOT NULL,
    court_type VARCHAR(20) NOT NULL,
    year VARCHAR(10) NOT NULL,
    filing_date DATE NOT NULL,
    plaintiff_petitioner_claimant VARCHAR(20) NOT NULL,
    case_status VARCHAR(20) NOT NULL,
    case_status_date DATE NOT NULL,
    case_status_remarks VARCHAR(100) NOT NULL,
    plaintiff_claimant_status VARCHAR(20) NOT NULL,
    plaintiff_claimant_status_date DATE NOT NULL,
    defendant_status VARCHAR(20) NOT NULL,
    defendant_status_date DATE NOT NULL,
    amount INT NOT NULL,
    main_cause VARCHAR(20) NOT NULL,
    individual_id INT NOT NULL,
    PRIMARY KEY (case_no, last_update),
    FOREIGN KEY (individual_id) REFERENCES Ibs.Individual(individual_id)
);
CREATE TABLE Ibs.Bankruptcy_Records (
    bankruptcy_case_no INT NOT NULL,
    last_update DATE NOT NULL,
    bankruptcy_year VARCHAR(10) NOT NULL,
    bankruptcy_filling_date DATE NOT NULL,
    bankruptcy_plaintiff VARCHAR(20) NOT NULL,
    case_status VARCHAR(20) NOT NULL,
    case_status_date DATE NOT NULL,
    case_status_remarks VARCHAR(100) NOT NULL,
    plaintiff_claimant_status VARCHAR(20) NOT NULL,
    plaintiff_claimant_status_date DATE NOT NULL,
    defendant_status VARCHAR(20) NOT NULL,
    defendant_status_date DATE NOT NULL,
    amount INT NOT NULL,
    main_cause VARCHAR(20) NOT NULL,
    private_trustees_appointed_name VARCHAR(100) NOT NULL,
    private_trustees_appointed_address VARCHAR(100) NOT NULL,
    individual_id INT NOT NULL,
    PRIMARY KEY (bankruptcy_case_no, last_update),
    FOREIGN KEY (individual_id) REFERENCES Ibs.Individual(individual_id)
);
CREATE TABLE Ibs.Individual_Financial_Search (
    individual_id INT NOT NULL,
    year VARCHAR(10) NOT NULL,
    month VARCHAR(10) NOT NULL,
    search_count INT NOT NULL,
    PRIMARY KEY (individual_id, year, month)
);
CREATE TABLE Ibs.Individual_Commercial_Search (
    individual_id INT NOT NULL,
    year VARCHAR(10) NOT NULL,
    month VARCHAR(10) NOT NULL,
    search_count INT NOT NULL,
    PRIMARY KEY (individual_id, year, month)
);
CREATE TABLE Ibs.Individual_Legal_Search (
    individual_id INT NOT NULL,
    year VARCHAR(10) NOT NULL,
    month VARCHAR(10) NOT NULL,
    search_count INT NOT NULL,
    PRIMARY KEY (individual_id, year, month)
);
CREATE TABLE Ibs.Individual_Financial_Search_Breakdown (
    individual_id INT NOT NULL,
    purpose VARCHAR(100) NOT NULL,
    year VARCHAR(10) NOT NULL,
    month VARCHAR(10) NOT NULL,
    search_count INT NOT NULL,
    PRIMARY KEY (individual_id, purpose, year, month)
);
CREATE TABLE Ibs.Individual_Commercial_Search_Breakdown (
    individual_id INT NOT NULL,
    purpose VARCHAR(100) NOT NULL,
    year VARCHAR(10) NOT NULL,
    month VARCHAR(10) NOT NULL,
    search_count INT NOT NULL,
    PRIMARY KEY (individual_id, purpose, year, month)
);
CREATE TABLE Ibs.Individual_Legal_Search_Breakdown (
    individual_id INT NOT NULL,
    purpose VARCHAR(100) NOT NULL,
    year VARCHAR(10) NOT NULL,
    month VARCHAR(10) NOT NULL,
    search_count INT NOT NULL,
    PRIMARY KEY (individual_id, purpose, year, month)
);
CREATE TABLE Ibs.Individual_Current_Business (
    individual_id INT NOT NULL,
    registration_no INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    position VARCHAR(50) NOT NULL,
    appointment_date DATE NOT NULL,
    PRIMARY KEY (individual_id, registration_no)
);
CREATE TABLE Ibs.Current_Business_Details (
    registration_no INT NOT NULL,
    business_name VARCHAR(100) NOT NULL,
    current_directors_todate_count INT NOT NULL,
    current_secretaries_todate_count INT NOT NULL,
    current_alternate_directors_todate_count INT NOT NULL,
    active_charges_todate_count INT NOT NULL,
    current_shareholders_owners_todate_count INT NOT NULL,
    subsidiary_associates_todate_count INT NOT NULL,
    PRIMARY KEY (registration_no)
);
CREATE TABLE Ibs.Individual_Previous_Business (
    individual_id INT NOT NULL,
    business_registration_no INT NOT NULL,
    business_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    position VARCHAR(50) NOT NULL,
    cessation_date DATE NOT NULL,
    PRIMARY KEY (individual_id, business_registration_no)
);
CREATE TABLE Ibs.Business_Litigation_Trace (
    business_registration_no INT NOT NULL,
    enquiries VARCHAR(100) NOT NULL,
    business_name VARCHAR(100) NOT NULL,
    current_year_trace VARCHAR(20) NOT NULL,
    previous_year_trace VARCHAR(50) NOT NULL,
    current_year DATE NOT NULL,
    PRIMARY KEY (business_registration_no, enquiries)
);
CREATE TABLE Ibs.Accreditations (
    business_registration_no INT NOT NULL,
    award_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (business_registration_no, award_name)
);
