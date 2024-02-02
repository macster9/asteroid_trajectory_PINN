import astropy
from tqdm.auto import tqdm, trange
from src.config import directories, time_threshold, r_earth
from src.tools import get_path, get_timestamp, get_lat_long, ra_to_deg, dec_to_deg
import json
import pandas as pd
import statistics
from scipy.stats import boxcox
import geopy.distance
import os
import numpy as np
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.time import Time


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


def get_distance(threshold=time_threshold):
    count = []
    observatories = pd.read_csv("data/observatories.csv")
    # observatories.index = observatories["code"]
    anomalies = []
    old_row = None
    observations = []
    for file in tqdm(os.listdir("data/temp/csvs/"), desc=f"Getting Distances... threshold: {threshold/60/60}hrs"):
        counter = 0
        df = pd.read_csv(os.path.join("data/temp/csvs", file))
        code = ""
        timestamp_old = 0
        for index, row in df.iterrows():
            if code != row["obs_code"]:
                if (code in observatories["code"].to_numpy()) and (row["obs_code"] in observatories["code"].to_numpy()):
                    if int(row["obs_y"]) < 1970:
                        continue
                    timestamp_new = get_timestamp(row, index, anomalies)
                    if (timestamp_new is None) or (old_row is None):
                        continue
                    dt = timestamp_new - timestamp_old
                    if dt < threshold:
                        coords1 = get_lat_long(observatories, old_row)
                        coords2 = get_lat_long(observatories, row)
                        if coords1 == coords2:
                            continue
                        counter += 1
                        x, y, z = calculate_distance(coords1, coords2, row, old_row)
                        if type(x) == str:
                            continue
                        # print(x, y, z)
            code = row["obs_code"]
            if int(row["obs_y"]) > 1970:
                timestamp_old = get_timestamp(row, index, anomalies)
                old_row = row
                if timestamp_old is None:
                    continue
            else:
                old_row = None
                continue
        count.append(counter)
    return count


def calculate_distance(coords1, coords2, row, old_row):
    try:
        geodesic_distance = geopy.distance.geodesic(coords1, coords2).m
        theta = np.deg2rad((360*geodesic_distance)/(2*np.pi*r_earth))
        distance = 2 * r_earth * np.sin(theta/2)
        ra_sep = ra_to_deg(row["RA_h"], row["RA_m"], row["RA_s"]) - ra_to_deg(old_row["RA_h"], old_row["RA_m"], old_row["RA_s"])
        dec_sep = dec_to_deg(row["DEC_d"], row["DEC_m"], row["DEC_s"]) - dec_to_deg(old_row["DEC_d"], old_row["DEC_m"], old_row["DEC_s"])
        ang_sep = np.sqrt(ra_sep**2 + dec_sep**2)
        asteroid_distance = distance/ang_sep
        asteroid = SkyCoord(ra=ra_to_deg(row["RA_h"], row["RA_m"], row["RA_s"])*u.degree,
                                                    dec=dec_to_deg(row["DEC_d"], row["DEC_m"], row["DEC_s"])*u.degree,
                                                    distance=asteroid_distance*u.km,
                                                    frame="gcrs",
                                                    obstime=[Time(f"{row['obs_y']}-{row['obs_m']}-{int(row['obs_d'])}")]).transform_to(frame="hcrs")      
    except (RuntimeError, RuntimeWarning, ValueError):
        return "0", "0", "0"
    return asteroid.cartesian.x, asteroid.cartesian.y, asteroid.cartesian.z


def collect_data(minimum=0.25, maximum=24, step=0.25):
    nb_observations = {}
    for i in trange(minimum * 60 * 60,
                    (maximum * 60 * 60) + (minimum * 60 * 60),
                    step * 60 * 60,
                    desc="Generating Histograms..."):
        nb_observations[i] = get_distance(threshold=i)
    json_object = json.dumps(nb_observations, indent=2)
    with open("data/sample.json", "w") as outfile:
        outfile.write(json_object)


def get_stats(data, lambda_=0.1):
    norm_data = boxcox(data, lmbda=lambda_)
    mean = round(statistics.mean(norm_data), 3)
    med = round(statistics.median(norm_data), 3)
    st_dev = round(statistics.stdev(norm_data), 3)
    aggregate = sum(norm_data)
    range_ = round(min(norm_data), 3), round(max(norm_data), 3)
    return mean, med, st_dev, aggregate, range_
