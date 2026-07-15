# Material Assignment


This tab can be used to assign materials to different parts of a CT-Scan, either by thresholding or by using already existing structures.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d3107-BGAASrjOaDCxo-5Z_FzB4Bd7gQoalt-W-nLR4KdV1OaEHEj5z1XLdwKwG3hbb1oI2NeWY7nsia17UohCOTEu1xdRhNHrkH_qISZiodxBvmB2825KoTWZlmmUEjOYNn6cxwLcd6wvhRg9RXsNx1kxnU-mVNs7zjC1E5QZFe25dTZOmGrFJYOIAPPKFk00uMOJgS0wvsWDYo2H263B6x9w_uM3JTabYz5BlNNQ=w1280)

# Material assignment

First, make sure to select the CT you want to use for the material assignment (1). Next, you can start assigning the materials.

- Select a material from the dropdown menu (2)

- To assign the material to a specific HU range (thresholding), enter the HU range and click "Assign to HU range" (3a). If you want to modify the range, reselect the material from the dropdown menu, change the range, and click "Assign to HU range" again.

- To assign the material to a structure, use the corresponding dropdown menu to select the structure, and click "Assign Material to Structure" (3b). You can assign the same material to multiple structures, as well as to a structure and one (or more) HU ranges.

- The materials with corresponding ranges or structures can be found in the two corresponding tables (4).

- To remove a material from the tables, select the material and click on remove material (5)

- Once you have assigned all the materials, click on Create material map (6). Each voxel will be assigned to the corresponding material ID. IMPORTANT: All voxels that do not have a material assigned will be automatically assigned to water!!

If everything was done properly, you will see the material map appear in the data tree. This can be visualized on the view tab. You might need to adjust the color window. The maps show the material ID corresponding to each voxel.

To delete a material map, click on "Delete Material Map". A pop-up window will open asking you to select the material map you want to delete.

# Material Properties

The table on the right-hand side contains a list of materials with their elemental compositions and the following properties: Den (density), RED, SPR, and Tissue. This last property is a binary value that indicates whether a material is a tissue (0=not a tissue, 1=is a tissue). These properties can be used to create density maps (see the appropriate section of the documentation).

The properties can be modified directly from the table. Materials can be added or removed using the appropriate buttons. If needed, new elements can also be added. Once you are done modifying the material properties, click "Save" to finalize the changes. The reset button brings the table back to the last saved version.  PLEASE NOTE: Adding/removing materials will alter their ID and, therefore, it will make the previous maps invalid!!