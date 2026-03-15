#%%
import os
import copy
import pickle
import pandas as pd
import geopandas as gpd
import networkx as nx
import pyproj
from helpers.functions_for_percentages import *
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
from constants.categories import weight, ranges, custom_order, columns_to_average

source = os.getcwd()

scenario_names = ["nofilters",  "transitions", "filters"]

#%%
print("Sorting CSV files by route_nr started ")
# sort files by 'route_nr' per scenario 
results_folder = os.path.abspath(os.path.join(source, '..', 'results','vienna'))
folders = [f for f in os.listdir(results_folder) if os.path.isdir(os.path.join(results_folder, f))]
# sort the files in each folder by 'route_nr'
for folder in folders:
    folder_path = os.path.join(results_folder, folder,'MultiGraph_walk_bike_PT')
    subfolders = [item for item in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, item))]
    if subfolders:
        print(f"There are folders inside the current folder: {subfolders}")
        
        for subfolder in subfolders:
            sub_routes = []
            subfolder_path = os.path.join(folder_path, subfolder)
            csv_files = [f for f in os.listdir(subfolder_path) if f.endswith('.csv')]
            
            for file in csv_files:
                file_path = os.path.join(subfolder_path, file)
                
                df = pd.read_csv(file_path)
                
                if 'route_nr' in df.columns:
                    # sort 'route_nr'
                    df = df.sort_values(by='route_nr', ascending=True)
                    if 'route_nr' in df.columns:
                        sub_routes.extend(df['route_nr'].unique())   

                    # save back to the same file
                    df.to_csv(file_path, index=False)
                    print(f"Sorted and saved: {file} in {subfolder}")
    else:
        print("There are no folders inside the current folder. Proceeding with CSV processing.")
        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        folder_routes = []
        for file in csv_files:
            file_path = os.path.join(folder_path, file)
            
            df = pd.read_csv(file_path)
            
            if 'route_nr' in df.columns:
                # sort 'route_nr'
                df = df.sort_values(by='route_nr', ascending=True)
                folder_routes.extend(df['route_nr'].unique())
            
                # save back to the same file
                df.to_csv(file_path, index=False)
                print(f"Sorted and saved: {file} in {folder}")
            else:
                print(f"Skipping {file} in {folder} (no 'route_nr' column).")

#%%
print(" Unique route_nr processing started")
# create the unique_route_nr file per scenario )
for name in scenario_names:
    if name == 'transitions':
        path = os.path.abspath(os.path.join(source, '..', 'results', 'vienna', name, 'MultiGraph_walk_bike_PT'))
        subfolders = [item for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))]
        for subfolder in subfolders:
            sub_path = os.path.abspath(os.path.join(path, subfolder))
            output_folder = os.path.join(sub_path, f'unique_route_nr_{subfolder}')
            os.makedirs(output_folder, exist_ok=True)

            files = [filename for filename in os.listdir(sub_path) if filename.endswith('.csv')]
            for file in files:
                if file.startswith(weight):
                    df = pd.read_csv(sub_path + '/' + file)
                    
                    # rename transition labels
                    df[f'modes_for_{weight}'] = df[f'modes_for_{weight}'].apply(rename_transition_labels)

                    df['OD'] = df[f'osm_ids_for_{weight}'].apply(lambda x: f'{x.split(";")[0]}-{x.split(";")[-1]}')

                    for mode in custom_order:
                        # % length for each mode
                        df[f'{mode}_length_perc'] = df.apply(
                            lambda row: calculate_mode_percentage(row[f'modes_for_{weight}'], row[f'lengths_for_{weight}'], mode),
                            axis=1
                        )
                        # % time for each mode
                        df[f'{mode}_time_perc'] = df.apply(
                            lambda row: calculate_mode_percentage(row[f'modes_for_{weight}'], row[f'times_for_{weight}'], mode),
                            axis=1
                        )

                grouped_df = df.groupby(['route_nr', 'OD'])[columns_to_average].mean().reset_index()

                length_range = file.split('_')[-1].replace('.csv', '')

                # Construct output file name
                output_file_name = f'{weight}_{length_range}.csv'
                output_file_path = os.path.join(output_folder, output_file_name)

                # Save grouped DataFrame
                grouped_df.to_csv(output_file_path, index=False)
                print(f'Processed and saved: {output_file_path}')

    
    else:
        path = os.path.abspath(os.path.join(source, '..', 'results', 'vienna', name, 'MultiGraph_walk_bike_PT'))

        output_folder = os.path.join(path, f'unique_route_nr_{name}')
        os.makedirs(output_folder, exist_ok=True)

        files = [filename for filename in os.listdir(path) if filename.endswith('.csv')]

        for file in files:
            if file.startswith(weight):
                df = pd.read_csv(path + '/' + file)

                # rename transition labels
                df[f'modes_for_{weight}'] = df[f'modes_for_{weight}'].apply(rename_transition_labels)

                df['OD'] = df[f'osm_ids_for_{weight}'].apply(lambda x: f'{x.split(";")[0]}-{x.split(";")[-1]}')

                for mode in custom_order:
                    # % length for each mode
                    df[f'{mode}_length_perc'] = df.apply(
                        lambda row: calculate_mode_percentage(row[f'modes_for_{weight}'], row[f'lengths_for_{weight}'], mode),
                        axis=1 )
                    # % time for each mode
                    df[f'{mode}_time_perc'] = df.apply(
                        lambda row: calculate_mode_percentage(row[f'modes_for_{weight}'], row[f'times_for_{weight}'], mode),
                        axis=1)

            grouped_df = df.groupby(['route_nr', 'OD'])[columns_to_average].mean().reset_index()

            length_range = file.split('_')[-1].replace('.csv', '')

            # Construct output file name
            output_file_name = f'{weight}_{length_range}.csv'
            output_file_path = os.path.join(output_folder, output_file_name)

            # Save grouped DataFrame
            grouped_df.to_csv(output_file_path, index=False)
            print(f'Processed and saved: {output_file_path}')

# %%

