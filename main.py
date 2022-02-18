'''Tool for processing and analysing hyperion imaging.

Author: José Verdú Díaz

This is the entry point of the application. The objective is
to keep this module as simple as possible, using it as a menu
system and delegating all other tasks to the other modules.
'''

import sys

from lib.Colors import Color
from lib.interface import load_input, make_sample_dirs
from lib.image import parse_tiff, show_image, save_image, normalize_quantile, load_image, create_gif
from lib.utils import print_title, print_menu, input_menu_option, input_text
from lib.browse_samples import list_samples, display_sample_df
from lib.consistency import check_repeated_sample_name

if __name__ == '__main__':

    MENU_OPTIONS = {
        0: 'Exit',
        1: 'Browse samples',
        2: 'Add new sample'
    }

    SAMPLE_OPTIONS = {
        0: 'Back',
        1: 'Normalize',
        2: 'View Raw',
        3: 'View Normalized',
        4: 'Apply ROI',
        5: 'Create GIF'

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
                        
                        tiff_file, txt_file, geojson_file = load_input(sample)
                        images, metals, labels, summary_df = parse_tiff(tiff_file, txt_file)
                        table, df = display_sample_df(images, metals, labels, summary_df, sample)

                        while True:
                            opt = input_menu_option(SAMPLE_OPTIONS, cancel = False, display = [table])

                            if opt == 0: break
                            elif opt == 1:
                                print(f'Normalizing {sample}, wait please...')
                                normalize_quantile(0.95, images, sample, metals)
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


