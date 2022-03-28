'''Utility functions

This module contains some auxiliary functions to read user input and 
display data on the terminal

Author: José Verdú Díaz

Methods
-------
clear
    Clear the terminal
print_title
    Prints the app title
print_menu
    Prints a menu
input_menu_option
    Make the user select an option from a menu
input_text
    Make the user enter a string
'''

import os
import sys
from tabulate import tabulate

from lib.models.Colors import Color
import lib.consistency as consistency

class suppress_output:
    def __init__(self, suppress_stdout=False, suppress_stderr=False):
        self.suppress_stdout = suppress_stdout
        self.suppress_stderr = suppress_stderr
        self._stdout = None
        self._stderr = None

    def __enter__(self):
        devnull = open(os.devnull, "w")
        if self.suppress_stdout:
            self._stdout = sys.stdout
            sys.stdout = devnull

        if self.suppress_stderr:
            self._stderr = sys.stderr
            sys.stderr = devnull

    def __exit__(self, *args):
        if self.suppress_stdout:
            sys.stdout = self._stdout
        if self.suppress_stderr:
            sys.stderr = self._stderr

def clear():
    '''Clear the terminal
    '''

    os.system('cls' if os.name == 'nt' else 'clear')


def print_title(debug = False):
    '''Prints the app title
    '''

    clear()
    clr = Color()
    print(clr.CYAN)
    print('      @@   @@ @@@@@ @@@@@@   @@@@@ ')
    print('      @@   @@  @@@  @@   @@ @@   @@')
    print('      @@@@@@@  @@@  @@@@@@  @@   @@')
    print('      @@   @@  @@@  @@      @@   @@')
    print('      @@   @@ @@@@@ @@       @@@@@ ')
    print()
    print('        *@@o.oO@@@@@@@@@@@Oo.o@@*')
    print('        o@@@@@@@@@@@@@@@@@@@@@@@o')
    print('         .@@@@@@@@@@@@@@@@@@@@@.')
    print('         °@@@@@@@@@@@@@@@@@@@@@°')
    print('        .°.     @@@@@@@     .°.')
    print('      o@@@@@@@##@@@@@@@##@@@@@@@o')
    print('    O@@@@@@@@@@@@@@@@@@@@@@@@@@@@@O')
    print('   @@@@@@@   *@@@@@@@@@@@*   @@@@@@@')
    print('  @@@@@@@@@@..@@@@@@@@@@@..@@@@@@@@@@')
    print('  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print('  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print('  *@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*')
    print('    °@@@@@@@@@@o°°   °°o@@@@@@@@@@@°')
    print('       °oOOo°              °oOOo°') 
    print(clr.BOLD)
    print('       Hyperion Image PrOcessing')
    print(clr.ENDC)
    
    if debug: print(f'{clr.RED}Debug mode active{clr.ENDC}')
    input('Press Enter to continue...')


def print_menu(options):
    '''Prints a menu

    Parameters
    ----------
    options
        Dictionary of options where the key is the option number and value 
        is the option name
    '''

    clr = Color()
    max_len = 0
    for k in options:
        if len(options[k]) > max_len: max_len = len(options[k])

    for k in options:
        if type(k) == str: print(f'\n{clr.PURPLE}{options[k].ljust(max_len + 4, "#")}{clr.ENDC}')
        else: print (f'{k} - {options[k]}')


def input_menu_option(options, cancel = True, display = [], show_menu = True):
    '''Make the user select an option from a menu

    Parameters
    ----------
    options
        Dictionary of options where the key is the option number and value 
        is the option name
    cancel, optional
        Add a cancel option, by default True
    display, optional
        List of strings to print between the title and the menu, by default []
    show_menu, optional
        Print the menu uptions, by default True

    Returns
    -------
        None if cancel is True and the user inputs 'c'
        Integer with the input of the user otherwise
    '''

    color = Color()
    while True:
        clear()
        for d in display: print(f'{d}\n')
        if show_menu: print_menu(options)
        try:
            if cancel: prompt = '\nSelect an option (\'c\' to cancel): '
            else: prompt = '\nSelect an option: '
            opt = input(prompt)

            if  opt == 'c': return None
            else: opt = int(opt)

            if opt not in list(options.keys()): input(f'{color.RED}Option doesn\'t exist! Press enter to continue...{color.ENDC}')
            else: return opt
        except: 
            input(f'{color.RED}Invalid option! Press enter to continue...{color.ENDC}')
            continue


def input_menu_toggle(options, cancel = True, display = [], show_menu = True):
    '''Make the user select an option from a menu

    Parameters
    ----------
    options
        Dictionary of options where the key is the option number and value 
        is the option name
    cancel, optional
        Add a cancel option, by default True
    display, optional
        List of strings to print between the title and the menu, by default []
    show_menu, optional
        Print the menu uptions, by default True

    Returns
    -------
        None if cancel is True and the user inputs 'c'
        Integer with the input of the user otherwise
    '''

    # WORK IN PROGRESS HERE!!!

    color = Color()
    toggle = [False for i in options]
    while True:
        clear()
        for d in display: print(f'{d}\n')

        if show_menu: print_menu(options)

        try:
            if cancel: prompt = '\nSelect an option to toggle (\'c\' to cancel): '
            else: prompt = '\nSelect an option to toggle: '
            opt = input(prompt)

            if  opt == 'c': return None
            else: opt = int(opt)

            if opt not in list(options.keys()): input(f'{color.RED}Option doesn\'t exist! Press enter to continue...{color.ENDC}')
            else: 
                toggle[opt] = not toggle[opt]
                options[opt].replace(options[opt][len(options[opt]) - 1:], '(X)')
        except: 
            input(f'{color.RED}Invalid option! Press enter to continue...{color.ENDC}')
            continue


def input_text(txt, cancel = True, display = [], checks = []):
    '''Make the user enter a string

    Parameters
    ----------
    txt
        String to be prompted to the user
    cancel, optional
        Add a cancel option, by default True
    display, optional
        List of strings to print between the title and the menu, by default []
    consistency, optional
        List of functions to pass the input text to, in order to
        perform consitency checks, by default []

    Returns
    -------
        _description_

    Raises
    ------
    None 
        if cancel is True and the user inputs 'c'
    String 
        with the input of the user otherwise
    '''

    color = Color()
    while True:
        clear()
        for d in display: print(f'{d}\n')
        try:
            prompt = f'\n{txt} (\'c\' to cancel): ' if cancel else f'\n{txt}: '
            name = str(input(prompt))

            if  name == 'c': return None
            else: 
                for c in checks: 
                    if not c(name): raise consistency.RepeatedNameException()
                return name

        except consistency.RepeatedNameException as e:
            input(f'{color.RED}{e} Press enter to continue...{color.ENDC}')
        except: 
            input(f'{color.RED}Invalid option! Press enter to continue...{color.ENDC}')
            continue


def input_yes_no(txt, display = []):
    '''Make the user input 'y' (yes) or 'n' (no)

    Parameters
    ----------
    txt
        String to be prompted to the user
    display, optional
        List of strings to print between the title and the menu, by default []

    Returns
    -------
    True
        if user enters 'y'
    False
        if user enters 'n'
    '''

    color = Color()
    while True:
        clear()
        for d in display: print(f'{d}\n')
        try:
            txt = f'\n{txt} (Enter \'y\' or \'n\'): {color.ENDC}'
            opt = str(input(txt))
            
            if opt == 'y': return True
            elif opt == 'n': return False
            else: input(f'{color.RED}Invalid option! Press enter to continue...{color.ENDC}')

        except: 
            input(f'{color.RED}Invalid option! Press enter to continue...{color.ENDC}')
            continue


def input_number(txt, cancel = True, display = [], range = None, type = 'int'):
    '''Make the user enter a number

    Parameters
    ----------
    txt
        String to be prompted to the user
    cancel, optional
        Add a cancel option, by default True
    display, optional
        List of strings to print between the title and the menu, by default []
    range, optional
        Tuple (min, max) If provided, checks that the number is inside the range
    type, optional
       type of the number, 'int' or 'float'

    Returns
    -------
    None 
        if cancel is True and the user inputs 'c'
    Number 
        with the input of the user otherwise
    '''

    color = Color()
    while True:
        clear()
        for d in display: print(f'{d}\n')
        try:
            prompt = f'\n{txt} (\'c\' to cancel): ' if cancel else f'\n{txt}: '
            number = str(input(prompt))

            if  number == 'c': return None
            else: 
                if type == 'int': number = int(number)
                elif type == 'float': number = float(number)

                if not None and range[0] <= number <= range[1]: return number
                else: input(f'{color.RED}The value is not inside the range! Press enter to continue...{color.ENDC}')

        except: 
            input(f'{color.RED}Invalid option! Press enter to continue...{color.ENDC}')
            continue


def input_df_toggle(sample, df, cancel = True, display = [], checks = []):
    color = Color()

    df['Toggle'] = '-'
    toggle = [False for i in range(df.shape[0])]

    while True:
        clear()
        for d in display: print(f'{d}\n')

        table = tabulate(df.loc[:, df.columns != 'Image'], headers = 'keys', tablefmt = 'github')
        print(table)

        try:
            txt = 'Select an option to toggle, or enter \'y\' to confirm'
            prompt = f'\n{txt} (\'c\' to cancel): ' if cancel else f'\n{txt}: '
            id = str(input(prompt))

            if  id == 'c': return None
            elif id == 'y':
                selected_images = [channel for i,channel in enumerate(df['Channel'].to_list()) if toggle[i]]
                return selected_images
            else: 
                id = int(id)

                for c in checks:
                    result = c(sample = sample, channel_id = id)
                    if not result is None: raise result

                toggle[id] = not toggle[id]
                df['Toggle'][id] = 'X' if toggle[id] else '-'

        except consistency.ThresholdExpectedException as e: 
            input(f'{color.RED}{e} Press enter to continue...{color.ENDC}')
            continue

        except Exception as e: 
            input(f'{color.RED}Invalid option! Press enter to continue...{color.ENDC}')
            input(e)
            continue