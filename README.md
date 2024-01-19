# Asteroid Trajectory Physics-Informed Neural Network

### Websites
* Near-Earth Object (NEA) Search Engine: https://neo.ssa.esa.int/search-for-asteroids
* Epherimedes page for example asteroid - needs scraping for distances https://neo.ssa.esa.int/search-for-asteroids?tab=eph&des=1566%20Icarus

To Do:
Go through list and scrape Epherimedes for each asteroid and get the distances of asteroid from Sun and Earth.
Then, make dataframes from these params and delete the old txt files. See help section for which is which.

PSDB-portlet/ephemerides?des=$desig&oc=$obscode&t0=$tini&t1=$tend&ti=$dt&tiu=$dtunit

e.g.

des=433+Eros&oc=500&t0=2019-08-25T00:00Z&t1=2019-09-01T00:00Z&ti=1&tiu=days

$desig

$obscode

$tini

$tend

$dt

$dtunit