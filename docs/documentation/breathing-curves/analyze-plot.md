# Analyze & plot


## Statistics

On the left panel, the user can get some statistics of the amplitude, cycle time and speed by pressing the Calculate statistics button. If information regarding the individual breathing cycles is available (e.g. phase or instance), this function will calculate the min & max value, the mean & standard deviation, as well as the median and inter-quartile range. This gives the user an insight in the (ir)regularity of the breathing pattern in terms of amplitude and frequency, as well as the maximum speed (important when used to drive motion of motors). If information regarding the individual breathing cycles it unavailable, only the maximum values will be calculated.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0eFTmKkE10r1ijVDN-jUZhzfd-VXjrursUF-TwNUsWlTNnyCOQcMBf8qxFSjT6KXjLznxCXQY5Qo9zu_FhMFULY1XhupUCqu20fzz1t4_0oWkfjAaGEJs7DPXSiLk9lc75NflNP_yHv9TUFaK3dRejo6zhZ_CWp8jgdCU6glNFb371hgNFfT6f9Dwcjmpz3w9_Fp5AsNvvyr_elVwZkQWKX-Du1KWx0pPP96pi-oE=w1280)

## Visualization

The amplitude can be visualized in multiple ways:

- Amplitude as a function of timestamp or time (Figure 1), which provides insights in amplitude fluctuations (e.g. coughing or baseline drift) over time

- Amplitude as a function of cycle time, which (Figure 2), which provides insights in (irregularities) in terms of the cycle time (i.e. frequency)

- Amplitude as a function of velocity (Figure 3)

The figure can be customized using the in-built functions in AMIGOpy:

- Using the options in the Figures tab in the menu bar, the user can customize the font size, background color, legend, legend font size (see Figure 1)

- The in-build functions from Matplotlib can be used to adjust the x- and y-range, edit the axes- and title names and save the plot as an image.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2jL14ErAegZ9wDCtyl6ghIOItI1736Q9xF_jTJd64lmDbSjhS6-JQLTL93we7NSZgcS7usrxy9vzMQa4P9Cv3GqhNb7WDkjZ_8qhFqTccDEPtrCJnijaoWDtXYNv9Gna-7ai20xM8rHnd94NoQFsm0X1jXqOqEPzdD2kV1mDowHiGuEGg9TmgkQJrGfw6_XvraoudqKB3ed9cX_jrEhm_4w0jMHohpbdpp8aA8=w1280)

Editing font size and legend

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d02HUMxXiWjQ3bsNbwXRMezv1H4W8OXPcV9HYku2vGT-55KfWYTfIE4Ueb10YRouHyM0ExMH_3MWRv6UDWS_V4aga2l8NKG2vdPFDpSnEOXxN5epSNMjGHuKJWsu89wji3PszAPKTqwlX3z3fkoIFSLTorPzP-3tczj4jIB72yq_hHOa5EJBBcHXABklB-R2N0kq8EcxRFSaqVlp2xjZHr0vvzAEPddiy7gb-EE=w1280)

Editing axes- and title names

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d3fDjXV16VvQP6extG0acQhvseukZ1heNPw58zSlMYcBWrPCfbdSvCOaS6_83tk0px1iCP3T1pdmIB1YRSq10K5Rw-SE6B6jtsv5cUmBi8eigRG8wRalkKxym3etn3sSkHeljN9t_g-_5pXCjnW7ntjBbm_rBixmfqzWOzipQDh-zvzDHaZS-qje-4dx3tW6yOf0IUjaGD6uPBH8sxPozjTfZ0Q74KZHazGzT7K=w1280)

Adjusting the range

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d1kTzvdH3e456ca2XucQ2SxeCU3yVQcmsAPBKsOEAHh-V4mrJMoQuWzPPARP_IxGf2pw2kaDPKWogGDnIheavczhICfz2IEWXzDLlGBKnj1KhljpX_32S8SR03jKqXH_leLZEGYLxyOrJ2sp-qGCFjhRXHME8JaYnMyeyxX-G4Of88IQktTw3OQdmdo7LQ_ZXpBdtBerOMofTqpbVCGod0Uh-Lvtn-CQFmN6GSayKw=w1280)

Saving the plot