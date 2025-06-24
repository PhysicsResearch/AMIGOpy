import pandas as pd
import sys

def load_csv_to_variables(csv_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Sort the DataFrame if needed
    # df = df.sort_values(by=df.columns[0])
    
    # Dynamically create variables from columns
    for column in df.columns:
        globals()[column] = df[column].to_numpy()

if __name__ == "__main__":
    csv_file_path = sys.argv[1]
    load_csv_to_variables(csv_file_path)