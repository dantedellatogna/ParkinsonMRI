import nibabel as nib
import numpy as np
from PIL import Image
import io
import base64
import sys
import json
from scipy import ndimage


def resize_volume(img):
    desired_width, desired_height = 400, 400

    width_factor = img.shape[0] / desired_width
    height_factor = img.shape[1] / desired_height

    img = ndimage.rotate(img, 90, reshape=False)
    img = ndimage.zoom(img, (1 / width_factor, 1 / height_factor, 1), order=1)
    return img


def normalize_image(img_array):
    img_array = img_array.astype(np.float32)  # Ensure float type
    img_array -= img_array.min()  # Set min to 0
    img_array /= img_array.max()  # Scale to 0-1
    img_array *= 255  # Scale to 0-255
    return img_array.astype(np.uint8)  # Convert to uint8 for PIL


def adjust_brightness(image, factor=1.5):
    brightened = np.clip(
        image * factor, 0, 255
    )  # Ensure values stay within valid range
    return brightened.astype(np.uint8)


def convert_to_image(file_path):
    nifti_img = nib.load(file_path)
    data = nifti_img.get_fdata()

    data = resize_volume(data)
    data = normalize_image(data)
    data = adjust_brightness(data, 1.5)

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
