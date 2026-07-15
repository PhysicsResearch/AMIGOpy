# Import & create


On the Import & create tab, the user can:

- Import files containing breathing curves in .csv/.vxp format

- Create their own analytical breathing curves

## Import

To import breathing curve data:

- Select the delimiter used to separate the columns in the csv/vxp files (by default comma-separated)

- Select the line containing the header information, as well as the lines containing metadata to skip

- Select the time-unit the time data is stored in (e.g. ms or s)

- Select whether to flip the amplitude (dependent on the acquisition system)

- Press on Import and select the file to import using the file dialog.

The file data will now be imported from the csv/vxp file and displayed in table format, as well as in raw text. Furthermore, additional parameters are calculated, such as the relative time within each cycle and velocity/speed of the breathing trace.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d25rHDpM-hHkHGM0b-EHtJ43uysuW1tEiOT1odukGfW_11iW4E9XnUUJ7ejGczazaWFB2stD136933q4kqrGd_m1lZNIhH1_Hp-3Y9IP-RY9WZKzTPX0mMfcZqgBrL2fd2MB1O6K1i213QZ5rtzWN-AkqFDBdUzQ6_q3P8EqlducScfcgh3nXVFSdarwSeNxdy9dOuXYgIlKLj6FgxOVGmcq1V-GGFbNaV6MI-P=w1280)

## VXP file format

The Breathing curves module was initially developed to import breathing curve data acquired using the Varian RPM (Respiratory Position Management) system. The RPM system is used mainly in radiation therapy to track and manage respiratory motion during treatment. The RPM systems consists of a marker block (with reflective markers), which is placed on the patient's chest or abdomen — somewhere that moves predictably with breathing. An infrared (IR) camera constantly tracks the 3D position of the marker block.

The .vxp file contains the following columns: amplitude, relative timestamp, phase, mark, valid flag, ttlin and ttlout. The amplitude parameter contains the measured movement of the block, as a function of time (denoted by the timestampvariable).The phaseparameter denotes the relative phase within the breathing curve. The markparameter indicates the start of the next phase, denoted with the value P. The valid flag parameters indicates the portion of the breathing curve that is error-free, i.e. valid for treatment (0 = error-free, 1 = error). The transistor-transistor logic (ttl) information stored in the ttlin and ttlout parameters indicates whether the radiation with on or off (0 = beam-off, 1 = beam-on).

## Create

To create a breathing curve yourself:

- Select the curve type to use as a template

- Select the number of breathing cycles to generate

- Select the default amplitude (in mm), as well as the breathing cycle time (in s)

- Select the sampling frequency (in Hz)

- Press on Set parameters

The parameters that will be used to generate the curve are now displayed in a table. The user can either

- use these parameters to create a regular breathing pattern

- or adjust the amplitude and/or breathing cycle time of specific cycles, in order to introduce irregularities in the breathing pattern

- Once the user is satisfied with the parameters, press Create

The data will now be displayed and stored in table format.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d3BO8Z-os59buL9BbiNA1yYeftTfmXniXlx1CZj39R4fxHFIRPweu_KIcvSP5XpseJv_aN3MGO3DfOXvU81WV5jSgqunXwAiT4sZA_9lqQ8Y00Cq6_PVLI8lBawVef_aU2eyU6W_sZlukI7QbEb5_57benEEyRTl0k688OXUHs6OXxlB8N3cs9Ge-bNPskhD3m9p9Y4pxP8mFmYE_03nrPfBCbpIlBwt2eXcIpQaxc=w1280)

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0wtUrn6gxNmiXpLj2DLlrXJjppsdW9_qSht-FtjPnrQC0GmvLqLYNYTQlaVv8xwkBE2Jw91_fdeM5W0veZUQ_uIHvrkoLxtHsyTZBKdOWxNuAXEgKnjKd3Wg-eiOKeTMcYY2JrHiEDZwsLoNdb6zBTDvQrCQ1Lbv_5E0y-d3cT7uHfTb8hrFHoJUrcC7LwbXopzmryvikYLs_0QM1kp4rHR1EKnKvkTtBishy5SBE=w1280)