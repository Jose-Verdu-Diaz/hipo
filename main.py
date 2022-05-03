'''Tool for processing and analysing hyperion imaging.

Author: José Verdú Díaz

This is the entry point of the application. The objective is
to keep this module as simple as possible, using it as a menu
system and delegating all other tasks to the the State object.
'''

import os
import sys
import random
import objgraph
import argparse

import lib.utils as utils
from lib.models.State import State
import lib.consistency as consistency


def main(args):
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
            2: 'Perform Analysis',
        'b': 'Fiber Segmentation',
            3: 'Import Labels',
        'c': 'Visualize ',    
            4: 'Show Images',
            5: 'Show Segmentation',
        'd': 'Edit',
            6: 'Change Name'
    }


    if state.debug: 
        MENU_OPTIONS.update(DEBUG_OPTIONS)
        SAMPLE_OPTIONS.update(DEBUG_OPTIONS)

    VISUALIZE_OPTIONS = {
        0: 'Raw',
        1: 'Mask'
    }


    while True:

        opt = utils.input_menu_option(MENU_OPTIONS, cancel = False)
        if opt == None: continue
        else: 
            # Exit
            if opt == 0: sys.exit()

            # Browse samples
            elif opt == 1:

                while True:
                    opt = utils.input_menu_option(dict(zip(list(state.samples.index),list(state.samples['Sample']))), display = [state.list_samples()], show_menu = False)

                    if opt == None: break
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


                            # Segment fibers
                            #elif opt == 3: state.segment_fibers()   


                            # Import Labels
                            elif opt == 3: state.import_labels()                     


                            # Show Images
                            elif opt == 4: 
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
                            elif opt == 5: state.show_segmentation()


                            # Show Segmentation
                            elif opt == 6: state.change_name(utils.input_text('Enter new sample name'))


                            #####################################################
                            ################### DEBUG OPTIONS ###################
                            #####################################################

                            elif opt == 100 and state.debug:
                                objgraph.show_most_common_types()
                                input('Press Enter to continue...')


                            elif opt == 200 and state.debug:
                                objgraph.show_growth()
                                input('Press Enter to continue...')


                            elif opt == 300 and state.debug:
                                objgraph.show_chain(
                                        objgraph.find_backref_chain(
                                            random.choice(objgraph.by_type('dict')),
                                            objgraph.is_proper_module),
                                        filename='chain.png')
                                input('Press Enter to continue...')


                            else:
                                pass


            elif opt == 2: 
                state = state.create_new(utils.input_text('Enter new sample name'))


            #####################################################
            ################### DEBUG OPTIONS ###################
            #####################################################

            elif opt == 100 and state.debug:
                objgraph.show_most_common_types()
                input('Press Enter to continue...')


            elif opt == 200 and state.debug:
                objgraph.show_growth()
                input('Press Enter to continue...')


            elif opt == 300 and state.debug:
                objgraph.show_chain(
                        objgraph.find_backref_chain(
                            random.choice(objgraph.by_type('Channel')),
                            objgraph.is_proper_module),
                        filename='chain.png')
                input('Press Enter to continue...')


            else: 
                print('UNEXPECTED OPTION')
                input('\nPress Enter to continue...')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Toggle debug mode)')
    args = parser.parse_args()
    main(args)

