import datetime
import warnings
import astropy
from tqdm.auto import tqdm, trange
from src.config import directories, time_threshold, r_earth, km_in_au
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
import pickle


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


def get_distance(threshold=time_threshold, save=True):
    """
    Extracting number of multiple observations made for each object to calculate distance(s) to object. Concatenated and
     stored in asteroid_data.pkl.
    :param threshold: threshold for amount of time in seconds for two observations to be made to accurately calculate
    distance.
    :param save: Boolean, to save or not to save? That is the question.
    :return: list of number of multiple observations for each object.
    """
    count = []
    observatories = pd.read_csv("data/observatories.csv")
    anomalies = []
    old_row = None
    observations = {}
    for file in tqdm(os.listdir("data/temp/csvs/"), desc=f"Getting Distances... threshold: {threshold / 60 / 60}hrs"):
        counter = 0
        df = pd.read_csv(os.path.join("data/temp/csvs", file))
        code = ""
        timestamp_old = 0
        for index, row in tqdm(df.iterrows(), colour="red", desc=f"{file[:-4]}: ", leave=False):
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
                        if np.isnan([coords1, coords2]).any() or coords1 == coords2:
                            continue
                        counter += 1
                        x, y, z = calculate_distance(coords1, coords2, row, old_row)

                        if np.isnan([x, y, z]).any():
                            continue
                        try:
                            observations[file[:-4]].append([x, y, z, timestamp_new])
                        except KeyError:
                            observations[file[:-4]] = [[x, y, z, timestamp_new]]
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
    if save:
        with open("data/asteroid_data.pkl", "wb") as pickle_file:
            pickle.dump(observations, pickle_file)
    return count


def altitude(coords, row, obstime):
    """
    Calculates Alt/Az coordinates of asteroid
    :param coords: lat/long of observation
    :param row: dataframe row - supplies RA & DEC
    :param obstime: Time of observation
    :return: The angle above the horizon the asteroid is observed in radians.
    """
    loc = astropy.coordinates.EarthLocation(lat=coords[0], lon=coords[1])
    aa = astropy.coordinates.AltAz(location=loc, obstime=obstime)
    asteroid1 = SkyCoord(ra=ra_to_deg(row["RA_h"], row["RA_m"], row["RA_s"]) * u.degree,
                         dec=dec_to_deg(row["DEC_d"], row["DEC_m"], row["DEC_s"]) * u.degree,
                         obstime=obstime).transform_to(aa)
    return np.rad2deg((asteroid1.alt.hour * np.pi) / 12)


def calculate_distance(coords1, coords2, row, old_row):
    """
    Calculation of the distance to an object given 2 observations.
    :param coords1: Co-ordinates of first observation.
    :param coords2: Co-ordinates of second observation.
    :param row: Row in dataframe for all information of first observation.
    :param old_row: Row in dataframe for all information of second observation.
    :return: X, Y, Z heliocentric cartesian co-ordinates of asteroid for this observation.
    """
    geodesic_distance = geopy.distance.geodesic(coords1, coords2).m
    theta = np.deg2rad((360 * geodesic_distance) / (2 * np.pi * r_earth))
    distance = 2 * r_earth * np.sin(theta / 2)
    obstime = Time(f"{row['obs_y']}-{row['obs_m']}-{int(float(row['obs_d']))}")
    alt1 = np.deg2rad(altitude(coords1, row, obstime) - 90)
    alt2 = np.deg2rad(altitude(coords2, old_row, obstime) - 90)
    if np.diff([np.rad2deg(alt1), np.rad2deg(alt2)]) > 1.0:
        return np.nan, np.nan, np.nan
    baseline = abs(np.cos(alt1)*distance)
    ra_sep = ra_to_deg(row["RA_h"], row["RA_m"], row["RA_s"]) - ra_to_deg(old_row["RA_h"], old_row["RA_m"],
                                                                          old_row["RA_s"])
    dec_sep = dec_to_deg(row["DEC_d"], row["DEC_m"], row["DEC_s"]) - dec_to_deg(old_row["DEC_d"], old_row["DEC_m"],
                                                                                old_row["DEC_s"])
    ang_sep = np.sqrt(ra_sep ** 2 + dec_sep ** 2)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        asteroid_distance = baseline / ang_sep
        asteroid = SkyCoord(ra=ra_to_deg(row["RA_h"], row["RA_m"], row["RA_s"]) * u.degree,
                            dec=dec_to_deg(row["DEC_d"], row["DEC_m"], row["DEC_s"]) * u.degree,
                            distance=asteroid_distance * u.km,
                            frame="gcrs",
                            obstime=obstime).transform_to(
            frame="hcrs")
    return asteroid.cartesian.x.value, asteroid.cartesian.y.value, asteroid.cartesian.z.value


def collect_data(minimum=0.25, maximum=12, step=0.25):
    """
    Collecting sample data for how many distance calculations can be made given different thresholds.
    :param minimum: Minimum time in hours.
    :param maximum: Maximum time in hours.
    :param step: Timestep in hours.
    :return: Writes sample.json storing this information.
    """
    nb_observations = {}
    for i in trange(int(minimum * 60 * 60),
                    int((maximum * 60 * 60) + (minimum * 60 * 60)),
                    int(step * 60 * 60),
                    desc="Generating Histograms..."):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            nb_observations[i] = get_distance(threshold=i, save=False)
    json_object = json.dumps(nb_observations, indent=2)
    with open("data/sample.json", "w") as outfile:
        outfile.write(json_object)


def get_stats(data, lambda_=0.1):
    """
    Gets statistics for sample.json.
    :param data: dataset
    :param lambda_: lambda parameter.
    :return: mean, median, standard deviation, aggregate, and range
    """
    norm_data = boxcox(np.asarray([ele if ele > 0 else 1E-3 for ele in data]), lmbda=lambda_)
    mean = round(statistics.mean(norm_data), 3)
    med = round(statistics.median(norm_data), 3)
    st_dev = round(statistics.stdev(norm_data), 3)
    aggregate = sum(norm_data)
    range_ = round(min(norm_data), 3), round(max(norm_data), 3)
    return mean, med, st_dev, aggregate, range_


def sort_ephemerides():
    """
    Sorting ephemerides data into a pkl file for future data benchmarking.
    :return: Pkl file of ephemerides; ephemerides_data.pkl
    """
    eph = {}
    num_obs = []
    for file in tqdm(os.listdir("data/temp/eph_txt/"), desc=f"Getting Ephemerides..."):
        with open(os.path.join("data/temp/eph_txt", file), "r") as eph_file:
            lines = eph_file.readlines()[9:-2]
            if not lines:
                continue
            observation = []
            for line in tqdm(lines, colour="red", desc=f"{file[:-4]}", leave=False):
                solar_r = float(line[131:136]) * u.au
                g_lat = np.deg2rad(float(line[117:122])) * u.rad
                g_long = np.deg2rad(float(line[123:128])) * u.rad
                mjd = float(line[20:32])
                t = astropy.time.Time(mjd + 2400000.5, format='jd')
                utc = t.to_datetime()
                galactic_coords = SkyCoord(l=g_long, b=g_lat, distance=solar_r, frame='galactic').transform_to("hcrs")
                x = galactic_coords.cartesian.x.value * km_in_au
                y = galactic_coords.cartesian.y.value * km_in_au
                z = galactic_coords.cartesian.z.value * km_in_au
                observation.append([x, y, z, utc])
            eph[file[:-4]] = observation
            num_obs.append([observation[0][-1], observation[-1][-1]])
    with open("data/ephemerides_data.pkl", "wb") as eph_pickle:
        pickle.dump(eph, eph_pickle)
    return num_obs
