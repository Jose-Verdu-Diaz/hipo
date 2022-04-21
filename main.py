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
        'a': 'Image Processing ',
           1: 'Apply ROI and Normalize',
           2: 'Modify Contrast',
           3: 'Modify Threshold',
        'b': 'Analyze ',
           4: 'Perform Analysis',
        'c': 'Fiber Segmentation',
           5: 'Segment fibers',
           6: 'Import Labels',
        'd': 'Visualize ',    
           7: 'Show Images',
           8: 'Show Segmentation',
           9: 'Show Histograms'
    }


    if state.debug: 
        MENU_OPTIONS.update(DEBUG_OPTIONS)
        SAMPLE_OPTIONS.update(DEBUG_OPTIONS)

    VISUALIZE_OPTIONS = {
        0: 'Raw',
        1: 'Normalized',
        2: 'Contrast',
        3: 'Threshold',
        4: 'Mask'
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


                            # Apply ROI and Normalize
                            elif opt == 1: state.normalize()


                            # Modify Contrast
                            elif opt == 2:
                                opt = utils.input_menu_option(dict(zip(list(state.current_sample.df.index),list(state.current_sample.df['Channel']))), display = [state.tabulate_sample()], show_menu = False)
                                if opt == None: continue
                                else: state.contrast(opt)


                            # Modify Threshold
                            elif opt == 3:
                                opt = utils.input_menu_option(dict(zip(list(state.current_sample.df.index),list(state.current_sample.df['Channel']))), display = [state.tabulate_sample()], show_menu = False)
                                if opt == None: continue
                                else: state.threshold(opt)


                            # Perform Analysis
                            elif opt == 4: state.analyse()


                            # Segment fibers
                            elif opt == 5: state.segment_fibers()   


                            # Import Labels
                            elif opt == 6: state.import_labels()                     


                            # Show Images
                            elif opt == 7: 
                                opt = utils.input_menu_toggle(VISUALIZE_OPTIONS)
                                if opt == None: continue
                                else:
                                    display = {
                                        'image': opt[0],
                                        'image_norm': opt[1],
                                        'image_cont': opt[2],
                                        'image_thre': opt[3],
                                        'mask': opt[4],
                                    }
                                    state.show_napari(display)
                                    # garbage collector not working with napari, restart hipo to clean memory
                                    sys.stdout.flush()
                                    os.execv(sys.executable, ['python'] + sys.argv)


                            # Show Segmentation
                            elif opt == 8: state.show_segmentation()


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


            elif opt == 2: state = state.create_new(utils.input_text('Enter new sample name'))


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

