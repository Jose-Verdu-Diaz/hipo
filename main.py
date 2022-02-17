'''
Author: José Verdú Díaz
'''

import sys

from lib.interface import load_input
from lib.image import parse_tiff, show_image
from lib.utils import print_title, print_menu, input_menu_option
from lib.browse_samples import list_samples, display_sample_df

if __name__ == '__main__':
    
    '''
    tiff_file, txt_file, geojson_file = load_input()
    images, metals, labels, summary_df = parse_tiff(tiff_file, txt_file)
    display_img_df(images, metals, labels, summary_df)
    for i, img in enumerate(images): normalize_quantile(0.90, img, metals[i])    
    '''

    menu_options = {
        0: 'Exit',
        1: 'Browse samples',
        2: 'Add new sample',
        3: 'Option 3'
    }

    while True:
        print_title()
        print_menu(menu_options)

        opt = input_menu_option(menu_options, cancel = False)
        if opt == None: continue
        else: 
            if opt == 0: sys.exit()

            elif opt == 1:
                print_title()
                df = list_samples()
                opt = input_menu_option(dict(zip(list(df.index),list(df['Sample']))))

                if opt == None: continue
                else:
                    print_title()
                    tiff_file, txt_file, geojson_file = load_input(df["Sample"][opt])
                    images, metals, labels, summary_df = parse_tiff(tiff_file, txt_file)
                    display_sample_df(images, metals, labels, summary_df, df["Sample"][opt])



            elif opt == 2:
                print_title()
                print('You selected option 2')

            elif opt == 3:
                print_title()
                print('You selected option 3')

            else: print('UNEXPECTED OPTION')

            input('\nPress Enter to continue...')


