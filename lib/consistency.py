'''Consistency functions

This module contains some functions to perform consitency checks
and avoid bugs.

Author: José Verdú Díaz

Methods
-------
check_repeated_sample_name
    Check if the sample name already exists
'''

from lib.browse_samples import list_samples
from lib.Colors import Color

class RepeatedNameException(Exception):
    color = Color()
    def __init__(self, message=f'Repeated name!'):
        super(RepeatedNameException, self).__init__(message)

def check_repeated_sample_name(name):
    '''Check if the sample name already exists

    Parameters
    ----------
    name
        Sample name to be checked

    Returns
    -------
        True if the name doesn't exist
        False if the name already exists
    '''
    color = Color()

    table, df = list_samples()
    
    if name in list(df['Sample']):
        return False
    else: return True