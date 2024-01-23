esa_url = "https://neo.ssa.esa.int//o/"

directories = {
    "data": {
        "core": "data",
        "temp": {
            "csvs": "csvs",
            "obs": "obs_txt",
            "eph": "eph_txt"
        }
    }
}

space_scopes = ["spitzer", "hubble", "james webb"]

omit_words = ["Observatory", "Observatorio", "Astronomical", "Astrophysical", "Observatoire", "Osservatorio"]

time_threshold = 10800