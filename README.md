# Asteroid Trajectory Physics-Informed Neural Network

### Websites
* Near-Earth Object (NEA) Search Engine: https://neo.ssa.esa.int/search-for-asteroids
* Epherimedes page for example asteroid - needs scraping for distances https://neo.ssa.esa.int/search-for-asteroids?tab=eph&des=1566%20Icarus

To Do:
Go through list and scrape Epherimedes for each asteroid and get the distances of asteroid from Sun and Earth.
Then, make dataframes from these params and delete the old txt files. See help section for which is which.

Results show that the optimum amount of time allowed between observations to determine distance to asteroid is 60 minutes.

For ephemerides function, the warning about "dubious year" is generated because we are predicting years/time in the future for whatever reason, and therefore cannot trust it.