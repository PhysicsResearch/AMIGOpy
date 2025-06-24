import sys
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, 
    QFileDialog, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt

def split_gcode(self):
    """
    A slot that collects user input, then calls the actual
    splitting logic.
    """
    # 1) Let user pick the G-code file
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Select G-code file",
        "",
        "G-code Files (*.gcode)"
    )
    if not file_path:
        return  # user canceled

    # 2) Ask how many sub-files
    num_splits, ok = QInputDialog.getInt(
        self,
        "Number of files",
        "How many parts do you want to split into?",
        2, 1, 20, 1
    )
    if not ok:
        return

    # 3) Collect the breakpoint layers
    split_points = []
    for i in range(num_splits - 1):
        layer_input, ok2 = QInputDialog.getInt(
            self,
            f"Breakpoint {i+1}",
            f"Enter the layer number where file #{i+1} ends:",
            100, 1, 100000, 1
        )
        if not ok2:
            return
        split_points.append(layer_input)

    # 4) Now call your actual function
    total_files = split_gcode_file(file_path, split_points)

    QMessageBox.information(
        self,
        "Done",
        f"Splitting complete! Created {total_files} files."
    )


def split_gcode_file(original_file_path, split_points):
    """
    Splits the G-code file into multiple parts based on layer numbers in `split_points`.
    Moves Z up 10 mm at the end of each file except the last one,
    sets extruder temps to 0 at each end, and restores temps at the next file start.
    Skips G28 and M84 lines.
    """
    # (Implementation from the previous assistant response)
    # -----------------------------------------------------
    with open(original_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Prepare base filename (without .gcode extension)
    if original_file_path.lower().endswith('.gcode'):
        base_filename = original_file_path[:-6]
    else:
        base_filename = original_file_path

    segments = []
    current_segment = []

    # Track extruder temps
    current_temps = {'T0': None, 'T1': None}
    extruders_used = set()

    split_index = 0
    extended_splits = split_points + [999999999]  # effectively 'infinity'
    current_layer = 0

    def start_new_segment():
        nonlocal current_segment, segments
        segments.append(current_segment)
        current_segment = []

    for line in lines:
        # Remove lines containing G28 or M84
        if 'G28' in line or 'M84' in line:
            continue

        # Temperature detection (M104/M109 T0/T1)
        temp_match = re.match(r'^(M10[49])\s+(T[0-1])\s+S(\d+)', line.strip(), re.IGNORECASE)
        if temp_match:
            tool = temp_match.group(2)
            temp = int(temp_match.group(3))
            current_temps[tool] = temp
            extruders_used.add(tool)

        # Layer detection (e.g. ";LAYER:...")
        if line.strip().startswith(";LAYER:"):
            try:
                layer_num = int(line.strip().split(":")[1])
                current_layer = layer_num
            except ValueError:
                pass

        # Check if we passed a split layer
        if current_layer > extended_splits[split_index]:
            start_new_segment()
            split_index += 1

        current_segment.append(line)

    # Append last segment
    if current_segment:
        segments.append(current_segment)

    def get_final_temps_in_segment(seg):
        temps = {'T0': None, 'T1': None}
        for l in seg:
            m = re.match(r'^(M10[49])\s+(T[0-1])\s+S(\d+)', l.strip(), re.IGNORECASE)
            if m:
                tool = m.group(2)
                temp = int(m.group(3))
                temps[tool] = temp
        return temps

    last_segment_temps = {'T0': None, 'T1': None}

    for i, segment_lines in enumerate(segments):
        out_filename = f"{base_filename}_{i+1}.gcode"
        segment_final_temps = get_final_temps_in_segment(segment_lines)

        with open(out_filename, 'w', encoding='utf-8') as out_f:
            # Restore temps at start (except for first file)
            if i > 0:
                for tool in extruders_used:
                    prev_temp = last_segment_temps[tool]
                    if prev_temp is not None:
                        out_f.write(f"M104 {tool} S{prev_temp}\n")
                        out_f.write(f"M109 {tool} S{prev_temp}\n")

            # Write segment lines
            for line in segment_lines:
                out_f.write(line)

            # If not last file, move Z up 10mm at end
            if i < len(segments) - 1:
                out_f.write("\n; --- LIFT NOZZLE 10mm ---\n")
                out_f.write("G91\n")
                out_f.write("G1 Z10 F600\n")
                out_f.write("G90\n")

            # Set extruders to 0
            for tool in extruders_used:
                out_f.write(f"M104 {tool} S0\n")

        # Update last segment temps
        for tool in extruders_used:
            if segment_final_temps[tool] is not None:
                last_segment_temps[tool] = segment_final_temps[tool]

    return len(segments)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("G-code Splitter Example")

        layout = QVBoxLayout()

        btn_split = QPushButton("Split G-code", self)
        btn_split.clicked.connect(self.handle_split_gcode)

        layout.addWidget(btn_split)

        self.setLayout(layout)
        self.resize(300, 100)

    def handle_split_gcode(self):
        # 1) Select a G-code file
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select G-code file", "", "G-code Files (*.gcode)"
        )
        if not file_path:
            return

        # 2) Ask how many sub-files we want
        num_splits, ok = QInputDialog.getInt(
            self, "Number of files", "Enter how many parts you want:",
            2, 1, 20, 1
        )
        if not ok:
            return

        # 3) Collect breakpoints
        split_points = []
        for i in range(num_splits - 1):
            layer_input, ok2 = QInputDialog.getInt(
                self,
                f"Breakpoint {i+1}",
                f"Enter the layer where file #{i+1} ends:",
                100, 1, 100000, 1
            )
            if not ok2:
                return
            split_points.append(layer_input)

        # 4) Actually call the function
        total_created = split_gcode_file(file_path, split_points)

        # 5) Show a result
        QMessageBox.information(self, "Done", f"Created {total_created} files.")

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
