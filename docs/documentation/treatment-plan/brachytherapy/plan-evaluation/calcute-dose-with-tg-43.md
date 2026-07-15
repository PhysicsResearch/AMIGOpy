# Calcute Dose with TG-43


Steps to calculate dose for DVH calculations:

1.Load DICOM data.

(or use Ctrl + D)

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0R6GG9OLfHnjhd46lSQoTQTpw_OUT4PhwTMysKpUPV1fw49bBLv8j4eZDdWNI9j-aqh3_OnTyEoMmXgn0oE7F1w7Hs7sigW0o2ENePHgGF-XbcUTsfHMrL5oEm4AhQiVuv9mxRthwgAdw0wj7IrxkRmCQkK_NG1kjzIeemlbXkvxJjjv9V7tgyyMXkgb1J0F4XK39mgN03LzY7mWBSfajzKgBoMfUrLGSychzXigw=w1280)

2.  Ensure you have loaded CT and RTPLAN for the patient. Structures (RTSTRUCT) need to be present as well for creation of masks.

See the documentation of  " Create mask" for further information after calculating the dose.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d3RpN5br4-mH03cM4ldzF9pbIbkW2UzEDd5ddkiEXY9Il3w8Dm3sVsg18kCZd_ZVT0OujuloO32wIpEJci_b9AjuhX6B1WIuXoYng6AePA3Nn0ZZh25DFGGfXGKcdrTvEk7FM7EOhNUW_ZAQ9OX_5XiBkcU3rehoDDpauISSCN5kHcaoeLMUZ5bZjwc1LyNVeNAEQOHxsGR8AthXcDJ_t8MgyaQZhjTmRvq0KFZbs8=w1280)

3. Select the plan under RTPLAN you would like to use for dose calculation.  And click "Plan"  --> "Brachy" --> "Plan" in the top menu.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2E3vXuEFsHFFsADdLOdD2ViPKfLdPr3xvCtgjEi9CmGCNGdRT3bYTd4xfiovUkbI-2UdOID_mGhmvCm9JlRSzW2NTNEFHt6CzcEa9wG_enY1J3-gR4xH5pUGmqV3ms6glwDmALGSWw4h6rOp8RuYkxEYoiHa7rMHsHqGgV5XL-iahrzqsLu3iIoJF-RIK8a7WkRQi1tQNd8q72MSPhnGje_fp8BLrFvm6sC9QpXPg=w1280)

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d1AF7C1M2ZvmmPceCKpE_mhAjGsPMR2oh-WKsCp3afalx61WMbGhxAbutd3aYFxMGhbu4mfaQUnyZr2ldVgwcpbNtzTOhz4uE_GWJErxDq1r6ieWFgO36Wr82eF_qDFCcPcIg_qcd8s_zNb8goyU7aZ8NciWnyheul14b9GHEWSKnuwTfqQx0zdfsR-GB4KB5tMgmAXN9xjz6WI58ENMn0xeRwTt46tV2F3T18jh4w=w1280)

4. Your plan is now loaded into AMIGO and should look similar to the following screen:

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d01jZi2wbuA0zUwwG_SGjCV0yxwVyQYygdbIKP6gdQLtmlDtG2tVZkL5aUOv-zEP78PXb-0hOL_OnXmmKAa6Iyxu-C07zrOLAb_CLPkRDEFuozp0viUMsr0UWKrxfEaantWtnbcqmix_aG960NKu38mTv5FmdssIYfcgWr9AoDdbrESeuzXMavzGEa9C-jX4U4zgAco1CY_p_nLAXwsn2sWKoNIt5_2XUoD4j2oQAg=w1280)

5. Click on the button "Calculate TG43 Dose" on the right side.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d1U28iieZ6PtubnNZSsk8tfI_tbpmWcvNeMYqoNCVCwaBciAWkBlb14CANAaib1PQ81I__sjfUAZ6zuBejr4mje8iq4nqkttIVAgOzdlGrRbOq-xaMEo39nkGo0GMWFpXmgQPxdV4DrHL3o804hGY1TZivfvuDooi7Hau7aZRgQtf3pjN8QDVS0ZtF-9fzlUIvORnznHcOWZimhtRZh1vNrGHmb15L3k8f11O5-lso=w1280)

6. Once the dose will be calculated it will appear in the left side panel underneath "RTDOSE" as "TG43_AMIGOpy_Series..."

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d193fqEjcvZPN3aIoAHQEHDD32xWGGX_h37klE8_fj9fxQcXTkclo2USsBN0ztou6JTE7h2tSBKANqbAFAV1xDolsvlLYFj2gt3AByO8ilr_qworHD_YOfauDno5-u6jYr38NukYCRUyfu1PnoTVcjZT7FUnAjEHwp5X6LwwAQTXcCofgfasRfXDgigwZGpOB3JOgJ0t0pQDyumDwVBBpYDgQUEJu-SprP_blLTDRQ=w1280)