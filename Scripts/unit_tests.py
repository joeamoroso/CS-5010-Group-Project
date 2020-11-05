# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 18:09:56 2020

@author: Joe
"""
import unittest
import os
from LEHD_Script import *


# =============================================================================
# Check if all 45 files are read in from the Census
# =============================================================================

class test_scraped_files(unittest.TestCase):

    def test_num_correct(self): 
        files = [f for f in os.listdir() if f.endswith('.csv.gz')] # Get all downloaded files into object
        self.assertEqual(len(files),45) # Assert that there are 45 tar files.



if __name__ == '__main__':
    unittest.main()    


import unittest
import os
from LEHD_Script import *


# =============================================================================
# Make sure all GEOIDs are 11 digits
# =============================================================================

class test_geoids(unittest.TestCase):
    
    def test_geoid_correct(self):
        ids = df_tract['GEOID'].astype('str')
        id_list = list(map(len,ids))
        ret = [x for x in id_list if x == 11]
        self.assertTrue(len(id_list),len(ret))    

    

if __name__ == '__main__':
    unittest.main()    
