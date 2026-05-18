import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.interpolate import griddata
import plotly.graph_objects as go
import pdb
import numpy as np

def select_tissue_values(df, tissue_name):
    return df[df['Tissue'] == tissue_name][['Z_eff', 'RED', 'SPR']]

def find_closest_row(df, value):
    return df.iloc[(df['Z_eff mean'] - value).abs().argsort()[:3]]

# Function to read the xlsx file and plot 3D surface with interpolated values and a reference point
def plot_3d_surface_with_reference(cal_mat_file_path, ref_file_path, filament, ref_tissue, save_plot):
    # Read the xlsx file
    df = pd.read_excel(cal_mat_file_path, engine='openpyxl') 
    ref = pd.read_excel(ref_file_path, engine='openpyxl')
    

    # Drop rows with non-numeric values in 'Flow', 'Infill', or 'RED' columns
    df = df[pd.to_numeric(df['Flow'], errors='coerce').notnull()]
    df = df[pd.to_numeric(df['Infill'], errors='coerce').notnull()]
    df = df[pd.to_numeric(df['RED'], errors='coerce').notnull()]

    # Convert columns to numeric
    df['Flow'] = pd.to_numeric(df['Flow'])
    df['Infill'] = pd.to_numeric(df['Infill'])
    df['RED'] = pd.to_numeric(df['RED'])

    # Select the range of rows to analyze
    df_range = df[df.iloc[:, 0] == filament]
    
    # Extract the columns for flow, infill, and RED values
    flow = df_range['Flow']
    infill = df_range['Infill']
    red_values = df_range['RED']
    # pdb.set_trace()
    reference_values = select_tissue_values(ref, ref_tissue)
    ref_red = reference_values['RED'].iloc[0]
    ref_zeff =  reference_values['Z_eff'].iloc[0]


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
    fig = go.Figure(data=[go.Surface(z=red_values_grid, x=flow_grid, y=infill_grid, colorscale='Viridis', opacity=0.7)])
    
    # Add a scatter point for the reference RED value
    fig.add_trace(go.Scatter3d(x=[ref_flow], y=[ref_infill], z=[ref_red], mode='markers', marker=dict(size=5, color='red')))

    # Set labels
    fig.update_layout(
        title= "RED:" + filament + "reference point:" + ref_tissue,
        scene=dict(
            xaxis_title='Flow',
            yaxis_title='Infill',
            zaxis_title='RED'
        )
    )
    if save_plot == True:
        # Save the interactive plot as an HTML file
        fig.write_html("interactive_3d_plot"+ ref_tissue+filament+".html")
        print(print("The interactive 3D plot has been saved as:" "interactive_3d_plot"+ref_tissue+filament+".html"))

    return [ref_flow, ref_infill, ref_red, ref_zeff, red_values_grid[closest_point_index]]



if __name__ == "__main__":

    # Example usage
    cal_mat_file_path = r'C:\Users\tim.stassen\OneDrive - Maastro\Desktop\RED_calibration_matrix_structured.xlsx'
    ref_file_path = r'C:\Users\tim.stassen\OneDrive - Maastro\Documents\ICRU44_reference_metrics.xlsx'
    filament = 'PolyLite PLA white' #'PolyLite ASA Galaxy Red' #'PolySonic PLA grey'
    # start_row = 36  # Replace with the starting row index
    # end_row = 53   # Replace with the ending row index
    reference_tissue =  'Adipose Tissue'
    # reference_red = 1.042  # Reference RED value
    save_plot = False
    ref_flow, ref_infill, ref_red, ref_zeff, found_red, found_Zeff = plot_3d_surface_with_reference(cal_mat_file_path, ref_file_path, filament, reference_tissue, save_plot)
    print('\n Tissue:', reference_tissue, '\t Z_eff:', ref_zeff, '\t RED:', ref_red,
        '\n Filament:', filament, '\n Flow:', ref_flow, '\t Infill:', ref_infill, '\t closest material RED:', "%.3f" % found_red, 'Z_eff filament:' '\n')