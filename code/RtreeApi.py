# encoding: utf-8
from math import log
from math import ceil
from time import time
from FileHandler import *
from MRtree import *
from PartitionAlgorithm import *
import datetime

#  ERRORS
class RtreeError(Exception):
    def __init__(self, value):
        super(RtreeError, self).__init__()
        self.value = value
    def __str__(self):
        return (str(type(self))) + " " + repr(self.value)

class RtreeApi(object):
    # d          : dimension de vectores del arbol
    # M          : capacidad maxima de nodos y hojas
    # maxE       : cantidad maxima de elementos que almacenara el Rtree
    # reset      : cuando es True, se construye un nuevo arbol, si no, se carga de disco
    # initOffset : offset desde se cargara nodo raiz
    def __init__(self, d, M = 100, maxE = 100000, reset = False, initOffset = 0, dataFile = 'rtree'):
        self.nfh = RtreeFileHandler(  loadDataFile = "data" + str(d) + "D.bin",
                                    dataFile = dataFile + str(d) + "D.bin",
                                    d = d, M = M,
                                    initOffset = initOffset)

        self.pa = None
        self.sa = None

        self.cache = []                              # cache: lista de nodos visitados
        self.k = 0                                   # k: nodos en cache
        self.H = int(ceil(log(maxE, self.M())) -1)   # H: altura maxima del arbol
        self.E = maxE

        #Metricas
        #Mean insertion time
        self.meanInsertionTime = None
        self.insertionsCount = 0

        #Mean internal and external nodes
        self.internalNodeCount = 0
        self.leafCount = 0

          #Mean search time
        self.meanSearchTime = None
        self.searchCount = 0

          #Mean visited nodes
        self.visitedNodes = 0

          #Mean splits per node
        self.splitCount = 0

        self.meanTotalNodes = 0
        self.meanInternalNodes = 0

        self.currentNode = None
        self.root        = None

        # Inicializacion de la raiz
        if reset:
            self.resetRoot()
        else:
            # Se carga la raiz de disco
            self.loadRoot(initOffset)

    def loadRoot(self, initOffset):
        self.currentNode = self.read(initOffset)
        self.root = self.currentNode

    def resetRoot(self):
        # Se construye una raiz vacia
        self.currentNode = self.newNode()

        # Creo dos hojas para mantener invariante de la raiz
        newLeaf1 = self.newLeaf()
        newLeaf2 = self.newLeaf()

        # Reservo un espacio en memoria para el nodo actual
        self.allocateTree()

        # Guardo dos hojas de la raiz en disco
        self.save(newLeaf1)
        self.save(newLeaf2)

        # Agrego las hojas al nodo raiz
        self.currentNode.insert(newLeaf1.getMbrPointer())
        self.currentNode.insert(newLeaf2.getMbrPointer())

        # Guardo el nodo raiz en disco
        self.save()

        self.setAsRoot() # convertir nodo actual en raiz

    # Advertencia : USAR SOLO CON ARBOLES PEQUEÑOS!
    def __str__(self):
        def toStr(tree, s = "", l = 0, i = 0):
            s = s + " "*(l*4) + "Node: l=" + str(l) + " i=" + str(i) + " ->\n" + " "*(l*4) + tree.toStr()

            if tree.isANode():
                i = 0
                children = tree.getChildren()
                if len(children) != 0:
                    s = s + "\n" 
                for child in children:
                    childTree = self.read(child.getPointer())
                    s = toStr(childTree, s, l + 1, i)
                    i = i + 1
            else:
                i = 0
                children = tree.getChildren()
                if len(children) != 0:
                    s = s + "\n" 
                for child in children:
                    s = s + " "*(4*l+1) + "Leaf: l=" + str(l) + " i=" + str(i) + " -> " + str(child) + "\n"
                    i = i + 1
            return s
        return toStr(self.currentNode)

    def printTree(self):
        self.printRec(self.currentNode)
        self.goToRoot()

    def printRec(self, currentNode):
        print(str(currentNode))

        if currentNode.isANode():
            for child in currentNode.getChildren():
                self.printRec(self.read(child.getPointer()))
        else:
            i = 0
            for child in currentNode.getChildren():
                print("i: " + str(i) + " " + (str(child)))
                i =  i + 1

    def allocateTree(self, tree = None):
        if tree == None:
            self.nfh.allocateTree(self.currentNode)
        else:
            self.nfh.allocateTree(tree)

    # Fija punteros auxiliares de la estructura a la  raiz
    def goToRoot(self):
        self.cache = []
        self.k     = 0
        self.currentNode = self.root

    def setAsRoot(self, offset = 0):
        self.currentNode.setAsRoot(offset)
        self.root = self.currentNode

    # Crea una nueva raiz recibiendo mbrPointer del hermano recien creado
    def makeNewRoot(self, childMbrPointer):
        newRoot = self.newNode()
        newRoot.setAsRoot(0) # raiz siempre en comienzo del archivo

        self.nfh.reAllocate(self.currentNode)

        newRoot.insert(self.currentNode.getMbrPointer())
        newRoot.insert(childMbrPointer)
        self.save(newRoot)

        self.root  = newRoot
        self.cache = [newRoot]
        self.k     = 1

    # Capacidad minima de nodos y hojas
    def m(self):
        return self.nfh.m

    # Capacidad maxima de nodos y hojas
    def M(self):
        return self.nfh.M

    def d(self):
        return self.nfh.d

    def needToSplit(self):
        res = self.currentNode.needToSplit()
        if res:
            self.incrementSplitCount()
        return res

    def newLeaf(self):
        self.incrementLeafCount()
        return MLeaf(M = self.M(), d = self.d())

    def newNode(self):
        self.incrementInternalNodeCount()
        return MNode(M = self.M(), d = self.d())

    # Busqueda radial de objeto
    def search(self, radialMbr, verbose = False):
        fileName = "../searchs/E:" + str(self.E) + " M:" + str(self.M()) + " d:" + str(self.d()) + " busqueda %s.txt"%datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        f = open(fileName, 'w+')
        f.write(str(radialMbr) + "\n\n")
        t0 = time()
        self.searchR(radialMbr, f, verbose)
        t1 = time()
        f.close()
        self.incrementMeanSearchTime(t1 - t0)
        self.goToRoot()

    def searchR(self, radialMbr, file, verbose):
        results = []
        if self.currentNode.isANode():
            self.incrementVisitedNodes()
            selections = self.chooseTreeForSearch(radialMbr)
            for s in  selections:
                self.seekNode(s)
                self.searchR(radialMbr, file, verbose)
        else:
            for c in self.currentNode.getChildren():
                if radialMbr.areIntersecting(c):
                    if verbose:
                        results = results + [c]
                    else:
                        results = results + [c.getPointer()]

            if self.currentHeigth() > 0:
                self.chooseParent()
        for r in results:
            file.write(str(r)+" ")

    # Insercion de un mbrPointer
    def insert(self, mbrPointer):
        pass

    def currentHeigth(self):
        return self.k

    # Guarda el nodo actual en disco
    def save(self,tree = None):
        if tree != None:
            self.nfh.saveTree(tree)
        else:
            self.nfh.saveTree(self.currentNode)

    # Lee y entrega un nodo u hoja de disco
    def read(self, treeOffset):
        return self.nfh.readTree(treeOffset)

    # Actualiza nodo actual insertando nuevo hijo y guardando posteriormente en disco
    def insertChild(self, newChild):
        self.currentNode.insert(newChild)
        self.updateCache()
        self.save()

    # Actualiza nodo actual con la nueva version de uno de sus hijos (mbr,pointer)
    def updateChild(self, mbrPointer):
        self.currentNode.updateChild(mbrPointer)
        self.updateCache()
        self.save()

    # Actualiza en el cache el nodo que acaba de cambiar
    def updateCache(self):
        k = self.currentHeigth()
        if len(self.cache) > k:
            self.cache[k] = self.currentNode

    # Vuelve puntero del nodo padre al ultimo almacenado en cache
    def goToLastLevel(self):
        self.k = len(self.cache)

    # Baja un nivel en el arbol y prepara cache y nodo actual
    def seekNode(self, mbrPointer):
        pointer = mbrPointer.getPointer()

        if len(self.cache) > self.k:
            self.cache[self.k - 1] = self.currentNode
        else:
            self.cache = self.cache + [self.currentNode]
        self.k = self.k + 1

        self.currentNode = self.read(pointer)
        return

    # Escoger el padre del nodo actual
    def chooseParent(self, destructive = True):
        if self.k > 0:
            self.currentNode = self.cache[self.k - 1]
            if destructive:
                self.cache = self.cache[0:self.k-1] # Por defecto el cache se destruye al subir al padre
            self.k = self.k - 1
        else:
            raise RtreeError("Ya esta en la raiz")

    # Escoge los nodos que intersectan con el mbr para proceder con la insercion
    def chooseTree(self, mbrPointer):
        childrenMbrs = self.currentNode.getChildren()
        return self.sa.select(mbrPointer, childrenMbrs)

    # Escoge los nodos segun criterio de busqueda
    def chooseTreeForSearch(self, mbrO):
        childrenMbrs = self.currentNode.getChildren()
        return self.sa.radialSelect(mbrO, childrenMbrs)

    # Ajusta mbrs de todos los nodos hasta llegar a la raiz
    def propagateAdjust(self):
        while self.currentHeigth() > 0:
            childMbrPointer = self.currentNode.getMbrPointer()

            self.chooseParent() # cambia currentNode y sube un nivel del arbol

            self.updateChild(childMbrPointer) # actualiza el nodo actual con la nueva version de su nodo hijo

    def incrementMeanSearchTime(self, delta):
        if self.meanSearchTime == None:
            self.meanSearchTime = delta
        else:
            self.meanSearchTime = (self.meanSearchTime * self.searchCount + delta) / (self.searchCount + 1)
        self.searchCount += 1

    def incrementMeanInsertionTime(self, delta):
        if self.meanInsertionTime == None:
            self.meanInsertionTime = delta
        else:
            self.meanInsertionTime = (self.meanInsertionTime * self.insertionsCount + delta) / (self.insertionsCount + 1)
        self.insertionsCount += 1

    def incrementVisitedNodes(self):
        self.visitedNodes += 1

    def incrementSplitCount(self):
        self.splitCount += 1

    def incrementLeafCount(self):
        self.leafCount += 1

    def incrementInternalNodeCount(self):
        self.internalNodeCount += 1

    def computeMeanNodes(self):
        self.meanTotalNodes = (self.meanTotalNodes * (self.insertionsCount - 1) + (self.internalNodeCount + self.leafCount))/self.insertionsCount
        self.meanInternalNodes = (self.meanInternalNodes * (self.insertionsCount - 1) + self.internalNodeCount)/self.insertionsCount

    def getMeanNodePartitions(self):
        return self.splitCount/(self.internalNodeCount + self.leafCount)

    def getMeanVisitedNodes(self):
        return self.visitedNodes/self.searchCount

if __name__ == "__main__":
    d = 2
    M = 100
    rApi = RtreeApi(d = d, M = 100, maxE = 10**6, reset = True, initOffset = 0)
    print(rApi)
