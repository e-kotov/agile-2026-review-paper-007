#%%
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from constants.tools import *

### code to create bar chart (by category) for modal split
source = os.getcwd()
results_folder = os.path.abspath(os.path.join(source, '..', 'results','vienna'))

filters_path = os.path.join(results_folder, 'filters', 'MultiGraph_walk_bike_PT', 'unique_route_nr_filters')

path = os.path.join(results_folder, 'transitions', 'MultiGraph_walk_bike_PT')
subfolders = [item for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))]

path_odpairs = os.path.join(results_folder, '..', '..', 'data', '06_OD_pairs')
path_output_original = os.path.join(results_folder, '..', '..', 'plots')

if not os.path.exists(path_output_original):
    os.makedirs(path_output_original)

input_file = 'random_nodes_start_end.csv'

modes = [mode for mode in custom_order if mode in custom_order]

# read OD pairs for details of categories
od_pairs = pd.read_csv(os.path.join(path_odpairs, input_file))
od_pairs['start_id'] = '110011_' + od_pairs['start_id'].str.split('_').str[1] + '_0000'
od_pairs['end_id'] = '220022_' + od_pairs['end_id'].str.split('_').str[1] + '_0000'
od_pairs['OD'] = od_pairs['start_id'].astype(str) + '-' + od_pairs['end_id'].astype(str)
od_pairs['route_nr'] = od_pairs['route_nr'].astype(str) + '_' + od_pairs['OD']
#%%
for subfolder in subfolders:
    
    path_data = os.path.join(path, subfolder , f'unique_route_nr_{subfolder}')
    path_weighted = path_data

    files = [f for f in os.listdir(path_data) if f.endswith('.csv')]
    print(f"Processing scenario: {subfolder} with {len(files)} files.")
    # read each file and aggregate data
    data = []
    data_filters = []
    for file in files:
        df = pd.read_csv(os.path.join(path_weighted, file))

        df = df[[c for c in df.columns if not c.endswith('_length_perc')]]
        for mode in modes_without_transition:  
            base_col = f"{mode}_time_perc"
            trans_col = f"transition_{mode}_time_perc"

            # if transition column exists, add it into base column
            if base_col in df.columns:
                if trans_col in df.columns:
                    df.loc[:, base_col] = df[base_col] + df[trans_col]
                    df.drop(columns=[trans_col], inplace=True)
            else:
                # case where base column is missing but transition_* exists
                print(f"Warning in scenario {subfolder}: {base_col} missing in {file}. Check data consistency.")
        data.append(df)
        
        df_filters = pd.read_csv(os.path.join(filters_path, file))
        df_filters = df_filters[[c for c in df_filters.columns if not c.endswith('_length_perc')]]
        for mode in modes_without_transition:  
            base_col = f"{mode}_time_perc"
            trans_col = f"transition_{mode}_time_perc"

            # if transition column exists, add it into base column
            if base_col in df_filters.columns:
                if trans_col in df_filters.columns:
                    df_filters.loc[:, base_col] = df_filters[base_col] + df_filters[trans_col]
                    df_filters.drop(columns=[trans_col], inplace=True)
            else:
                # case where base column is missing but transition_* exists
                print(f"Warning in filters data: {base_col} missing in {file}. Check data consistency.")
        data_filters.append(df_filters)

    # concatenate all dataframes into one and rename columns
    data = pd.concat(data, ignore_index=True)
    data = data.rename(columns=column_mapping)

    data_filters = pd.concat(data_filters, ignore_index=True)
    data_filters = data_filters.rename(columns=column_mapping)

    # remove rows with Zero length (i.e., same start and end point)
    mode_sum = data[data.columns[data.columns.isin(modes)]].sum(axis=1)
    data = data[mode_sum > 0]

    mode_sum = data_filters[data_filters.columns[data_filters.columns.isin(modes)]].sum(axis=1)
    data_filters = data_filters[mode_sum > 0]

    # check if each row sums to ~100%, if not --> exit with message
    row_sums = data[data.columns[data.columns.isin(modes)]].sum(axis=1)
    row_correct = data[np.isclose(row_sums, 100, atol=0.005)]
    if len(row_correct) != len(data):
        print('Some rows do NOT sum to 100% - check the input data!')
        exit(1)

    row_sums = data_filters[data_filters.columns[data_filters.columns.isin(modes)]].sum(axis=1)
    row_correct = data_filters[np.isclose(row_sums, 100, atol=0.005)]
    if len(row_correct) != len(data_filters):
        print('Some rows do NOT sum to 100% - check the input data!')
        exit(1)

    # add up transition modes to their corresponding 'normal' modes if present
    if data.columns.str.contains('transition').any():
        for mode in modes_without_transition:
            try:
                data[mode] = data[mode] + data[f'transition_{mode}']
            except KeyError:
                continue

    if data_filters.columns.str.contains('transition').any():
        for mode in modes_without_transition:
            try:
                data_filters[mode] = data_filters[mode] + data_filters[f'transition_{mode}']
            except KeyError:
                continue

    # data_info = data[['route_nr', 'lower', 'upper', 'walk', 'bike', 'car', 'bus', 'tram', 'subway', 'train']]
    data['route_nr'] = data['route_nr'].astype(str) + '_' + data['OD'].astype(str)
    data_filters['route_nr'] = data_filters['route_nr'].astype(str) + '_' + data_filters['OD'].astype(str)

    # now I want to have only the roytes that are common in data and data_filters
    common_routes = set(data['route_nr']).intersection(set(data_filters['route_nr']))

    data = data[data['route_nr'].isin(common_routes)]
    data_filters = data_filters[data_filters['route_nr'].isin(common_routes)]

    # This part is only if I want to keep the affected routes !
    mode_cols = [col for col in modes if col in data.columns and col in data_filters.columns]

    data.set_index('route_nr', inplace=True)
    data_filters.set_index('route_nr', inplace=True)

    # compare each row between data and data_filters
    # Keep only rows where at least one mode has changed
    mask_changed = (data[mode_cols] != data_filters[mode_cols]).any(axis=1)

    # filter both 
    data = data[mask_changed].copy()
    data_filters = data_filters[mask_changed].copy()
    print("Original number of routes: ", len(common_routes))
    print(f"Number of routes without changes: {len(common_routes) - len(data)}")
    print(f"Number of routes with changes: {len(data)}")
    print(f"Percentage of routes with changes: {len(data) / len(common_routes) * 100:.2f}%")
    data.head(10)

    def make_barchart(df, od_pairs, modes, colors_inner, title_suffix, ax):
        # merge with od_pairs
        df_info = pd.merge(df, od_pairs, how='inner', on='route_nr')

        # group by length category
        mean_pct = (
            df_info[df_info.columns[df_info.columns.isin(modes + ['lower', 'upper'])]]
            .groupby(['lower', 'upper'])
            .mean()
            .reset_index()
        )
        count_by_category = (df_info.groupby(['lower', 'upper'])
            .size().reset_index(name='count'))

        # TOTAL row
        total_row = df_info[modes].mean().to_frame().T
        total_row['lower'] = df_info['lower'].min()
        total_row['upper'] = df_info['upper'].max()
        total_row = total_row[mean_pct.columns]
        mean_pct = pd.concat([mean_pct, total_row], ignore_index=True)

        count_by_category.loc[len(count_by_category)] = [
            df_info['lower'].min(),
            df_info['upper'].max(),
            count_by_category['count'].sum()]

        x_labels = [f"{int(row['lower'])//1000}-{int(row['upper'])//1000}"
            for _, row in mean_pct.iterrows()]
        x_labels = x_labels[:-1] + ['total']
        counts = count_by_category['count'].tolist()
        new_labels = [f"{lbl}\n({int(cnt)})" for lbl, cnt in zip(x_labels, counts)]

        #plotting 
        x = np.arange(len(x_labels)) * 1.8  

        bottom = [0] * len(mean_pct)

        for mode in modes:
            bars = ax.bar( x, mean_pct[mode],
                bottom=bottom,
                label=mode,
                color=colors_inner.get(mode, 'gray'))
            bottom = [i + j for i, j in zip(bottom, mean_pct[mode])]

            ax.bar_label(
                bars, labels=[f'{v:.0f}' if v >= 3 else '' for v in mean_pct[mode]],
                label_type='center',
                fontsize=13,
                color='k')

        ax.set_ylim([0, 101])
        ax.set_ylabel("Mean Percentage [%]", fontsize=16)
        ax.set_xlabel("Length Category [km]\n(Number of Altered Routes)", fontsize=16)
        ax.set_xticks(x)
        ax.set_xticklabels(new_labels, fontsize=13 , rotation=90)
        ax.set_title(f"Modal Split - {title_suffix}", fontsize=18)

        ax.tick_params(axis='y', labelsize=14)
        ax.tick_params(axis='x', labelsize=14)
        ax.vlines(x=ax.get_xticks()[-1] - 0.5, ymin=0, ymax=100, color='k', linestyle='--')

    modes_plot = [m for m in modes_without_transition if m not in ['lower', 'upper', 'district']]

    if subfolder == 'feasibility_filter_walk_1125' or subfolder == 'feasibility_filter_bike_1250':
        
        fig, axes = plt.subplots(1, 2, figsize=(26, 8), sharey=True)

        title_name = rename_dict.get(subfolder, subfolder)

        make_barchart(
            df=data,
            od_pairs=od_pairs,
            modes=modes_plot,
            colors_inner=colors_inner,
            title_suffix=f" {title_name}",
            ax=axes[0])

        make_barchart(
            df=data_filters,
            od_pairs=od_pairs,
            modes=modes_plot,
            colors_inner=colors_inner,
            title_suffix="Baseline Thresholds",
            ax=axes[1])

        legend_handles = [ plt.Line2D([0], [0], marker='s', color='none',
                    markerfacecolor=colors_inner[m], markersize=11)
            for m in modes_plot ]

        axes[1].legend(
            legend_handles,
            modes_without_transition,
            title='Mode',
            bbox_to_anchor=(1, 1),
            loc='upper left',
            fontsize=14,        
            title_fontsize=16)


        axes[1].legend(title='Mode', bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        if subfolder == 'feasibility_filter_walk_1125':
            plt.savefig(os.path.join(path_output_original, f"combined_barchart_{subfolder}.png"),
                        dpi=300, bbox_inches='tight')
        elif subfolder == 'feasibility_filter_bike_1250':
            plt.savefig(os.path.join(path_output_original, f"combined_barchart_{subfolder}.png"),
                        dpi=300, bbox_inches='tight')
        else:
            print(f" ")
        plt.show()

    # ---- CALCULATE MEAN SHARE PER GROUP ----
    group_definitions = {'Walk': ['walk'], 'Bike': ['bike'], 'PT': PT_modes}

    results = []

    for group_name, group_cols in group_definitions.items():
        
        # Keep only those columns that exist in both dataframes
        cols = [c for c in group_cols if c in data.columns and c in data_filters.columns]
        if len(cols) == 0:
            continue  # nothing to compare

        scenario_mean = data[cols].sum(axis=1).mean()
        filters_mean = data_filters[cols].sum(axis=1).mean()
        diff = scenario_mean - filters_mean

        results.append({'group': group_name,
            'scenario_mean': scenario_mean,
            'filters_mean': filters_mean,
            'difference': diff,
            'change': 'increased' if diff > 0 else
                    'decreased' if diff < 0 else
                    'no change' })

    df_change = pd.DataFrame(results)
    print(df_change)

    def compute_overall_mean_time(df, od_pairs, time_col):
        df_info = pd.merge(df, od_pairs, how='inner', on='route_nr')
        return df_info[time_col].mean()

    # Compute mean overall time (Scenario vs Filters)
    mean_time_scenario = compute_overall_mean_time(data, od_pairs, "sum_time_for_time")
    mean_time_filters  = compute_overall_mean_time(data_filters, od_pairs, "sum_time_for_time")

    # Absolute Δ time
    delta_time = mean_time_scenario - mean_time_filters 

    # Percent Δ time (relative change)
    percent_delta = (delta_time / mean_time_scenario) * 100

    print("---- Overall Time Summary ----")
    print(f"Percent Δ Time: {percent_delta:.2f}%")

    #LENGTHH !!!!
    # Compute mean overall time (Scenario vs Filters)
    mean_len_scenario = compute_overall_mean_time(data, od_pairs, "sum_length_for_time")
    mean_len_filters  = compute_overall_mean_time(data_filters, od_pairs, "sum_length_for_time")

    # Absolute Δ time
    delta_len =  mean_len_filters - mean_len_scenario 

    # Percent Δ time (relative change)
    percent_delta = (delta_len / mean_len_scenario) * 100

    print("---- Overall Length Summary ----")
    print(f"Percent Δ Length: {percent_delta:.2f}%")
# %%



#%%%%

# Table 3 results for no filters
path = os.path.join(results_folder, 'nofilters', 'MultiGraph_walk_bike_PT')
subfolders = [item for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))]

for subfolder in subfolders:
    
    path_data = os.path.join(path, subfolder)
    path_weighted = path_data

    files = [f for f in os.listdir(path_data) if f.endswith('.csv')]
    print(f"Processing scenario: {subfolder} with {len(files)} files.")
    # read each file and aggregate data
    data = []
    data_filters = []
    for file in files:
        df = pd.read_csv(os.path.join(path_weighted, file))

        df = df[[c for c in df.columns if not c.endswith('_length_perc')]]
        for mode in modes_without_transition:  
            base_col = f"{mode}_time_perc"
            trans_col = f"transition_{mode}_time_perc"

            # if transition column exists, add it into base column
            if base_col in df.columns:
                if trans_col in df.columns:
                    df.loc[:, base_col] = df[base_col] + df[trans_col]
                    df.drop(columns=[trans_col], inplace=True)
            else:
                # case where base column is missing but transition_* exists
                print(f"Warning in scenario {subfolder}: {base_col} missing in {file}. Check data consistency.")
        data.append(df)
        
        df_filters = pd.read_csv(os.path.join(filters_path, file))
        df_filters = df_filters[[c for c in df_filters.columns if not c.endswith('_length_perc')]]
        for mode in modes_without_transition:  
            base_col = f"{mode}_time_perc"
            trans_col = f"transition_{mode}_time_perc"

            # if transition column exists, add it into base column
            if base_col in df_filters.columns:
                if trans_col in df_filters.columns:
                    df_filters.loc[:, base_col] = df_filters[base_col] + df_filters[trans_col]
                    df_filters.drop(columns=[trans_col], inplace=True)
            else:
                # case where base column is missing but transition_* exists
                print(f"Warning in filters data: {base_col} missing in {file}. Check data consistency.")
        data_filters.append(df_filters)

    # concatenate all dataframes into one and rename columns
    data = pd.concat(data, ignore_index=True)
    data = data.rename(columns=column_mapping)

    data_filters = pd.concat(data_filters, ignore_index=True)
    data_filters = data_filters.rename(columns=column_mapping)

    # remove rows with Zero length (i.e., same start and end point)
    mode_sum = data[data.columns[data.columns.isin(modes)]].sum(axis=1)
    data = data[mode_sum > 0]

    mode_sum = data_filters[data_filters.columns[data_filters.columns.isin(modes)]].sum(axis=1)
    data_filters = data_filters[mode_sum > 0]

    # check if each row sums to ~100%, if not --> exit with message
    row_sums = data[data.columns[data.columns.isin(modes)]].sum(axis=1)
    row_correct = data[np.isclose(row_sums, 100, atol=0.005)]
    if len(row_correct) != len(data):
        print('Some rows do NOT sum to 100% - check the input data!')
        exit(1)

    row_sums = data_filters[data_filters.columns[data_filters.columns.isin(modes)]].sum(axis=1)
    row_correct = data_filters[np.isclose(row_sums, 100, atol=0.005)]
    if len(row_correct) != len(data_filters):
        print('Some rows do NOT sum to 100% - check the input data!')
        exit(1)

    # add up transition modes to their corresponding 'normal' modes if present
    if data.columns.str.contains('transition').any():
        for mode in modes_without_transition:
            try:
                data[mode] = data[mode] + data[f'transition_{mode}']
            except KeyError:
                continue

    if data_filters.columns.str.contains('transition').any():
        for mode in modes_without_transition:
            try:
                data_filters[mode] = data_filters[mode] + data_filters[f'transition_{mode}']
            except KeyError:
                continue

    # data_info = data[['route_nr', 'lower', 'upper', 'walk', 'bike', 'car', 'bus', 'tram', 'subway', 'train']]
    data['route_nr'] = data['route_nr'].astype(str) + '_' + data['OD'].astype(str)
    data_filters['route_nr'] = data_filters['route_nr'].astype(str) + '_' + data_filters['OD'].astype(str)

    # now I want to have only the roytes that are common in data and data_filters
    common_routes = set(data['route_nr']).intersection(set(data_filters['route_nr']))

    data = data[data['route_nr'].isin(common_routes)]
    data_filters = data_filters[data_filters['route_nr'].isin(common_routes)]

    # This part is only if I want to keep the affected routes !
    mode_cols = [col for col in modes if col in data.columns and col in data_filters.columns]

    data.set_index('route_nr', inplace=True)
    data_filters.set_index('route_nr', inplace=True)

    # compare each row between data and data_filters
    # Keep only rows where at least one mode has changed
    mask_changed = (data[mode_cols] != data_filters[mode_cols]).any(axis=1)

    # filter both 
    data = data[mask_changed].copy()
    data_filters = data_filters[mask_changed].copy()
    print("Original number of routes: ", len(common_routes))
    print(f"Number of routes without changes: {len(common_routes) - len(data)}")
    print(f"Number of routes with changes: {len(data)}")
    print(f"Percentage of routes with changes: {len(data) / len(common_routes) * 100:.2f}%")
    data.head(10)

    def make_barchart(df, od_pairs, modes, colors_inner, title_suffix, ax):
        # merge with od_pairs
        df_info = pd.merge(df, od_pairs, how='inner', on='route_nr')

        # group by length category
        mean_pct = (df_info[df_info.columns[df_info.columns.isin(modes + ['lower', 'upper'])]]
            .groupby(['lower', 'upper']).mean().reset_index())
        count_by_category = (df_info.groupby(['lower', 'upper'])
            .size().reset_index(name='count'))

        # TOTAL row
        total_row = df_info[modes].mean().to_frame().T
        total_row['lower'] = df_info['lower'].min()
        total_row['upper'] = df_info['upper'].max()
        total_row = total_row[mean_pct.columns]
        mean_pct = pd.concat([mean_pct, total_row], ignore_index=True)

        count_by_category.loc[len(count_by_category)] = [
            df_info['lower'].min(),df_info['upper'].max(),
            count_by_category['count'].sum()]

        x_labels = [
            f"{int(row['lower'])//1000}-{int(row['upper'])//1000}"
            for _, row in mean_pct.iterrows()]
        x_labels = x_labels[:-1] + ['total']
        counts = count_by_category['count'].tolist()
        new_labels = [f"{lbl}\n({int(cnt)})" for lbl, cnt in zip(x_labels, counts)]

    # ---- CALCULATE MEAN SHARE PER GROUP ----
    group_definitions = { 'Walk': ['walk'], 'Bike': ['bike'], 'PT': PT_modes}

    results = []

    for group_name, group_cols in group_definitions.items():
        
        # Keep only those columns that exist in both dataframes
        cols = [c for c in group_cols if c in data.columns and c in data_filters.columns]
        if len(cols) == 0:
            continue  # nothing to compare

        scenario_mean = data[cols].sum(axis=1).mean()
        filters_mean = data_filters[cols].sum(axis=1).mean()
        diff = scenario_mean - filters_mean

        results.append({
            'group': group_name,
            'scenario_mean': scenario_mean,
            'filters_mean': filters_mean,
            'difference': diff,
            'change': 'increased' if diff > 0 else
                    'decreased' if diff < 0 else
                    'no change' })

    df_change = pd.DataFrame(results)
    # print(df_change)

    def compute_overall_mean_time(df, od_pairs, time_col):
        df_info = pd.merge(df, od_pairs, how='inner', on='route_nr')
        return df_info[time_col].mean()

    # Compute mean overall time (Scenario vs Filters)
    mean_time_scenario = compute_overall_mean_time(data, od_pairs, "sum_time_for_time")
    mean_time_filters  = compute_overall_mean_time(data_filters, od_pairs, "sum_time_for_time")

    # Absolute Δ time
    delta_time = mean_time_scenario - mean_time_filters

    # Percent Δ time (relative change)
    percent_delta = (delta_time / mean_time_scenario) * 100

    print("---- Overall Time Summary ----")
    print(f"Percent Δ Time: {percent_delta:.2f}%")

    #LENGTHH !
    # Compute mean overall time (Scenario vs Filters)
    mean_len_scenario = compute_overall_mean_time(data, od_pairs, "sum_length_for_time")
    mean_len_filters  = compute_overall_mean_time(data_filters, od_pairs, "sum_length_for_time")

    # Absolute Δ time
    delta_len = mean_len_scenario -mean_len_filters

    # Percent Δ time (relative change)
    percent_delta = (delta_len / mean_len_scenario) * 100

    print("---- Overall Length Summary ----")
    print(f"Percent Δ Length: {percent_delta:.2f}%")
# %%

