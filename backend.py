import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import nibabel as nib
from scipy import ndimage
import json
import sys
from torchvision.models.video import r3d_18, R3D_18_Weights

MODEL_PATH = "parkinson_classification_RESNET_2.pth"


def load_model():
    try:
        weights = R3D_18_Weights.DEFAULT
        model = r3d_18(weights=weights)

        model.fc = nn.Sequential(
            nn.Linear(model.fc.in_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 1),
            nn.Sigmoid(),
        )

        for param in model.parameters():
            param.requires_grad = False
        for param in model.fc.parameters():
            param.requires_grad = True

        model.stem[0] = nn.Conv3d(
            in_channels=1,
            out_channels=model.stem[0].out_channels,
            kernel_size=model.stem[0].kernel_size,
            stride=model.stem[0].stride,
            padding=model.stem[0].padding,
            bias=model.stem[0].bias is not None,
        )

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)

        sys.stderr.write(f"Loading model from: {MODEL_PATH}\n")  # Debugging log
        model.load_state_dict(
            torch.load(MODEL_PATH, map_location=device, weights_only=True)
        )  # Removed `weights_only`
        model.eval()

        return model, device

    except Exception as e:
        sys.stderr.write(f"Error loading model: {e}\n")
        print(json.dumps({"error": str(e)}))  # Ensure JSON output
        sys.exit(1)


model, device = load_model()


def read_nifti_file(filepath):
    scan = nib.load(filepath)
    scan = scan.get_fdata()
    return scan


def zscore_normalize(volume):
    if volume.ndim > 3:
        volume = volume[:, :, :, 0]

    mean = np.mean(volume)
    std = np.std(volume)
    volume = (volume - mean) / std
    return volume.astype("float32")


def resize_volume(img):
    desired_depth, desired_width, desired_height = 64, 128, 128

    depth_factor = img.shape[-1] / desired_depth
    width_factor = img.shape[0] / desired_width
    height_factor = img.shape[1] / desired_height

    img = ndimage.rotate(img, 90, reshape=False)
    img = ndimage.zoom(
        img, (1 / width_factor, 1 / height_factor, 1 / depth_factor), order=1
    )
    return img


def process_scan(path):
    volume = read_nifti_file(path)
    volume = zscore_normalize(volume)
    volume = resize_volume(volume)
    volume[volume < 0] = 0  # Ensure non-negative values
    return torch.Tensor(volume).unsqueeze(0).unsqueeze(0)


def run_inference(nifti_file):
    try:
        volume = process_scan(nifti_file).to(device)
        with torch.no_grad():
            output = model(volume)

        prediction = 1 if output.item() > 0.5 else 0
        diagnosis = "Parkinson's Disease" if prediction == 1 else "Control Group"

        result = {
            "Output": float(output.item()),
            "Prediction": prediction,
            "Diagnosis": diagnosis,
        }

        print(json.dumps(result))  # Ensure only JSON output
        return result

    except Exception as e:
        sys.stderr.write(f"Error in inference: {e}\n")  # Log error
        print(json.dumps({"error": str(e)}))
        return {"error": str(e)}


if __name__ == "__main__":
    try:
        # Read input as JSON
        input_json = sys.stdin.read().strip()
        if not input_json:
            raise ValueError("No input received")

        data = json.loads(input_json)
        nifti_file = data.get("file_path")

        if not nifti_file:
            raise ValueError("Missing file path.")

        slices = run_inference(nifti_file)

    except Exception as e:
        sys.stderr.write(f"Script error: {e}\n")  # Log script errors
        print(json.dumps({"error": str(e)}))
