# Compiling


Compilation requires two steps

1)  PyInstaller - Compile the code

2)  InnoSetup - create an installation wrapper

- ### PyInstaller

- The configuration file used is Launch_ImGUI.spec. Ensure that paths, icons, and hooks are correctly defined to match your setup.

- Currently, the source code is stored on the Z: drive (network), while the output folder is set to C: (local disk). Some packages, such as pydicom, must be explicitly defined in the hooks folder to ensure proper compilation.Note that the Launch_ImGUI.spec needs to be copied to the output folder.

- The configuration file is tracked and available in the Git repository.

Command (to be executed within the output folder)

pyinstaller Launch_ImGUI.spec

- ### InnoSetup

The configuration file (compile.iss) for the InnoSoftware is tracked and available in the Git repository. The input and output folder needs to be adjusted to match your system.

- Copy the file to the output folder. Open InnoSetup (link above) and load the configuration file.

- Click on Build >> Compile

The file my_setup.exe will be created within a folder called Output.