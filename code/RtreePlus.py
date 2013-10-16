# encoding: utf-8
from SelectionManager import *
from RtreeApi import *

# Clases auxiliares para manejar estados posibles posteriores a una insercion recursiva
class RtreePlusStatus(object):
    def __init__(self, tree = None, data = None):
        self.tree = tree
        self.data = data

    def handle(self):
        pass
    pass

class RtreePlusAdjustStatus(RtreePlusStatus):
    def __init__(self, tree):
        super(RtreePlusAdjustStatus, self).__init__(tree)

    def handle(self):
        return self.tree.adjustOneLevel()

class RtreePlusSplitStatus(RtreePlusStatus):
    def __init__(self, tree, splitMbrPointer):
        super(RtreePlusInsertStatus, self).__init__(tree, splitMbrPointer)

    def handle(self):
        return self.tree.splitOneLevel(self.splitMbrPointer)

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
    def __init__(self, d, M = 100, maxE = 100000, reset = False, initOffset = 0, partitionType = 2):
        super(RtreePlus, self).__init__(d = d, M = M, maxE = maxE, reset = reset, initOffset = initOffset, partitionType = partitionType, dataFile = "r+tree")
        self.sa = RtreePlusSelection() # Algoritmo de seleccion de mejor nodo a insertar en base a interseccion de areas
        self.visitedNodes = {}
        self.pendingSplits = {}

        for h in self.H:
            # self.pendingSplits[h] = {}
            self.visitedNodes[h]  = {}

    def insert(self, mbrPointer):
        t0 = time()

        self.insertR(mbrPointer)
        self.goToRoot()

        t1 = time()
        self.incrementMeanInsertionTime(t1-t0)
        self.computeMeanNodes()

    def markNodeAsVisited(self, node):
        self.visitedNodes[self.currentHeigth()][next.getPointer()] = True

    def nodeIsVisited(self, node):
        return self.visitedNodes[self.currentHeigth()][next.getPointer()] == True

    def goToLastLevel(self):
        super(RtreePlus, self).goToLastLevel()
        return RtreePlusStatus(self)

    def insertR(self, mbrPointer):
        # Bajo por todos los nodos adecuados
        if self.currentNode.isANode():
            trees = self.chooseTree(self.currentNode, mbrPointer)

            if len(trees) == 0:
                self.insertOnNewNode(mbrPointer)
            else:
                for next in trees:
                    if not self.nodeIsVisited(next):
                        self.seekNode(next)
                        self.markNodeAsVisited(next)
                        childStatus = self.insertR(mbrPointer)
                        return childStatus.handle()
        # Al encontrar una hoja
        else:
            if self.currentNode.needToSplit():
                newLeaf = self.splitLeaf(self.currentNode.getChildren() + [mbrPointer])
                return RtreePlusSplitStatus(self, newLeaf)
            else:
                self.insertChild(mbrPointer)
                return RtreePlusAdjustStatus(self)

    def insertOnNewNode(self, mbrPointer):
        # El mbr a insertar no intersecta con ningun nodo, por ende, se genera una nueva tupla de nodo, hoja
        newNode = self.newNode()
        newLeaf = self.newLeaf()

        self.allocateTree(newNode)
        self.save(newLeaf)

        leafMbrPointer = newLeaf.getMbrPointer()
        newNode.insert(leafMbrPointer)
        self.save(newNode)

        if self.needToSplit():
            self.makeNewRoot(newNode.getMbrPointer())
        else:
            self.insertChild(mbrPointer)
            self.propagateAdjust()

    # Ajusta Mbr del nodo padre del nodo actual
    def adjustOneLevel(self):
        if self.currentHeigth() > 0:
            childMbrPointer = self.currentNode.getMbrPointer()
            self.chooseParent(destructive = False) # cambia currentNode y sube un nivel del arbol
            self.updateChild(childMbrPointer) # actualiza el nodo actual con la nueva version de su nodo hijo
            return RtreePlusAdjustStatus(self)
        else:
            return RtreePlusBackToRecursionLevel(self)

    # Analogo a insert, inserta nodo de split en el padre
    def splitOneLevel(self, splitMbrPointer):
        lastSplit = splitMbrPointer

        if self.currentHeigth() > 0:
            self.chooseParent(destructive = False) # cambia currentNode y sube un nivel del arbol

            self.updateChild(self.currentNode.getMbrPointer())

            if self.needToSplit():
                if self.currentNode.isANode():
                    lastSplit = self.splitNode(lastSplit)
                    return RtreePlusSplitStatus(self, lastSplit)
                else:
                    lastSplit = self.splitLeaf(lastSplit)
                    return RtreePlusSplitStatus(self, lastSplit)
            else:
                self.insertChild(lastSplit)
                return RtreePlusAdjustStatus(self)

    # Gatilla split en nodo, propaga split de nodos hijos de ser necesario y retorna el mbrPointer del nuevo nodo
    def splitNode(self, lastSplit):
        mbrPointers = self.currentNode.getChildren() + [lastSplit]
        partitionData = self.pa.partition(self.currentNode.getMbr(), mbrPointers, self.m())
        self.currentNode.setData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newNode = self.newNode()
        newNode.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.nfh.saveTree(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.nfh.saveTree(newNode)          # Guardo el nuevo nodo (u hoja) en disco

        newMbrPointer = newNode.getMbrPointer()
        # self.propagateSplitUpwards(newMbrPointer)

        if self.pa.needsToSplitChilds():
            self.propagateSplitDownwards(self.pa.getRecursiveSplits(), self.pa.getCut(), self.pa.getDim())
        return newMbrPointer

    # Gatilla split en hoja y retorna el mbrPointer de la nueva hoja
    def splitLeaf(self, lastSplit):
        mbrPointers = self.currentNode.getChildren() + [lastSplit]
        partitionData = self.pa.partition(self.currentNode.getMbr(), mbrPointers, self.m(), True) # leafMode = True
        self.currentNode.setData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newLeaf = self.newLeaf()
        newLeaf.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.nfh.saveTree(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.nfh.saveTree(newLeaf)          # Guardo el nuevo nodo (u hoja) en disco

        newMbrPointer = newLeaf.getMbrPointer()
        return newMbrPointer

    # TODO
    def propagateSplitDownwards(self, recSplits, cut, dim):
        pass

    # TODO
    def splitOnCut(self, cut, dim):
        partitionData = self.pa.partitionOnCut(self.currentNode.getMbr(), self.currentNode.getChildren())

if __name__=="__main__":
    d = 2
    M = 100
    rtree = RtreePlus(d = d, M = 100, maxE = 10**6, reset = True, initOffset = 0, partitionType = 0)

    objects = [randomMbrPointer(d) for i in range(200)]

    for o in objects:
        rtree.insert(o)