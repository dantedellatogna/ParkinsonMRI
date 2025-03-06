import nibabel as nib
import numpy as np
from PIL import Image
import io
import base64
import sys
import json


def convert_to_image(file_path):
    nifti_img = nib.load(file_path)
    data = nifti_img.get_fdata()

    slices = []
    for i in range(data.shape[2]):
        slice_data = data[:, :, i]

        img = Image.fromarray(slice_data.astype(np.uint8))

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")

        slices.append(base64_img)

    return slices


if __name__ == "__main__":
    # Read the file path from command-line arguments
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided"}))
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        images = convert_to_image(file_path)
        print(json.dumps({"slices": images}))  # Print output as JSON
    except Exception as e:
        print(json.dumps({"error": str(e)}))
