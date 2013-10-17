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
        return self.tree

    def isHandler(self):
        return True

class RtreePlusUpdateReferenceStatus(RtreePlusStatus):
    def __init__(self, tree):
        super(RtreePlusUpdateReferenceStatus, self).__init__(tree)

    def handle(self):
        return self.tree

    def isHandler(self):
        return False

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

class RtreePlusSplitStatusNoScale(RtreePlusStatus):
    def __init__(self, tree, splitMbrPointer):
        super(RtreePlusSplitStatusNoScale, self).__init__(tree, splitMbrPointer)

    def handle(self):
        return self.tree.splitOneLevel(self.data, False)

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
        super(RtreePlus, self).__init__(d = d, M = M, maxE = maxE, reset = reset, initOffset = initOffset, dataFile = "rplustree")
        # Algoritmo de seleccion de mejor nodo a insertar
        # en base a interseccion de areas
        self.pa = SweepPartition()
        self.sa = RtreePlusSelection()
        self.reachedNodes = {}

        for h in range(self.H):
            self.reachedNodes[h]  = {}

        self.iterator = 0

    # Fin de la cadena recursiva, actualiza su propia referencia posterior a la cadena de recursiones
    def handle(self, newSelf):
        self = newSelf
        return None

    def goToRoot(self):
        for h in range(self.H):
            self.reachedNodes[h]  = {}
        super(RtreePlus, self).goToRoot()

    def insert(self, mbrPointer):
        t0 = time()

        self.insertR(mbrPointer)
        self.iterator = self.iterator + 1

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
        return RtreePlusUpdateReferenceStatus(self)

    def chooseNearestTree(self, mbrPointer):
        return self.sa.selectNearest(mbrPointer, self.currentNode.getChildren())

    def insertR(self, mbrPointer):
        print("insertR:" + str(self.iterator))

        print("ARBOL:")
        print(self)
        print("\n")

        # Bajo por todos los nodos adecuados
        if self.currentNode.isANode():
            trees = self.chooseTree(mbrPointer)

            if len(trees) == 0:
                trees = [self.chooseNearestTree(mbrPointer)]

            for next in trees:
                if not self.nodeIsVisited(next):
                    self.seekNode(next)
                    self.markNodeAsVisited(next)

                    lastStatus = self.insertR(mbrPointer)
                    while lastStatus.isHandler():
                        lastStatus = lastStatus.handle()
                    self = lastStatus.handle()

                    self.chooseParent()
            return RtreePlusUpdateReferenceStatus(self)
        # Al encontrar una hoja
        else:
            if self.currentNode.needToSplit():
                newLeaf = self.splitLeaf(mbrPointer)
                return RtreePlusSplitStatus(self, newLeaf)
            else:
                self.insertChild(mbrPointer)
                return RtreePlusAdjustStatus(self)

    # Ajusta Mbr del nodo padre del nodo actual
    def adjustOneLevel(self):
        print("adjustOneLevel")
        if self.currentHeigth() > 0:
            lastNode = self.currentNode.getMbrPointer()

            self.chooseParent(destructive = False) # cambia currentNode y sube un nivel del arbol

            self.updateChild(lastNode) # actualiza el nodo actual con la nueva version de su nodo hijo

            return RtreePlusAdjustStatus(self)
        else:
            return RtreePlusBackToRecursionLevel(self)

    # Analogo a insert, inserta nodo de split en el padre
    def splitOneLevel(self, splitMbrPointer):
        print("splitOneLevel")
        lastSplit = splitMbrPointer
        lastNode  = self.currentNode.getMbrPointer()

        if self.currentHeigth() > 0:
            self.chooseParent(destructive = False) # cambia currentNode y sube un nivel del arbol

            self.updateChild(lastNode)

            if self.needToSplit():
                if self.currentNode.isANode():
                    lastSplit = self.splitNode(lastSplit)
                else:
                    lastSplit = self.splitLeaf(lastSplit)

                return RtreePlusSplitStatus(self, lastSplit)
            else:
                print("encontre nodo donde insertar")
                self.insertChild(lastSplit)

                print(self.currentNode)
                print("arbol:")
                print(self)

                return RtreePlusAdjustStatus(self)
        else:
            print("makeNewRoot")
            print("cache:")
            print(self.cache)
            self.makeNewRoot(lastSplit)
            return RtreePlusBackToRecursionLevel(self)

    # Gatilla split en nodo, propaga split de nodos hijos de ser necesario y retorna el mbrPointer del nuevo nodo
    def splitNode(self, lastSplit):
        print("spliNode")
        mbrPointers = self.currentNode.getChildren() + [lastSplit]
        partitionData = self.pa.partition(self.currentNode.getMbr().expand(lastSplit), mbrPointers, self.m())
        self.currentNode.setData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newNode = self.newNode()
        newNode.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.save(self.currentNode)  # Guardo el nodo (u hoja) antiguo en disco
        self.save(newNode)           # Guardo el nuevo nodo (u hoja) en disco

        lastStatus = self.propagateSplitDownwards(self.pa.getCut(), self.pa.getDim())
        while lastStatus.isHandler():
            lastStatus = lastStatus.handle() # manejo splits o ajustes hasta donde corresponda
        self = lastStatus.handle()

        return newNode.getMbrPointer() # retorno el mbr que debo insertar en el padre

    # Gatilla split en hoja y retorna el mbrPointer de la nueva hoja
    def splitLeaf(self, lastSplit):
        print("splitLeaf")
        mbrPointers = self.currentNode.getChildren() + [lastSplit]
        partitionData = self.pa.partition(self.currentNode.getMbr().expand(lastSplit), mbrPointers, self.m(), True) # leafMode = True
        self.currentNode.setData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newLeaf = self.newLeaf()
        newLeaf.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.save(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.save(newLeaf)          # Guardo el nuevo nodo (u hoja) en disco

        print("newLeaf")
        print(newLeaf)
        print("currentNode")
        print(self.currentNode)
        print("\n")

        return newLeaf.getMbrPointer()

    def splitNodeByCut(self, cut, dim):
        print("splitNodeByCut")
        mbrPointers = self.currentNode.getChildren()
        partitionData = self.pa.partitionOnCut(mbrPointers, cut, dim)

        newNode = self.newNode() # Creo un hermano que contendra los mbrs de su corte respectivo

        self.currentNode.setDataChildren(partitionData[0]) # Cambio el nodo actual a la nueva particion (se mantiene su mbr)
        newNode.setDataChildren(partitionData[1])

        self.save(self.currentNode) # Guardo el nodo en disco
        self.save(newNode)

        return newNode.getMbrPointer()

    def propagateSplitDownwards(self, cut, dim):
        print("propagateSplitDownwards")
        if self.currentNode.isANode() and self.pa.needsToSplitChilds():
            for nextChild in self.pa.getRecursiveSplits():
                if self.nodeIsVisited(nextChild):
                    continue

                self.seekNode(nextChild)
                self.markNodeAsVisited(nextChild)

                currentNodeStatus = RtreePlusAdjustStatus(self)

                while currentNodeStatus.isHandler():
                    currentNodeStatus = currentNodeStatus.handle() # propago ajuste de nodo actual hasta la raiz actual

                self = currentNodeStatus

                newBrother = self.splitNodeByCut(cut, dim)
                brotherStatus = RtreePlusSplitStatus(self, newBrother)

                while brotherStatus.isHandler():
                    brotherStatus = brotherStatus.handle() # propago split del nuevo nodo hermano hasta que logre insertar

                self = brotherStatus

                if self.currentNode.isANode() and self.pa.needsToSplitChilds():
                    childStatus = self.propagateSplitDownwards(cut, dim)
                    while childStatus.isHandler():
                        childStatus = childStatus.handle()

                    self = childStatus

                self.chooseParent() # destructive
            return RtreePlusBackToRecursionLevel(self)
        return RtreePlusUpdateReferenceStatus(self)

if __name__ == "__main__":
    d = 2
    M = 4
    E = 20
    r = 0.25

    rtree = RtreePlus(d = d, M = M, maxE = E, reset = True, initOffset = 0)
    gen = MbrGenerator()
    objects = [gen.next(d) for i in range(E)]
    print("Data generada")

    for o in objects:
        rtree.insert(o)

    print(rtree)

    print(gen.nextRadial(d, r))
    randomMbr = gen.nextRadial(d, r*(d**0.5))
    print("Generando busqueda")
    rtree.search(radialMbr = randomMbr, fileResults = None, verbose = True, genFile = False)