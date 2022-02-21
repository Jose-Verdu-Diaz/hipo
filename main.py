'''Tool for processing and analysing hyperion imaging.

Author: José Verdú Díaz

This is the entry point of the application. The objective is
to keep this module as simple as possible, using it as a menu
system and delegating all other tasks to the other modules.
'''

import sys

from lib.Colors import Color
from lib.interface import load_input, make_sample_dirs, delete_sample
from lib.image import parse_tiff, show_image, normalize_quantile, load_image, create_gif, apply_ROI
from lib.utils import print_title, print_menu, input_menu_option, input_text, input_yes_no
from lib.browse_samples import list_samples, display_sample_df
from lib.consistency import check_repeated_sample_name, check_overwrite, check_operation_requirements

if __name__ == '__main__':

    MENU_OPTIONS = {
        0: 'Exit',
        1: 'Browse samples',
        2: 'Add new sample'
    }

    SAMPLE_OPTIONS = {
        0: 'Back',
        1: 'Apply ROI and Normalize',
        2: 'View Raw',
        3: 'View Normalized',
        4: 'Create GIF',
        5: 'Remove Sample',
        6: 'Perform analysis'
    }

    color = Color()

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
                        table, df = display_sample_df(images, metals, labels, summary_df, sample)

                        while True:
                            opt = input_menu_option(SAMPLE_OPTIONS, cancel = False, display = [table])

                            if opt == 0: break

                            elif opt == 1:
                                masked = apply_ROI(geojson_file, images)

                                if not check_overwrite(sample, 'norm_quant') and not input_yes_no(f'{color.YELLOW}Sample already normalized. Overwrite?', display=[table]): continue

                                print(f'Normalizing {sample}, wait please...')
                                normalize_quantile(0.95, masked, sample, metals)
                                input(f'\n{color.GREEN}Images normalized uccessfully! Press Enter to continue...{color.ENDC}')

                            elif opt == 2:
                                while True:
                                    opt = input_menu_option(dict(zip(list(df.index),list(df['Channel']))), cancel = True, display = [table], show_menu = False)

                                    if opt == None: break
                                    else: show_image(images[opt])

                            elif opt == 3:
                                while True:
                                    opt = input_menu_option(dict(zip(list(df.index),list(df['Channel']))), cancel = True, display = [table], show_menu = False )

                                    if opt == None: break
                                    else: 
                                        img = load_image(f'samples/{sample}/img_norm/{metals[opt]}.png')
                                        show_image(img)

                            elif opt == 4:
                                create_gif(sample)

                            elif opt == 5:
                                name = input_text(f'{color.RED}{color.BOLD}YOU ARE ABOUT TO DELETE THIS SAMPLE, DATA WILL BE LOST, ENTER NAME OF THE SAMPLE TO CONFIRM{color.ENDC}', display=[table])

                                if name == None:
                                    continue
                                elif name == sample:
                                    delete_sample(name)
                                    break
                                else:
                                    input(f'{color.RED}The input does not match the sample name. Press Enter to continue...{color.ENDC}')

                            elif opt == 6:
                                res = check_operation_requirements(sample, 'analysis')
                                if not res == None:
                                    input(f'{color.YELLOW}{res} is required before applying the ROIs. Press Enter to continue...{color.ENDC}')
                                else:
                                    input('Analysis currently not available')

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


