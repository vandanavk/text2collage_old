import re
import string
from time import time
import os
import nltk
from pattern.en import singularize
from rake_nltk import Rake

import generatePhotoLayout
import retrieveImageFromURL

stopwords = ["a", "able", "about", "above", "abroad", "according", "accordingly", "across", "actually",
             "adj", "acm", "after", "afterwards", "again", "against", "ago", "ahead", "ain't", "all",
             "allow", "allows", "almost", "alone", "along", "alongside", "already", "also", "although",
             "always", "am", "amid", "amidst", "among", "amongst", "an", "and", "another", "any",
             "anybody", "anyhow", "anyone", "anything", "anyway", "anyways", "anywhere", "apart",
             "appear", "appreciate", "appropriate", "are", "aren't", "around", "as", "a's", "aside",
             "ask", "asking", "associated", "at", "available", "away", "awfully", "back", "backward",
             "backwards", "be", "became", "because", "become", "becomes", "becoming", "been", "before",
             "beforehand", "begin", "behind", "being", "believe", "below", "beside", "besides", "best",
             "better", "between", "beyond", "both", "brief", "but", "by", "came", "can", "cannot",
             "can't", "cant", "caption", "cause", "causes", "certain", "certainly", "changes", "clearly",
             "co", "co.", "com", "come", "comes", "concerning", "consequently", "consider",
             "considering", "contain", "containing", "contains", "corresponding", "center", "career",
             "could", "couldn't", "course", "currently", "dare", "definitely", "described",
             "description", "despite", "did", "didn't", "different", "directly", "do", "does",
             "doesn't", "doing", "done", "don't", "down", "downwards", "during", "each", "edu", "eg",
             "eight", "eighty", "either", "else", "elsewhere", "end", "ending", "enough", "entirely",
             "especially", "et", "etc", "even", "ever", "evermore", "every", "everybody", "everyone",
             "everything", "everywhere", "ex", "exactly", "example", "except", "fairly", "far",
             "farther", "few", "fewer", "fifth", "first", "five", "follow", "followed", "following",
             "follows", "for", "forever", "former", "formerly", "forth", "forward", "found", "four",
             "from", "further", "furthermore", "get", "gets", "getting", "given", "gives", "go", "goes",
             "going", "gone","got","gotten","greetings","had","hadn't","half","happens","hardly", "has",
             "hasn't" ,"have","haven't","having","he","he'd","he'll","hello","help","hence","her","here",
             "hereafter","hereby","herein","here's","hereupon","hers","herself","he's","hi","him","himself",
             "his","hither","hopefully","how","howbeit","however","hundred","i'd","ie","if","ignored","i'll",
             "i'm","immediate","immediately","in","inasmuch","inc","inc.","indeed","indicate","indicated",
             "indicates","inner","inside","insofar","instead","into","inward","is","isn't","it","it'd","it'll",
             "its","it's","itself","i've","just","keep","keeps","kept","know","known","knows","last",
             "lately","later","latter","latterly","least","less","lest","let","let's","like","liked","likely",
             "likewise","called","look","looking","looks","low","lower","ltd","made","mainly","make","makes",
             "many","may","maybe","mayn't","me","mean","meantime","meanwhile","merely","might","mightn't","mine",
             "minus","miss","more","moreover","most","mostly","mr","mrs","much","must","mustn't","my","myself",
             "name","namely","nd","near","nearly","necessary","need","needn't","needs","neither","never",
             "neverf","neverless","nevertheless","new","next","nine","ninety","no","nobody","non","none",
             "nonetheless","noone","no-one","nor","normally","not","nothing","notwithstanding","novel","now",
             "nowhere","obviously","of","off","often","oh","ok","okay","old","on","once","one","ones","one's",
             "only","onto","opposite","or","other","others","otherwise","ought","oughtn't","our","ours","ourselves",
             "out","outside","over","overall","own","particular","particularly","past","per","perhaps","placed",
             "please","plus","possible","presumably","probably","provided","provides","que","quite","qv",
             "rather","rd","re","really","reasonably","recent","recently","regarding","regardless","regards",
             "relatively","respectively","right","round","said","same","saw","say","saying","says","second",
             "secondly","see","seeing","seem","seemed","seeming","seems","seen","self","selves","sensible",
             "sent","serious","seriously","seven","several","shall","shan't","she","she'd","she'll","she's",
             "should","shouldn't","since","six","so","some","somebody","someday","somehow","someone","something",
             "sometime","sometimes","somewhat","somewhere","soon","sorry","specified","specify","specifying",
             "still","sub","such","sup","sure","take","taken","taking","tell","tends","th","than","thank",
             "thanks","thanx","that","that'll","thats","that's","that've","the","their","theirs","them",
             "themselves","then","thence","there","thereafter","thereby","there'd","therefore","therein",
             "there'll","there're","theres","there's","thereupon","there've","these","they","they'd","they'll",
             "they're","they've","thing","things","think","third","thirty","this","thorough","thoroughly",
             "those","though","three","through","throughout","thru","thus","till","to","together","too","took",
             "toward","towards","tried","tries","truly","try","trying","t's","twice","two","un","under",
             "underneath","undoing","unfortunately","unless","unlike","unlikely","until","unto","up","upon",
             "upwards","us","use","used","useful","uses","using","usually","value","various","versus","very",
             "via","viz,vs,w","want","wants","was","wasn't","way","we","we'd","welcome","well","we'll","went",
             "were","we're","weren't","we've","what","whatever","what'll","what's","what've","when","whence",
             "whenever","where","whereafter","whereas","whereby","wherein","where's","whereupon","wherever",
             "whether","which","whichever","while","whilst","whither","who","who'd","whoever","whole","who'll",
             "whom","whomever","who's","whose","why","will","willing","wish","with","within","without","wonder",
             "won't","would","wouldn't","yes","yet","you","you'd","you'll","your","you're","yours","yourself",
             "yourselves","you've","zero", "job", "career", "opportunity", "location", "place", "wear", "wore",
             "pull", "pulled", "pulling", "take", "takes", "taken", "stand", "sit", "live", "lived", "lives",
             "walk", "walking", "walked", "didn", "didnt", "youd", "theyd"]


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
        self.r = Rake(stopwords)

    # not_punctuation = lambda self, w: not (len(w) == 1 and (not w.isalpha()))

    def getTags(self):
        """
        Extract possible tags from the text using RAKE
        :return: Tag set
        """
        meaningset = []
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
