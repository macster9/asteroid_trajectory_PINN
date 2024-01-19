import requests
import pandas as pd
import os
from src.config import *
from src.tools import datetime_str, get_hrs_minutes, get_eph_portal, get_path, get_lat_long
from tqdm import tqdm


def scrape_asteroids():
    search_results = pd.read_csv("data/searchResult.csv")
    for obj in tqdm(search_results["Object designation"], desc="Scraping Files: "):
        designation_url = esa_url + "PSDB-portlet/download?file=" + obj + ".rwo"
        r = requests.get(designation_url, allow_redirects=True)
        with open(os.path.join(get_path("data/temp", directories["data"]["temp"]["obs"]), obj + ".txt"), "wb") as file:
            file.write(r.content)
    return None


def get_observatory_list():
    observatory_db = requests.get("https://minorplanetcenter.net/iau/lists/ObsCodes.html").content.split(b"\n")[2:-2]
    data = []
    for line in tqdm(observatory_db, desc="Scrape Locations..."):
        code = line[:3].decode("ascii")
        latitude, longitude = get_lat_long(line[30:].decode("ascii"))
        if not latitude:
            print(f"Could not find {line[30:].decode('ascii')}")
            continue
        data.append([code, latitude, longitude])
    pd.DataFrame(data, columns=["code", "latitude", "longitude"]).to_csv(
        os.path.join(get_path("core", directories["data"]), "observatories.csv")
    )
    return None


def get_ephemerides():
    for file in tqdm(os.listdir(get_path("data/temp", directories["data"]["temp"]["csvs"])), desc="Reading CSVs..."):
        df = pd.read_csv(os.path.join(get_path("data/temp", directories["data"]["temp"]["csvs"]), file))
        first_obs = df.iloc[0]
        last_obs = df.iloc[-1]
        designation = int(first_obs["desig"])
        observation_code = 500  # geocentric observatory
        ini_time, fin_time = get_hrs_minutes(df)
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
