import pandas as pd
import numpy as np
import os
import re
import math
import time
import random
from varclushi import VarClusHi


def is_monotonic(temp_series):
    return all(temp_series[i] <= temp_series[i + 1] for i in range(len(temp_series) - 1)) or \
        all(temp_series[i] >= temp_series[i + 1] for i in range(len(temp_series) - 1))

def prepare_bins(bin_data, c_i, target_col, max_bins):
    force_bin = True
    binned = False
    remarks = np.nan
    # ----------------- Monotonic binning -----------------
    for n_bins in range(max_bins, 2, -1):
        try:
            bin_data[c_i + "_bins"] = pd.qcut(bin_data[c_i], n_bins, duplicates="drop")
            monotonic_series = bin_data.groupby(c_i + "_bins")[target_col].mean().reset_index(drop=True)
            if is_monotonic(monotonic_series):
                force_bin = False
                binned = True
                remarks = "binned monotonically"
                break
        except:
            pass
    # ----------------- Force binning -----------------
    # creating 2 bins forcefully because 2 bins will always be monotonic
    if force_bin or (c_i + "_bins" in bin_data and bin_data[c_i + "_bins"].nunique() < 2):
        _min=bin_data[c_i].min()
        _mean=bin_data[c_i].mean()
        _max=bin_data[c_i].max()
        bin_data[c_i + "_bins"] = pd.cut(bin_data[c_i], [_min, _mean, _max], include_lowest=True)
        if bin_data[c_i + "_bins"].nunique() == 2:
            binned = True
            remarks = "binned forcefully"
    
    if binned:
        return c_i + "_bins", remarks, bin_data[[c_i, c_i+"_bins", target_col]].copy()
    else:
        remarks = "couldn't bin"
        return c_i, remarks, bin_data[[c_i, target_col]].copy()

def iv_woe_4iter(bin_data, target_col, class_col):
    if "_bins" in class_col:
        bin_data[class_col] = bin_data[class_col].cat.add_categories(['Missing'])
        bin_data[class_col] = bin_data[class_col].fillna("Missing")
        intermediate_df = bin_data.groupby(class_col).agg(
            {class_col.replace("_bins", ""):["min", "max"], target_col: ["count", "sum", "mean"]}
        ).reset_index()
    else:
        bin_data[class_col] = bin_data[class_col].fillna("Missing")
        intermediate_df = bin_data.groupby(class_col).agg(
            {class_col:["first", "first"], target_col: ["count", "sum", "mean"]}
        ).reset_index()
    
    intermediate_df.columns = ["sample_class", "min_value", "max_value", "sample_count", "event_count", "event_rate"]
    intermediate_df["non_event_count"] = intermediate_df["sample_count"] - intermediate_df["event_count"]
    intermediate_df["non_event_rate"] = 1 - intermediate_df["event_rate"]
    intermediate_df = intermediate_df[
        ["sample_class", "min_value", "max_value", "sample_count",
         "non_event_count", "non_event_rate", "event_count", "event_rate"]
    ]
    
    if "_bins" not in class_col and "Missing" in intermediate_df["min_value"]:
        intermediate_df["min_value"] = intermediate_df["min_value"].replace({"Missing": np.nan})
        intermediate_df["max_value"] = intermediate_df["max_value"].replace({"Missing": np.nan})
    intermediate_df["feature"] = class_col
    if "_bins" in class_col:
        intermediate_df["sample_class_label"]=intermediate_df["sample_class"].replace({"Missing": np.nan}).astype('category').cat.codes.replace({-1: np.nan})
    else:
        intermediate_df["sample_class_label"]=np.nan
    intermediate_df = intermediate_df[
        ["feature", "sample_class", "sample_class_label", "sample_count", "min_value", 
         "max_value", "non_event_count", "non_event_rate", "event_count", "event_rate"]
    ]
    
    """
    Get distribution of good and bad
    """
    intermediate_df['distr_non_event'] = intermediate_df["non_event_count"]/intermediate_df["non_event_count"].sum()
    intermediate_df['distr_event'] = intermediate_df["event_count"]/intermediate_df["event_count"].sum()

    intermediate_df['woe'] = np.log(intermediate_df['distr_non_event'] / intermediate_df['distr_event'])
    intermediate_df['iv'] = (intermediate_df['distr_non_event'] - intermediate_df['distr_event']) * intermediate_df['woe']
    
    intermediate_df["woe"] = intermediate_df["woe"].replace([np.inf,-np.inf],0)
    intermediate_df["iv"] = intermediate_df["iv"].replace([np.inf,-np.inf],0)
    
    return intermediate_df

def var_iter(data, target_col, max_bins):
    woe_iv = pd.DataFrame()
    remarks_list = []
    for c_i in data.columns:
        if c_i not in [target_col]:
            # check if binning is required. if yes, then prepare bins and calculate woe and iv.
            """
            ----logic---
            binning is done only when feature is continuous and non-binary.
            Note: Make sure dtype of continuous columns in dataframe is not object.
            """
            c_i_start_time=time.time()
            if np.issubdtype(data[c_i], np.number) and data[c_i].nunique() > 2:
                class_col, remarks, bin_data = prepare_bins(data[[c_i, target_col]].copy(), c_i, target_col, max_bins)
                agg_data = iv_woe_4iter(bin_data.copy(), target_col, class_col)
                remarks_list.append({"feature": c_i, "remarks": remarks})
            else:
                agg_data = iv_woe_4iter(data[[c_i, target_col]].copy(), target_col, c_i)
                remarks_list.append({"feature": c_i, "remarks": "categorical"})
            # print("---{} seconds. c_i: {}----".format(round(time.time() - c_i_start_time, 2), c_i))
            woe_iv = woe_iv.append(agg_data)
    return woe_iv, pd.DataFrame(remarks_list)

def calc_iv_woe(data, target_col, max_bins):
    func_start_time = time.time()
    woe_iv, binning_remarks = var_iter(data, target_col, max_bins)
    print("------------------IV and WOE calculated for individual groups.------------------")
    print("Total time elapsed: {} minutes".format(round((time.time() - func_start_time) / 60, 3)))
    
    woe_iv["feature"] = woe_iv["feature"].replace("_bins", "", regex=True)    
    woe_iv = woe_iv[["feature", "sample_class", "sample_class_label", "sample_count", "min_value", "max_value",
                     "non_event_count", "non_event_rate", "event_count", "event_rate", 'distr_non_event',
                     'distr_event', 'woe', 'iv']]
    
    iv = woe_iv.groupby("feature")[["iv"]].agg(["sum", "count"]).reset_index()
    print("------------------Aggregated IV values for features calculated.------------------")
    print("Total time elapsed: {} minutes".format(round((time.time() - func_start_time) / 60, 3)))
    
    iv.columns = ["feature", "iv", "number_of_classes"]
    null_percent_data=pd.DataFrame(data.isnull().mean()).reset_index()
    null_percent_data.columns=["feature", "feature_null_percent"]
    iv=iv.merge(null_percent_data, on="feature", how="left")
    print("------------------Null percent calculated in features.------------------")
    print("Total time elapsed: {} minutes".format(round((time.time() - func_start_time) / 60, 3)))

    iv = iv.merge(binning_remarks, on="feature", how="left")
    woe_iv = woe_iv.merge(iv[["feature", "iv", "remarks"]].rename(columns={"iv": "iv_sum"}), on="feature", how="left")
    print("------------------Binning remarks added and process is complete.------------------")
    print("Total time elapsed: {} minutes".format(round((time.time() - func_start_time) / 60, 3)))
    return iv, woe_iv.replace({"Missing": np.nan})


def main(featureFilePath):
    # Read generated features file
    ibs_df = pd.read_csv(featureFilePath, index_col=0)
    ibs_df.drop("ownerID", axis=1, inplace=True)

    # Aggregate IBS features
    mean_ibs_df = ibs_df.groupby("entityNo").mean()
    mean_ibs_df.columns = "mean_" + mean_ibs_df.columns
    max_ibs_df = ibs_df.groupby("entityNo").max()
    max_ibs_df.columns = "max_" + max_ibs_df.columns
    min_ibs_df = ibs_df.groupby("entityNo").min()
    min_ibs_df.columns = "min_" + min_ibs_df.columns

    # Combine aggregated IBS features
    combined_ibs_df = pd.concat([mean_ibs_df, max_ibs_df, min_ibs_df], axis=1)
    combined_df = ibs_df.merge(combined_ibs_df, how="left", left_on="entityNo", right_index=True)

    # Drop features with more than 50% missing values
    combined_df = combined_df.loc[:, combined_df.isin([np.nan, '-']).mean() < 0.5]

    # Assign a random target
    combined_df["target"] = [random.randint(0,1) for i in range(len(combined_df))]

    # Export all calculated features for reference
    combined_df.to_csv("../../Feature_Generation/calculated_features/ibs features.csv")

    # Calculate and export WOE and IV calculations
    iv, woe_iv = calc_iv_woe(combined_df.copy(), target_col="target", max_bins=20)
    iv.to_csv("../iv_calculations/ibs iv calculations.csv")
    woe_iv.to_csv("../iv_calculations/ibs woe iv calculations.csv")

    # Select features with IV value > 0.04
    selected_iv = iv[iv["iv"]>0.04]
    selected_iv = selected_iv[selected_iv["remarks"]!="categorical"]

    # Cluster variables
    clus_df = combined_df[selected_iv["feature"].values.tolist()]
    var_clus_model = VarClusHi(clus_df, maxeigval2 = 0.7, maxclus=20)
    var_clus_model.varclus()
    var_clus_df = var_clus_model.rsquare
    var_clus_df["IV"] = [selected_iv[selected_iv["feature"]==i]["iv"].values[0] for i in var_clus_df["Variable"]]
    var_clus_df["Absolute Correlation"] = [np.abs(np.corrcoef(combined_df["target"], combined_df[c])[0,1]) for c in var_clus_df["Variable"]]

    # For each cluster, select the variable with the highest absolute correlation with the target variable
    var_clus_df.sort_values(by=["Cluster", "Absolute Correlation"], ascending=[True, False], inplace=True)
    selected_var_df = var_clus_df.groupby('Cluster').head(1)
    selected_var_list = selected_var_df["Variable"].values.tolist()

    # Export selected variables
    combined_df[selected_var_list + ["target",]].to_csv('selected_features/ibs_selected_features.csv', index=False)

    return selected_var_list



if __name__ == "__main__":
    ibsFilePath = "../../Feature_Generation/calculated_features/ibs features.csv"
    print('Computing IBS IV Calculation Procedure')
    main(ibsFilePath)
    print(f'====> IBS Feature Calculation Process Completed!')





