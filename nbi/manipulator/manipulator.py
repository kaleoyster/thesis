"""Contains NBI data manipulation functions
"""
import sys

__author__ = 'Akshay Kale'
__copyright__ = 'GPL'
__credit__ = []
__email__ = 'akale@unomaha.edu'

class Manipulator:
    def __init__(self):
        pass

    def mapper(self, keys):
        """Creates dictionary"""
        pass
     
    def get_values(self, keys, dictionary):
        """Return a list of values and keys"""
        return [dictionary[key] for key in keys]

    def create_dictionary(self, keys, values):
        return {key: value for key, value in zip(keys, values)}
        
    def transform_timeseries(self):
        pass
        
