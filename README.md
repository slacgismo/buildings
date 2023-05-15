
# GridLAB-D Buildings

Building data by state and county.  

## Loading data

~~~
>>> from buildings import Buildings
>>> data = Buildings(state="NH",county="Grafton",aws_profile="gridlabd")
>>> data
                          climate  year   centroid                                          footprint  height  ground_area  code  class  mixed  type  windows  floors  floor_area
id                                                                                                                                                                               
87MCM9QG+43HG-13-13-13-12      6A  1972  drv0d1h7y                         drv0d1hebqt,7t62,7gy3,kqfz     4.0        112.5     1      1  False     1     0.14       1       112.5
87MCM9QG+2325-11-11-13-11      6A  1972  drv0d1h6h    drv0d1h66se,yu,7dx,krm,m9f,m2k,nhf,3u2v,45e,744     3.9         96.3     1      1  False     1     0.14       1        96.3
87MCM9QG+352F-11-9-10-8        6A  1972  drv0d1hdc                          drv0d1hddhr,e048,e0zx,g1q     3.0         49.5     1      1  False     1     0.14       1        49.5
87MCPFQ9+7RCP-14-12-14-13      6A     0  drv0u6316                            drv0u63158x,28m,f55,t5k    28.2        136.3     5      1  False     0     0.14       1       136.3
87MCMCR3+56M2-10-4-10-4        6A  1988  drv0dc8em                            drv0dc8ej17,t52,w7z,n9d     4.6         53.7     2      1  False     5     0.14       1        53.7
...                           ...   ...        ...                                                ...     ...          ...   ...    ...    ...   ...      ...     ...         ...
87MCH6HR+6VM4-29-21-29-21      6A  1975  drszzj5s9                         drszzj5mjz2,td9r,sjm8,eb7e     4.2        483.6     1      4  False   150     0.07       1       483.6
87MCPCVC+VP4X-17-17-19-17      6A  1972  drv0g5qr5                drv0g5qr2by,t3m,qzpd,qvdg,qty7,q6xy     4.1        242.4     1      8  False     5     0.21       1       242.4
87PC636M+9FXQ-16-14-17-13      6A  1920  druge825t                          druge825jyw,7wb,hjve,7bm3     7.4        148.5     1      1  False    20     0.14       2       296.9
87PC4397+H7H3-23-12-23-13      6A     0  drufgp95r                         drufgp968z0,4v6t,hn9y,7fn2    17.1        267.1     1      8  False     0     0.21       1       267.1
87M9PP46+R5Q3-16-16-16-16      6A     0  dru8eh8kh  dru8eh87ggb,96,fkr,fwt,k162,kdsx,kect,ks5g,kqn...     7.0        207.0     2      1  False    21     0.14       2       414.1

[47529 rows x 13 columns]
~~~

Notes

1. Prior to August 7, 2023 access is retricted to users with permission to read the AWS repository using an AWS profile for the HiPAS GridLAB-D project.

## Data Fields

| Field | Type | Description
| ----- | ---- | -----------
| `id` | `str` | Building unique identifier (see AutoBEM-4 for details)
| `climate` | `str` | Building climate zone
| `year` | `int` | Year of construction
| `centroid` | `str` | Geohash of building centroid
| `footprint` | `str` | Geohash of building footprint (see Note 1)
| `height` | `real` | Building height from imagery (m^2)
| `ground_area` | `real` | Building footprint area (m^2)
| `code` | `int` | Building code (see `building_code.json`)
| `class` | `int` | Building class (see `building_class.json`)
| `mixed` | `bool` | Mixed type flag
| `type` | `int` | Building type (see `building_type.json`)
| `windows` | `real` | Average window wall ratio (pu wall area)
| `floors` | `int` | Number of floors
| `floor_area`| `real` | Total conditioned floor area (m^2)

Notes:

1. The building footprint is coded using geohashes, except that only
the trailing characters of the hash code are recorded. For example

~~~
drv0d1hebqt,7t62,7gy3,kqfz
~~~

should be interpreted as

~~~
drv0d1hebqt,drv0d1h7t62,drv0d1h7gy3,drv0d1hkqfz
~~~

## Data Accessors

Some fields are encoded for storage efficient. Data accessors are provided to decode these fields.

### `get_centroid(index)`

Get the building centroid. Centroid are recorded with an accuracy of 2.4 cos(latitude) meters.

### `get_footprint(index)`

Get the building footprint. Footprint vertices are recorded with an accurage of 7.4 cos(latitude) meter.

### `get_class(index)`

Get the building class. See `building_class.json` for a list of known classes.

### `get_code(index)`

Get the building construction code. See `building_code.json` for a list of known building codes.

### `get_type(index)`

Get the building type. See `building_type.json` for a list of known building types.

## Reference

* New, Joshua et al, "Model America - data and models of every U.S. building", Oak Ridge National Laboratory, 4/13/2021. URL: https://doi.ccs.ornl.gov/ui/doi/339

