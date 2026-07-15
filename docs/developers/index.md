# Developers


Interface

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d3p93vH9CveyMloqqszpzZUxyEpASnoTskxEa6MgFUJT5G0T9UUwxROTOp-coQvLrSxEa_lk1pCsKPT1Hps8qKGXS62Jbz5c1V1UzmfH-WSY9SJpuC2aZjvsPajD1kFDR9F72ZpmHmydvuzLyMED6eSfxELNBPFoRp4QUIITE32i-oGKrwB3ExBRF55pCvNUuqFbjx4O7RyYjv3OGRypzCfJJkBVdpq_MlcuErk2oc=w1280)

# PyQT5

The GUI was created using PyQT5 (Designer). Using the same tool is important to avoid conflicts with future versions.

In order to make changes to the GUI, use the following steps:

- Open anaconda prompt

- Activate your "amigo" environment (More information about environments and anaconda can be found here.)

- Type  "designer" to open the PyQT5 Designer tool

- Use Designer to edit the file ImGUI.ui  and execute the following command to convert the .ui file to a .py file:  pyuic5 -x ImGUI.ui -o ImGUI.py(IMPORTANT: Do not edit the file ImGUI.py manually !)

Note: Add a custom and meaningful name to EACH element you add to the GUI. If you use a default name, it will create issues when merging the code.

After pulling you might face issues due to missing packages in case they haven't been installed. If that is the case, use the .yml file to update the virtual envoriment

conda env update -n amigo -f amigo.yml