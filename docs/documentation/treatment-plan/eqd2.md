# EQD2


The tab EQD2 under the Treatment Plan tab allows for converting an entire dose matrix (for example, from an RTDOSE file) into its EQD2 equivalent (top part of the tab) or converting a single value to EQD2 (bottom part of the tab). The EQD2 dose is calculated using the equation:

where D is the total dose, n is the number of fractions. The α/β ratios depend on the tissue type and can be found in the literature.

## CONVERT DOSE MATRIX TO EQD2

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2DJOlLqS-PvDgc_gX9QFJGJNz8DytMzS8_AFFIzaQZ1iZl-9qoAcjIhoEztk8DwpRTON5iAZlg4XEIkvBc64uihLlthvSfcwOMioZWfCAnzxl62VTd65pDYzS7rX5rBVpORb1WWArAVvk5rsKhIfV1GKCcJVmu0sE2qH75wX4jMdHdYUEgS_rnTD3SWxQ7rXB7wyLfG9vJQYBnnNNPXktmBVxRlu-iI5jBxzzM=w1280)

Before doing the conversion, at least one structure needs to be created (see documentation on contouring or on processing of RTSTRUCT files). Once you are in the EQD2 tab, select the CT series you want to use to calculate the EQD2 dose from the data tree on the left. The program will automatically look for structures associated with the CT and doses inside the same study

Next, you can choose the dose you want to convert from the corresponding drop-down menu (1).  To assign α/β values to a structure, select the structure from the corresponding drop-down menu (2), type in the α/β ratio (3), and click on add (4). If everything was done correctly, the α/β ratio and the structure name will appear in the list underneath (5). To modify the assigned ratio, select the structure again from the drop-down menu and reassign the value. Use the delete button to remove a structure from the list (6). Once all the structures have been assigned, click on "save α/β values" (7). If everything was done correctly, a new element will appear in the data tree (8). You can visualize the  α/β value for each voxel from the View tab. IMPORTANT: THE DEFAULT  α/β VALUE FOR EACH VOXEL IS 3. YOU NEED TO ASSIGN THE  α/β RATIO TO AT LEAST ONE STRUCTURE. Next, type in the number of fractions (9) and click on "convert to EQD2 (10)". A new dose will appear on the data tree (11). This can be visualized from the view tab.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0DB62ND8Aww04G8iwZxgQL7NS2Tbz7d5hGuVAQ_gHXqDqMem27y7XlX83unnXjqj9Lwmj4LVtWXtCBJ6azddEq3dAhNe3zydb575eqQx1Oku0VuZD2Y4hK6tbXVNrgi1rqtFv4TF8H1hNoqgYX41-68rdLD5v0yIZftmkoRwrK3aBIy8mx70EzoTxxEarJuf0v5Z7XuUrJ7OmpVegP4F069_dCQMsGc4moxqGLpoI=w1280)

## EQD2 CALCULATOR

The EQD2 calculator can be used to calculate the EQD2 equivalent dose of a single value. Insert the total dose (NOT THE DOSE PER FRACTION!), the number of fractions, and the α/β ratios. Then, click on "Calculate EQD2" to calculate the EQD2 value.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2hkIgh9guwMKnJvpCDJf_alVg4it4M0ERlPJfeTcdem_GB_lgO0cTJaupYqkxQ4sOupqEpHqiORrBaAnIprzJMenu7KUOdQTkjutnifc7Vz2W5ypQR59uvJ68JBqruGF4Sv7kvE99V1zmNJMZGyko3BJwvB2iCB9WE1Sabm59ElUM4TvYN1Nv_sNZuRRz9hpaHIXBj4rkX_KcQlnOZs-mg4xl1vYu3POM3oEVaTXQ=w1280)