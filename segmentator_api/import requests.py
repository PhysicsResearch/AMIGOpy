import requests

nifti_path = "20240214_1300__average.nii.gz"
url = "http://127.0.0.1:5000/segment/"

with open(nifti_path, "rb") as f:
    files = {'file': ('ct.nii.gz', f, 'application/octet-stream')}
    response = requests.post(url, files=files)

if response.status_code == 200:
    with open("received_segmentation.nii.gz", "wb") as out_file:
        out_file.write(response.content)
else:
    print("Error:", response.json())