from geopy.geocoders import Nominatim
from src.config import *
import datetime
import os
import shutil
import numpy as np


def get_lat_long(df, row):
    code = row["obs_code"]
    observatory = df.loc[df["code"] == code]
    return round(observatory["latitude"].values[0], 3), round(observatory["longitude"].values[0], 3)


def get_lat_long_deprecated(location):
    """
    Function to get the lat and long of location from the name of an observatory site only.
    :param location: location name
    :type location: string
    :return: Latitude, Longitude | Bool, Bool
    """
    if any(ele in location.lower() for ele in space_scopes):
        print("\n", location)
        return False, False
    location = location.split("(")[0]
    geo_locator = Nominatim(user_agent="MyApp")
    try:
        new_location = location.split(",")[0]
        return geo_locator.geocode(new_location).latitude, geo_locator.geocode(new_location).longitude
    except AttributeError:
        try:
            new_location = location.split(",")[1]
            return geo_locator.geocode(new_location).latitude, geo_locator.geocode(new_location).longitude
        except AttributeError:
            print("\n", location)
            return False, False
        except IndexError:
            try:
                new_location = location + " Observatory"
                return geo_locator.geocode(new_location).latitude, geo_locator.geocode(new_location).longitude
            except AttributeError:
                try:
                    new_location = location.split("-")[1]
                    return geo_locator.geocode(new_location).latitude, geo_locator.geocode(new_location).longitude
                except (AttributeError, IndexError):
                    try:
                        new_location = location + " telescope"
                        return geo_locator.geocode(new_location).latitude, geo_locator.geocode(new_location).longitude
                    except AttributeError:
                        try:
                            new_location = location
                            for word in omit_words:
                                new_location = location.replace(word, "")
                            return geo_locator.geocode(new_location).latitude, geo_locator.geocode(
                                new_location).longitude
                        except (AttributeError, IndexError):
                            print("\n", location)
                            return False, False


def gen_dict_extract(key, var, path=""):
    """
    iterates through a dictionary finding all the key, value pairs within nested dictionaries. Used to get directory
    paths.
    :param key: dictionary key
    :type key: string
    :param var: dictionary value
    :type var: dictionary index
    :param path: directory path
    :type path: string
    :return: directory path(s)
    """
    if path == "":
        path = key
    if key == "core":
        yield var[key]
    if hasattr(var, 'items'):
        for k, v in var.items():
            if isinstance(v, dict):
                if k not in path:
                    path += "/" + k
                    yield path
                for result in gen_dict_extract(key, v, path=path):
                    yield result
            if k != "core":
                if not isinstance(v, dict):
                    yield path+"/"+v
    elif type(var) != dict:
        yield path + "/" + str(var)


def get_path(path, directory):
    """
    Iterable for the gen_dict_extract function.
    :param path: dictionary key
    :type path: string
    :param directory: dictionary value
    :type directory: dictionary index
    :return: the following iteration through the gen_dict_extract iterator.
    """
    return next(gen_dict_extract(path, directory))


def get_eph_portal(designation: int, obs_code, t_ini, t_end, dt, dt_unit):
    """
    Gets the ephemerides portal.
    :param designation: asteroid designation
    :param obs_code: observatory code
    :type obs_code: integer
    :param t_ini: observation start time
    :type t_ini: datetime string
    :param t_end: observation end time
    :param dt: timestep
    :type dt: integer
    :param dt_unit: timestep unit
    :type dt_unit: string
    :return: ESA NEO ephemerides portal
    """
    return f"PSDB-portlet/ephemerides?des={str(designation)}&oc={obs_code}&t0={t_ini}&t1={t_end}&ti={dt}&tiu={dt_unit}"


def datetime_str(yyyy, mo, dd, hh, mi):
    """
    Converts strings of date objects to a datetime format.
    :param yyyy: Year
    :param mo: Month
    :param dd: Day
    :param hh: Hour
    :param mi: Minute
    :return: Datetime string
    """
    return f"{int(yyyy)} {str(int(mo)).zfill(2)} {str(int(float(dd))).zfill(2)} {str(hh).zfill(2)} {str(mi).zfill(2)}"


def datetime_str_deprecated(yyyy, mo, dd, hh, mi):
    """
    Converts strings of date objects to a datetime format.
    :param yyyy: Year
    :param mo: Month
    :param dd: Day
    :param hh: Hour
    :param mi: Minute
    :return: Datetime string
    """
    return f"{int(yyyy)}-{str(int(mo)).zfill(2)}-{str(int(dd)).zfill(2)}T{str(hh).zfill(2)}:{str(mi).zfill(2)}Z"


def get_timestamp(row, index, anomalies):
    try:
        hrs, mins = get_hrs_minutes(row)
    except ValueError:
        anomalies.append([index, row["desig"]])
        return None
    time_string = datetime_str(row["obs_y"], row["obs_m"], row["obs_d"], hrs, mins)
    return datetime.datetime.strptime(time_string, "%Y %m %d %H %S").timestamp()


def get_hrs_minutes_eph(first_last_observation_df):
    """
    Converts decimal after day float into hh, mm
    :param first_last_observation_df: dataframe of the first and last observation of an asteroid
    :return: two lists of initial observation hrs and minutes and final observation hrs and minutes.
    """
    ini_days = first_last_observation_df["obs_d"].iloc[0]
    ini_hrs = int((ini_days - int(ini_days)) * 24)
    ini_minutes = int((((ini_days - int(ini_days)) * 24) - int((ini_days - int(ini_days)) * 24)) * 60)

    fin_days = first_last_observation_df["obs_d"].iloc[-1]
    fin_hrs = int((fin_days - int(fin_days)) * 24)
    fin_minutes = int((((fin_days - int(fin_days)) * 24) - int((fin_days - int(fin_days)) * 24)) * 60)
    return [ini_hrs, ini_minutes], [fin_hrs, fin_minutes]


def get_hrs_minutes(dataframe):
    days = float(dataframe["obs_d"])
    hrs = int((days - int(days)) * 24)
    mins = int((((days - int(days)) * 24) - int((days - int(days)) * 24)) * 60)
    return hrs, mins


def ra_to_deg(hh, mm, ss):
    return ((np.float32(hh) + np.float32(mm) / 60 + np.float32(ss / 3600)) * 15) - 90


def dec_to_deg(dd, mm, ss):
    return np.float32(dd) + np.float32(mm) / 60 + np.float32(ss) / 3600


def delete_temp_files():
    return shutil.rmtree("data/temp")