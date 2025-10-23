import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.interpolate import griddata
# import plotly.graph_objects as go
import pdb
import numpy as np

def give_tissues(tissue_file_path):
    human_tissues = pd.read_excel(tissue_file_path, engine='openpyxl')
    return human_tissues['Tissue'].tolist()

def select_tissue_values(df, tissue_name):
    return df[df['Tissue'] == tissue_name][['Z_eff', 'RED', 'SPR']]

def find_closest_rows(df, value):
    return df.iloc[(df['Z_eff mean'] - value).abs().argsort()[:12]]

def find_best_matching_filament(tissue_file_path, filament_file_path, tissue):
    # Read the xlsx file
    tissues = pd.read_excel(tissue_file_path, engine='openpyxl')
    filament = pd.read_excel(filament_file_path, engine='openpyxl')
    # pdb.set_trace()
    tissue_values = select_tissue_values(tissues, tissue)
    z_eff_tissue = tissue_values['Z_eff'].iloc[0]
    red_tissue = tissue_values['RED'].iloc[0]
    # pdb.set_trace()
    closest_filaments = find_closest_rows(filament, z_eff_tissue)
    # print('Tissue:', tissue, '\t', 'Z_eff: \t'"%.3f" % z_eff_tissue, '\n')
    # print(closest_filaments)
    return {'closest filaments': closest_filaments, 
            'zeff': z_eff_tissue, 
            'red': red_tissue}

def RED_or_RED_and_infill(input1, input2, cal_mat_file_path, ref_file_path, filament, ref_tissue):
    if input1 == 'Flow and Infill':
        values = determine_RED_settings(cal_mat_file_path, ref_file_path, filament, ref_tissue)
    elif input1 == 'Flow' and input2 == 'Extrapolate':
        values = determine_RED_settings_flow_only(cal_mat_file_path, ref_file_path, filament, ref_tissue, extrapolate=True)
    elif input1 == 'Flow' and input2 == 'No':
        values = determine_RED_settings_flow_only(cal_mat_file_path, ref_file_path, filament, ref_tissue, extrapolate=False)
    return values

# Function to read the xlsx file and plot 3D surface with interpolated values and a reference point
def determine_RED_settings(cal_mat_file_path, ref_file_path, filament, ref_tissue):
    # Read the xlsx file
    df = pd.read_excel(cal_mat_file_path, engine='openpyxl') 
    ref = pd.read_excel(ref_file_path, engine='openpyxl')
    

    # Drop rows with non-numeric values in 'Flow', 'Infill', or 'RED' columns
    df = df[pd.to_numeric(df['Flow'], errors='coerce').notnull()]
    df = df[pd.to_numeric(df['Infill'], errors='coerce').notnull()]
    df = df[pd.to_numeric(df['RED mean'], errors='coerce').notnull()]

    # Convert columns to numeric
    df['Flow'] = pd.to_numeric(df['Flow'])
    df['Infill'] = pd.to_numeric(df['Infill'])
    df['RED'] = pd.to_numeric(df['RED mean'])

    # Select the range of rows to analyze
    df_range = df[df.iloc[:, 0] == filament]
    
    # Extract the columns for flow, infill, and RED values
    flow = df_range['Flow']
    infill = df_range['Infill']
    red_values = df_range['RED mean']
    zeff_values = df_range['Z_eff mean']
    # pdb.set_trace()
    cal_mat_mean_zeff = zeff_values.mean()
    # pdb.set_trace()
    reference_values = select_tissue_values(ref, ref_tissue)
    
    ref_red = reference_values['RED'].iloc[0]
    ref_zeff = reference_values['Z_eff'].iloc[0]


    # Create a grid for the surface plot with steps of 1
    flow_grid, infill_grid = np.meshgrid(np.arange(flow.min(), flow.max() + 1, 1),
                                         np.arange(infill.min(), infill.max() + 1, 1))

    # Interpolate the RED values to fit the grid
    red_values_grid = griddata((flow, infill), red_values, (flow_grid, infill_grid), method='linear')
    # pdb.set_trace()
    # Find the point where RED value is closest to the reference RED value
    closest_point_index = np.unravel_index(np.nanargmin(np.abs(red_values_grid - ref_red)), red_values_grid.shape)
    ref_flow = flow_grid[closest_point_index]
    ref_infill = infill_grid[closest_point_index]
    
    # pdb.set_trace()
    # Create a 3D plot using Plotly
    # fig = go.Figure(data=[go.Surface(z=red_values_grid, x=flow_grid, y=infill_grid, colorscale='Viridis', opacity=0.7)])
    
    # # Add a scatter point for the reference RED value
    # fig.add_trace(go.Scatter3d(x=[ref_flow], y=[ref_infill], z=[ref_red], mode='markers', marker=dict(size=5, color='red')))

    # # Set labels
    # fig.update_layout(
    #     title= "RED:" + filament + "reference point:" + ref_tissue,
    #     scene=dict(
    #         xaxis_title='Flow',
    #         yaxis_title='Infill',
    #         zaxis_title='RED'
    #     )
    # )
    # if save_plot == True:
    #     # Save the interactive plot as an HTML file
    #     fig.write_html("interactive_3d_plot"+ ref_tissue+filament+".html")
    #     print(print("The interactive 3D plot has been saved as:" "interactive_3d_plot"+ref_tissue+filament+".html"))

        

    return {'found_flow': ref_flow, 
            'found_infill': ref_infill, 
            'reference_red':ref_red,
            'reference_zeff': ref_zeff, 
            'found_red':red_values_grid[closest_point_index], 
            'mean_zeff':cal_mat_mean_zeff}


# Function to read the xlsx file and plot 3D surface with interpolated values and a reference point
def determine_RED_settings_flow_only(cal_mat_file_path, ref_file_path, filament, ref_tissue, extrapolate):
    # Read the xlsx file
    df = pd.read_excel(cal_mat_file_path, engine='openpyxl') 
    ref = pd.read_excel(ref_file_path, engine='openpyxl')
    

    # Drop rows with non-numeric values in 'Flow', 'Infill', or 'RED' columns
    df = df[pd.to_numeric(df['Flow'], errors='coerce').notnull()]
    # df = df[pd.to_numeric(df['Infill'], errors='coerce').notnull()]
    df = df[pd.to_numeric(df['RED mean'], errors='coerce').notnull()]

    # Convert columns to numeric
    df['Flow'] = pd.to_numeric(df['Flow'])
    # df['Infill'] = pd.to_numeric(df['Infill'])
    df['RED'] = pd.to_numeric(df['RED mean'])

    # Select the range of rows to analyze
    df_range = df[df.iloc[:, 0] == filament]
    df_range_infill_100 = df_range[df_range['Infill'] == 100]
    
    # Extract the columns for flow, infill, and RED values
    flow = df_range_infill_100['Flow']
    infill = df_range_infill_100['Infill']
    
    red_values = df_range_infill_100['RED mean']
    zeff_values = df_range_infill_100['Z_eff mean']
    cal_mat_mean_zeff = zeff_values.mean()
    # pdb.set_trace()
    reference_values = select_tissue_values(ref, ref_tissue)
    
    ref_red = reference_values['RED'].iloc[0]
    ref_zeff = reference_values['Z_eff'].iloc[0]
    # pdb.set_trace()

    flow_steps = np.arange(flow.min(), flow.max() + 1, 1)
    # pdb.set_trace()
    # Reindex the DataFrame to include all flow steps
    df_interp = df_range_infill_100.set_index('Flow').reindex(flow_steps)
    # pdb.set_trace()
    # Interpolate missing values
    df_interp['RED mean'] = df_interp['RED mean'].interpolate()
    # pdb.set_trace()
    if extrapolate == True: 
        x = df_interp.index.values
        y = df_interp['RED mean'].values

        # extra_x = np.arange(x[-1] + 1, x[-1] + 11, 1) # 10 steps extra
        extra_x = np.arange(x[-1] + 1, x[-1] + 5, 1) # 4 extra steps
        coeffs = np.polyfit(x[-2:], y[-2:], 1)
        slope, intercept = coeffs
        extra_y = slope * extra_x + intercept

        df_extra = pd.DataFrame({'Flow': extra_x, 'RED mean': extra_y})
        df_interp = df_interp.reset_index().rename(columns={'index': 'Flow'})
        df_interp = pd.concat([df_interp, df_extra], ignore_index=True)

    else:
        # Reset index to restore the 'Flow' column
        df_interp = df_interp.reset_index().rename(columns={'index': 'Flow'})

    closest_idx = (df_interp['RED mean'] - ref_red).abs().idxmin()
    # pdb.set_trace()
    # Get the corresponding Flow and Value
    closest_flow = df_interp.loc[closest_idx, 'Flow']
    closest_RED = df_interp.loc[closest_idx, 'RED mean']                           
    # pdb.set_trace()
        # print(f"Closest Flow: {closest_flow}, Closest RED: {closest_RED}")
        
    return {'found_flow': closest_flow, 
            'found_red': closest_RED,
            'mean_zeff':cal_mat_mean_zeff,
            'reference_red':ref_red,
            'reference_zeff': ref_zeff,
            }


    # Interpolate the RED values to fit the grid
    # red_values_grid = griddata((flow, infill), red_values, (flow_grid), method='linear')
    # red_values_grid = griddata((flow), red_values, (flow_grid), method='linear')
    # Find the point where RED value is closest to the reference RED value


    # ref_infill = infill_grid[closest_point_index]
    
    # pdb.set_trace()
    # Create a 3D plot using Plotly
    # fig = go.Figure(data=[go.Surface(z=red_values_grid, x=flow_grid, y=infill_grid, colorscale='Viridis', opacity=0.7)])
    
    # Add a scatter point for the reference RED value
    # fig.add_trace(go.Scatter3d(x=[ref_flow], y=[ref_infill], z=[ref_red], mode='markers', marker=dict(size=5, color='red')))

    # Set labels
    # fig.update_layout(
    #     title= "RED:" + filament + "reference point:" + ref_tissue,
    #     scene=dict(
    #         xaxis_title='Flow',
    #         yaxis_title='Infill',
    #         zaxis_title='RED'
    #     )
    # )
    # if save_plot == True:
    #     # Save the interactive plot as an HTML file
    #     fig.write_html("interactive_3d_plot"+ ref_tissue+filament+".html")
    #     print(print("The interactive 3D plot has been saved as:" "interactive_3d_plot"+ref_tissue+filament+".html"))

    # return {'found_flow': closest_flow, 
    #         # 'found_infill': ref_infill, 
    #         'reference_red':ref_red,
    #         'reference_zeff': ref_zeff, 
    #         'found_red':closest_RED, 
    #         'mean_zeff':cal_mat_mean_zeff}

# fcn_3DPrinting/material_selection.py
def calculate_red_settings(input1, input2, cal_mat_path, icru_path, filament, tissue):
    result = RED_or_RED_and_infill(input1, input2, cal_mat_file_path, icru_path, filament, tissue)
    return result

if __name__ == "__main__":

    cal_mat_file_path = r'C:\Users\tim.stassen\OneDrive - Maastro\Desktop\material_selection\Hunemohr\calibration_matrix_values_structured_prusaXL_hunemohr.xlsx'
    tissue_file_path = r'C:\Users\tim.stassen\OneDrive - Maastro\Desktop\material_selection\ICRU44_reference_metrics.xlsx'
    filament = 'Maastro PLA+Ca' #'PolyLite PETG Black'
    tissue = 'Skeleton - cortical bone' #'Adipose Tissue'
    # result = determine_RED_settings(cal_mat_file_path, tissue_file_path, filament, tissue, save_plot=True)
    # print('RED', result['found_red'], '\t flow:', result['found_flow'], '\t infill:', result['found_infill'])
    
    result = determine_RED_settings_flow_only(cal_mat_file_path, tissue_file_path, filament, tissue, extrapolate=True)
    # print('RED', result['found_red'], '\t flow:', result['found_flow'])


