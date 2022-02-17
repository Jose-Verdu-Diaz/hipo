'''
Author: José Verdú Díaz
'''

import sys

from lib.interface import load_input
from lib.image import parse_tiff, show_image, save_image, normalize_quantile, load_image
from lib.utils import print_title, print_menu, input_menu_option, input_text
from lib.browse_samples import list_samples, display_sample_df

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
        3: 'View Normalized'
    }

    while True:
        print_title()

        opt = input_menu_option(MENU_OPTIONS, cancel = False)
        if opt == None: continue
        else: 
            if opt == 0: sys.exit()

            elif opt == 1:

                while True:
                    print_title()
                    df = list_samples()
                    opt = input_menu_option(dict(zip(list(df.index),list(df['Sample']))))

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
                                print('Normalizing, wait please...')
                                for i,img in enumerate(images): normalize_quantile(0.95, img, sample, metals[i])

                            elif opt == 2:
                                while True:
                                    opt = input_menu_option(dict(zip(list(df.index),list(df['Channel']))), cancel = True, display = [table], show_menu = False )

                                    if opt == None: break
                                    else: show_image(images[opt])

                            elif opt == 3:
                                while True:
                                    opt = input_menu_option(dict(zip(list(df.index),list(df['Channel']))), cancel = True, display = [table], show_menu = False )

                                    if opt == None: break
                                    else: 
                                        img = load_image(f'samples/{sample}/img_norm/{metals[opt]}.png')
                                        show_image(img)

                            else:
                                pass
                        

            elif opt == 2:
                print('You selected option 2')
                input('\nPress Enter to continue...')


            else: 
                print('UNEXPECTED OPTION')
                input('\nPress Enter to continue...')


