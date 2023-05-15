"""GridLAB-D building data"""

import os
import json
import pandas
import boto3
from geocoding import geocode

CACHEDIR = os.path.join(os.environ["GLD_ETC"] if "GLD_ETC" in os.environ else "/usr/local/opt/gridlabd/current/share/gridlabd","buildings","US")

class Buildings:
    """Building data accessor

    The building data accessor is implemented using a Pandas DataFrame.

    Example:
    
        >>> from buildings import Buildings
        >>> buildings = Buildings("ME","Knox",aws_profile="gridlabd")
        >>> buildings["87PG4V7P+M843-10-8-10-9"].floor_area
        117.1
    """
    default_s3bucket = "buildings.gridlabd.us"
    default_aws_profile = None
    building_class = list(json.load(open("building_class.json")).keys())
    building_code = list(json.load(open("building_code.json")).keys())
    building_type = list(json.load(open("building_type.json")).keys())

    def __init__(self, 
            state, 
            county, 
            country = "US", 
            s3bucket = None, 
            aws_profile = None, 
            index='id'):
        """Load building data

        Arguments:

            state (str)         - state postal code

            county (str)        - county name
            
            country (str)       - country to read data from (default is 'US')
            
            s3bucket (str)      - S3 bucket to download data from (default is 'buildings.gridlabd.us')
            
            aws_profile (str)   - AWS profile name (default is None)
            
            index (list or str) - index column(s) to use (default is 'id')
        """

        name = f"{state}_{county.replace(' ','_')}.csv.gz"
        file = os.path.join(CACHEDIR,name)
        if not os.path.exists(file):
            if not s3bucket:
                s3bucket = self.default_s3bucket
            if not aws_profile:
                aws_profile = self.default_aws_profile
            session = boto3.Session(profile_name=aws_profile) if aws_profile else boto3
            s3 = session.client('s3')
            os.makedirs(CACHEDIR,exist_ok=True)
            s3.download_file(s3bucket,f"{country}/{state}_{county}.csv.gz",file)
            s3.close()
        self.df = pandas.read_csv(file,index_col=index)

    def __repr__(self):
        return str(self.df)

    def __getattr__(self,name):
        return getattr(self.df,name)

    def __getitem__(self,index):
        return self.df.loc[index]

    def get_centroid(self,index):
        """Get a latitude and longitude of a point inside the building"""
        return geocode(self.loc[index].centroid)

    def get_footprint(self,index):
        """Get a latitude and longitude of the building footprint"""
        vertex = self.loc[index].footprint.split(",")
        root = vertex[0]
        footprint = [geocode(root)]
        for item in vertex[1:]:
            loc = root[:-len(item)] + item
            footprint.append(geocode(loc))
        return footprint

    def get_class(self,index):
        """Get a building class"""
        return self.building_class[self.loc[index]['class']]

    def get_code(self,index):
        """Get a building construction code"""
        return self.building_code[self.loc[index]['code']]

    def get_type(self,index):
        """Get a building type"""
        return self.building_type[self.loc[index]['type']]
    
if __name__ == "__main__":

    import unittest

    class Test(unittest.TestCase):

        def test_default(self):

            buildings = Buildings("ME","Knox",aws_profile="gridlabd")
            index = "87PG4V7P+M843-10-8-10-9"
            self.assertEqual(buildings[index].centroid,"dryfgq8x6")
            self.assertEqual(buildings.get_centroid(index),(44.1141, -69.1142))
            self.assertEqual(buildings.get_footprint(index),[(44.11418, -69.11418), (44.11414, -69.11411), (44.11408, -69.11417), (44.11411, -69.11425)])
            self.assertEqual(buildings.get_class(index),"IECC")
            self.assertEqual(buildings.get_code(index),"DOE-Ref-Pre-1980")
            self.assertEqual(buildings.get_type(index),"SINGLE FAMILY RESIDENTIAL")
            self.assertEqual(buildings[index].year,1940)
            self.assertEqual(buildings[index].climate,"6A")
            self.assertEqual(buildings[index].height,6.1)
            self.assertEqual(buildings[index].ground_area,58.5)
            self.assertEqual(buildings[index].mixed,False)
            self.assertEqual(buildings[index].windows,0.14)
            self.assertEqual(buildings[index].floors,2)
            self.assertEqual(buildings[index].floor_area,117.1)

    unittest.main()
