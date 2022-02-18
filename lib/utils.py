'''Utility functions

This module contains some auxiliary functions.

Author: José Verdú Díaz
'''

from dis import dis
import os

from lib.Colors import Color
from lib.consistency import RepeatedNameException

def clear(): 
    os.system('cls' if os.name == 'nt' else 'clear')

def print_title():
    clear()
    color = Color()
    print(f'{color.CYAN}88  88{color.RED}  88888{color.GREEN} Yb    dP{color.YELLOW} 8888b.')
    print(f'{color.CYAN}88  88{color.RED}     88{color.GREEN}  Yb  dP{color.YELLOW}   8I  Yb ')
    print(f'{color.CYAN}888888{color.RED} o.  88{color.GREEN}   YbdP{color.YELLOW}    8I  dY ')
    print(f'{color.CYAN}88  88{color.RED} \"bodP\'{color.GREEN}    YP{color.YELLOW}    8888Y\" ')
    print(color.ENDC)

def print_menu(options):
    for key in options.keys(): print (key, ' - ', options[key] )

def input_menu_option(options, cancel = True, display = [], show_menu = True):
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
