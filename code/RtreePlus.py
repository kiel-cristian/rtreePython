# encoding: utf-8
from SelectionManager import *
from RtreeApi import *
from MbrGenerator import *

# Clases auxiliares para manejar estados posibles posteriores a una insercion recursiva.
# La idea de usar estas estructuras es la de manejar los casos de borde sin salir de la recursion principal
# (Basado en Trampolines)
class RtreePlusStatus(object):
    def __init__(self, tree = None, data = None):
        self.tree = tree
        self.data = data

    def handle(self):
        return None

class RtreePlusAdjustStatus(RtreePlusStatus):
    def __init__(self, tree):
        super(RtreePlusAdjustStatus, self).__init__(tree)

    def handle(self):
        return self.tree.adjustOneLevel()

class RtreePlusSplitStatus(RtreePlusStatus):
    def __init__(self, tree, splitMbrPointer):
        super(RtreePlusSplitStatus, self).__init__(tree, splitMbrPointer)

    def handle(self):
        return self.tree.splitOneLevel(self.data)

class RtreePlusBackToRecursionLevel(RtreePlusStatus):
    def __init__(self, tree):
        super(RtreePlusBackToRecursionLevel, self).__init__(tree)

    def handle(self):
        return self.tree.goToLastLevel()

class RtreePlus(RtreeApi):
    # d          : dimension de vectores del arbol
    # M          : capacidad maxima de nodos y hojas
    # maxE       : cantidad maxima de elementos que almacenara el RtreePlus
    # reset      : cuando es True, se construye un nuevo arbol, si no, se carga de disco
    # initOffset : offset desde se cargara nodo raiz
    def __init__(self, d, M = 100, maxE = 100000, reset = False, initOffset = 0):
        super(RtreePlus, self).__init__(d = d, M = M, maxE = maxE, reset = reset, initOffset = initOffset, dataFile = "r+tree")
        # Algoritmo de seleccion de mejor nodo a insertar
        # en base a interseccion de areas
        self.pa = SweepPartition()
        self.sa = RtreePlusSelection()
        self.reachedNodes = {}

        for h in range(self.H):
            self.reachedNodes[h]  = {}

    def goToRoot(self):
        for h in range(self.H):
            self.reachedNodes[h]  = {}
        super(RtreePlus, self).goToRoot()

    def insert(self, mbrPointer):
        print("insert")
        t0 = time()

        self.insertR(mbrPointer)

        t1 = time()
        self.incrementMeanInsertionTime(t1-t0)
        self.computeMeanNodes()
        self.goToRoot()

    def markNodeAsVisited(self, next):
        try:
            self.reachedNodes[self.currentHeigth()][next.getPointer()] = True
        except:
            self.reachedNodes[self.currentHeigth()] = {}
            self.reachedNodes[self.currentHeigth()][next.getPointer()] = True

    def nodeIsVisited(self, next):
        try:
            return self.reachedNodes[self.currentHeigth()][next.getPointer()] == True
        except:
            return False

    def goToLastLevel(self):
        super(RtreePlus, self).goToLastLevel()
        # return RtreePlusStatus(self)

    def chooseNearestTree(self, mbrPointer):
        return self.sa.selectNearest(mbrPointer, self.currentNode.getChildren())

    def chooseAnyTree(self):
        return self.sa.selectAny(self.currentNode.getChildren())

    # Ajusta mbrs de todos los nodos hasta llegar a la raiz
    def propagateAdjust(self, destructive = True):
        while self.currentHeigth() > 0:
            childMbrPointer = self.currentNode.getMbrPointer()

            self.chooseParent(destructive) # cambia currentNode y sube un nivel del arbol

            self.updateChild(childMbrPointer) # actualiza el nodo actual con la nueva version de su nodo hijo

        self.goToLastLevel()

    # Propaga el split hasta donde sea necesario
    def propagateSplit(self, splitMbrPointer, destructive = True):
        lastSplit = splitMbrPointer
        lastNode = self.currentNode

        while self.currentHeigth() >= 0:
            # Se llego a la raiz
            if self.currentHeigth() == 0:
                self.makeNewRoot(lastSplit)
                break

            self.chooseParent(destructive) # cambia currentNode y sube un nivel del arbol
            self.updateChild(lastNode.getMbrPointer())

            if self.needToSplit():
                lastSplit = self.splitNode(lastSplit)
                lastNode  = self.currentNode
            else:
                self.insertChild(lastSplit)
                break
        self.propagateAdjust(destructive)

    def insertR(self, mbrPointer):
        # Bajo por todos los nodos adecuados
        if self.currentNode.isANode():
            trees = self.chooseTree(mbrPointer)

            if len(trees) == 0:
                trees = [self.chooseNearestTree(mbrPointer)]

            if len(trees) == 0:
                trees = [self.chooseAnyTree()]

            if trees[0] == None:
                newLeaf = self.newLeaf()
                newLeaf.insert(mbrPointer)
                self.save(newLeaf)

                if self.currentNode.needToSplit():
                    self.propagateSplit(newLeaf, False)
                else:
                    self.insert(newLeaf.getMbrPointer())
                    self.propagateAdjust(False)
            else:
                for next in trees:
                    if not self.nodeIsVisited(next):
                        self.seekNode(next)
                        self.markNodeAsVisited(next)

                        self.insertR(mbrPointer)
        else:
            if self.needToSplit():
                newLeafMbrPointer = self.splitLeaf(mbrPointer)
                self.propagateSplit(newLeafMbrPointer, False) # propago hacia el padre el split
            else:
                self.insertChild(mbrPointer)
                self.propagateAdjust(False) # ajusta mbrs hasta la raiz

        if self.currentHeigth() > 0:
            self.chooseParent()

    # Gatilla split en nodo, propaga split de nodos hijos de ser necesario y retorna el mbrPointer del nuevo nodo
    def splitNode(self, lastSplit):
        mbrPointers = self.currentNode.getChildren() + [lastSplit]
        partitionData = self.pa.partition(self.currentNode.getMbr(), mbrPointers, self.m())
        self.currentNode.setData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newNode = self.newNode()
        newNode.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.save(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.save(newNode)           # Guardo el nuevo nodo (u hoja) en disco

        self.propagateSplitDownwards(self.pa.getCut(), self.pa.getDim())

        return newNode.getMbrPointer() # retorno el mbr que debo insertar en el padre

    # Gatilla split en hoja y retorna el mbrPointer de la nueva hoja
    def splitLeaf(self, lastSplit):
        mbrPointers = self.currentNode.getChildren() + [lastSplit]
        partitionData = self.pa.partition(self.currentNode.getMbr(), mbrPointers, self.m(), True) # leafMode = True
        self.currentNode.setData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newLeaf = self.newLeaf()
        newLeaf.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.save(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.save(newLeaf)          # Guardo el nuevo nodo (u hoja) en disco

        return newLeaf.getMbrPointer()

    def splitNodeByCut(self, cut, dim):
        mbrPointers = self.currentNode.getChildren()
        partitionData = self.pa.partitionOnCut(mbrPointers, cut, dim)

        newNode = self.newNode() # Creo un hermano que contendra los mbrs de su corte respectivo

        self.currentNode.setDataChildren(partitionData[0]) # Cambio el nodo actual a la nueva particion (se mantiene su mbr)
        newNode.setDataChildren(partitionData[1])

        self.save(self.currentNode) # Guardo el nodo en disco
        self.save(newNode)

        return newNode.getMbrPointer()

    def insertOnParent(self, mbrPointer):
        if self.currentHeigth() > 0:
            self.chooseParent(False)

            if self.currentNode.needToSplit():
                self.propagateSplit(mbrPointer, False)
            else:
                self.currentNode.insert(mbrPointer)
                self.propagateAdjust(False)
        else:
            self.makeNewRoot(mbrPointer)

        self.goToLastLevel()

    def propagateSplitDownwards(self, cut, dim):
        if self.pa.needsToSplitChilds():
            for nextChild in self.pa.getRecursiveSplits():
                self.seekNode(nextChild)
                self.markNodeAsVisited(nextChild)

                lastSplit = self.splitNodeByCut(cut, dim)
                self.insertOnParent(lastSplit)

                self.propagateSplitDownwards(cut, dim)
        else:
            self.chooseParent()


if __name__ == "__main__":
    d = 2
    M = 4
    E = 20
    r = 0.25

    rtree = RtreePlus(d = d, M = M, maxE = E, reset = True, initOffset = 0)
    print(rtree)

    gen = MbrGenerator()
    objects = [gen.next(d) for i in range(E)]
    print("Data generada")

    for o in objects:
        rtree.insert(o)
        print("\nTree:")
        print(rtree)

    print(rtree)

    print(gen.nextRadial(d, r))
    print("Search Results")
    randomMbr = gen.nextRadial(d, r)
    results = rtree.search(randomMbr, True)
    for m in results:
        print("d: " + str(randomMbr.distanceTo(m)))
        print("\t" + (str(m)))

    print(rtree.root)