# 
import pandas as pd
import tkinter as tk
from tkinter import filedialog


ATOMIC_NUMBER_TO_SYMBOL = {
    1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne',
    11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar', 19: 'K', 20: 'Ca',
    21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe', 27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn',
    31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr', 37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr',
    41: 'Nb', 42: 'Mo', 43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd', 47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn',
    51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe', 55: 'Cs', 56: 'Ba', 57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd',
    61: 'Pm', 62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy', 67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb',
    71: 'Lu', 72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt', 79: 'Au', 80: 'Hg',
    81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Th', 85: 'At', 86: 'Rn', 87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th',
    91: 'Pa', 92: 'U', 93: 'Np', 94: 'Pu', 95: 'Am', 96: 'Cm', 97: 'Bk', 98: 'Cf', 99: 'Es', 100: 'Fm',
    101: 'Md', 102: 'No', 103: 'Lr', 104: 'Rf', 105: 'Db', 106: 'Sg', 107: 'Bh', 108: 'Hs', 109: 'Mt', 110: 'Ds',
    111: 'Rg', 112: 'Cn', 113: 'Nh', 114: 'Fl', 115: 'Mc', 116: 'Lv', 117: 'Ts', 118: 'Og'
}

def create_dataframe(self):
    # Open file dialog to select a CSV file
    root = tk.Tk()
    root.withdraw()  # Preventing the root window from appearing
    filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")]) 
    data = []
    additional_tags = ['Den', 'RED', 'Zeff', 'I', 'SPR','HUlow','HUhigh']
    all_columns = set(additional_tags)
    
    lb=0
    with open(filename, 'r') as file:
        for line in file:
            if not line.startswith('#'):
                data.append(line.strip().split(','))
            elif line.startswith('#') and lb==0:
                self.mat_table_label.setText(line.strip())
                lb=1

    rows_list = []
    for row in data:
        row_data = {'Name': row[0]}
        i = 1
        while i < len(row):
            key = row[i].strip()
            if key.isdigit():
                atomic_number = int(key)
                symbol = ATOMIC_NUMBER_TO_SYMBOL.get(atomic_number, str(atomic_number))
                all_columns.add(symbol)
                mass_fraction = float(row[i + 1])
                row_data[symbol] = mass_fraction
                i += 2
            else:
                tag = key
                if i + 1 < len(row):
                    value = float(row[i + 1]) if row[i + 1].replace('.', '', 1).isdigit() else row[i + 1]
                    row_data[tag] = value
                i += 2
        rows_list.append(row_data)

    # Sorting columns by atomic number
    column_order = ['Name'] + sorted(
        [col for col in all_columns if col not in additional_tags + ['Name']],
        key=lambda x: list(ATOMIC_NUMBER_TO_SYMBOL.values()).index(x) if x in ATOMIC_NUMBER_TO_SYMBOL.values() else float('inf')
    ) + [col for col in additional_tags if col in all_columns]

    df = pd.DataFrame(rows_list, columns=column_order)
    df.fillna(0, inplace=True)
    return df


if __name__ == '__main__':
    df = create_dataframe()
    print(df)


