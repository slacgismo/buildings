"""AutoBEM-4 Building Data processing"""

import sys, os
import json
import pandas
import s3fs
import statistics
from geocoding import geohash

AWSPROFILE = "gridlabd"
CACHEDIR = "./data"
S3BUCKET = "loads.gridlabd.us"

def to_year(s):
    try:
        return int(float(s))
    except:
        return 0

def to_centroid(s,prec=9):
    return geohash(*[float(x) for x in s.split('/')],prec)

def to_footprint(s):
    seq = [to_centroid(x,11) for x in s.split("_")]
    def common(a,b):
        return min([n for n in range(len(a)) if a[n] != b[n]]) if a != b else 0
    return ','.join([x[common(x,seq[min(n,0)]):] for n,x in enumerate(seq)])

def to_area(s):
    return round(float(s)*0.09,1)

def to_height(s):
    return round(float(s),1)

def to_floors(s):
    try:
        return int(float(s))
    except:
        return 0

def to_windows(s):
    try:
        return statistics.mean([float(x) for x in s.split('_')])
    except:
        return 0.0

def is_mixed(s):
    return s != '0'

building_class = {'':0}
def to_class(s):
    global building_class
    try:
        return building_class[s]
    except:
        n = len(building_class)
        building_class[s] = n
        return n

building_type = {'':0}
def to_type(s):
    global building_type
    try:
        return building_type[s]
    except:
        n = len(building_type)
        building_type[s] = n
        return n

building_code = {'':0}
def to_code(s):
    global building_code
    try:
        return building_code[s]
    except:
        n = len(building_code)
        building_code[s] = n
        return n

def extract_data(profile=AWSPROFILE,s3bucket=S3BUCKET,cachedir=CACHEDIR,verbose=False,force=True):
    """Extracts the raw data from the AutoBEM-4 files"""
    s3 = s3fs.core.S3FileSystem(anon=(profile==None),profile=profile)
    for file in s3.ls(f"{s3bucket}/buildings/geodata"):
        local = os.path.basename(file)
        cache = f"{cachedir}/{local}"
        if not os.path.exists(cache) or force:
            check = f"{os.environ['HOME']}/Downloads/{local}"
            if os.path.exists(check):
                source = open(check,"rb")
                if verbose: print(f"Processing {local}...",flush=True)
            else:
                source = s3.open(file)
                if verbose: print(f"Downloading {local}...",flush=True)
            data = pandas.read_csv(source,compression='gzip',
                index_col=['state','county'],
                usecols = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
                header = 1,
                names = [
                    "id","county","state","climate","year","centroid","footprint","height","ground_area",
                    "code","class","mixed","type","windows","floors","floor_area",
                ],
                converters = {
                    "year" : to_year,
                    "centroid" : to_centroid,
                    "footprint" : to_footprint,
                    "height" : to_height,
                    "ground_area" : to_area,
                    "mixed" : is_mixed,
                    "windows" : to_windows,
                    "floors" : to_floors,
                    "floor_area" : to_area,
                    "class" : to_class,
                    "type" : to_type,
                    "code" : to_code,
                }).sort_index()
            os.makedirs(cachedir,exist_ok=True)
            for index in data.index.unique():
                file = f"{cachedir}/{'_'.join(index).replace(' ','_')}.csv.gz"
                if verbose: print(f"Writing {file}...",flush=True)
                data.loc[index].reset_index().drop(columns=['state','county']).to_csv(file,compression='gzip',index=False,header=True)
            with open("building_class.json","w") as fh:
                json.dump(building_class,fh,indent=4)
            with open("building_type.json","w") as fh:
                json.dump(building_type,fh,indent=4)
            with open("building_code.json","w") as fh:
                json.dump(building_code,fh,indent=4)

def load_data(state,county,cachedir=CACHEDIR):
    """Load the building data for the state and county"""
    file = f"{cachedir}/{state}_{county.replace(' ','_')}.csv.gz"
    return pandas.read_csv(file,index_col='id')

def analyse(state,county):
    """Analyse the building data for a state and county"""
    data = load_data(state,count)

    data.plot(kind='scatter',x='floors',y='height',grid=True).figure.savefig(f"{state}_{county}-floors-height.png")
    tall = data[data.floors>1]
    floor_height = tall.height / tall.floors
    avg_floor_height = floor_height.mean()
    std_floor_height = floor_height.std()
    # print(avg_floor_height,'+/-',std_floor_height)
    normaldist = statistics.NormalDist(0,1)
    median = normaldist.pdf(0)
    data['probability'] = [normaldist.pdf(x)/median for x in ( data.height - data.floors*avg_floor_height ) / std_floor_height]

    data.plot(kind='scatter',x='height',y='probability',grid=True).figure.savefig(f"{state}_{county}-height-probability.png")

    data.reset_index().set_index('probability').sort_index().to_csv(f"{state}_{county}.csv",index=True,header=True)
