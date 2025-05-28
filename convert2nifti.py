from pathlib import Path
import os

# input_dir = "C:/Users/dante/OneDrive/Documentos/Projects/Parkinson-MRI/dataset/control_group_t1_axial_new/PPMI"
input_dir = "C:/Users/dante/OneDrive/Documentos/datasets/pd_t2_sagital/PPMI"
output_dir = (
    "C:/Users/dante/OneDrive/Documentos/Projects/Parkinson-MRI/dataset/t2/pd_t2_sagital"
)
# os.system(f"cd ./{input_dir}")
print(input_dir)

count = 0

for subject_path in os.listdir(input_dir):
    # os.system(f"cd ./{subject_path}")
    is_dcm = False
    dmc_folder = ""
    current_folder = f"{input_dir}/{subject_path}"
    print(current_folder)
    while is_dcm == False:
        print(current_folder)
        for file in os.listdir(current_folder):
            if file.endswith(".dcm"):
                is_dcm = True
                dcm_fold = current_folder
                print("aaaaaaaa")
                break

        if is_dcm == True:
            os.system(f"dcm2niix -o {output_dir} {dcm_fold}/")
        else:
            next_folder = os.listdir(current_folder)[0]
            # os.system(f"cd ./{next_folder}")
        current_folder = f"{current_folder}/{next_folder}"

    # os.system(f"cd ./{input_dir}")
