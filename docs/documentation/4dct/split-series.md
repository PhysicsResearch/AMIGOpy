# Split Series


Stacked 4DCT phases

Depending on the acquisition settings, 4DCT sequences can be exported with a single series number. When opened, all phases will be stacked. Although the method to split the phases is probably within the header (perhaps within a private tag), it is not obvious what is the best way to automatically split them, as this was observed for only one dataset.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d1GNxQW1EUaAVKFqVoDtj68u44cn9la2wj3ocfv9ZPfkCLKYhn5g8gV-AoiuFTR6dic_kiE7YkaOOC3csYSwiltLRQCfdE5FIFfLtnCYfebL8DfgIvcaTYTkb5zD_jb_FCqH7mU4SpxjU3nXBBMubBvJ5BEgHRDAtfdW4IkEYuvOVIOcRhfzC3fAxqcaGISVAWWFI1cU1CfplnMp9rszOMq1Jxxleqy4e5svenYCD0=w1280)

The current solution is to load the data normally and, if the phases are stacked, go to the menu:

Tools >> Series >> Split

A popup menu will open (if you have more the one screen it might be a bit hidden - look for it) asking how many intervals it should be split.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d32rWEOgfXoeJUSycg7tz8T4GllUfL6xFnXDk4DpjDER--A0Wj0u_FDtlklFzYTSNc085hKmxVfFqUV6zsa4ryfVU_djt0g0Tl7bZ2g7O-tIP752kWINjAL5w3sgd2CjKEIwaUvuMqIF5Jt3zxvKOI5xTlKbn7mHex_AtGiXhfI-bHDqCFIhg-QHxTzIWjLmEPEsjEKkr41oexDgUAsA-p5hCTv2Od_JZChVf0B_KA=w1280)

Note that it should be the exact number or the software will stop. In a 4DCT, all phases have the same number of slices. You can count how many times they are repeated by looking into the coronal or sagittal view.

Note that all names will be the same in the list, but the header should be different. Look into the metadata (ImageComments) and on the top-right image where some of the headers are shown. This information will help you identify and verify the correct splitting of the phases.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0Ty0d-56Sbtdaw7YeO3P-n9sgtlneCAbImWNnbGjgzAMLDr9Wm_i31bTO8y-9-9O_kAD0HrwCGJ6wsouwdmb1eEJEKeZMx0i1lonfzxp1D_Vv29TSG2ImXA5muGnAjQ_9n5DvgRjgPQ3JFM-IqyuRzedQzS_BaCcTQHVRf7-OOPswsgRrlPn_sHWDAvOSwFhCcxUncw6MLzOvFN7oJsFFuNlUlfV5JUapp_yjg2TQ=w1280)