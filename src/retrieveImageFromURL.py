from bs4 import BeautifulSoup
import urllib2
import os
import json
import re
import string

header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
        }


class Agent:
    def __init__(self, q, t, d):
        """

        :param q: query keywords
        :param t: tag set
        :param d: parent directory
        """
        self.query = q
        self.tagset = t
        self.directory = d

    def saveImages(self, sortedmatchingtag, qcopy, q):
        """
        Save the image with highest Keyword Overlap value
        :param sortedmatchingtag: image links of images sorted in decreasing order of Keyword Overlap value
        :param qcopy: copy of the query without spaces
        :param q: query keywords
        """
        for t in sortedmatchingtag:
            try:
                req = urllib2.Request(t, headers={'User-Agent': header})
                raw_img = urllib2.urlopen(req).read()
                f = open(self.directory + "/images/" + qcopy + ".jpg", 'wb')

                f.write(raw_img)
                f.close()
                print "Saved image for " + q
                break
            except Exception as e:
                continue

    def retrieveImages(self):
        """
        Retrieve images for query keywords of each sentence.
        Retrieve image tags and compare with sentence tags.
        Sort image links in decreasing order of keyword overlap value.
        Call saveImage
        """
        for i, q in enumerate(self.query):
            matchingtags = {}
            querytag = []
            for tag in self.tagset[i]:
                for x in tag.split():
                    querytag.append(x.lower())
            if isinstance(q, list):
                qcopy = ''.join(x for x in q)
            else:
                qcopy = q.replace(' ', '')
            if os.path.exists(self.directory + "/images/" + qcopy + ".jpg"):
                continue
            if isinstance(q, list):
                q = '+'.join(x for x in q)
            else:
                q = q.replace(' ', '+')

            url = 'https://www.google.com/search?q=' + q + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg&safe=active'
            soup = BeautifulSoup(urllib2.urlopen(urllib2.Request(url, headers=header)), 'html.parser')
            for a in soup.find_all("div", {"class": "rg_meta"}):
                link, Type, tags = json.loads(a.text)["ou"], json.loads(a.text)["ity"], json.loads(a.text)["s"]
                tags = re.sub('[' + string.punctuation + ']', '', tags)
                taglist = [x for x in tags.split()]
                commontag = [x.lower() for x in taglist if x.lower() in querytag]
                matchingtags[link] = len(commontag)

            sortedmatchingtag = sorted(matchingtags, key=matchingtags.get, reverse=True)
            self.saveImages(sortedmatchingtag, qcopy, q)


class Environment:
    def __init__(self, query, tagset, directory):
        """

        :param query: query keywords for the text
        :param tagset: tag set for the text
        :param directory: parent directory
        """
        self.main(query, tagset, directory)

    def main(self, query, tagset, directory):
        """
        Call the Agent to retrieve and save images
        :param query: query keywords for the text
        :param tagset: tag set for the text
        :param directory: parent directory
        """
        if not os.path.exists(directory + '/images'):
            os.makedirs(directory + '/images')
        a = Agent(query, tagset, directory)
        a.retrieveImages()
