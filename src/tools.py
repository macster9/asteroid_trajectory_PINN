from geopy.geocoders import Nominatim


def get_lat_long(location):
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
            return False, False
        except IndexError:
            try:
                new_location = location + " Observatory"
                return geo_locator.geocode(new_location).latitude, geo_locator.geocode(new_location).longitude
            except AttributeError:
                try:
                    new_location = location.split("-")[1]
                    return geo_locator.geocode(new_location).latitude, geo_locator.geocode(new_location).longitude
                except AttributeError:
                    return False, False
                except IndexError:
                    return False, False


def gen_dict_extract(key, var, path=""):
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
    else:
        yield path + "/" + var


def get_path(path, directory):
    return next(gen_dict_extract(path, directory))


def get_eph_portal(designation, obs_code, t_ini, t_end, dt, dt_unit):
    return f"PSDB-portlet/ephemerides?des={designation}&oc={obs_code}&t0={t_ini}&t1={t_end}&ti={dt}&tiu={dt_unit}"


def datetime_str(yyyy, mo, dd, hh, mi):
    return f"{int(yyyy)}-{str(int(mo)).zfill(2)}-{str(int(dd)).zfill(2)}T{str(hh).zfill(2)}:{str(mi).zfill(2)}Z"


def get_hrs_minutes(first_last_observation_df):
    ini_days = first_last_observation_df["obs_d"].iloc[0]
    ini_hrs = int((ini_days - int(ini_days)) * 24)
    ini_minutes = int((((ini_days - int(ini_days)) * 24) - int((ini_days - int(ini_days)) * 24)) * 60)

    fin_days = first_last_observation_df["obs_d"].iloc[-1]
    fin_hrs = int((fin_days - int(fin_days)) * 24)
    fin_minutes = int((((fin_days - int(fin_days)) * 24) - int((fin_days - int(fin_days)) * 24)) * 60)
    return [ini_hrs, ini_minutes], [fin_hrs, fin_minutes]
