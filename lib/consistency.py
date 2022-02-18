'''Consistency functions

This module contains some functions to keep the app consistent
and avoid bugs.

Author: José Verdú Díaz
'''

from lib.browse_samples import list_samples
from lib.Colors import Color

class RepeatedNameException(Exception):
    color = Color()
    def __init__(self, message=f'Repeated name!'):
        super(RepeatedNameException, self).__init__(message)

def check_repeated_sample_name(name):
    color = Color()

    table, df = list_samples()
    
    if name in list(df['Sample']):
        #input(f'{color.RED}Repeated name! Press enter to continue...{color.ENDC}')
        return False
    else: return True