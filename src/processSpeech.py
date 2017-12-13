import re
import string
from time import time
import os
import nltk
from pattern.en import singularize
from rake_nltk import Rake
import codecs

import generatePhotoLayout
import retrieveImageFromURL


class Agent:
    """
    The class 'Agent' is responsible for executing keyword extraction.
    Sensor - receives input text.
    Agent Function - extracts tags and query keywords.
    Actuator - provides tags and keywords.
    """
    def __init__(self, t):
        """

        :param t: Input text
        Save input text and tokenize into sentences.
        """
        self.text = t
        self.sentences = nltk.sent_tokenize(self.text)
        f = codecs.open('stopwords.txt', encoding='utf-8')
        stopw = f.read()
        stopwords = stopw.split(',')
        self.r = Rake(stopwords)

    def getTags(self):
        """
        Extract possible tags from the text using RAKE
        :return: Tag set
        """
        meaningset = []
        if len(self.sentences) == 1:
            s = re.sub('[' + string.punctuation + ']', '', self.sentences[0])
            self.r.extract_keywords_from_text(s)
            rp = self.r.get_ranked_phrases()
            final_nouns = []
            for n in rp:
                tokens = nltk.tokenize.word_tokenize(n)
                if len(tokens) == 1:
                    item, tag = nltk.pos_tag(tokens)[0]
                    if 'NN' in tag:
                        if len(item) > 1:
                            final_nouns.append(singularize(item))
                else:
                    final_nouns.append(n)
            return final_nouns

        for s in self.sentences:
            s = re.sub('[' + string.punctuation + ']', '', s)
            self.r.extract_keywords_from_text(s)
            rp = self.r.get_ranked_phrases()
            final_nouns = []
            for n in rp:
                tokens = nltk.tokenize.word_tokenize(n)
                if len(tokens) == 1:
                    item, tag = nltk.pos_tag(tokens)[0]
                    if 'NN' in tag:
                        if len(item) > 1:
                            final_nouns.append(singularize(item))
                else:
                    final_nouns.append(n)
            meaningset.append(final_nouns)
        return meaningset

    def getKeywords(self):
        """
        Extract keywords using POS tagging
        :return: Query keywords
        """
        nouns = []
        if len(self.sentences) == 1:
            s = re.sub('[' + string.punctuation + ']', '', self.sentences[0])
            self.r.extract_keywords_from_text(s)
            rp = self.r.get_ranked_phrases()
            for n in rp:
                tokens = nltk.tokenize.word_tokenize(n)
                if len(tokens) == 1:
                    item, tag = nltk.pos_tag(tokens)[0]
                    if 'NN' in tag:
                        if len(item) > 1:
                            nouns.append(singularize(item))
                else:
                    nouns.append(n)
            return nouns
        for s in self.sentences:
            s = re.sub('[' + string.punctuation + ']', '', s)
            tokens = nltk.tokenize.word_tokenize(s)
            tagged = nltk.pos_tag(tokens)
            final_nouns = []
            for item, t in tagged:
                if 'NN' in t:
                    if singularize(item) not in final_nouns and len(item) > 1:
                        final_nouns.append(singularize(item))
            nouns.append(final_nouns)
        return nouns


class Environment:
    """
    The class Environment is responsible for data processing,
    providing percept sequences to the Agent, and calling 
    other environments.
    """
    def __init__(self):
        self.main()

    def main(self):
        """
            This is the starting point for the entire system.
            The function is responsible for:
            1. Reading files that contain input text.
            2. Interacting with the Agent for text Processing and receiving
            relevant keywords and tags.
            3. Passing on tags and keywords as information to the Image 
            Retrieval module's Environment.
            4. Call layout generator
        """
        directory = os.path.dirname(os.getcwd())
        print "The parent directory is " + directory
        print "Please ensure the directory structure is as follows before proceeding.\n"
        print directory
        print "|___ src"
        print "|___ input"
        print "Note: the input folder name can be different\n"
        folder = raw_input("Enter the name of the folder that contains input text: ")

        for filename in os.listdir(directory+'/'+folder):
            if filename.endswith('.txt'):
                print "\nConverting "+filename+" to an illustration"
                f = open(directory+'/' + folder + '/' + filename, 'r')
                text = f.read().decode('ascii', 'ignore')
                f.close()

                a = Agent(text)

                time_init = time()
                meaningset = a.getTags()

                nouns = a.getKeywords()

                print "\nThe keywords for the query are: "
                for n in nouns:
                    print n
                print "\nThe words that are used as tags are: "
                for m in meaningset:
                    print m
                print "\n"

                total_time = time() - time_init
                print "Total time for keyword extraction: %.3f seconds." % total_time
                print "\n"

                time_init = time()
                retrieveImageFromURL.Environment(nouns, meaningset, directory)
                total_time = time() - time_init
                print "Total time for image retrieval: %.3f seconds." % total_time
                time_init = time()
                generatePhotoLayout.Environment(nouns, filename, directory)
                total_time = time() - time_init
                print "Total time for GA: %.3f seconds." % total_time

if __name__ == "__main__":
    try:
        Environment()
    except Exception as e:
        print e
