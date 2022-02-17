'''
Author: José Verdú Díaz
'''

import sys

from lib.interface import load_input
from lib.image import parse_tiff, show_image, save_image
from lib.utils import print_title, print_menu, input_menu_option
from lib.browse_samples import list_samples, display_sample_df

if __name__ == '__main__':
    
    '''
    tiff_file, txt_file, geojson_file = load_input()
    images, metals, labels, summary_df = parse_tiff(tiff_file, txt_file)
    display_img_df(images, metals, labels, summary_df)
    for i, img in enumerate(images): normalize_quantile(0.90, img, metals[i])    
    '''

    MENU_OPTIONS = {
        0: 'Exit',
        1: 'Browse samples',
        2: 'Add new sample'
    }

    SAMPLE_OPTIONS = {
        0: 'Back',
        1: 'Normalize',
        2: 'View'
    }

    while True:
        print_title()

        opt = input_menu_option(MENU_OPTIONS, cancel = False)
        if opt == None: continue
        else: 
            if opt == 0: sys.exit()

            elif opt == 1:
                print_title()
                df = list_samples()
                opt = input_menu_option(dict(zip(list(df.index),list(df['Sample']))))
                sample = df["Sample"][opt]

                if opt == None: continue
                else:
                    tiff_file, txt_file, geojson_file = load_input(sample)
                    images, metals, labels, summary_df = parse_tiff(tiff_file, txt_file)
                    table = display_sample_df(images, metals, labels, summary_df, sample)

                    while True:                       
                        opt = input_menu_option(SAMPLE_OPTIONS, cancel = False, display = [table])

                        if opt == 0: break
                        else: 
                            print(opt)
                            input('\nPress Enter to continue...')

                    #for i,img in enumerate(images):
                    #    save_image(img, metals[i], sample)

                    #show_image(images)
                        



            elif opt == 2:
                print_title()
                print('You selected option 2')
                input('\nPress Enter to continue...')

            elif opt == 3:
                print_title()
                print('You selected option 3')
                input('\nPress Enter to continue...')

            else: 
                print('UNEXPECTED OPTION')
                input('\nPress Enter to continue...')


