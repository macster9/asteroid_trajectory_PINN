from tqdm import tqdm
from src.config import directories
from src.tools import get_path
import pandas as pd
import os


def convert_asteroid_file():
    """
    ESA NEO site files are .rwo files - essentially proprietary binaries and have a Linux-only interface. So, we
    download these files and then establish which characters are in which rows and convert to csv format.
    :return: Print statement.
    """
    for file in tqdm(os.listdir(get_path("data/temp", directories["data"]["temp"]["obs"])), desc="Saving to CSVs"):
        csv_data = {
            "desig": [],
            "obs_y": [],
            "obs_m": [],
            "obs_d": [],
            "time_acc": [],
            "RA_h": [],
            "RA_m": [],
            "RA_s": [],
            "RA_acc": [],
            "RA_RMS": [],
            "DEC_d": [],
            "DEC_m": [],
            "DEC_s": [],
            "DEC_acc": [],
            "DEC_RMS": [],
            "obs_code": []
        }
        with open(os.path.join(get_path("data/temp", directories["data"]["temp"]["obs"]), file), "rb") as asteroid_data:
            data = asteroid_data.readlines()[7:]
            for line in data:
                if "=" in line[17:21].decode("ascii"):
                    break
                if "." not in line[56:64].decode("ascii").strip():
                    continue
                csv_data["desig"].append(line[:11].decode("ascii").strip())
                csv_data["obs_y"].append(line[17:21].decode("ascii").strip())
                csv_data["obs_m"].append(line[22:24].decode("ascii").strip())
                csv_data["obs_d"].append(line[25:40].decode("ascii").strip())
                csv_data["time_acc"].append(line[40:49].decode("ascii").strip())
                csv_data["RA_h"].append(line[50:52].decode("ascii").strip())
                csv_data["RA_m"].append(line[53:55].decode("ascii").strip())
                csv_data["RA_s"].append(line[56:64].decode("ascii").strip())
                csv_data["RA_acc"].append(line[64:77].decode("ascii").strip())
                csv_data["RA_RMS"].append(line[77:82].decode("ascii").strip())
                csv_data["DEC_d"].append(line[103:107].decode("ascii").strip())
                csv_data["DEC_m"].append(line[107:110].decode("ascii").strip())
                csv_data["DEC_s"].append(line[110:117].decode("ascii").strip())
                csv_data["DEC_acc"].append(line[117:126].decode("ascii").strip())
                csv_data["DEC_RMS"].append(line[130:136].decode("ascii").strip())
                csv_data["obs_code"].append(line[180:183].decode("ascii").strip())
            df = pd.DataFrame(csv_data)
            df.to_csv(os.path.join(get_path("data/temp",
                                            directories["data"]["temp"]["csvs"]),
                                   file[:-4].replace(" ", "_") + ".csv"))
    return print("Converted .rwo files to .csv")


def get_distance(observation):
    return None
