'''Tool for processing and analysing hyperion imaging.

Author: José Verdú Díaz

This is the entry point of the application. The objective is
to keep this module as simple as possible, using it as a menu
system and delegating all other tasks to the other modules.
'''

import os
import sys

import lib.image as image
import lib.utils as utils
import lib.browse as browse
from lib.models.Colors import Color
import lib.interface as interface
from lib.models.State import State
from lib.models.Sample import Sample
import lib.consistency as consistency


if __name__ == '__main__':

    state = State()

    utils.print_title()

    MENU_OPTIONS = {
        0: 'Exit',
        1: 'Browse samples',
        2: 'Add new sample'
    }

    SAMPLE_OPTIONS = {
        0: 'Back',
        'a': 'Normalize ',
           1:  'Apply ROI and Normalize',
        'b': 'Threshold ',
           2:  'Change Threshold',
           3:  'Apply Threshold',
        'c': 'Contrast ',
           4:  'Change Contrast (napari)',
        'd': 'Analyze ',
           5:  'Perform Analysis',
        'e': 'Visualize ',    
           6:  'View Raw',
           7:  'View Normalized',
           8: 'Napari Show',
        'f': 'Histogram ', 
           9: 'View Histogram (norm)',
           10: 'View Histogram (cont)',
           11: 'View Histogram (thre)',
        'g': 'Fiber Segmentation',
           12: 'Segment fibers',
           13: 'Show Segmentation',
        'h': 'Edit ', 
           14: 'Remove Sample',
    }

    color = Color()

    if not os.path.exists('samples'): os.mkdir('samples')

    while True:

        opt = utils.input_menu_option(MENU_OPTIONS, cancel = False)
        if opt == None: continue
        else: 
            if opt == 0: sys.exit()

            elif opt == 1:

                while True:
                    table = state.list_samples()
                    opt = utils.input_menu_option(dict(zip(list(state.samples.index),list(state.samples['Sample']))), display = [table], show_menu = False)

                    if opt == None: break
                    else:
                        res = state.load_sample(name = state.samples["Sample"][opt])
                        if res == 0: continue

                        table = state.tabulate_sample()

                        while True:
                            opt = utils.input_menu_option(SAMPLE_OPTIONS, cancel = False, display = [table])

                            if opt == 0: break


                            elif opt == 1: state.normalize()

                            elif opt == 2:
                                opt = utils.input_menu_option(dict(zip(list(state.samples.df.index),list(state.samples.df['Channel']))), display = [table], show_menu = False)
                                if opt == None: continue
                                if df['Cont.'][opt] == '-':
                                    input(f'{color.YELLOW}The channel contrast has to be adjusted first. Press Enter to continue...{color.ENDC}')
                                    continue

                                threshold = utils.input_number('Enter threshold (between 0 and 255).', display=[table], range = (0,255), type = 'int')
                                if threshold == None: continue
                                interface.update_sample_json(sample, channel = opt, update_dict = {'threshold': threshold})
                                
                                table, df = browse.sample_df(images, metals, labels, summary_df, sample)


                            elif opt == 3:
                                images_norm, channels = interface.load_dir_images(sample, 'img_cont', df['Channel'].loc[df['Th.']!='-'].tolist())
                                image.apply_threshold(sample, images_norm, channels, df)
                                input(f'\n{color.GREEN}Images thresholded successfully! Press Enter to continue...{color.ENDC}')


                            elif opt == 4:
                                opt = utils.input_menu_option(dict(zip(list(state.current_sample.df.index),list(state.current_sample.df['Channel']))), display = [table], show_menu = False)
                                if opt == None: continue
                                else: 
                                    state.contrast(opt)
                                    table = state.tabulate_sample()


                            elif opt == 5:
                                res = image.analyse_images(sample, geojson_file)
                                if res == None: input(f'{color.YELLOW}No thresholded images found. Press Enter to continue...{color.ENDC}')
                                else: input(f'\n{color.GREEN}Images analysed successfully!\nReport generated at samples/{sample}/analysis.csv. Press Enter to continue...{color.ENDC}')


                            elif opt == 6: state.show_napari('image')

                            elif opt == 7: state.show_napari('image_norm')


                            elif opt == 8:
                                selected_images = utils.input_df_toggle(sample, df, checks = [consistency.check_existing_threshold])
                                if selected_images == None: continue
                                else:
                                    images_norm, channels = interface.load_dir_images(sample, 'img_thre', img = selected_images)
                                    image.show_napari(images_norm, channels)


                            elif opt == 9:
                                selected_images = utils.input_df_toggle(sample, df)
                                if selected_images == None: continue
                                else:
                                    images_norm, channels = interface.load_dir_images(sample, 'img_norm', img = selected_images)
                                    image.view_histogram(images_norm, channels, geojson_file)


                            elif opt == 10:
                                selected_images = utils.input_df_toggle(sample, df) # Must add consistency check
                                if selected_images == None: continue
                                else:
                                    images_norm, channels = interface.load_dir_images(sample, 'img_cont', img = selected_images)
                                    image.view_histogram(images_norm, channels, geojson_file)


                            elif opt == 11:
                                selected_images = utils.input_df_toggle(sample, df, checks = [consistency.check_existing_threshold])
                                if selected_images == None: continue
                                else:
                                    images_norm, channels = interface.load_dir_images(sample, 'img_thre', img = selected_images)
                                    image.view_histogram(images_norm, channels, geojson_file)


                            elif opt == 12:
                                input('Segmentation is performed using the contrasted Tm(169) channel.')
                                img, channels = interface.load_dir_images(sample, 'img_cont', img = ['Tm(169)'])
                                image.segment_fibers(sample, img[0], geojson_file)
                                input(f'{color.GREEN}Fibers Segmented successfully! Press Enter to continue...{color.ENDC}')


                            elif opt == 13: pass


                            elif opt == 14:
                                name = utils.input_text(f'{color.RED}{color.BOLD}YOU ARE ABOUT TO DELETE THIS SAMPLE, DATA WILL BE LOST, ENTER NAME OF THE SAMPLE TO CONFIRM{color.ENDC}', display=[table])

                                if name == None:
                                    continue
                                elif name == sample:
                                    interface.delete_sample(name)
                                    break
                                else:
                                    input(f'{color.RED}The input does not match the sample name. Press Enter to continue...{color.ENDC}')


                            else:
                                pass
                        

            elif opt == 2:
                name = utils.input_text('Enter new sample name', checks = [consistency.check_repeated_sample_name])

                if name == None: pass
                else:

                    sample = Sample(name=name)
                    sample.make_dir_structure()
                    state.set_samples()

                    print(f'\n{color.GREEN}Sample created successfully!{color.ENDC}')
                    input(f'\n{color.YELLOW}Add sample files in {color.UNDERLINE}samples/{name}/input{color.ENDC}{color.YELLOW}. Press Enter to continue...{color.ENDC}')


            else: 
                print('UNEXPECTED OPTION')
                input('\nPress Enter to continue...')