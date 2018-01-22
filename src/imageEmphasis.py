import pickle
import os
import csv

emphasis = {}


def emphasisFromText(phraseScore, imageList):
    """
    Compute the emphasis score based on RAKE's phrase score
    and assign it to the corresponding image
    :param phraseScore: Score given to each sentence by RAKE
    :param imageList: Image equivalent to each sentence
    """
    for i, img in enumerate(imageList):
        total = 0
        if len(phraseScore) == 1:
            for index, (s, p) in enumerate(phraseScore[0]):
                if index == i:
                    total = s
                    break
        else:
            for s, p in phraseScore[i]:
                total += s
        emphasis[img] = total
    dumpToFile()


def emphasisFromFile(filename):
    """
    In case a collage is created from a collection of
    images, then consider the emphasis value provided for
    each image by the user. The user needs to specify this
    in a csv format. Column 1 containing file name without
    extension and Column 2 containing emphasis score as
    integer.
    :param filename: Full path to CSV file along with name
    """
    try:
        with open(filename, 'rb') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                emphasis[row[0]] = int(row[1])
        dumpToFile()
    except Exception as e:
        print "User has not specified image emphasis."
        print "Using random emphasis values."


def dumpToFile():
    """
    Image emphasis value is dumped to a pkl file
    and read by the photo layout generator.
    """
    if os.path.exists('imgEmphasis.pkl'):
        os.remove('imgEmphasis.pkl')
    f = open('imgEmphasis.pkl', 'wb')
    pickle.dump(emphasis, f)
    f.close()
