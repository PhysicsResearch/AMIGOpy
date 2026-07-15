# Text Files (e.g. csv)


### CSV View Module

The CSV View module was designed to offer a tool for quick inspection of text files, commonly named CSV, but applicable to various file extensions. AMIGOpy can export different types of information into CSV files, and we frequently use CSV files from diverse sources, such as patient breathing curves, dose measurements, and CT calibration data.

This module enables users to:

- Inspect CSV files with ease.

- Plot the data for visual analysis.

- Perform basic operations like swapping columns, and executing arithmetic operations such as addition, subtraction, multiplication, and division.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d1ycrsirt0hpuZfsQVU5_MvSVQiEiVF7UQwylSRMWdZGCpQ-R3xluqThT8z2B0SfVEuumW5QF5r7gxQNBfElx2f5wRMoPe2ZGOXJK2znJk4vb-zHEQhk__PXeWqNEug11Lm9j9eYKsOUOrQOKE5UEhA3HXen6D53RkG4Sig-r5wsK_QXo0gy87SDQWA8BbThHhSoB9QK5Qz5cq2N4wbWSsRtDls9fFiwnGMbZfgzlo=w1280)

Click "Load File" to open the file selection dialogue. If the file you want to open is not visible, select "All Files" in the dialogue box. Once you open the file, the first 100 lines will be displayed in the software. You can then inspect the file to determine how many lines should be skipped (header) and the separator type (e.g., comma ",") used in the file.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2anH-pbFIMGOluJSi595RNXDzmM2MI5K15oz6gjqgq1bZd6Z18XsN137uRiktoaQFgHMBkF8D4-IEodPhcXdqAIMJS69TpbRz2rRaoRd9geEXRo0R0hEQZ7zhHNt2hkq0WjlfNJ3cFvh0ZNJjJQYutb8nsIZg8odemwrDv6ehhFB3Tqnlr_g_YHrj_WxnStBKgnCeK-3m9nH7YDjZRCkG3ELdwRFs-LskTTldtoL0=w1280)

Adjust the number of header lines to skip and the separator type, then load the file again. The columns will now be displayed in a table that includes the entire file.

# Plot

Select the columns to be displayed in the graph using the dropdown menus labelled "X-Axis" and "Y-Axis," then click "Plot." In the example below, the breathing curve is plotted with the timestamp in column "C3" and the amplitude in column "C1."

Note:

- To keep the current plot when adding additional data, select the checkbox next to the "Plot" button. If the checkbox is not selected, the new plot will replace the existing one.

- Additional icons at the top-left of the plot allow for further customization.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d07nd4BPMOW8uBoC7q_hmrEEe9Ta5907fHK4a6ASwY5kA4WO3uyefc7zmcPdNsXPJZc1FuFvwFQqhClb_SgpLV396JPVL881SC8rSp4OhpvOMKNoNA7iNUPrrwfJTRlLhDjEtzclnC0HxNvGCXHSPZ_DEJOzYEb-WatytYeUz-fq0ibu68R7sguWq5TRZXOjXp0nIteprS7lw-XqIcASvLPQeuIFYBLe2Wdw8eHm1M=w1280)

# Operations

At the bottom left of the table, there is a dropdown menu with some basic operations. Select the desired operation, enter a number in the space below (for arithmetic operations), and then press "Apply."

Examples:

- Swap: Swaps the values between the columns indicated in the X-Axis and Y-Axis menus.

- Copy: Copies the values from the column indicated in X-Axis to the column indicated in Y-Axis.

- Multiplication/Division/etc.: Multiplies, divides, etc., the values of the column in X-Axis by the value provided by the user. For example, in the scenario above, the amplitude should be multiplied by a scale factor of 10.

Note: The graph needs to be updated manually by selecting the columns and pressing the plot.