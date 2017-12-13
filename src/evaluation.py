import matplotlib.pyplot as plt
import numpy as np
import nltk
import re
import string
import os
# from rouge import Rouge
from nltk.translate.bleu_score import SmoothingFunction

cc = SmoothingFunction()


def plot_bar_graph(x, r1, r2, r3, r4, r5, xtitle, ytitle, gtitle, xticks, filename, directory):
    """
    Plot BLUE score vs n-gram length
    :param x: x-axis data
    :param r1: user1 data
    :param r2: user2 data
    :param r3: user3 data
    :param r4: user4 data
    :param r5: user5 data
    :param xtitle: x-axis title
    :param ytitle: y-axis title
    :param gtitle: graph title
    :param xticks: x tick labels
    :param filename: input textfile name
    :param directory: parent directory
    """
    ind = np.arange(len(x))
    width = 0.1
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, np.array(r1), width)
    rects2 = ax.bar(ind + width, np.array(r2), width)
    rects3 = ax.bar(ind + (2*width), np.array(r3), width)
    rects4 = ax.bar(ind + (3 * width), np.array(r4), width)
    rects5 = ax.bar(ind + (4*width), np.array(r5), width)
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(xticks)
    plt.title(gtitle)
    ax.set_ylabel(ytitle)
    ax.set_xlabel(xtitle)
    ax.legend((rects1[0], rects2[0], rects3[0], rects4[0], rects5[0]), ('U1', 'U2', 'U3', 'U4', 'U5'))
    fig.savefig(directory+'/BLEUvsnGram_'+filename+'.png')


def main():
    """
    This function compares user's sentences with the original sentence and compute the BLEU score.
    It then plots the BLEU score vs n-gram length.
    This is done for each of the input text files.
    Note: this requires that user's sentences be present in the usersentences folder with the
    folder structure specified in the instructions file.
    """
    directory = os.path.dirname(os.getcwd())
    # rscore = Rouge()

    if not os.path.exists(directory + '/graphs'):
        os.makedirs(directory+'/graphs')

    inputfolder = raw_input("Enter the name of the folder that contains input text: ")
    for userfolder in os.listdir(directory+'/usersentences'):
        if '.DS_Store' in userfolder:
            continue
        bleu = []
        rouge = []
        udata = []
        overallbleu = []
        overallrouge = []
        try:
            f = open(directory + '/' + inputfolder + '/' + userfolder + '.txt', 'r')
            referencetext = f.read().decode('ascii', 'ignore')
            f.close()
            references = nltk.sent_tokenize(referencetext)
            listofreflist = []
            print "Evaluating the result for " + userfolder
            for r in references:
                ref = re.sub('[' + string.punctuation + ']', '', r)
                rtemp = nltk.word_tokenize(ref)
                listofreflist.append(rtemp)
            for userfile in os.listdir(directory+'/usersentences/'+userfolder):
                if userfile.endswith('.txt'):
                    f = open(directory + '/usersentences/' + userfolder + '/' + userfile, 'r')
                    candidatetext = f.read().decode('ascii', 'ignore')
                    f.close()
                    candidates = nltk.sent_tokenize(candidatetext)
                    listofcandlist = []
                    for c in candidates:
                        cand = re.sub('[' + string.punctuation + ']', '', c)
                        ctemp = nltk.word_tokenize(cand)
                        listofcandlist.append(ctemp)

                    rdata = []
                    rdata.append(round(nltk.translate.bleu_score.corpus_bleu(listofreflist, listofcandlist, weights=[1], smoothing_function=cc.method3), 3))
                    rdata.append(round(nltk.translate.bleu_score.corpus_bleu(listofreflist, listofcandlist, weights=[0.5,0.5], smoothing_function=cc.method3), 3))
                    rdata.append(round(nltk.translate.bleu_score.corpus_bleu(listofreflist, listofcandlist, weights=[0.33,0.33,0.33], smoothing_function=cc.method3), 3))
                    rdata.append(round(nltk.translate.bleu_score.corpus_bleu(listofreflist, listofcandlist, weights=[0.25,0.25,0.25,0.25], smoothing_function=cc.method3), 3))

                    udata.append(rdata)
                    bleu.append(round(nltk.translate.bleu_score.corpus_bleu(listofreflist, listofcandlist, weights=[0.5,0.5], smoothing_function=cc.method3), 3))
                    # rouge.append(rscore.get_scores(candidates, references, avg=True))
        except Exception as e:
            # print e
            continue
        # print userfolder + " " + str(float(sum(bleu))/float(len(bleu)))
        # overallbleu.append(bleu)
        # print overallbleu

        graphx = [x for x in range(1,5)]
        xticks = [str(x) for x in range(1, 5)]
        plot_bar_graph(graphx, udata[0], udata[1], udata[2], udata[3], udata[4], 'n-gram length', 'BLEU Score', 'Human translation scores for '+userfolder, xticks, userfolder, directory+'/graphs')

        # overallrouge.append(rouge)
        # print overallrouge
    print "\nResults are stored in " + directory + '/graphs'

if __name__ == "__main__":
    main()
