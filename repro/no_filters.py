#%%
import os 
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from constants.categories import mode_groups_1
from matplotlib.cbook import boxplot_stats
from helpers.functions_for_percentages import rename_transition_labels
from constants.tools import colors_inner, rename_dict, modes_without_transition

source = os.getcwd()
results_folder = os.path.abspath(os.path.join(source, '..', 'results','vienna'))
output_folder = os.path.join(os.path.join(source, '..', 'plots'))
os.makedirs(output_folder, exist_ok=True)

folders = [f for f in os.listdir(results_folder) if os.path.isdir(os.path.join(results_folder, f))]
modes = ['walk', 'bike', 'bus', 'tram', 'subway', 'train'] 

#%%
for folder in folders:
    if folder == 'filters':
        continue
    folder_path = os.path.join(results_folder, folder,'MultiGraph_walk_bike_PT')
    subfolders = [item for item in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, item))]
    
    filter_path = os.path.join(results_folder, 'filters', 'MultiGraph_walk_bike_PT', 'unique_route_nr_filters' )
    filter_csv_files = [f for f in os.listdir(filter_path) if f.endswith('.csv')]

    for i,subfolder in enumerate(subfolders):
        if not subfolder.startswith('unique'):
            subfolder_path = os.path.join(folder_path,subfolders[i])
            sub_sub_folder =  [item for item in os.listdir(subfolder_path) if os.path.isdir(os.path.join(subfolder_path, item))]
            for inner in sub_sub_folder:
                sub_sub_folder_path = os.path.join(subfolder_path, inner)
                csv_inner = [f for f in os.listdir(sub_sub_folder_path) if f.endswith('.csv')]

                df_common_scen = []
                df_common_filters = []

                for csv in csv_inner:
                    df_inner = pd.read_csv(os.path.join(sub_sub_folder_path, csv))
                    if 'route_nr' not in df_inner.columns:
                        raise ValueError(f"'route_nr' column missing in file {csv}")

                    scen_routes = set(df_inner['route_nr'].unique())

                    df_filters = pd.read_csv(os.path.join(filter_path, csv))
                    if 'route_nr' not in df_filters.columns:
                        raise ValueError(f"'route_nr' column missing in file {csv}")

                    filter_routes = set(df_filters['route_nr'].unique())

                    common = scen_routes.intersection(filter_routes)

                    df_common_scen.append(df_inner[df_inner['route_nr'].isin(common)])
                    df_common_filters.append(df_filters[df_filters['route_nr'].isin(common)])
                
                # Combine all CSVs into one DataFrame
                df_scen = pd.concat(df_common_scen, ignore_index=True)
                df_filters = pd.concat(df_common_filters, ignore_index=True)

                key_cols = ['route_nr', 'OD']

                merged = df_scen.merge( df_filters, on=key_cols,
                    how='inner', suffixes=('_scen', '_filter'))

                # Columns that must be different or checked
                other_cols = [c for c in df_scen.columns if c not in key_cols]

                differences = {}

                for col in other_cols:
                    col_s = col + '_scen'
                    col_f = col + '_filter'

                    diffs = merged[merged[col_s] != merged[col_f]]

                    if not diffs.empty:
                        differences[col] = diffs
                
                if len(differences) == 0:
                    print("All non-key columns match for every (route_nr, OD).")

                # Merge columns (main + transition)
                for mode, submodes in mode_groups_1.items():
                    cols = [f"{s}_time_perc" for s in submodes if f"{s}_time_perc" in df_scen.columns]
                    if cols:
                        df_scen[f"{mode}_merged_time_perc"] = df_scen[cols].sum(axis=1)
                
                for mode, submodes in mode_groups_1.items():
                    cols = [f"{s}_time_perc" for s in submodes if f"{s}_time_perc" in df_filters.columns]
                    if cols:
                        df_filters[f"{mode}_merged_time_perc"] = df_filters[cols].sum(axis=1)

                # Use only merged columns that exist
                merged_cols_scenario = [f"{m}_merged_time_perc" for m in modes if f"{m}_merged_time_perc" in df_scen.columns]
                merged_cols_filters = [f"{m}_merged_time_perc" for m in modes if f"{m}_merged_time_perc" in df_filters.columns]

                if merged_cols_scenario:
                    # Check that rows sum to 100% (±1%)
                    df_scen['total_perc'] = df_scen[merged_cols_scenario].sum(axis=1)
                    invalid = df_scen[~df_scen['total_perc'].between(99, 101)]

                    if len(invalid) > 0:
                        print(f" {len(invalid)} rows in scenario {subfolders[i]} do not sum to 100%. Mean = {df_scen['total_perc'].mean():.2f}%")

                    # aggregated mean per mode
                    avg_mode_perc = df_scen[merged_cols_scenario].mean()

                    mode_labels = [c.replace('_merged_time_perc', '') for c in merged_cols_scenario]
                
                if merged_cols_filters:
                    # Check that rows sum to 100% (±1%)
                    df_filters['total_perc'] = df_filters[merged_cols_filters].sum(axis=1)
                    invalid = df_filters[~df_filters['total_perc'].between(99, 101)]

                    if len(invalid) > 0:
                        print(f" {len(invalid)} rows in FILTERS {subfolders[i]} do not sum to 100%. Mean = {df_filters['total_perc'].mean():.2f}%")

                if merged_cols_scenario and merged_cols_filters:
                    pairs_scen = df_scen[['route_nr', 'OD']]
                    pairs_filters = df_filters[['route_nr', 'OD']]

                    # Detect duplicates BEFORE drop
                    dup_scen = pairs_scen[pairs_scen.duplicated()]
                    dup_filters = pairs_filters[pairs_filters.duplicated()]

                    if not dup_scen.empty:
                        print(f"[Scenario] WARNING: {len(dup_scen)} duplicate (route_nr, OD) pairs:")
                        print(dup_scen.drop_duplicates().to_string(index=False))

                    if not dup_filters.empty:
                        print(f"[Filters] WARNING: {len(dup_filters)} duplicate (route_nr, OD) pairs:")
                        print(dup_filters.drop_duplicates().to_string(index=False))

                    # Compute unique counts
                    unique_scen = pairs_scen.drop_duplicates()
                    unique_filters = pairs_filters.drop_duplicates()

                    n_common_routes_scen = unique_scen.shape[0]
                    n_common_routes_filters = unique_filters.shape[0]

                    if n_common_routes_scen != n_common_routes_filters:
                        print(" WARNING: Scenario and Filters have different numbers of OD-route combinations!")

                    print(f"{folder} - {inner}")
                    print(f"Scenario unique: {n_common_routes_scen}, Filters unique: {n_common_routes_filters}")

                    # Compute averages
                    avg_scen = df_scen[merged_cols_scenario].mean()
                    avg_filters = df_filters[merged_cols_filters].mean()

                    # Mode labels
                    mode_labels = [c.replace("_merged_time_perc", "") for c in merged_cols_scenario]

        else: 
            subfolder_path = os.path.join(folder_path,subfolders[i])
            csv_inner = [f for f in os.listdir(subfolder_path) if f.endswith('.csv')]

            df_common_scen = []
            df_common_filters = []

            for csv in csv_inner:
                df_inner = pd.read_csv(os.path.join(subfolder_path, csv))
                if 'route_nr' not in df_inner.columns:
                    raise ValueError(f"'route_nr' column missing in file {csv}")

                scen_routes = set(df_inner['route_nr'].unique())

                df_filters = pd.read_csv(os.path.join(filter_path, csv))
                if 'route_nr' not in df_filters.columns:
                    raise ValueError(f"'route_nr' column missing in file {csv}")

                filter_routes = set(df_filters['route_nr'].unique())

                common = scen_routes.intersection(filter_routes)

                df_common_scen.append(df_inner[df_inner['route_nr'].isin(common)])
                df_common_filters.append(df_filters[df_filters['route_nr'].isin(common)])
            
            # Combine all CSVs into one DataFrame
            df_scen = pd.concat(df_common_scen, ignore_index=True)
            df_filters = pd.concat(df_common_filters, ignore_index=True)

            key_cols = ['route_nr', 'OD']

            merged = df_scen.merge( df_filters,  on=key_cols, how='inner', suffixes=('_scen', '_filter'))

            # Columns that must be different or checked
            other_cols = [c for c in df_scen.columns if c not in key_cols]

            differences = {}

            for col in other_cols:
                col_s = col + '_scen'
                col_f = col + '_filter'

                diffs = merged[merged[col_s] != merged[col_f]]

                if not diffs.empty:
                    differences[col] = diffs
            
            if len(differences) == 0:
                print("All non-key columns match for every (route_nr, OD).")
            
            # Merge columns (main + transition)
            for mode, submodes in mode_groups_1.items():
                cols = [f"{s}_time_perc" for s in submodes if f"{s}_time_perc" in df_scen.columns]
                if cols:
                    df_scen[f"{mode}_merged_time_perc"] = df_scen[cols].sum(axis=1)
            
            for mode, submodes in mode_groups_1.items():
                cols = [f"{s}_time_perc" for s in submodes if f"{s}_time_perc" in df_filters.columns]
                if cols:
                    df_filters[f"{mode}_merged_time_perc"] = df_filters[cols].sum(axis=1)

            # Use only merged columns that exist
            merged_cols_scenario = [f"{m}_merged_time_perc" for m in modes if f"{m}_merged_time_perc" in df_scen.columns]
            merged_cols_filters = [f"{m}_merged_time_perc" for m in modes if f"{m}_merged_time_perc" in df_filters.columns]

            if merged_cols_scenario:
                # Check that rows sum to 100% (±1%)
                df_scen['total_perc'] = df_scen[merged_cols_scenario].sum(axis=1)
                invalid = df_scen[~df_scen['total_perc'].between(99, 101)]

                if len(invalid) > 0:
                    print(f" {len(invalid)} rows in scenario {subfolders[i]} do not sum to 100%. Mean = {df_scen['total_perc'].mean():.2f}%")

                # aggregated mean per mode
                avg_mode_perc = df_scen[merged_cols_scenario].mean()

                mode_labels = [c.replace('_merged_time_perc', '') for c in merged_cols_scenario]
            
            if merged_cols_filters:
                # Check that rows sum to 100% (±1%)
                df_filters['total_perc'] = df_filters[merged_cols_filters].sum(axis=1)
                invalid = df_filters[~df_filters['total_perc'].between(99, 101)]

                if len(invalid) > 0:
                    print(f" {len(invalid)} rows in FILTERS {subfolders[i]} do not sum to 100%. Mean = {df_filters['total_perc'].mean():.2f}%")

            if merged_cols_scenario and merged_cols_filters:
                pairs_scen = df_scen[['route_nr', 'OD']]
                pairs_filters = df_filters[['route_nr', 'OD']]

                # Detect duplicates BEFORE drop
                dup_scen = pairs_scen[pairs_scen.duplicated()]
                dup_filters = pairs_filters[pairs_filters.duplicated()]

                if not dup_scen.empty:
                    print(f"[Scenario] WARNING: {len(dup_scen)} duplicate (route_nr, OD) pairs:")
                    print(dup_scen.drop_duplicates().to_string(index=False))

                if not dup_filters.empty:
                    print(f"[Filters] WARNING: {len(dup_filters)} duplicate (route_nr, OD) pairs:")
                    print(dup_filters.drop_duplicates().to_string(index=False))

                # Compute unique counts
                unique_scen = pairs_scen.drop_duplicates()
                unique_filters = pairs_filters.drop_duplicates()

                n_common_routes_scen = unique_scen.shape[0]
                n_common_routes_filters = unique_filters.shape[0]

                if n_common_routes_scen != n_common_routes_filters:
                    print(" WARNING: Scenario and Filters have different numbers of OD-route combinations!")
                print(f"{folder} ")
                print(f"Scenario unique: {n_common_routes_scen}, Filters unique: {n_common_routes_filters}")
    
                # Compute averages
                avg_scen = df_scen[merged_cols_scenario].mean()
                avg_filters = df_filters[merged_cols_filters].mean()

                # Mode labels
                mode_labels = [c.replace("_merged_time_perc", "") for c in merged_cols_scenario]

                # Combine averages into one DataFrame for plotting
                df_plot = pd.DataFrame({ 'Mode': mode_labels, 'Fastest Path': avg_scen.values, 'Average Thresholds': avg_filters.values })

                # Set bar width and positions
                bar_width = 0.35
                x = np.arange(len(mode_labels))

                fig, ax = plt.subplots(figsize=(12, 6))

                # Scenario bars
                ax.bar(x - bar_width/2, df_plot['Fastest Path'], width=bar_width, label='Fastest Path', color="#E0A36A")

                # Filters bars
                ax.bar(x + bar_width/2, df_plot['Average Thresholds'], width=bar_width, label='Average Thresholds', color="#9A7FA0")

                for i in range(len(mode_labels)):
                    ax.text(x[i] - bar_width/2, df_plot['Fastest Path'][i] + 1, f"{df_plot['Fastest Path'][i]:.1f}%", 
                            ha='center', fontweight='bold')
                    ax.text(x[i] + bar_width/2, df_plot['Average Thresholds'][i] + 1, f"{df_plot['Average Thresholds'][i]:.1f}%", 
                            ha='center', fontweight='bold')

                # Labels, title, legend
                ax.set_xticks(x)
                ax.set_xticklabels(mode_labels)
                ax.set_ylabel("Modal Split Percentages")
                ax.set_xlabel("Modes")
                ax.set_title(f"Modal Split Comparison – {n_common_routes_scen} Common Routes")
                max_value = df_plot.select_dtypes(include=np.number).max().max()
                ax.set_ylim(0, max_value + 10)
                ax.legend()

                plt.tight_layout()
                plt.savefig(os.path.join(output_folder, f'modal_split_Pure_Fastest_Path_filters.png'), dpi=300)
                plt.show()
# %%
