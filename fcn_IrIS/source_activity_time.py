from PyQt5.QtWidgets import QTableWidgetItem
from datetime import datetime
import math

def calculate_time_from_ref(self,channel_name):
    # Reference datetime
    reference_datetime = datetime(2024, 1, 1, 1, 0)  # January 1, 2024, at 1:00 AM
    # Check if ':' exists in the string
    if ':' in channel_name:
        # Extract the date part after the colon
        date_part = channel_name.split(": ")[1]
    else:
        # Use the entire string as the date part
        date_part = channel_name
    # Replace 'h', 'm', and 's' to make it a valid datetime format
    date_part = date_part.replace('h', ':').replace('m', ':').replace('s', '')
    # Define the datetime format for parsing
    format = "%Y-%m-%d_%H:%M:%S"
    # Convert to datetime
    datetime1 = datetime.strptime(date_part, format)
    # Calculate the difference in minutes
    time_delta = datetime1 - reference_datetime
    minutes_since_reference = time_delta.total_seconds() / 60
    #
    return minutes_since_reference
    
  
def update_reference_time_table(self):
    # Iterate over each row in the table
    for row in range(self.Source_Cal_table.rowCount()):
        # Get the date from the first column (assuming it is column index 0)
        date_cell = self.Source_Cal_table.item(row, 0)
        if date_cell:
            try:
                minutes_since_reference = calculate_time_from_ref(self,date_cell.text())
                # Create a new QTableWidgetItem with the calculated minutes
                minutes_item = QTableWidgetItem(str(int(minutes_since_reference)))
                # Set the new item in the 4th column (index 3)
                self.Source_Cal_table.setItem(row, 3, minutes_item)
            except ValueError as e:
                print("Date format error:", e)
                
def time_since_calibration(self, minutes):
    last_row = None
    previous_value = None
    
    # Iterate over each row in the table
    for row in range(self.Source_Cal_table.rowCount()):
        # Get the value from the 4th column (index 3)
        time_cell = self.Source_Cal_table.item(row, 3)
        if time_cell:
            current_value = float(time_cell.text())
            # Check if the provided minutes are less than the current row value
            if minutes < current_value:
                if previous_value is not None:
                    # Get the value from the 3rd column of the previous row
                    ac_val = self.Source_Cal_table.item(row - 1, 1).text()
                    # Return the difference and the value from the 3rd column
                    return minutes - previous_value, ac_val
                break  # This would happen if the first row itself is greater than the minutes
            previous_value = current_value  # Update the previous value
            last_row = row                  # Update the last_row index to current row
    
    # If the loop completes and your number is still larger, return the difference and the last value from the 3rd column
    if last_row is not None:
        ac_val = self.Source_Cal_table.item(last_row, 1).text()
        return minutes - previous_value, ac_val
    else:
        # Handle cases where the table might be empty or has only one row, etc.
        return None  # Or handle this edge case as per your application needs

def calculate_current_activity(initial_activity, time_since_calibration_minutes):
    half_life_days = 73.83  # half-life of Ir-192 in days
    time_since_calibration_days = time_since_calibration_minutes / 1440  # convert minutes to days
    decay_factor = math.exp(-0.663 * (time_since_calibration_days / half_life_days))
    current_activity = float(initial_activity) * decay_factor
    return current_activity