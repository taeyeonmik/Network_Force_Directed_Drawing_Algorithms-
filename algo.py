import time
from tqdm import tqdm
from itertools import combinations
import matplotlib.pyplot as plt
import numpy as np
from utils import initnode, initedge,\
                  Repulsion, Attraction, Gravity, AccelerationApply,\
                  divisionline2D, memory_usage, Analyzer
from quadtree import Region, QuadTree
from octettree import Space, OctetTree

class Algo:
    def __init__(self, preG, G, edges_idx, iter=100, octet=False):
        self.preG = preG
        self.G = G
        self.nodes = initnode(G, octet=octet)           # Initialize nodes
        self.edges = initedge(G.edges())                # Initialize edges
        self.edges_idx = edges_idx
        self.iter = iter
        self.octet = octet

    def run(self,
            repulsiontype='Eades', repulsioncons=10, repulsionideal=10,
            attractiontype='Eades', attractioncons=100, attractionideal=0.1,
            draw=False, savepath=None, memorycheck=False):

        # create force objects
        repulsion = Repulsion(type=repulsiontype)    # ["Eades", "FR", "linRepulsion"]
        attraction = Attraction(type=attractiontype) # ["Eades", "FR", "Normal", "Linlog"]
        gravity = Gravity()

        # time analyzer
        IterTimeAnalyzer = Analyzer()
        RepulsionTimeAnalyzer = Analyzer()
        AttractionTimeAnalyzer = Analyzer()
        ApplyForceTimeAnalyzer = Analyzer()

        # run
        for iter in tqdm(range(self.iter)):
            if iter == 0 and memorycheck:
                memory_usage(iter, message='before iter 1')
            if iter == self.iter - 1 and memorycheck:
                memory_usage(iter, message='before dernier iter')
            iterbefore = time.time()

            # init Tree
            minx, maxx, meanx = min([n.x for n in self.nodes]), max([n.x for n in self.nodes]), sum([abs(n.x) for n in self.nodes])/len(self.nodes)
            miny, maxy, meany = min([n.y for n in self.nodes]), max([n.y for n in self.nodes]), sum([abs(n.y) for n in self.nodes])/len(self.nodes)
            # Octet tree
            if self.octet:
                minz, maxz, meanz = min([n.z for n in self.nodes]), max([n.z for n in self.nodes]), sum([abs(n.z) for n in self.nodes])/len(self.nodes)
                width, length, height = maxx - minx, maxy - miny, maxz - minz
                # figure = Space(cx, cy, cz, w, l, h)
                figure = Space(minx + width / 2, miny + length / 2, minz + height / 2, width, length, height)
                Tree = OctetTree(figure)
            # Quad tree
            else:
                width, length = maxx - minx, maxy - miny
                # figure = Region(cx, cy, w, h)
                figure = Region(minx + width / 2, miny + length / 2, width, length)
                Tree = QuadTree(figure)


            if iter == 0 and memorycheck:
                memory_usage(iter, message='before insert')
            # Inserer des noeuds dans la structure de Tree
            for n in self.nodes:
                Tree.insert(n)
            if iter == 0 and memorycheck:
                memory_usage(iter, message='after insert')

            """
                repulsion
                1) Cette force s'applique sur tous les paires de noeuds
                   quel que soit la présence de l'arret entre ces deux.
                2) Il y a trois types de force repulsive
                   "Eades", "FR", et "linRepulsion"
            """
            comb = list(combinations(self.nodes, 2))
            if iter == 0 and memorycheck:
                memory_usage(iter, message='before Repusion')
            Repulsionbefore = time.time()

            if repulsiontype == "Eades":
                combidx = list(combinations(list(range(0, len(self.nodes))), 2))
                rpfactors = []
                for cb, cbidx in zip(comb, combidx):
                    rpfactor = repulsion.Eades(cb[0], cb[1], constant=repulsioncons, octet=self.octet)
                    # s'il y a une arret on garde le facteur repulsif pour calculer la force attractive avec ceci.
                    if cbidx in self.edges_idx:
                        rpfactors.append(rpfactor)
            else:
                for cb in comb:
                    if repulsiontype == "FR":
                        repulsion.FR(cb[0], cb[1], ideal=repulsionideal, octet=self.octet)
                    elif repulsiontype == "linRepulsion":
                        repulsion.RepulsionbyDegree(cb[0], cb[1], constant=repulsioncons, octet=self.octet)

            Repulsionafter = time.time()
            RepulsionTimeAnalyzer.append((Repulsionafter - Repulsionbefore))
            if iter == 0 and memorycheck:
                memory_usage(iter, message='after Repusion')

            """
                Attraction
                1) Cette force ne s'applique sur que les noueds qui sont liés entre eux 
                2) Il y a quatre types de force repulsive
                   "Eades", "FR", "Normal", et "Linlog"
            """
            # force d'attraction
            if iter == 0 and memorycheck:
                memory_usage(iter, message='before Attraction')
            Attractionbefore = time.time()

            if repulsiontype == "Eades" and attractiontype == "Eades":
                for pair, rpf in zip(self.edges_idx, rpfactors):
                    attraction.Eades(self.nodes[pair[0]], self.nodes[pair[1]], repulsionfactor=rpfactor, ideal=attractionideal, constant=attractioncons, octet=self.octet)
            else:
                for pair in self.edges_idx:
                    if attractiontype == "FR":
                        attraction.FR(self.nodes[pair[0]], self.nodes[pair[1]], ideal=attractionideal, octet=self.octet)
                    elif attractiontype in ["Normal", "Linlog"]:
                        attraction.Normal(self.nodes[pair[0]], self.nodes[pair[1]], constant=attractioncons, octet=self.octet)

            Attractionafter = time.time()
            AttractionTimeAnalyzer.append((Attractionafter - Attractionbefore))
            if iter == 0 and memorycheck:
                memory_usage(iter, message='after Attraction')

            # gravité
            g = 0.0001
            gravity.gravity(Tree, g)

            # Calcul d'accélaration et l'application des forces finales
            ApplyForcebefore = time.time()
            AccelerationApply(self.nodes, self.octet, dt=0.001)
            ApplyForceafter = time.time()
            ApplyForceTimeAnalyzer.append((ApplyForceafter - ApplyForcebefore))

            iterafter = time.time()
            IterTimeAnalyzer.append((iterafter - iterbefore))

            # drawing
            if self.octet:
                pos = {n: (self.nodes[i].x, self.nodes[i].y, self.nodes[i].z) for n, i in zip(self.preG.nodes(), range(len(self.nodes)))}
            else:
                pos = {n: (self.nodes[i].x, self.nodes[i].y) for n, i in zip(self.preG.nodes(), range(len(self.nodes)))}

            if draw:
                # coordonnances
                xs = [n.x for n in self.nodes]
                ys = [n.y for n in self.nodes]
                if self.octet:
                    zs = [n.z for n in self.nodes]

                # scatter plotting
                fig = plt.figure(figsize=(6, 6))
                if self.octet:
                    ax = fig.add_subplot(111, projection='3d')
                    ax.scatter(xs, ys, zs, marker='o', s=10)
                else:
                    ax = fig.add_subplot(111)
                    ax.scatter(xs, ys, marker='o', s=10)

                # plotting for edges
                for i, j in enumerate(self.preG.edges()):
                    x = np.array((pos[j[0]][0], pos[j[1]][0]))
                    y = np.array((pos[j[0]][1], pos[j[1]][1]))
                    if self.octet:
                        z = np.array((pos[j[0]][2], pos[j[1]][2]))
                        ax.plot(x, y, z, color='black', alpha=0.5)
                    else:
                        ax.plot(x, y, color='black', alpha=0.5)

                # division line
                if not self.octet:
                    # horizontal
                    ax.axhline(Tree.figure.cy, 0.0, 1.0, color='blue', linewidth=1.5)
                    # vertical
                    ax.axvline(Tree.figure.cx, 0.0, 1.0, color='blue', linewidth=1.5)
                    divisionline2D(ax, Tree)

                # plt.axis('off') # background
                plt.title(f"Repulsive and Attraction Force {repulsiontype} - {attractiontype} : iter {iter}")
                plt.savefig(f'{savepath}pos{iter}.png')
                plt.close('all')

            if iter == 0 and memorycheck:
                memory_usage(iter, message='after iter 1')
            if iter == self.iter - 1 and memorycheck:
                memory_usage(iter, message='after dernier iter')

        """ return
            1) Tree : Tree mis à jour
            2) nouvelles positions des noeuds
            3) TimeAnalyzers
        """
        return Tree, [(n.x, n.y, n.z) for n in self.nodes] if self.octet else [(n.x, n.y) for n in self.nodes], \
               IterTimeAnalyzer, RepulsionTimeAnalyzer, AttractionTimeAnalyzer, ApplyForceTimeAnalyzer




