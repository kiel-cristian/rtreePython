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
        self.sa = RtreePlusSelection()
        self.visitedNodes = {}

        for h in range(self.H):
            self.visitedNodes[h]  = {}

    def goToRoot(self):
        for h in range(self.H):
            self.visitedNodes[h]  = {}
        super(RtreePlus, self).goToRoot()

    def insert(self, mbrPointer):
        t0 = time()

        self.insertR(mbrPointer)

        t1 = time()
        self.incrementMeanInsertionTime(t1-t0)
        self.computeMeanNodes()
        self.goToRoot()

    def markNodeAsVisited(self, next):
        self.visitedNodes[self.currentHeigth()][next.getPointer()] = True

    def nodeIsVisited(self, next):
        return self.visitedNodes[self.currentHeigth()][next.getPointer()] == True

    def goToLastLevel(self):
        super(RtreePlus, self).goToLastLevel()
        return RtreePlusStatus(self)

    def insertR(self, mbrPointer):
        # Bajo por todos los nodos adecuados
        if self.currentNode.isANode():
            trees = self.chooseTree(mbrPointer)

            if len(trees) == 0:
                self.insertOnNewNode(mbrPointer)
                return None
            else:
                for next in trees:
                    if not self.nodeIsVisited(next):
                        self.seekNode(next)
                        self.markNodeAsVisited(next)
                        lastStatus = self.insertR(mbrPointer)
                        while lastStatus != None:
                            lastStatus = lastStatus.handle()
                        self.chooseParent()
                        return None
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
    def splitOneLevel(self, splitMbrPointer, internalMode = False):
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

        self.save(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.save(newNode)           # Guardo el nuevo nodo (u hoja) en disco

        if self.pa.needsToSplitChilds():
            for child in self.pa.getRecursiveSplits():
                self.seekNode(child)
                self.markNodeAsVisited(child)
                lastStatus = self.propagateSplitDownwards(self.pa.getCut(), self.pa.getDim())
                while lastStatus != None:
                    lastStatus = lastStatus.handle() # manejo splits o ajustes hasta donde corresponda
                self.chooseParent() # destructiveMode = True
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

    def propagateSplitDownwards(self, cut, dim):
        if self.currentNode.isALeaf():
            # No hay nada mas que hacer
            return RtreePlusStatus(self)
        else:
            newBrother = self.splitNodeByCut(cut, dim)
            # Se efectuan splits de nodos de forma recursiva a los hijos y se manejan ajustes
            if self.pa.needsToSplitChilds():
                for nextChild in self.pa.getRecursiveSplits():
                    self.seekNode(nextChild)
                    self.markNodeAsVisited(nextChild)
                    nextStatus = self.propagateSplitDownwards(cut, dim)
                    while nextStatus != None:
                        nextStatus = nextStatus.handle()
                    self.chooseParent() # destructive = True

            # Y ahora se prepara insercion del nuevo hermano en el nodo padre actual
            self.chooseParent()
            if self.currentNode.needToSplit():
                return RtreePlusSplitStatus(newBrother)
            else:
                self.insertChild(newBrother)
                return RtreePlusAdjustStatus(self.currentNode.getMbrPointer())


if __name__ == "__main__":
    d = 2
    M = 100
    rtree = RtreePlus(d = d, M = 10, maxE = 10**6, reset = True, initOffset = 0)

    gen = MbrGenerator()
    objects = [gen.next(d) for i in range(100)]
    print("Data generada")

    for o in objects:
        rtree.insert(o)

    '''
    print(rtree)
    r = 0.25
    print(gen.nextRadial(d, r))
    print("Search Results")
    randomMbr = gen.nextRadial(d, r)
    results = rtree.search(randomMbr, True)
    for m in results:
        print("d: " + str(randomMbr.distanceTo(m)))
        print("\t" + (str(m)))
    '''