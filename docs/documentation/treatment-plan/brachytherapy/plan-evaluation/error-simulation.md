# Error Simulation


To execute an error simulation, you first need to determine the uncertainty bands. Please work through the documentation on "Uncertainty Bands" first before proceeding the steps below.

- Press the tab "Error Simulation" in the right top corner.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d25OpLEoYqj8K4tMIjU6T-glBQUdggI2C2Ls3PpjEYJy1ul5zqHhi76hCbQUfYp0PgTBF9G_mp-pl8uZPcWHY5sreCEcSVU0Oj18Uj-ldt761RGMkt_2uplbhaGpaW4jFiQfPC7JX-yPKEZKvKpY7qPZswHn_ierQUcQUWCUKSkBm65JUZwwD_5QnWzy1b4oTqLHB5ANuQRSWGh7YW8GIFqZ5Lf1YoYg_pXoNK1nKs=w1280)

2. The following tab appears:

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0_jou2_v0oZx5fFqRf210VJjm3igR5Bu5KtTHoFQKWWaBcNMFuMZhpJjg_u_ZF78Dk9ajRsA4sqyivRoBB9AqronSwQRMe1WuEQmgnUMQjYn1FPw6Y3-oiLACN43dQiqcaut8i_7cfjbzsnvfEc41kheMMlhzmVj0ZBbiwpbg3tHtQyq2fD6kiCyBRJl1ds8Mlj2je3bvIhdP82UCb8vRR_1JYhSB5Rjz_lNGVcAE=w1280)

3. Fill out the positional and/or time deviations you would like to apply to the dwell positions in the treatment plan.

- Positional deviations

- Negative value: catheter too far into the body (e.g. "-2 mm")

- Positive value: catheter not far enough into the body (e.g. "3 mm")

- Time deviations

- Negative value: reduced dwell time (e.g. "-1 s")

- Positive value: prolonged dwell time (e.g. "2 s")

Note: Currently, the software applies the deviation to the dwell positions of each catheter individually and to all catheters at once.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d1sWgdUDggvPzr2TqrC6o791Gi_83vrVzsrSL8icZx1F-porFW9bJa2_iujSgxwj48KOgTCqPTgvZ7wcd9VdPRiWyDhjrzNN7XiUKKYZhtWuPrC1_n6AG3yrdJMZftRUlmKdztLCNA3zQ54PeW3GxPJ82JVrLTnd9qfR07aJWjkjezURJkGkxgcDnPtyTQkD12g153v9qPgwKy7z7Fd9xq7X8GuxMgc1U0bam02=w1280)

4. Press the "Apply Error Simulation" button.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d3AII1FoFrSIgfGrAGfKeZgs5_YqlrDtRvUH3QuatfaH3m1EJtkCVxpdaubD82uda0c3FlbNnEY5JRd2ltEEs9CJsZJ_nWx8nsbAcx5b56GpXVPxpPFsigOAa1_aJ__dzMGxGHw0oSN2poAEWYY0G2pB2S-0sD8Tg9nsSVa82MV19djMepPQOSt9WNgED4sd0lHovXoubdlfo2lQb6awxkyJbsBwHffYNOl1_Zqvdg=w1280)

5. The results will appear in a table, stating the percentage of the error-simulated-DVH that falls outside the uncertainty band.

In the example below:

11.6% of the error-simulated-DVH for catheter 1 will be outside the uncertainty band.

16.7% of the error-simulated-DVH for the error simulation applied to all catheters at once will be outside the uncertainty band.

The DVHs as a result of the error simulation applied to catheter 0 and 2 individually remained within the uncertainty band (0%).

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d3iu_lYpDsDjl8x4dxg1Mdf3eDNTDcOrX441iMd506pWnSh5NbJQ_l_Xe_-3g3eOTJ3UCFO1t3feIAzE7N9KNPe0Oa26bXcfEbTsY0Ue1H0NR1t-3ZQuYGNOZTULmVCoyoYhza6RyfDYYvmyta5XnkHuqeUBc5miJDhACErDsdCS1vfI1uDd38Gm-0bbwT-0nS1_pCPgQD6CrrWC34wHq-DDwSRIe8F-gK-fFQ5=w1280)

Plotting the Error Simulated DVHs

After simulating the errors you can visualize them by pressing the "Show in Plot" button.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d1e8MQIOtw91qx2ZzTxOynw9UsAuaBLZkBA5aF27W81sXBkQsg4ung8t6yZh7wmvoBUSl4hom9HmDAQGjWTOxuGEW1mT6so8KrcbcAgdOPEHyAi726Scz3ku2i-fDTbn2pMoWfe9Dt1_v3qETtPZt6aaN5vKcvefPq-CU3YomxP8P4iB5h_kQNcrYjdocs0nqzC9gWNnFkCvy9QItmDbS7kI_YyxPN6jJW-gL-j=w1280)

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d1BZP2Y6XsPoEQjF1l_Eo9R8IEGYSJVQZWDsyDuaUu0RfYv3xVDYv3Z92LpWySD7-povYnyw9KWVKzPBW_w1lP1PZprsWFs2qtERSD1pTusxMzNT9dQ8qRj8LYLly9z2XrXP90PIiib8HtM4dgGAhdKGBXoFFIpVvBpRTtYjYp-1sz4W6HxDunv9Q9v-yiCiKgyn3ZAWv1bhYoV4jNpRRJaM5j_VgdgswtV2bCWNuw=w1280)

By clicking the loop sign in the toolbar at the top, you can zoom in on an area you would like to. Whereas the cross of arrows allows you to drag the plot from left to right, or up to bottom.

- Red illustrates the (parts of the) DVH that are outside the uncertainty band.

- Green illustrates the (parts of the) DVH that are inside the uncertainty band.

- Blue illustrates the DVH to which the error simulation was applied.