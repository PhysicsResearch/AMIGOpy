import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.interpolate import griddata
import plotly.graph_objects as go
import pdb

def select_tissue_values(df, tissue_name):
    return df[df['Tissue'] == tissue_name][['Z_eff', 'RED', 'SPR']]

def find_closest_row(df, value):
    return df.iloc[(df['Z_eff mean'] - value).abs().argsort()[:3]]

def find_best_matching_filament(tissue_file_path, filament_file_path, tissue):
    # Read the xlsx file
    tissues = pd.read_excel(tissue_file_path, engine='openpyxl')
    filament = pd.read_excel(filament_file_path, engine='openpyxl')
    # pdb.set_trace()
    tissue_values = select_tissue_values(tissues, tissue)
    z_eff_tissue = tissue_values['Z_eff'].iloc[0]

    closest_filaments = find_closest_row(filament, z_eff_tissue)
    print('Tissue:', tissue, '\t', 'Z_eff: \t'"%.3f" % z_eff_tissue, '\n')
    print(closest_filaments)
    # pdb.set_trace()


if __name__ == "__main__":

    tissue_file_path = r'C:\Users\tim.stassen\OneDrive - Maastro\Documents\ICRU44_reference_metrics.xlsx'
    filament_file_path = r'C:\Users\tim.stassen\OneDrive - Maastro\Documents\Filament_metrics.xlsx'
    tissue = 'Adipose Tissue'
    find_best_matching_filament(tissue_file_path, filament_file_path, tissue)



