from tqdm import tqdm
from config import directories, data_storage
from tools import get_path
import pandas as pd
import os


def convert_asteroid_file():
    for file in tqdm(os.listdir(get_path("data/temp", directories["data"]["temp"]["obs"])), desc="Saving to CSVs"):
        with open(os.path.join(get_path("data/temp", directories["data"]["temp"]["obs"]), file), "rb") as asteroid_data:
            data = asteroid_data.readlines()
            for line in data:
                if "=" in line[17:21].decode("ascii"):
                    break
                if "." not in line[56:64].decode("ascii").strip():
                    continue
                data_storage["desig"].append(line[:11].decode("ascii").strip())
                data_storage["obs_y"].append(line[17:21].decode("ascii").strip())
                data_storage["obs_m"].append(line[22:24].decode("ascii").strip())
                data_storage["obs_d"].append(line[25:40].decode("ascii").strip())
                data_storage["time_acc"].append(line[40:49].decode("ascii").strip())
                data_storage["RA_h"].append(line[50:52].decode("ascii").strip())
                data_storage["RA_m"].append(line[53:55].decode("ascii").strip())
                data_storage["RA_s"].append(line[56:64].decode("ascii").strip())
                data_storage["RA_acc"].append(line[64:77].decode("ascii").strip())
                data_storage["RA_RMS"].append(line[77:82].decode("ascii").strip())
                data_storage["DEC_d"].append(line[103:107].decode("ascii").strip())
                data_storage["DEC_m"].append(line[107:110].decode("ascii").strip())
                data_storage["DEC_s"].append(line[110:117].decode("ascii").strip())
                data_storage["DEC_acc"].append(line[117:126].decode("ascii").strip())
                data_storage["DEC_RMS"].append(line[130:136].decode("ascii").strip())
            df = pd.DataFrame(data_storage)
            df.to_csv(os.path.join(get_path("data/temp",
                                            directories["data"]["temp"]["csvs"]),
                                   file[:-4].replace(" ", "_") + ".csv"))
    return None