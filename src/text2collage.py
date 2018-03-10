import processText
import generatePhotoLayout
import imageEmphasis
import os
import argparse

parser = argparse.ArgumentParser(description='This library converts a given paragraph '
                                             'of text into an equivalent image illustration, '
                                             'represented as a collage of images. It also gives '
                                             'the user the option of creating a collage of '
                                             'images from a folder containing a set of images.')
parser.add_argument('-i', default=["collection"], choices=['text', 'collection'], nargs=1,
                    help='Interactiveness:'
                         'Choose if text needs to be converted to a collage of images'
                         'or a folder containing images needs to be represented as a collage.'
                         'Default: collection')
parser.add_argument('-d', nargs=1,
                    help='Absolute path of folder containing text input (if text to '
                         'collage is chosen) or folder containing images (if image collection'
                         'to collage is chosen)')
parser.add_argument('-cw', default=1920, type=int, nargs=1,
                    help='Width of canvas. Default: 1920')
parser.add_argument('-ch', default=1080, type=int, nargs=1,
                    help='Height of canvas. Default: 1080')
parser.add_argument('-e', default='random', choices=['random', 'auto', 'user'], nargs=1,
                    help='Importance estimator for the images in the collage. The'
                         'importance assigned, will help the library decide the scale of '
                         'each image. Default: Random')
parser.add_argument('-b', default=3, type=int, nargs=1,
                    help='Beta: Space between images in the collage (in pixels).'
                         'Default: 3')
parser.add_argument('-GA', default=[500, 10, 0.7, 0.2, 0.15], type=float, nargs=5,
                    help='GA parameters - number of iterations, population size,'
                         'crossover probability, mutation probability, lambda (fitness'
                         'function parameter - lam).'
                         'Default: Number of generations - 500,'
                         ' Population size - 10, Crossover probability - 0.7,'
                         ' Mutation probability - 0.2, Lambda (fitness component'
                         'trade-off factor) - 0.15')

if __name__ == "__main__":
    try:
        args = vars(parser.parse_args())
        canvasw = args['cw'][0] if isinstance(args['cw'], list) else args['cw']
        canvash = args['ch'][0] if isinstance(args['ch'], list) else args['ch']
        beta = args['b'][0] if isinstance(args['b'], list) else args['b']
        imp = args['e'][0] if isinstance(args['e'], list) else args['e']
        GAparams = args['GA']
        GAparams[:2] = map(int, GAparams[:2])
        option = args['i'][0]

        foldername = os.path.abspath(args['d'][0])
        if not foldername:
            print "A directory of text or image files is required"
            exit(0)
        if option == 'text':
            processText.Environment(foldername, imp, canvasw, canvash, beta, GAparams)
        elif option == 'collection':
            if imp == 'user':
                filename = raw_input("Enter the absolute path to the file containing image emphasis values: ")
                imageEmphasis.emphasisFromFile(filename)
            elif imp == 'auto':
                imp = 'random'
            generatePhotoLayout.Environment([], '', foldername, imp, canvasw, canvash, beta, GAparams)
    except Exception as e:
        print e
