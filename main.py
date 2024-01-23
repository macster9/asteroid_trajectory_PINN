from src.manipulate import *
from src.scrape import *
import datetime
import pandas as pd
from src.config import *
import os


def get_timestamp(row, index, anomalies):
    try:
        hrs, mins = get_hrs_minutes(row)
    except ValueError:
        anomalies.append([index, row["desig"]])
        return None
    time_string = datetime_str(row["obs_y"], row["obs_m"], row["obs_d"], hrs, mins)
    return datetime.datetime.strptime(time_string, "%Y %m %d %H %S").timestamp()


if __name__ == "__main__":
    observatories = pd.read_csv("data/observatories.csv")["code"].to_numpy()
    anomalies = []
    for file in os.listdir("data/temp/csvs/"):
        counter = 0
        df = pd.read_csv(os.path.join("data/temp/csvs", file))
        code = ""
        timestamp_old = 0
        for index, row in df.iterrows():
            if code != row["obs_code"]:
                if (code in observatories) and (row["obs_code"] in observatories):
                    # print(code, row["obs_code"])
                    if int(row["obs_y"]) < 1970:
                        continue
                    timestamp_new = get_timestamp(row, index, anomalies)
                    if timestamp_new is None:
                        continue
                    dt = timestamp_new-timestamp_old
                    if dt < time_threshold:
                        # print(datetime.datetime.fromtimestamp(dt), dt)
                        counter += 1
            code = row["obs_code"]
            if int(row["obs_y"]) > 1970:
                timestamp_old = get_timestamp(row, index, anomalies)
                if timestamp_old is None:
                    continue
            else:
                continue
        print(counter)
        # get_distance()
    print(anomalies)
    # todo: generate histogram of number of observations where we can calculate distances for each asteroid
