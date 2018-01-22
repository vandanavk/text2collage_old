import processText
import generatePhotoLayout
import imageEmphasis
import os


def collageOfImages(foldername):
    print "Emphasis values can be provided in a CSV file. By default, random values are assigned."
    filename = raw_input("Enter the absolute path to the file containing image emphasis values: ")
    imageEmphasis.emphasisFromFile(filename)
    generatePhotoLayout.Environment([], '', foldername)


def text2collage():
    processText.Environment()

if __name__ == "__main__":
    try:
        foldername = raw_input("Enter folder that contains images: ")
        collageOfImages(os.path.abspath(foldername))
    except Exception as e:
        print e
