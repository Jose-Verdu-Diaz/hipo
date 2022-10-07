'''Tool for processing and analysing hyperion imaging.

Author: José Verdú Díaz

This is the entry point of the application. The objective is
to keep this module as simple as possible, using it as a menu
system and delegating all other tasks to the the State object.
'''

import os
import sys
import argparse

import lib.utils as utils
from lib.models.State import State
from lib.models.Colors import Color


def main(args):

    clr = Color()

    print(f'{clr.CYAN}Loading HIPO...{clr.ENDC}')

    if not os.path.exists('samples'): os.mkdir('samples')

    state = State(debug=args.debug)

    utils.print_title(state.debug)

    MENU_OPTIONS = {
        0: 'Exit',
        1: 'Browse samples',
        2: 'Add new sample'
    }
    DEBUG_OPTIONS = {
        'D': 'DEBUG ',
        100: 'Show most common types',
        200: 'Show Growth',
        300: 'Show Chain'
    }

    SAMPLE_OPTIONS = {
        0: 'Back',           
        'a': 'Analyze ',
            1: 'Change Threshold',
            2: 'Analyze',
        'b': 'Segmentation',
            3: 'Import Fiber Labels',
            4: 'Segment Dot-Like Elements',
        'c': 'Visualize ',    
            5: 'Show Images',
            6: 'Show Segmentation',
        'd': 'Edit',
            7: 'Change Name'
    }


    if state.debug: 
        MENU_OPTIONS.update(DEBUG_OPTIONS)
        SAMPLE_OPTIONS.update(DEBUG_OPTIONS)

    VISUALIZE_OPTIONS = {
        0: 'Raw',
        1: 'Mask'
    }

    while True:
        extra_opt = '(e)xit | (n)ew sample'
        menu = dict(zip(list(state.samples.index),list(state.samples['Sample'])))
        menu['e'] = 'Exit'
        menu['n'] = 'New sample'
        opt = utils.input_menu_option(menu, display = [extra_opt, state.list_samples()], show_menu = False, cancel=False)

        # Create Sample
        if opt == 'e':
            sys.exit()

        # Create Sample
        elif opt == 'n':
            res = utils.input_text('Enter new sample name')
            if res == None: continue
            state = state.create_new(res)

        else:
            res = state.load_sample(name = state.samples["Sample"][opt])
            if res == 0: continue

            while True:
                opt = utils.input_menu_option(SAMPLE_OPTIONS, cancel = False, display = [state.tabulate_sample()])

                if opt == 0:
                    state = state.clear_current_sample()
                    break


                # Modify Threshold
                elif opt == 1:
                    opt = utils.input_menu_option(dict(zip(list(state.current_sample.df.index),list(state.current_sample.df['Channel']))), display = [state.tabulate_sample()], show_menu = False)
                    if opt == None: continue
                    else: state.threshold(opt)


                # Perform Analysis
                elif opt == 2: state.analyse()


                # Import Fiber Labels
                elif opt == 3: state.import_labels()                     


                # Segment Point-Like Elements
                elif opt == 4: pass


                # Show Images
                elif opt == 5: 
                    opt = utils.input_menu_toggle(VISUALIZE_OPTIONS)
                    if opt == None: continue
                    else:
                        display = {
                            'image': opt[0],
                            'mask': opt[1]
                        }
                        state.show_napari(display)
                        # garbage collector not working with napari, restart hipo to clean memory
                        sys.stdout.flush()
                        os.execv(sys.executable, ['python'] + sys.argv)


                # Show Segmentation
                elif opt == 6: state.show_segmentation()


                # Show Segmentation
                elif opt == 7: state.change_name(utils.input_text('Enter new sample name'))


                else:
                    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Toggle debug mode)')
    args = parser.parse_args()
    main(args)

