import random
from deap import base, creator, tools, algorithms
import numpy as np
import os
from bs4 import BeautifulSoup
from treelib import *
from PIL import Image
from PIL import ImageFile
import pickle
import matplotlib.pyplot as plt

ImageFile.LOAD_TRUNCATED_IMAGES = True

# np.random.seed(0)
osname = os.uname()[0]

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

    def makeTree(self, n):
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
        for i in usedimage:
            w, h = self.cw, self.ch
            name = self.imgdata.keys()[i]
            iTree.create_node(name, nodenum, parent=(nodenum / 2), data=LayoutNode(name, w, h))
            nodenum += 1
        return iTree

    def solveLayout(self, tree):
        for i in range(len(tree.nodes), 0, -1):
            node = tree.get_node(i)
            if len(node.fpointer) == 0:
                imgkey = self.imgdata.keys()[i - len(self.imgdata)]
                (ar, ti), pix = self.imgdata[imgkey]
            else:
                if node.data.name == 'V':
                    ar = 0
                    for c in sorted(tree.children(i)):
                        ar += c.data.aspectratio
                if node.data.name == 'H':
                    sumar = 0
                    multar = 1

                    # what is the purpose of sorting?
                    for c in sorted(tree.children(i)):
                        sumar += c.data.aspectratio
                        multar *= c.data.aspectratio
                    ar = float(multar) / float(sumar)
            node.data.aspectratio = ar

        for i in range(1, len(tree.nodes) + 1):
            node = tree.get_node(i)
            ar = node.data.aspectratio
            # root node, cw and ch are canvas width and height
            if node.bpointer == None:
                node.data.width = min(self.cw, ar * self.ch) - self.beta
                node.data.height = float(node.data.width) / float(ar) - self.beta
            else:
                p = tree.get_node(i / 2)
                pn, pw, ph = p.data.name, p.data.width, p.data.height
                # print i, pn, pw, ph
                node.data.width = min(pw, ar * ph) - self.beta
                node.data.height = float(node.data.width) / float(ar) - self.beta
                # print i, node.data.name, node.data.width, node.data.height, ar
        return

    def initIndividual(self, icls, n):
        """
        Initialize the individual - full binary tree
        Compute height, width and aspect ratio of each node
        according to the paper by Fan.
        :param n: number of images
        :return: Tree
        """
        iTree = self.makeTree(n)
        self.solveLayout(iTree)

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

    def __init__(self, cw, ch, b, imgdata, gen, popsize, Pc, Pm, lam):
        """
        Initialize GA toolbox
        :param gen: Number of GA generations
        :param popsize: Population size
        :param Pc: Crossover probability
        :param Pm: Mutation probability
        :param lam: Lambda - fitness function parameter
        :param cw: canvas width
        :param ch: canvas height
        :param b: beta (Space between images)
        :param imgdata: data about the images to be displayed
        """
        self.cw = cw
        self.ch = ch
        self.beta = b
        self.imgdata = imgdata
        self.ngen = gen
        self.popsize = popsize
        self.Pc = Pc
        self.Pm = Pm
        self.lam = lam
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
        self.toolbox.register("mutate", self.__mutate, indpb=0.2)
        self.toolbox.register("select", tools.selRoulette)

    def main(self):
        """
        Execute the GP algorithm to find a suitable layout
        :return: Best individual
        """
        pop = self.toolbox.population(n=self.popsize)
        hof = tools.ParetoFront(similar=np.array_equal)
        # hof = tools.HallOfFame(maxsize=1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("min", np.min)

        pop, log = algorithms.eaSimple(population=pop, toolbox=self.toolbox,
                            cxpb=self.Pc, mutpb=self.Pm, ngen=self.ngen, stats=stats,
                            halloffame=hof, verbose=False)

        return hof[0], log

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
        lam = self.lam
        sumti = 0
        S = self.cw * self.ch

        for i in range(len(self.imgdata), len(individual.nodes) + 1):
            node = individual.get_node(i)
            wi = node.data.width
            hi = node.data.height
            si = float(wi * hi) / float(S)
            imgkey = self.imgdata.keys()[i - len(self.imgdata)]
            (ar, ti), pix = self.imgdata[imgkey]
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
        self.solveLayout(indi)

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
    def __init__(self, n, f, d, imp, canvasw, canvash, beta, GAparams):
        """

        :param n: query keywords
        :param f: input filename
        :param d: parent directory
        :param imp: Random/Auto/User-specified importance estimator
        :param canvasw: Collage canvas width
        :param canvash: Collage canvas height
        :param beta: Inter-image space
        :param GAparams: GA parameters
        """
        self.main(n, f, d, imp, canvasw, canvash, beta, GAparams)

    def main(self, nouns, filename, directory, imp, canvasw, canvash, beta, GAparams):
        """
        Process image data, generate HTML files to show the layout,
        compute left,top position for every image in the best individual
        :param nouns: query keywords
        :param filename: input text filename
        :param directory: parent directory
        :param imp: Random/Auto/User-specified importance estimator
        :param canvasw: Collage canvas width
        :param canvash: Collage canvas height
        :param beta: Inter-image space
        :param GAparams: GA parameters
        """

        # Get image emphasis
        imgemphasis = {}
        if imp == 'auto' or imp == 'user':
            try:
                f = open('imgEmphasis.pkl', 'rb')
                imgemphasis = pickle.load(f)
                f.close()
            except:
                pass

        maxemphasis = 5
        minemphasis = 1
        if imgemphasis != {}:
            maxemphasis = max(imgemphasis.values())
            minemphasis = min(imgemphasis.values())

        imgdata = {}
        sumt = 0
        if nouns != [] and filename != '':
            for i, n in enumerate(nouns):
                try:
                    # t = word_score[n]
                    if isinstance(n, list):
                        n = ''.join(x for x in n)
                    else:
                        n = n.replace(' ', '')
                    n = n + '.jpg'
                    im = Image.open(directory + '/images/' + n)
                    w, h = im.size
                    ar = float(w) / float(h)
                    t = 1
                    if imgemphasis == {}:
                        t = random.randint(1, 5)
                    else:
                        # scale emphasis to a range 1-5
                        emphRange = maxemphasis - minemphasis
                        if emphRange == 0 or n not in imgemphasis:
                            t = 1
                        else:
                            t = (((imgemphasis[n] - minemphasis) * 4) / emphRange) + 1
                    sumt += t
                    imgdata[n] = ((ar, int(t)), im.size)
                except:
                    pass
        else:
            for files in os.listdir(directory):
                try:
                    if files.endswith(('.jpg', '.png', '.jpeg', '.JPG', '.PNG', '.JPEG')):
                        fname = os.path.splitext(os.path.basename(files))[0]
                        im = Image.open(directory + '/' + files)
                        w, h = im.size
                        ar = float(w) / float(h)
                        t = 1
                        if imgemphasis == {}:
                            t = random.randint(1, 5)
                        else:
                            # scale emphasis to a range 1-5
                            emphRange = maxemphasis - minemphasis
                            if emphRange == 0 or fname not in imgemphasis:
                                t = 1
                            else:
                                t = (((imgemphasis[fname] - minemphasis) * 4) / emphRange) + 1
                        sumt += t
                        imgdata[files] = ((ar, int(t)), im.size)
                except:
                    pass

        for i in range(len(imgdata)):
            imgkey = imgdata.keys()[i]
            (ar, ti), pix = imgdata[imgkey]
            ti = float(ti) / float(sumt)
            imgdata[imgkey] = ((ar, round(ti, 2)), pix)

        gen, popsize, Pc, Pm, lam = GAparams
        ga = Agent(canvasw, canvash, beta, imgdata, gen, popsize, Pc, Pm, lam)
        indi, stats = ga.main()
        indi.show()

        x = [i for i in range(len(stats))]
        y = [float(stats[i]['min']) for i in range(len(stats))]
        plt.plot(x, y)
        plt.xlabel('Generations')
        plt.ylabel('Fitness')
        plt.title('Fitness value over GA iterations')
        plt.show()

        canvas = Image.new('RGB', (canvasw, canvash))

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
            try:
                node = indi.get_node(i)
                node.data.width = round(float(node.data.width), 2)
                node.data.height = round(float(node.data.height), 2)
                if filename == '':
                    foldername = ''
                else:
                    foldername = 'images'

                if osname == 'Windows':
                    name = directory + '\\'+foldername+'\\' + node.data.name
                else:
                    name = directory + '/'+foldername+'/' + node.data.name

                im = Image.open(name)
                im = im.resize((int(node.data.width), int(node.data.height)), Image.ANTIALIAS)
                canvas.paste(im, (node.data.x1, node.data.y1))

                imgkey = imgdata.keys()[i - len(imgdata)]
                index = 0
                for index, n in enumerate(nouns):
                    n = ''.join(x for x in n)
                    if n == node.data.name:
                        break
                positions = "position:absolute;top:" + str(node.data.y1) + ";left:" + str(node.data.x1) + \
                    ";width:" + str(int(node.data.width)) + ";height:" + str(int(node.data.height))
                img = img + "<img style=" + positions + " src=" + name + "></img>"
            except Exception as e:
                if "height and width must be > 0" in e:
                    print "Unable to include all images in the canvas."
                    print "Increase the size of the canvas so that all the images can fit."
                    print "For 150 images, a canvas of size > 7500x7500 is recommended."
                    print "Please try again."
                    return
                else:
                    print e
                pass

        html = html + img + """</html>"""

        if osname == 'Windows':
            openfolder = directory + '\\results'
        else:
            openfolder = directory + '/results'
        if not os.path.exists(openfolder):
            os.makedirs(openfolder)
        soup = BeautifulSoup(html, 'html.parser')

        if osname == 'Windows':
            openfolder = directory + '\\results\\'
        else:
            openfolder = directory + '/results/'
        if filename != '':
            with open(openfolder + filename.split('.txt')[0] + '.html', 'w') as f:
                f.write(str(soup.prettify('utf-8')))
            canvas.save(openfolder + filename.split('.txt')[0] + '.jpg')
            print "The collage is saved in " + openfolder + filename.split('.txt')[0] + ".html\n"
        else:
            with open(openfolder + 'collage.html', 'w') as f:
                f.write(str(soup.prettify('utf-8')))
            canvas.save(openfolder + 'collage.jpg')
            print "The collage is saved in " + directory + "/results/collage.html\n"


