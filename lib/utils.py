"""Utility functions

This module contains some auxiliary functions to read user input and 
display data on the terminal

Author: José Verdú-Díaz

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
"""
import os
import sys
import pandas as pd
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
    """Clear the terminal"""

    os.system("cls" if os.name == "nt" else "clear")


def print_title(debug=False):
    """Prints the app title"""

    clear()
    clr = Color()
    print(clr.CYAN)
    print("      @@   @@ @@@@@ @@@@@@   @@@@@ ")
    print("      @@   @@  @@@  @@   @@ @@   @@")
    print("      @@@@@@@  @@@  @@@@@@  @@   @@")
    print("      @@   @@  @@@  @@      @@   @@")
    print("      @@   @@ @@@@@ @@       @@@@@ ")
    print()
    print("        *@@o.oO@@@@@@@@@@@Oo.o@@*")
    print("        o@@@@@@@@@@@@@@@@@@@@@@@o")
    print("         .@@@@@@@@@@@@@@@@@@@@@.")
    print("         °@@@@@@@@@@@@@@@@@@@@@°")
    print("        .°.     @@@@@@@     .°.")
    print("      o@@@@@@@##@@@@@@@##@@@@@@@o")
    print("    O@@@@@@@@@@@@@@@@@@@@@@@@@@@@@O")
    print("   @@@@@@@   *@@@@@@@@@@@*   @@@@@@@")
    print("  @@@@@@@@@@..@@@@@@@@@@@..@@@@@@@@@@")
    print("  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print("  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print("  *@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*")
    print("    °@@@@@@@@@@o°°   °°o@@@@@@@@@@@°")
    print("       °oOOo°              °oOOo°")
    print(clr.BOLD)
    print("       Hyperion Image PrOcessing")
    print(clr.ENDC)

    if debug:
        print(f"{clr.RED}Debug mode active{clr.ENDC}")
    input("Press Enter to continue...")


def print_menu(options):
    """Prints a menu

    Parameters
    ----------
    options
        Dictionary of options where the key is the option number and value
        is the option name
    """

    clr = Color()
    max_len = 0
    for k in options:
        if len(options[k]) > max_len:
            max_len = len(options[k])

    for k in options:
        if type(k) == str:
            if k == "D":
                print(
                    f'\n{clr.RED}{clr.BOLD}{options[k].ljust(max_len + 4, "#")}{clr.ENDC}'
                )
            else:
                print(f'\n{clr.PURPLE}{options[k].ljust(max_len + 4, "#")}{clr.ENDC}')
        else:
            print(f"{k} - {options[k]}")


def input_menu_option(options, cancel=True, display=[], show_menu=True):
    """Make the user select an option from a menu

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
    """

    color = Color()
    while True:
        clear()
        for d in display:
            print(f"{d}\n")
        if show_menu:
            print_menu(options)
        try:
            if cancel:
                prompt = "\nSelect an option ('c' to cancel): "
            else:
                prompt = "\nSelect an option: "
            opt = input(prompt)

            if cancel and opt == "c":
                return None
            else:
                if opt.isdigit():
                    opt = int(opt)

            if opt not in list(options.keys()):
                input(
                    f"{color.RED}Option doesn't exist! Press enter to continue...{color.ENDC}"
                )
            else:
                return opt
        except:
            input(
                f"\n{color.RED}Invalid option! Press enter to continue...{color.ENDC}"
            )
            continue


def input_menu_toggle(options, cancel=True, untoggable=0, display=[]):
    """Make the user select an option from a menu

    Parameters
    ----------
    options
        Dictionary of options where the key is the option number and value
        is a bool. The first options must be the channels fro ma sample, and
        additional options must be appended at the end
    cancel, optional
        Add a cancel option, by default True
    untoggable, optional,
        Int indicating the amount of non-toggable options in the 1st row.
    display, optional
        List of strings to print between the title and the menu, by default []
        The last element must correspond to the toggable options, where:
            1rst row is: '| non-toggable | non-toggable | toggable | ... | toggable |'
            2nd row is an empty line (newline escape character)
            3rd row is the header of a table
            4th row is the separator is the separator between header and elements
            5th to Nth elements are toggable options on the table

            Example:
                |  (c)ancel  |  (s)how  |  (m)ask  |  (l)abels  |

                |    | Channel   | Label             |
                |----|-----------|-------------------|
                |  0 | BCKG(190) | 190BCKG           |
                |  1 | Ba(138)   | 138Ba             |
                |  2 | Bi(209)   | 209Bi             |

    Returns
    -------
        None if cancel is True and the user inputs 'c' (cancel)
        Dictionary of toggled options if the user inputs 's' (show)
    """

    clr = Color()
    while True:
        _display = display.copy()
        clear()
        for i, d in enumerate(_display):
            if i == len(_display) - 1:
                # Divide lines
                lines = d.split("\n")

                # Select Toggable options of first line
                first = lines[0].split("|")
                first = [f for f in first if f]
                _first = first[untoggable:]
                _first.reverse()

                # Color if toggle
                for j, f in enumerate(_first):
                    key = f.split("(")[1].split(")")[0]
                    k = len(first) - j - 1
                    if options[key]:
                        first[k] = f"{clr.GREEN}{f}{clr.ENDC}"
                    else:
                        first[k] = f"{clr.GREY}{f}{clr.ENDC}"
                lines[0] = f'| {" | ".join(first)} |'

                # Color if channel toggled
                for j, l in enumerate(lines[4:]):
                    if options[j]:
                        lines[j + 4] = (
                            l.replace("|", f"{clr.ENDC}|{clr.GREEN}") + clr.ENDC
                        )
                    else:
                        lines[j + 4] = (
                            l.replace("|", f"{clr.ENDC}|{clr.GREY}") + clr.ENDC
                        )

                print("\n".join(lines))

            else:
                print(f"{d}\n")

        try:
            if cancel:
                prompt = "\nSelect an option ('c' to cancel): "
            else:
                prompt = "\nSelect an option: "
            opt = input(prompt)

            if opt == "c":
                return None
            elif opt == "s":
                return options
            elif opt.isdigit():
                opt = int(opt)

            if opt not in list(options.keys()):
                input(
                    f"{clr.RED}Option doesn't exist! Press enter to continue...{clr.ENDC}"
                )
            else:
                options[opt] = not options[opt]

        except:
            input(f"{clr.RED}Invalid option! Press enter to continue...{clr.ENDC}")
            continue


def input_text(txt, cancel=True, display=[], checks=[]):
    """Make the user enter a string

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
    """

    color = Color()
    while True:
        clear()
        for d in display:
            print(f"{d}\n")
        try:
            prompt = f"\n{txt} ('c' to cancel): " if cancel else f"\n{txt}: "
            name = str(input(prompt))

            if name == "c":
                return None
            else:
                for c in checks:
                    if not c(name):
                        raise consistency.RepeatedNameException()
                return name

        except consistency.RepeatedNameException as e:
            input(f"{color.RED}{e} Press enter to continue...{color.ENDC}")
        except:
            input(f"{color.RED}Invalid option! Press enter to continue...{color.ENDC}")
            continue


def input_yes_no(txt, display=[]):
    """Make the user input 'y' (yes) or 'n' (no)

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
    """

    color = Color()
    while True:
        clear()
        for d in display:
            print(f"{d}\n")
        try:
            txt = f"\n{txt} (Enter 'y' or 'n'): {color.ENDC}"
            opt = str(input(txt))

            if opt == "y":
                return True
            elif opt == "n":
                return False
            else:
                input(
                    f"{color.RED}Invalid option! Press enter to continue...{color.ENDC}"
                )

        except:
            input(f"{color.RED}Invalid option! Press enter to continue...{color.ENDC}")
            continue


def input_number(txt, cancel=True, display=[], range=None, type="int"):
    """Make the user enter a number

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
    """

    color = Color()
    while True:
        clear()
        for d in display:
            print(f"{d}\n")
        try:
            prompt = f"\n{txt} ('c' to cancel): " if cancel else f"\n{txt}: "
            number = str(input(prompt))

            if number == "c":
                return None
            else:
                if type == "int":
                    number = int(number)
                elif type == "float":
                    number = float(number)

                if not None and range[0] <= number <= range[1]:
                    return number
                else:
                    input(
                        f"{color.RED}The value is not inside the range! Press enter to continue...{color.ENDC}"
                    )

        except:
            input(f"{color.RED}Invalid option! Press enter to continue...{color.ENDC}")
            continue


def input_df_toggle(sample, df, cancel=True, display=[], checks=[]):
    color = Color()

    df["Toggle"] = "-"
    toggle = [False for i in range(df.shape[0])]

    while True:
        clear()
        for d in display:
            print(f"{d}\n")

        table = tabulate(
            df.loc[:, df.columns != "Image"], headers="keys", tablefmt="github"
        )
        print(table)

        try:
            txt = "Select an option to toggle, or enter 'y' to confirm"
            prompt = f"\n{txt} ('c' to cancel): " if cancel else f"\n{txt}: "
            id = str(input(prompt))

            if id == "c":
                return None
            elif id == "y":
                selected_images = [
                    channel
                    for i, channel in enumerate(df["Channel"].to_list())
                    if toggle[i]
                ]
                return selected_images
            else:
                id = int(id)

                for c in checks:
                    result = c(sample=sample, channel_id=id)
                    if not result is None:
                        raise result

                toggle[id] = not toggle[id]
                df["Toggle"][id] = "X" if toggle[id] else "-"

        except consistency.ThresholdExpectedException as e:
            input(f"{color.RED}{e} Press enter to continue...{color.ENDC}")
            continue

        except Exception as e:
            input(f"{color.RED}Invalid option! Press enter to continue...{color.ENDC}")
            input(e)
            continue


def memory_usage(local_vars, global_vars):
    print("Displaying local variables...")
    var_names, var_sizes = [], []
    for var, obj in local_vars:
        var_names.append(var)
        var_sizes.append(sys.getsizeof(obj))

    df = (
        pd.DataFrame(list(zip(var_names, var_sizes)), columns=["Var", "Size"])
        .sort_values(["Size"], ascending=False)
        .reset_index(drop=True)
    )
    print(tabulate(df, headers="keys", tablefmt="github"))

    print("Displaying global variables...")
    var_names, var_sizes = [], []
    for var, obj in global_vars:
        var_names.append(var)
        var_sizes.append(sys.getsizeof(obj))

    df = (
        pd.DataFrame(list(zip(var_names, var_sizes)), columns=["Var", "Size"])
        .sort_values(["Size"], ascending=False)
        .reset_index(drop=True)
    )

    print(tabulate(df, headers="keys", tablefmt="github"))
    input("Press Enter to continue...")
