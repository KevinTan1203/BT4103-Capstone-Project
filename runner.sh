#!/bin/bash

# Print the current working directory
echo "Current directory: $(pwd)"
echo

# What follows this will be a series of scripts being executed in order for
# the purposes of testing the logical flow and execution in each individual script
# as well as the complete run of the prohject from start to end

# Executes the Data Extraction Runner Script
echo "==> Stage 1: Performing Data Extraction Process"
echo
cd "EINS/"
echo "Current directory: $(pwd)"
echo "Data Extraction on EINS Reports..."
python3 "eins_extraction_runner.py"
echo "==> EINS Data Extraction Completed!"
echo

echo "Switching directory to IBS folder location."
echo
cd "../IBS"
echo "Current directory: $(pwd)"
echo "Data Extraction on IBS Reports..."
python3 "ibs_extraction_runner.py"
echo "=> IBS Data Extraction Completed!"
echo

# Executes the Data Generation Runner Script
echo "==> Stage 2: Performing Data Generation Process"
echo
echo "Running Data Generation Process for EINS and IBS"
echo "Switching directory to Random_Generation folder location."
echo
cd "../Random_Generation"
echo "Current directory: $(pwd)"
python3 "random_combined_generation.py"
echo "==> Data Generation Process for EINS and IBS Completed!"
echo

# Executes the Data Concatenation Runner Script
echo "==> Stage 3: Performing Data Compilation Process"
echo "Switching directory to Data Compilation folder location."
echo
cd "Data_Concatenation/"
echo "Current directory: $(pwd)"
for file_path in *.py; do 
    echo "Executing Python file: $(basename "$file_path")"
    python3 "$file_path"; done

echo "==> Data Compilation Completed!"
echo

# Executes the Feature Generation Process
echo "==> Stage 4: Performing Feature Generation Process"
echo
echo "Switching directory to Feature Generation folder location."
cd "../../Feature_Generation"
echo "Current directory: $(pwd)"
echo "Running EINS Feature Calculation Process..."
python3 "eins_feature_calculation.py"
echo "==> EINS Feature Calculation Process Completed!"
echo
echo "Running IBS Feature Calculation Process..."
echo
python3 "ibs_feature_calculation.py"
echo "==> IBS Feature Calculation Process Completed!"
echo "==> Feature Calculation Process Completed!"
echo

# Executes the Information Value Section
echo "==> Stage 5: Performing Information Value Calculation Process"
echo
echo "Switching directory to Information Value folder location."
echo
cd "../Information_Value"
echo "Current directory: $(pwd)"
echo
echo "Computing Combined Information Value Calculation for EINS and IBS Data..."
python3 "combined_iv_calculation.py"
echo "==> Successfully Performed Combined Information Value Calculation for EINS and IBS Features!"
echo

# Return to root directory
cd "../"
echo "Current directory: $(pwd)"
echo
echo "==> Data Pipeline Process Completed!"
echo "Data Extraction => Data Generation => Data Compilation => Feature Generation => Information Value Calculation"
