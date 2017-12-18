import random
from deap import base, creator, tools, algorithms
import numpy as np
import os
from bs4 import BeautifulSoup
from treelib import *
from PIL import Image
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

# np.random.seed(0)


class LayoutNode:
    """
    Store data related to each node.
    Data: name, width, height, aspect ratio, <left,top> position
    """
    name = ''
    width = 0
    height = 0
    aspectratio = 1
    x1 = 0
    y1 = 0

    def __init__(self, n, w, h):
        self.name = n
        self.width = w
        self.height = h


class Agent:
    """
    Execute GP algorithm to find a layout for images
    """
    def getInternalNode(self):
        """
        Return a name for internal nodes in the binary tree
        :return: 'v' or 'h'
        """
        name = random.sample(set('VH'), 1)
        return name[0]

    def initIndividual(self, icls, n):
        """
        Initialize the individual - full binary tree
        Compute height, width and aspect ratio of each node
        according to the paper by Fan.
        :param n: number of images
        :return: Tree
        """
        nodenum = 1
        iTree = Tree()
        name = self.getInternalNode()
        iTree.create_node(name, nodenum, data=LayoutNode(name, self.cw, self.ch))
        nodenum += 1
        for i in range(n - 2):  # create internal nodes
            w, h = self.cw, self.ch
            name = self.getInternalNode()
            iTree.create_node(name, nodenum, parent=(nodenum / 2), data=LayoutNode(name, w, h))
            nodenum += 1
        usedimage = [x for x in range(n)]
        random.shuffle(usedimage)
        for i in range(len(usedimage)):
            w, h = self.cw, self.ch
            name = self.imgdata.keys()[i]
            iTree.create_node(name, nodenum, parent=(nodenum / 2), data=LayoutNode(name, w, h))
            nodenum += 1
        for i in range(len(iTree.nodes), 1, -1):
            node = iTree.get_node(i)
            if len(node.fpointer) == 0:
                imgkey = self.imgdata.keys()[i - len(self.imgdata)]
                (ar, ti), pix = self.imgdata[imgkey]
            else:
                if node.data.name == 'V':
                    ar = 0
                    for c in sorted(iTree.children(i)):
                        ar += c.data.aspectratio
                if node.data.name == 'H':
                    sumar = 0
                    multar = 1
                    for c in sorted(iTree.children(i)):
                        sumar += c.data.aspectratio
                        multar *= c.data.aspectratio
                    ar = float(multar) / float(sumar)
            node.data.aspectratio = ar
        for i in range(1, len(iTree.nodes) + 1):
            node = iTree.get_node(i)
            ar = node.data.aspectratio
            if node.bpointer == None:
                node.data.width = min(self.cw, ar * self.ch) - self.beta
                node.data.height = float(node.data.width) / float(ar) - self.beta
            else:
                p = iTree.get_node(i / 2)
                pn, pw, ph = p.data.name, p.data.width, p.data.height
                node.data.width = min(pw, ar * ph) - self.beta
                node.data.height = float(node.data.width) / float(ar) - self.beta
                # print node.data.name, node.data.width, node.data.height
        return icls(iTree)

    def initPopulation(self, pcls, ind_init, n):
        """
        Initialize the population
        :param ind_init: initialize individual
        :param n: number of individuals
        :return: population
        """
        color = []
        numimages = len(self.imgdata)
        for i in range(1, n + 1):
            color.append(numimages)
        return pcls(ind_init(c) for c in color)

    def __init__(self, cw, ch, b, imgdata):
        """
        Initialize GA toolbox
        :param cw: canvas width
        :param ch: canvas height
        :param b: beta (Space between images)
        :param imgdata: data about the images to be displayed
        """
        self.cw = cw
        self.ch = ch
        self.beta = b
        self.imgdata = imgdata
        # Instantiate creator variables
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", Tree, fitness=creator.FitnessMin)

        # Create toolbox
        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", self.initIndividual,
                              creator.Individual)

        self.toolbox.register("population", self.initPopulation, list, self.toolbox.individual)

        # Register toolbox functions
        self.toolbox.register("evaluate", self.__get_fitness)
        self.toolbox.register("mate", self.cxOnePointCopy)
        self.toolbox.register("mutate", self.__mutate, indpb=0.02)
        self.toolbox.register("select", tools.selRoulette)

    def main(self):
        """
        Execute the GP algorithm to find a suitable layout
        :return: Best individual
        """
        pop = self.toolbox.population(n=10)
        hof = tools.ParetoFront(similar=np.array_equal)
        # hof = tools.HallOfFame(maxsize=1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("min", np.min)
        stats.register("avg", np.mean)

        algorithms.eaSimple(population=pop, toolbox=self.toolbox,
                            cxpb=0.7, mutpb=0.2, ngen=500, stats=stats,
                            halloffame=hof, verbose=False)

        return hof[0]

    def getk(self, si, ti):
        """
        Part of computation of fitness value
        :param si: existing size of image
        :param ti: desired size of image
        :return: k
        """
        return 5 if (float(si) / float(ti)) < 0.5 else 1

    # Score individual fitness
    def __get_fitness(self, individual):
        """
        Compute fitness based on the function given in the paper by Fan
        :param individual: a full binary tree representing a possible layout
        :return: fitness value
        """
        SiList = []
        TiList = []
        KiList = []
        lam = 0.15
        sumti = 0
        S = self.cw * self.ch
        for i in range(len(self.imgdata)):
            imgkey = self.imgdata.keys()[i]
            (ar, ti), pix = self.imgdata[imgkey]
            sumti += ti

        for i in range(len(self.imgdata), len(individual.nodes) + 1):
            node = individual.get_node(i)
            wi = node.data.width
            hi = node.data.height
            si = float(wi * hi) / float(S)
            imgkey = self.imgdata.keys()[i - len(self.imgdata)]
            (ar, ti), pix = self.imgdata[imgkey]
            ti = float(ti) / float(sumti)
            k = self.getk(si, ti)
            SiList.append(si)
            TiList.append(ti)
            KiList.append(k)
        C1 = 0
        for i in range(len(SiList)):
            C1 += (KiList[i] * ((SiList[i] - TiList[i]) ** 2))
        C2 = 0
        for i in range(len(SiList)):
            C2 += SiList[i]

        C2 = lam * (1 - C2)

        fitness = C1 + C2
        return fitness,

    def recomputeWH(self, indi):
        """
        After crossover or mutation, the data for each node needs to be
        recomputed. This data is width, height, and aspect ratio.
        :param indi: the tree for which width and height is being recomputed
        """
        for i in range(len(indi.nodes), 1, -1):
            node = indi.get_node(i)
            if len(node.fpointer) == 0:
                imgkey = self.imgdata.keys()[i - len(self.imgdata)]
                (ar, ti), pix = self.imgdata[imgkey]
            else:
                if node.data.name == 'V':
                    ar = 0
                    for c in sorted(indi.children(i)):
                        ar += c.data.aspectratio
                if node.data.name == 'H':
                    sumar = 0
                    multar = 1
                    for c in sorted(indi.children(i)):
                        sumar += c.data.aspectratio
                        multar *= c.data.aspectratio
                    ar = float(multar) / float(sumar)
            node.data.aspectratio = ar
        for i in range(1, len(indi.nodes) + 1):
            node = indi.get_node(i)
            ar = node.data.aspectratio
            if node.bpointer == None:
                node.data.width = min(self.cw, ar * self.ch) - self.beta
                node.data.height = float(node.data.width) / float(ar) - self.beta
            else:
                p = indi.get_node(i / 2)
                pn, pw, ph = p.data.name, p.data.width, p.data.height
                node.data.width = min(pw, ar * ph) - self.beta
                node.data.height = float(node.data.width) / float(ar) - self.beta
                # print node.data.name, node.data.width, node.data.height

    # def __create_value(self, node):
    #     """
    #     As part of mutation, change the name of the internal node
    #     :param node: node of the tree
    #     :return: changed name of the internal node
    #     """
    #     node.data.name = self.getInternalNode()
    #     return node

    # Mutate genes
    def __mutate(self, individual, indpb):
        """
        Change the name of internal nodes with a certain probability
        :param individual: individual represented as tree
        :param indpb: probability of mutation
        :return: mutated individual
        """
        for i in range(1, len(self.imgdata)):
            if random.random() <= indpb:
                node = individual.get_node(i)
                if node.data.name == 'H':
                    node.tag = node.data.name = 'V'
                else:
                    node.tag = node.data.name = 'H'
                # self.__create_value(individual.get_node(i))

        # for i in range(len(self.imgdata), len(individual.nodes) + 1):
        #     if random.random() <= indpb:
        #         j = i
        #         while j == i:
        #             j = random.randint(len(self.imgdata), len(individual.nodes))
        #         basenode = individual.get_node(i)
        #         swapnode = individual.get_node(j)
        #         basename = basenode.data.name
        #         swapname = swapnode.data.name
        #         basenode.tag = basenode.data.name = swapname
        #         swapnode.tag = swapnode.data.name = basename

        self.recomputeWH(individual)
        return individual,

    def cxOnePointCopy(self, ind1, ind2):
        """
        Swap subtrees with a certain probability
        :param ind1: first individual
        :param ind2: second individual
        :return: 2 individuals after crossover
        """
        size = len(self.imgdata)
        cxpoint = random.randint(2, size - 1)
        p1 = p2 = cxpoint / 2
        tempsubtree2 = ind2.subtree(cxpoint)
        tempsubtree1 = ind1.subtree(cxpoint)

        ind1.remove_subtree(cxpoint)
        ind2.remove_subtree(cxpoint)

        ind1.paste(p1, tempsubtree2)
        ind2.paste(p2, tempsubtree1)

        for i in range(1, len(ind1.nodes) + 1):
            node = ind1.get_node(i)
            sorted(node._fpointer)
        for i in range(1, len(ind2.nodes) + 1):
            node = ind2.get_node(i)
            sorted(node._fpointer)
        self.recomputeWH(ind1)
        self.recomputeWH(ind2)
        return ind1, ind2


class Environment:
    """
    Processing images that need to be added to the layout
    Interface with GA agent
    Save results
    """
    def __init__(self, n, f, d):
        """

        :param n: query keywords
        :param f: input filename
        :param d: parent directory
        """
        self.main(n, f, d)

    def main(self, nouns, filename, directory):
        """
        Process image data, generate HTML files to show the layout,
        compute left,top position for every image in the best individual
        :param nouns: query keywords
        :param filename: input text filename
        :param directory: parent directory
        """
        canvasw, canvash = 1920, 1080
        print "GA to generate a compact collage begins..."
        print "Enter the desired canvas size: "
        w = raw_input("Width ")
        h = raw_input("Height ")
        if w:
            canvasw = int(w)
        if h:
            canvash = int(h)

        beta = 3
        imgdata = {}
        for i, n in enumerate(nouns):
            try:
                # t = word_score[n]
                if isinstance(n, list):
                    n = ''.join(x for x in n)
                else:
                    n = n.replace(' ', '')
                im = Image.open(directory + '/images/' + n + '.jpg')
                w, h = im.size
                ar = float(w) / float(h)
                t = random.randint(1, 5)
                imgdata[n] = ((ar, t), im.size)
            except:
                pass
        ga = Agent(canvasw, canvash, beta, imgdata)
        indi = ga.main()
        indi.show()

        html = """
                <html>
                <head>
                <title>Photo layout</title>
                </head>
                <body>
                <p>
            """
        img = ''
        for i in range(1, len(indi.nodes) + 1):
            pnode = indi.get_node(i)
            for c in sorted(indi.children(i)):
                c.data.x1 = pnode.data.x1
                c.data.y1 = pnode.data.y1
                if c.identifier % 2 == 1:  # right child
                    if pnode.data.name == 'V':
                        c.data.x1 += int(indi.siblings(c.identifier)[0].data.width)
                    if pnode.data.name == 'H':
                        c.data.y1 += int(indi.siblings(c.identifier)[0].data.height)
                        # print c.data.name, c.data.x1, c.data.y1, c.data.width, c.data.height

        for i in range(len(imgdata), len(indi.nodes) + 1):
            node = indi.get_node(i)
            name = directory + '/images/' + node.data.name + '.jpg'
            im = Image.open(name)
            im = im.resize((int(node.data.width), int(node.data.height)), Image.ANTIALIAS)
            imgkey = imgdata.keys()[i - len(imgdata)]
            index = 0
            for index, n in enumerate(nouns):
                n = ''.join(x for x in n)
                if n == node.data.name:
                    break
            positions = "position:absolute;top:" + str(node.data.y1) + ";left:" + str(node.data.x1) + \
                    ";width:" + str(int(node.data.width)) + ";height:" + str(int(node.data.height))
            img = img + "<img style=" + positions + " src=" + name + " title=" + str(index + 1) + "></img>"

        html = html + img + """</html>"""

        if not os.path.exists(directory + '/results'):
            os.makedirs(directory + '/results')
        soup = BeautifulSoup(html, 'html.parser')
        with open(directory + '/results/' + filename.split('.txt')[0] + '.html', 'w') as f:
            f.write(str(soup.prettify('utf-8')))

        print "The collage is saved in " + directory + '/results/' + filename.split('.txt')[0] + ".html\n"
