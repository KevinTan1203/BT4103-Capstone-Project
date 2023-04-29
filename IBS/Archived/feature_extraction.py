import json
import pandas as pd

xls = pd.ExcelFile('Output/tables_v1.xlsx')
tables_map = {}
for sheet_name in xls.sheet_names:
    tables_map[sheet_name] = list(xls.parse(sheet_name).columns)[1:]

with open("features.json", "w") as outfile:
    json.dump(tables_map, outfile)
