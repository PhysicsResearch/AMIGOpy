# Create Mask


Steps to create a Structure Mask for DVH calculations:

1.Load DICOM data.

NOTE: You can either use the dose series from the treatment plan (in this case, "Eclipse Doses_Series: 6") or calculate the dose using TG-43.

Please refer to the documentation on "Calculate Dose with TG-43" for information on calculating the dose using TG-43.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0otlKEi79u0BEP3bm_HfUiVEKk7BqouozzbEoxLvFekeuttn-JfoN7qngVNjgGIfuuzKXRxnmMVXoGjOlOeIjmH4i4a8mbIy4HZWS4vnjT8bHEdSPeE9rRTXeR2miGwkwTZJJM9qnBVtNgi3g9SMQDPVuGFjEtSP6K4HxCHPQsRncFoNMZ1vLXD7kAEWSdBx4Tf63F7xnt4R3_5P62B1V3V39J95QUkG3qb2G6=w1280)

2. Ensure you have loaded the CT and RTDOSE series for the patient. Structures must be present as well.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2ZQUAV4syxER041COnEkipasKOudc_pmRV2B_1ak6vt7Elkg1qUa132siqJIR1huDQpbwQFkMTrXG-rT5DzwE2tD3w8ZJAPKZyuYhkQ5kOCGc_145QJzHRJRw_tVwkq3XXbLAP7i8A455ZDsZ4Hk5b4N9hLVO-av7lwXVd_umWF6uJhfTjOdff0czQjY8whbP6bskBVXIv7tGsoxP8dFnan0fddIIupUjFJ2HpMKU=w1280)

3.Select the structures you would like to include in your mask in the lower right corner underneath the tab “STRUCT”.

In this example, only two (Bones, NS_Control) structures out of the three present in the dataset are selected.

4.   Select a CT image you would like to use for the structure mask.

5.    Click the button “Create Mask”.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0mbPJ_y5-yFhBTosUy4q9P9SoN2X9ajQDFnFhZO7fj7ILHqdWuDSYc2QOWCocmTUj_6nObsi18ajSo9wzQg3AWdejcvoAyEQxZ9RkD9paI15rkaK9dZTs70VSWVebZ2Zdehig1NfMA_iR7krL_sYOvTNUzwEwKXm_uWYXHHBnPdeT73dBcdJEbz2SJNI7ELoQJhAItbBgGEYDrbIvAlasL21QTbVZFJzLwDBYGN6s=w1280)

6.Once your mask is created, it appears in the panel of the left.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d1GqWMvo2ihRFt_z6olp6UB5-mgqVbSHHbYFQXvvezzLB5YxeEnpdNJMMm4v_kwHS6RSV3-tqVPphO06hmMM-DvlJIKbQ1A3xPtc6hVas00-NYd1gFaqc2mM5Vm2um3uCDP3UXOmnp41BJwsxIT1YSSzCgUMaBW23AY4Fp85KLJ-Kg852d4QcvqlrfxIznYqEVySA2X0YbrthAZgkU2ne2gIqSq87yeX2pqY253=w1280)

7. Now your structure is ready and can be used for the plan evaluation. Please click "Plan" in the top bar, followed by "Plan Evaluation" to get to the Plan Evaluation window.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d12THpzjPZCHPORawSBGJhygghOoX9HAkY7ZDhQ_RLW8jMBTRvTgQXvfbZitMu30CIjjI7j7IjVL2QXGHX8jDCpCM28ygerAUKDhvYKDyiMRaHiDRZNaAwuMeTmuYUiYaqnPLxwD7W1YgCql867oX72sdPuH3aU7hXThDPA3z0s0qMyCdHdCrfN_eFZvjdwbjirDMXxj3UfPSyVa6BggUKn4yh2vDBtJfbV7yiIa68=w1280)

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d16PkFgJmbkSSwj6S99zsGIQZi8vWBz0VQCeBpiVD6fARYnYebXPyvusAO239H9Inh2M8WGlj9ldrf4hZ4TBpQCCXfurlCNI7jqwtGMXgL394fimoiJJtLNXG6M-HGGNPP1ZFn88TSb1DEHCnfbis7ZUeucjTh25wxrfllzbhx259igpXby6Zo4-JBV3EJeOaUd4Gr8dXnrjDjbBzKwh2L5H-LNjOEABVlIaxt_aWc=w1280)

8. The following screen in the Plan Evaluation screen:

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2ZMAsGJULQc4pFUZznSI2FmKVRRrNCJYZ_Wb8oODc8fuHAysYuhXKvVVERtUOdl1UV7qOWbIno33IybkYxvFSOksiDN3v9PakzuHPnhVaU9b_v9q57axj7ONReV76ps_72xuqQ216H5W_5DAmkkOCFseXZyu7DKCk64AJs490XYjcTT1SJDCHDuO8HW70IoIQ0uKSKRbABWxD9uVtOObB3mvW7hGvC5lHFkJt28zM=w1280)