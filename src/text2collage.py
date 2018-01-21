import processText
import generatePhotoLayout
import os


def collageOfImages(foldername):
    # directory = os.path.dirname(os.getcwd())
    generatePhotoLayout.Environment([], '', foldername)


def text2collage():
    processText.Environment()

if __name__ == "__main__":
    try:
        foldername = raw_input("Enter folder that contains images: ")
        collageOfImages(os.path.abspath(foldername))
    except Exception as e:
        print e
