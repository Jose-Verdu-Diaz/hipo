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
from tabulate import tabulate

from lib.Colors import Color
from lib.consistency import RepeatedNameException


def clear():
    '''Clear the terminal
    '''

    os.system('cls' if os.name == 'nt' else 'clear')


def print_title():
    '''Prints the app title
    '''

    clear()
    color = Color()
    print(f'{color.CYAN}88  88{color.RED}  88888{color.GREEN} Yb    dP{color.YELLOW} 8888b.')
    print(f'{color.CYAN}88  88{color.RED}     88{color.GREEN}  Yb  dP{color.YELLOW}   8I  Yb ')
    print(f'{color.CYAN}888888{color.RED} o.  88{color.GREEN}   YbdP{color.YELLOW}    8I  dY ')
    print(f'{color.CYAN}88  88{color.RED} \"bodP\'{color.GREEN}    YP{color.YELLOW}    8888Y\" ')
    print(color.ENDC)


def print_menu(options):
    '''Prints a menu

    Parameters
    ----------
    options
        Dictionary of options where the key is the option number and value 
        is the option name
    '''

    for key in options.keys(): print (key, ' - ', options[key] )


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
        print_title()
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


def input_text(txt, cancel = True, display = [], consistency = []):
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
        print_title()
        for d in display: print(f'{d}\n')
        try:
            prompt = f'\n{txt} (\'c\' to cancel): ' if cancel else f'\n{txt}: '
            name = str(input(prompt))

            if  name == 'c': return None
            else: 
                for c in consistency: 
                    if not c(name): raise RepeatedNameException()
                return name

        except RepeatedNameException as e:
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
        print_title()
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
        print_title()
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


def input_df_toggle(df, cancel = True, display = []):
    color = Color()

    df['Toggle'] = '-'
    toggle = [False for i in range(df.shape[0])]

    while True:
        print_title()
        for d in display: print(f'{d}\n')

        table = tabulate(df, headers = 'keys', tablefmt = 'github')
        print(table)

        try:
            txt = 'Select an option to toggle, or enter \'y\' to confirm'
            prompt = f'\n{txt} (\'c\' to cancel): ' if cancel else f'\n{txt}: '
            id = str(input(prompt))

            if  id == 'c': return None
            elif id == 'y': return toggle
            else: 
                id = int(id)
                toggle[id] = not toggle[id]
                df['Toggle'][id] = 'X' if toggle[id] else '-'


        except: 
            input(f'{color.RED}Invalid option! Press enter to continue...{color.ENDC}')
            continue