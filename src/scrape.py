import urllib3.exceptions
from src.tools import *
from tqdm import tqdm
import pandas as pd
import numpy as np
import geopy.exc
import requests
import os


def get_observations():
    """
    Gets a list of all observations of asteroids on ESA NEO record. Contains RA & DEC but no Distance.
    :return: Print statement.
    """
    search_results = pd.read_csv("data/searchResult.csv")
    for obj in tqdm(search_results["Object designation"], desc="Scraping Files: "):
        designation_url = esa_url + "PSDB-portlet/download?file=" + obj + ".rwo"
        r = requests.get(designation_url, allow_redirects=True)
        with open(os.path.join(get_path("data/temp", directories["data"]["temp"]["obs"]), obj + ".txt"), "wb") as file:
            file.write(r.content)
    return print("Observations downloaded.")


def get_observatory_list():
    """
    Scrapes the list of observatories asteroid observations are made from and stores code/lat/long in observatories.csv
     in data directory.

     Approximating geocentric distance of observatories in Earth radii to be ~1, then computing arccos of parallax
     constant to get the geocentric latitude.
    :return: Print statement.
    """
    observatory_db = requests.get("https://minorplanetcenter.net/iau/lists/ObsCodes.html").content.split(b"\n")[2:-2]
    data = []
    for line in tqdm(observatory_db, desc="Scrape Locations..."):
        code = line[:3].decode("ascii")
        loc = line[30:].decode("ascii")
        long = line[5:13].decode("ascii")
        if line[13:21].decode("ascii") == "        ":
            continue
        lat = np.rad2deg(np.arccos(np.float64(line[13:21].decode("ascii"))))
        data.append([code, loc, long, lat])
    pd.DataFrame(data, columns=["code", "location", "longitude", "latitude"]).to_csv(
        os.path.join(get_path("core", directories["data"]), "observatories.csv")
    )
    return print("List of Observatories downloaded.")


def get_ephemerides():
    """
    Gets the ephemerides of all asteroids on ESA NEO record. Contains RA, DEC, and Distance.
    :return: Print statement.
    """
    for file in tqdm(os.listdir(get_path("data/temp", directories["data"]["temp"]["csvs"])), desc="Reading CSVs..."):
        df = pd.read_csv(os.path.join(get_path("data/temp", directories["data"]["temp"]["csvs"]), file))
        first_obs = df.iloc[0]
        last_obs = df.iloc[-1]
        designation = int(first_obs["desig"])
        observation_code = 500  # geocentric observatory
        ini_time, fin_time = get_hrs_minutes_eph(df)
        t_ini = datetime_str(first_obs["obs_y"], first_obs["obs_m"], first_obs["obs_d"], ini_time[0], ini_time[1])
        t_end = datetime_str(last_obs["obs_y"], last_obs["obs_m"], last_obs["obs_d"], fin_time[0], fin_time[1])
        dt = 30
        dt_unit = "days"
        ephemerides_url = esa_url + get_eph_portal(designation, observation_code, t_ini, t_end, dt, dt_unit)
        r = requests.get(ephemerides_url, allow_redirects=True)
        with open(os.path.join(get_path(
                "data/temp", directories["data"]["temp"]["eph"]),
                file[:-3] + "txt"), "wb") as new_file:
            new_file.write(r.content)
        return print("Ephemerides downloaded.")
