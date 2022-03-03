'''Tool for processing and analysing hyperion imaging.

Author: José Verdú Díaz

This is the entry point of the application. The objective is
to keep this module as simple as possible, using it as a menu
system and delegating all other tasks to the other modules.
'''

import sys
import os

from lib.Colors import Color
from lib.interface import load_input, make_sample_dirs, delete_sample, populate_channels_json, load_dir_images, update_channel_threshold_json
from lib.image import parse_tiff, show_image, normalize_quantile, load_image, create_gif, appy_threshold, analyse_images, show_napari, threshold_napari, view_histogram
from lib.utils import print_title, input_menu_option, input_text, input_yes_no, input_number, input_df_toggle
from lib.browse_samples import list_samples, sample_df
from lib.consistency import check_repeated_sample_name, check_overwrite, check_operation_requirements

if __name__ == '__main__':

    MENU_OPTIONS = {
        0: 'Exit',
        1: 'Browse samples',
        2: 'Add new sample'
    }

    SAMPLE_OPTIONS = {
        0: 'Back',
        'a': 'Normalize ',
        1: 'Apply ROI and Normalize',
        'b': 'Threshold ',
        2: 'Change Threshold',
        3: 'Change Threshold (napari)',
        4: 'Apply Threshold',
        'c': 'Analyze ',
        5: 'Perform Analysis',
        'd': 'Visualize ',    
        6: 'View Raw',
        7: 'View Normalized',
        8: 'Create GIF', 
        9: 'Napari Show',
        10: 'View Histogram',
        'f': 'Edit ', 
        11: 'Remove Sample',
    }

    color = Color()

    if not os.path.exists('samples'): os.mkdir('samples')

    while True:
        print_title()

        opt = input_menu_option(MENU_OPTIONS, cancel = False)
        if opt == None: continue
        else: 
            if opt == 0: sys.exit()

            elif opt == 1:

                while True:
                    print_title()
                    table, df = list_samples()
                    opt = input_menu_option(dict(zip(list(df.index),list(df['Sample']))), display = [table], show_menu = False)

                    if opt == None: break
                    else:
                        sample = df["Sample"][opt]
                        
                        sample_input = load_input(sample)
                        if sample_input == None: continue

                        (tiff_file, txt_file, geojson_file) = sample_input
                        images, metals, labels, summary_df = parse_tiff(tiff_file, txt_file)
                        populate_channels_json(sample, metals, labels)
                        table, df = sample_df(images, metals, labels, summary_df, sample)

                        while True:
                            opt = input_menu_option(SAMPLE_OPTIONS, cancel = False, display = [table])

                            if opt == 0: break


                            elif opt == 1:         
                                top_quantile = input_number('Enter the top quantile (between 0 and 1).', display=[table], range = (0,1), type = 'float')
                                if top_quantile == None: continue

                                if not check_overwrite(sample, 'norm_quant') and not input_yes_no(f'{color.YELLOW}Sample already normalized. Overwrite?', display=[table]): continue

                                print(f'Normalizing {sample}, wait please...')
                                normalize_quantile(top_quantile, geojson_file, images, sample, metals)
                                input(f'\n{color.GREEN}Images normalized uccessfully! Press Enter to continue...{color.ENDC}')


                            elif opt == 2:
                                opt = input_menu_option(dict(zip(list(df.index),list(df['Channel']))), display = [table], show_menu = False)
                                if opt == None: continue

                                threshold = input_number('Enter threshold (between 0 and 1).', display=[table], range = (0,1), type = 'float')
                                if threshold == None: continue
                                update_channel_threshold_json(sample, opt, threshold)
                                
                                table, df = sample_df(images, metals, labels, summary_df, sample)


                            elif opt == 3: # napari
                                opt = input_menu_option(dict(zip(list(df.index),list(df['Channel']))), display = [table], show_menu = False)
                                if opt == None: continue
                                else: 
                                    images_norm, channels = load_dir_images(sample, 'img_norm', [df['Channel'][opt]])
                                    threshold_napari(images_norm[0], channels[0])


                            elif opt == 4:
                                res = check_operation_requirements(sample, 'img_threshold')
                                if not res == None:
                                    input(f'{color.YELLOW}{res} is required before applying the thresholds. Press Enter to continue...{color.ENDC}')
                                else:
                                    images_norm, channels = load_dir_images(sample, 'img_norm', df['Channel'].loc[df['Th.']!='-'].tolist())
                                    appy_threshold(sample, images_norm, channels, 0.5)
                                    input(f'\n{color.GREEN}Images thresholded successfully! Press Enter to continue...{color.ENDC}')


                            elif opt == 5:
                                res = analyse_images(sample, geojson_file)
                                if res == None: input(f'{color.YELLOW}No thresholded images found. Press Enter to continue...{color.ENDC}')
                                else: input(f'\n{color.GREEN}Images analysed successfully!\nReport generated at samples/{sample}/analysis.csv. Press Enter to continue...{color.ENDC}')


                            elif opt == 6:
                                while True:
                                    opt = input_menu_option(dict(zip(list(df.index),list(df['Channel']))), cancel = True, display = [table], show_menu = False)

                                    if opt == None: break
                                    else: show_image(images[opt])


                            elif opt == 7:
                                while True:
                                    opt = input_menu_option(dict(zip(list(df.index),list(df['Channel']))), cancel = True, display = [table], show_menu = False )

                                    if opt == None: break
                                    else: 
                                        img = load_image(f'samples/{sample}/img_norm/{metals[opt]}.png')
                                        show_image(img)


                            elif opt == 8:
                                create_gif(sample)


                            elif opt == 9:
                                selected_images = input_df_toggle(sample, df)
                                if selected_images == None: continue
                                else:
                                    images_norm, channels = load_dir_images(sample, 'img_threshold', img = selected_images) # Images return unordered, must fix
                                    show_napari(images_norm, channels)


                            elif opt == 10:
                                opt = input_menu_option(dict(zip(list(df.index),list(df['Channel']))), display = [table], show_menu = False)
                                if opt == None: continue
                                else: 
                                    images_norm, channels = load_dir_images(sample, 'img_norm', [df['Channel'][opt]])
                                    view_histogram(images_norm[0])


                            elif opt == 11:
                                name = input_text(f'{color.RED}{color.BOLD}YOU ARE ABOUT TO DELETE THIS SAMPLE, DATA WILL BE LOST, ENTER NAME OF THE SAMPLE TO CONFIRM{color.ENDC}', display=[table])

                                if name == None:
                                    continue
                                elif name == sample:
                                    delete_sample(name)
                                    break
                                else:
                                    input(f'{color.RED}The input does not match the sample name. Press Enter to continue...{color.ENDC}')


                            else:
                                pass
                        

            elif opt == 2:
                name = input_text('Enter new sample name', consistency = [check_repeated_sample_name])

                if name == None: pass
                else:
                    make_sample_dirs(name)

                    print(f'\n{color.GREEN}Sample created successfully!{color.ENDC}')
                    input(f'\n{color.YELLOW}Add sample files in {color.UNDERLINE}samples/{name}/input{color.ENDC}{color.YELLOW}. Press Enter to continue...{color.ENDC}')

            else: 
                print('UNEXPECTED OPTION')
                input('\nPress Enter to continue...')