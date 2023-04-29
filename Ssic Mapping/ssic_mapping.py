import pandas as pd
import numpy as np
import re

def create_categories(current_ssic):
    names = ('Section', 'Division', 'Group', 'Class', 'Sub-Class')
    number = len(names)
    categories = [np.NaN] * number
    codes = [np.NaN] * number

    data = {}
    for name in names:
        data[name] = []
    data['code'] = []

    file_name, sheet_no, header = current_ssic

    df = pd.read_excel(
        f'./Dataset/ssic_data/{file_name}', sheet_name=sheet_no, header=header)
    for index, row in df.iterrows():
        code = str(row.iloc[0])
        title = str(row.iloc[1])
        if code.replace(' ', '').isalpha():
            categories[0] = title
            for index in range(1, number):
                categories[index] = np.NaN
                codes[index] = np.NaN
        else:
            for index in range(1, number):
                if not isinstance(codes[index], str) or codes[index] not in code:
                    categories[index] = title
                    codes[index] = code
                    for index2 in range(index + 1, number):
                        categories[index2] = np.NaN
                        codes[index2] = np.NaN
                    if index == number - 1:
                        data['code'].append(code)
                        for index2 in range(number):
                            data[names[index2]].append(categories[index2])
                    else:
                        for index2 in range(index + 1, number):
                            categories[index2] = np.NaN
                            codes[index2] = np.NaN
                    break
    return pd.DataFrame(data)


def merge_codes(df, previous_ssic):
    for file_name, sheet_no, header in previous_ssic:
        right_df = pd.read_excel(f'./Dataset/ssic_data/{file_name}', sheet_name=sheet_no, header=header, dtype=str).iloc[:, 1:3]
        right_df = right_df.applymap(lambda x: re.sub(r'\D+', '', x))
        df = df.merge(right_df, left_on=df.columns[-1], right_on=right_df.columns[0], how='left')
    df = df.drop(columns='code')
    return df


def ssic_mapping(id, mapping):
    ssic_years = mapping.columns[5:]
    for ssic_year in ssic_years:
        if mapping[ssic_year].isin([id]).any():
            return mapping[mapping[ssic_year] == id] \
                .drop_duplicates(subset=ssic_year) \
                .drop(columns=ssic_years) \
                .reset_index(drop=True)



if __name__ == '__main__':
    current_ssic = ('ssic2020-classification-structure.xlsx', 0, 4)
    previous_ssic = [
        ('correspondence-tables-between-ssic2020-2015v18.xlsx', 0, 4),
        ('ssic2015v2018ssic2015ctr.xls', 0, 4),
        ('ssic2015-2010ctr.xls', 0, 0),
        ('ssic2005-2010ctr.xls', 1, 0),
        ('ssic2000-2005ctr.xls', 1, 0),
    ]
    df = create_categories(current_ssic)
    df = merge_codes(df, previous_ssic)
    df.to_csv('./Dataset/ssic_data/ssic_mapping.csv', index=False)
