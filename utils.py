import random
import psutil
import math
from math import sqrt, log
import networkx as nx

from quadtree import QuadTree
from octettree import OctetTree

def initnode(G, octet=False):
    random.seed(42)
    # Graph to scipy sparse matrix
    matrice = nx.to_scipy_sparse_matrix(G, dtype='f', format='lil')
    nodes = []
    for i in range(len(matrice.getnnz(axis=0))):
        n = Node(octet=octet)  # Using OctetTree
        n.mass = 1 + matrice.getnnz(axis=0)[i]
        # coordonnance
        n.x, n.y = round(random.uniform(0, 2), 2), round(random.uniform(0, 2), 2)
        if octet:
            n.z = round(random.uniform(0, 2), 2)
        nodes.append(n)
    return nodes

def initedge(edges):
    egs = []
    for edge in edges:
        # if edge[1] <= edge[0]:
        #     continue
        e = Edge()
        e.n1, e.n2 = edge[0], edge[1]
        egs.append(e)
    return egs

class Node:
    def __init__(self, octet=True):
        self.x, self.y = 0.0, 0.0
        self.dx, self.dy = 0.0, 0.0
        if octet:
            self.z = 0.0
            self.dz = 0.0
        self.mass = 0.0 # le nombre de noeuds qui sont liés + 1

class Edge:
    def __init__(self):
        self.n1 = None
        self.n2 = None

class Force:
    def __init__(self, type=None):
        self.type = type

    def Repulsion_movement(self, distance, type, n1, n2, xDist, yDist, zDist=0, ideal=None, constant=None):
        if distance > 0:
            if type == "Eades":
                factor = constant / distance
            elif type == "FR":
                factor = ideal**2 / distance # constant = ideal spring length
            elif type == "RepulsionbyDegree":
                factor = constant * n1.mass * n2.mass / distance
            n1.dx += xDist * factor
            n1.dy += yDist * factor
            n2.dx -= xDist * factor
            n2.dy -= yDist * factor
            if zDist:
                n1.dz += zDist * factor
                n2.dz -= zDist * factor
            if type == "Eades":
                return factor # repulsion facteur

    def Attraction_movement(self, distance, type, n1, n2, xDist, yDist, zDist=0, ideal=None, constant=None, repulsionfactor=None):
        if distance > 0:
            if type == "Eades":
                springfactor = constant * log(distance / ideal) # constant = ideal spring length
                factor = -(springfactor - repulsionfactor)
            elif type == "FR":
                factor = -(distance / ideal) # constant = ideal spring length
            elif type == "Normal":
                factor = -constant * distance
            elif type == "Linlog":
                factor = -constant * log(1 + distance)
            n1.dx += xDist * factor
            n1.dy += yDist * factor
            n2.dx -= xDist * factor
            n2.dy -= yDist * factor
            if zDist:
                n1.dz += zDist * factor
                n2.dz -= zDist * factor

    def Gravity_movement(self, distance, n, xDist, yDist, zDist=0, constant=None):
        if distance > 0:
            factor = n.mass * constant / distance
        n.dx -= xDist * factor
        n.dy -= yDist * factor
        if zDist:
            n.dz -= zDist * factor

class Repulsion(Force):
    """
        ideal    = ideal spring length
        constant = repulsion constant
    """
    # Eades
    def Eades(self, n1, n2, constant=10, octet=False):
        # self.type = "Eades"
        xDist = n1.x - n2.x
        yDist = n1.y - n2.y
        zDist = 0
        if octet:
            zDist = n1.z - n2.z
            distance = xDist * xDist + yDist * yDist + zDist * zDist  # Distance squared
        else:
            distance = xDist * xDist + yDist * yDist  # Distance squared

        # calcule des mouvements and return the repulsion factor
        repulsionfactor = self.Repulsion_movement(distance, self.type, n1, n2, xDist, yDist, zDist=zDist, constant=constant)
        return repulsionfactor

    # Fruchterman & Reingold
    def FR(self, n1, n2, ideal=10, octet=False):
        # self.type = "FR"
        xDist = n1.x - n2.x
        yDist = n1.y - n2.y
        zDist = 0
        if octet:
            zDist = n1.z - n2.z
            distance = sqrt(xDist * xDist + yDist * yDist + zDist * zDist)
        else:
            distance = sqrt(xDist * xDist + yDist * yDist)
        # calcule des mouvements
        self.Repulsion_movement(distance, self.type, n1, n2, xDist, yDist, zDist=zDist, ideal=ideal)

    # linRepulsion dans Force Atlas
    def RepulsionbyDegree(self, n1, n2, constant=10, octet=False):
        # self.type = "linRepulsion"
        xDist = n1.x - n2.x
        yDist = n1.y - n2.y
        zDist = 0
        if octet:
            zDist = n1.z - n2.z
            distance = xDist * xDist + yDist * yDist + zDist * zDist  # Distance squared
        else:
            distance = xDist * xDist + yDist * yDist  # Distance squared
        # calcule des mouvements
        self.Repulsion_movement(distance, self.type, n1, n2, xDist, yDist, zDist=zDist, constant=constant)


class Attraction(Force):
    """
    ideal = ideal spring length
    constant = attraction constant
    """
    def Eades(self, n1, n2, repulsionfactor=0, ideal=0.1, constant=100, octet=False):
        # self.type = "Eades"
        xDist = n1.x - n2.x
        yDist = n1.y - n2.y
        zDist = 0
        if octet:
            zDist = n1.z - n2.z
            distance = sqrt(xDist * xDist + yDist * yDist + zDist * zDist)  # Distance squared
        else:
            distance = sqrt(xDist * xDist + yDist * yDist)  # Distance squared
        # calcule des mouvements
        self.Attraction_movement(distance, self.type, n1, n2, xDist, yDist, zDist=zDist, ideal=ideal, constant=constant, repulsionfactor=repulsionfactor)

    def FR(self, n1, n2, ideal=0.1, octet=False):
        # self.type = "FR"
        xDist = n1.x - n2.x
        yDist = n1.y - n2.y
        zDist = 0
        if octet:
            zDist = n1.z - n2.z
            distance = xDist * xDist + yDist * yDist + zDist * zDist  # Distance squared
        else:
            distance = xDist * xDist + yDist * yDist  # Distance squared
        # calcule des mouvements
        self.Attraction_movement(distance, self.type, n1, n2, xDist, yDist, zDist=zDist, ideal=ideal)

    def Normal(self, n1, n2, constant=100, octet=False):
        # self.type = type
        xDist = n1.x - n2.x
        yDist = n1.y - n2.y
        zDist = 0
        if octet:
            zDist = n1.z - n2.z
            distance = xDist * xDist + yDist * yDist + zDist * zDist  # Distance squared
        else:
            distance = xDist * xDist + yDist * yDist  # Distance squared
        # calcule des mouvements
        self.Attraction_movement(distance, self.type, n1, n2, xDist, yDist, zDist=zDist, constant=constant)

class Gravity(Force):
    def gravity(self, Tree, g, globalcnt=0):
        if isinstance(Tree, OctetTree):
            octetchecker = True
        else:
            octetchecker = False

        sousregion = Tree.sousregion
        nonclusters, clusters = [], []
        for sous in sousregion:
            if not isinstance(sous, QuadTree) or isinstance(sous, OctetTree):
                if sous is not None:
                    nonclusters.append(sous)
            # le critère de la création d'un cluster.
            elif (isinstance(sous, QuadTree) and sous.nb_noeud >= 3) or (isinstance(sous, OctetTree) and sous.nb_noeud >= 4):
                clusters.append(sous)

        # calcul du centre
        if len(nonclusters) > 0:
            ClusterCenters = []
            for clst in clusters:
                cx, cy = 0.0, 0.0
                if octetchecker:
                    cz = 0.0
                cnt = 0
                for sous in clst.sousregion:
                    if isinstance(sous, Node):
                        cx += sous.x
                        cy += sous.y
                        if octetchecker:
                            cz += sous.z
                        cnt += 1
                    elif isinstance(sous, QuadTree) or isinstance(sous, OctetTree):
                        cx += sous.figure.cx
                        cy += sous.figure.cy
                        if octetchecker:
                            cz += sous.figure.cz
                        cnt += 1
                if octetchecker:
                    ClusterCenters.append((cx/cnt, cy/cnt, cz/cnt)) # centre du cluster
                else:
                    ClusterCenters.append((cx/cnt, cy/cnt))  # centre du cluster

            for n in nonclusters:
                for center in ClusterCenters:
                    xDist = n.x - center[0]
                    yDist = n.y - center[1]
                    if octetchecker:
                        zDist = n.z - center[2]
                        distance = sqrt(xDist * xDist + yDist * yDist + zDist * zDist)  # Distance squared
                    else:
                        zDist = 0
                        distance = sqrt(xDist * xDist + yDist * yDist)
                    self.Gravity_movement(distance, n, xDist, yDist, zDist=zDist, constant=g)
                    globalcnt += 1

        # recursivement
        for i, sous in enumerate(sousregion):
            try:
                Tree = sous
                self.gravity(Tree, g)
            except:
                None

    def gravity_simple(self, center, n, g):
        xDist = n.x - center[0]
        yDist = n.y - center[1]
        if len(center) == 3: # octet
            zDist = n.z - center[2]
        else:
            zDist = None
        if zDist:
            distance = sqrt(xDist * xDist + yDist * yDist + zDist * zDist)  # Distance squared
        else:
            distance = sqrt(xDist * xDist + yDist * yDist)  # Distance squared
        self.Gravity_movement(distance, n, xDist, yDist, zDist=zDist, constant=g)

def AccelerationApply(nodes, OctetChecker, dt=0.001):
    for n in nodes:
        if n.mass != 0:
            # calculer l'acceleration puis l'appliquer
            n.dx = (n.dx / n.mass) * dt
            n.dy = (n.dy / n.mass) * dt
            if OctetChecker:
                n.dz = (n.dz / n.mass) * dt

            # Application des forces finales
            n.x += n.dx
            n.y += n.dy
            if OctetChecker:
                n.z += n.dz

def divisionline2D(ax, Tree):
    sousregion = Tree.sousregion
    for i, sous in enumerate(sousregion):
        if isinstance(sous, QuadTree):
            # 수평선
            ax.axhline(sous.figure.cy, 0.0, 1.0, color='gray', linewidth=0.5)
            # 수직선
            ax.axvline(sous.figure.cx, 0.0, 1.0, color='gray', linewidth=0.5)
            try:
                Tree = sous
                # tracer les lignes récursivement jusqu'à le dernier arbre
                divisionline2D(ax, Tree)
            except:
                None
        else:
            pass

def divisionplane3D(ax, Tree):
    # non implémenté
    return None

def TreeStructureDraw():
    # non implémenté
    return None

#  J'ai ramène ces codes sur internet.
def memory_usage(iter, message: str = 'debug'):
    # current process RAM usage
    p = psutil.Process()
    rss = p.memory_info().rss / 2 ** 20 # Bytes to MB
    print(f"[iter : {iter} / {message}] memory usage: {rss: 10.5f} MB")


#  J'ai ramène cet Analyzer des fichiers de TP
class Analyzer:
    # Constructeur de la classe analyse
    # Complexite en temps/espace, pire et meilleur cas : O(1)
    def __init__(self):
        self.cost = [];
        self.cumulative_cost = [];
        self.cumulative_square = 0.;

    # Ajoute un cout, une valeur a l'analyse.
    # Complexite en temps/espace, pire cas : O(size)
    # Complexite en temps/espace, meilleur cas : O(1)
    # Complexite amortie : O(1)
    # @param x est la valeur que l'on souhaite ajouter a l'analyse.
    def append(self, x):
        self.cost.append(x)

        self.cumulative_cost.append(
            self.cumulative_cost[len(self.cumulative_cost) - 1] + x if len(self.cumulative_cost) > 0 else x)
        self.cumulative_square = self.cumulative_square + x * x

    # Renvoie la somme des couts enregistres dans cette analyse.
    # Complexite en temps/espace, meilleur cas : O(1)
    # @returns la somme des couts enregistres dans cette analyse.
    def get_total_cost(self):
        return self.cumulative_cost[len(self.cumulative_cost) - 1]

    # Renvoie le cout amorti d'une operation.
    # Complexite en temps/espace, meilleur cas : O(1)
    # @param pos est l'indice de l'operation pour laquelle on veut connaitre le cout amorti.
    # @returns le cout amorti d'une operation.
    def get_amortized_cost(self, pos):
        return self.cumulative_cost[pos] / pos if pos > 0 else self.cumulative_cost[pos]

        # Renvoie la moyenne des couts de toutes les operations enregistrees dans l'analyse.

    # Complexite en temps/espace, meilleur cas : O(1)
    # @returns la moyenne des couts de toutes les operations enregistrees dans l'analyse.
    def get_average_cost(self):
        if len(self.cumulative_cost) == 0:
            raise Exception('List is empty')
        return self.cumulative_cost[len(self.cumulative_cost) - 1] / len(self.cumulative_cost);

    # Renvoie la variance des couts de toutes les operations enregistrees dans l'analyse.
    # Complexite en temps/espace, meilleur cas : O(1)
    # @returns la variance des couts de toutes les operations enregistrees dans l'analyse.
    def get_variance(self):
        mean = self.get_average_cost()
        mean_square = mean * mean
        return self.cumulative_square - mean_square

    # Renvoie l'ecart-type des couts de toutes les operations enregistrees dans l'analyse.
    # Complexite en temps/espace, meilleur cas : O(1)
    # @returns l'ecart-type des couts de toutes les operations enregistrees dans l'analyse.
    def get_standard_deviation(self):
        return math.sqrt(self.get_variance())

    # Sauvegarde la liste des couts et des couts amortis dans un fichier.
    # Complexite en temps, meilleur/pire cas : O(size)
    # @param path est le chemin du fichier dans lequel la sauvegarde est faite.
    def save_values(self, path):
        f = open(path, 'w')
        for i in range(len(self.cost)):
            f.write(str(i) + " " + str(self.cost[i]) + "  " + str(self.get_amortized_cost(i)) + "\n")
        f.close()
