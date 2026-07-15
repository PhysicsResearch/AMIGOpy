# Visualization


Visualization features are described in the sub-pages while this page shows an overview of the visualization layers (see example here)

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0vyiOh5jUUlqjLQBfMhzJ8Bby6IPDfgiaqxDg29LGmNXHb6skf8Nmp07bMcM3JqfWuz-RVQ0C901UrBRQTVbFjUvrlV8xUccEfBo7P0aDxo-5QBmTedcFey9LlONw1ukhOAq-wxt6aDkx1tbsRvT3N13A067R73nE6mr7z-wtkCKSNAk1R8mMNhTMrKCx1PYrQaQCk0NfU2AD2W5DDriBrlPIpj0Z3O3NaPOEYot4=w1280)

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d1cVNTcgJyzMNET-vkzuhiLtyhC1lZZ6L8cetXKfzRmLuBkD09OO2HvkrcNHbyz4bxasl4VHH7lvASMCqUUkEVJCnFy0dqWZx1jEWtVID8PU04SwL9ERJjWLh7mgNFPqoF2raVnKl9ACmWw7Dl4fcOys9l3jKbULy0PcNMP30lnawWBeAsGj8v4VOuf4iVGeYuPtdhU_B7YrViihQm8FQxNb2iDRcY4XbfgjImp=w1280)

# Layers

AMIGOpy uses four visualization layers where three are defined by the user and the las one is used to display annotation, contours and other features created by the software.

It is useful to overlay multimodality images (e.g. CT and MRI) and also to visualise dose distributions in radiotherapy.

Note that window levels will be applied to to selected layer only so each layer can have different visualization settings.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0zwtrjzbcWyKS9fAw5DE0-TPxMoDLuardqAaZAnm8sa2shiBu2ekYKPvuyKt--9DYDs83qvj4XBokMe4aluWYrHB1jD9v-kjmrn_cEN-VvYQp3nzxVNhz5qs6tylEJdzQ_hGhEdOs1-W00zKzxNR5OfaLXRc46GEtGbUkgPcd0DkWu2FQg7ghxdUKMuPPRq6HgEN5JQFr1p-keTOmkl81bKkDZOyP0geSEGhxJtI8=w1280)

Select the active layer (from 0 to 2) using the dropdown menu and assign a data set to load into that specific layer (see next item)

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2ECSby7JqtFe9G7UKLDBVtY-6UbbMVt-vxD64M5ftRLCu5mJM_7mrfAHoHROMrJ6vDKOgiwC6ICD6SfUKvagC2Q3xmJzoCKQGtCL_vrPglbwDIDP8ag3hWhGL6NiN2-X4VTd37WDrLhFP_KPgIXyRsOGbLoNYplnz4xuYIRK0G18oxnXteSb0Oe4oEEaGo_aRSi9JFHRnAJypVz1xYMZ2cGz7QPZsyh9wbRX1ZMfk=w1280)

Use the data tree to select a dataset that will be displayed using the active layer.

Repate the operation selecting different layer to create image overlays.

Remarks

- The slide bars used to change the slices will be adjusted to the current layer. E.g., Layer 1 dataset has 100 images, while Layer 2 data has 50. The slider will go up to 50 if Layer 2 is the active layer, while it will go up to 100 if Layer 1 is the active layer.

- The dataset in Layer 1 is used as a reference so offsets will be calculated using the Layers as reference.