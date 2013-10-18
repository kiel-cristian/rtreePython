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

    # Escoge los nodos que intersectan con el mbr para proceder con la insercion, si no encuentra, entrega el mas cercano
    def chooseTree(self, mbrPointer):
        trees = super(RtreePlus, self).chooseTree(mbrPointer)
        if len(trees) == 0:
            return [self.chooseNearestTree(mbrPointer)]
        else:
            return trees

    def chooseNearestTree(self, mbrPointer):
        return self.sa.selectNearest(mbrPointer, self.currentNode.getChildren())

    def insertR(self, mbrPointer):
        #print("insertR:" + str(self.iterator))
        #print("ARBOL:")
        #print(self)
        #print("\n")

        # Bajo por todos los nodos adecuados
        if self.currentNode.isANode():
            trees = self.chooseTree(mbrPointer)

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

    # Inserta un nuevo nodo proveniente de un split hacia abajo
    def insertOneLevel(self, mbrPointer, parent, k):
        if parent.needToSplit():
            lastSplit = self.splitNode(mbrPointer, parent, k)

            if k - 1 > 0:
                newParent = self.currentParent(k - 1)
                self.splitOneLevel(self, lastSplit, newParent, k - 1)
            else:
                self.makeNewRoot(lastSplit, parent)
                return
        else:
            parent.insert(mbrPointer)
            self.save(parent)
            self.updateCache(parent, k)
            self.adjustOneLevel(parent, k)

    # Ajusta Mbr del nodo padre del nodo actual
    def adjustOneLevel(self, node = None, k = None):
        #print("adjustOneLevel")
        if node != None:
            if k > 0:
                parent = self.currentParent(k)

                parent.updateChild(node.getMbrPointer())
                self.save(parent)
                self.updateCache(parent, k)

                self.adjustOneLevel(self.currentParent(k - 1), k - 1)
        else:
            if self.currentHeigth() > 0:
                lastNode = self.currentNode.getMbrPointer()

                self.chooseParent(destructive = False) # cambia currentNode y sube un nivel del arbol

                self.updateChild(lastNode) # actualiza el nodo actual con la nueva version de su nodo hijo

                return RtreePlusAdjustStatus(self)
            else:
                return RtreePlusBackToRecursionLevel(self)

    # Analogo a insert, inserta nodo de split en el padre
    def splitOneLevel(self, splitMbrPointer, node = None, k = None):
        #print("splitOneLevel")
        lastSplit = splitMbrPointer
        lastNode  = self.currentNode.getMbrPointer()

        # Modo recursivo
        if node != None:
            if k > 0:
                parent = self.currentParent(k)

                parent.updateChild(node.getMbrPointer())

                if parent.needToSplit():
                    lastSplit = self.splitNode(lastSplit, parent, k)
                    self.splitOneLevel(lastSplit, parent, k - 1)
                else:
                    parent.insert(lastSplit)
                    self.save(parent)
                    self.updateCache(parent, k)
                    self.adjustOneLevel(parent, k)
        # Modo normal
        else:
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
                    self.insertChild(lastSplit)
                    return RtreePlusAdjustStatus(self)
            else:
                #print("makeNewRoot")
                self.makeNewRoot(lastSplit)
                return RtreePlusBackToRecursionLevel(self)

    # Gatilla split en nodo, propaga split de nodos hijos de ser necesario y retorna el mbrPointer del nuevo nodo
    def splitNode(self, lastSplit, node = None, k = None):
        #print("spliNode")
        # Modo recursivo hacia arriba
        if node != None:
            mbrPointers = node.getChildren() + [lastSplit]
            partitionData = self.pa.partition(node.getMbr().expand(lastSplit), mbrPointers, self.m())
            node.setData(partitionData[0][0], partitionData[0][1:])            # Guardo en el nodo (u hoja) antiguo la primera particion
            newNode = self.newNode()
            newNode.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

            self.save(newNode)
            self.save(node)
            self.updateCache(node, k)

            return newNode.getMbrPointer()
        # Modo por default
        else:
            mbrPointers = self.currentNode.getChildren() + [lastSplit]
            partitionData = self.pa.partition(self.currentNode.getMbr().expand(lastSplit), mbrPointers, self.m())
            self.currentNode.setData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
            newNode = self.newNode()
            newNode.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

            if self.pa.needsToSplitChilds():
                parent  = self.currentParent()
                k       = self.currentHeigth()

                # Ahora, se propagan divisiones recursivamente
                self.propagateSplitDownwards(parent, k, self.currentNode, self.pa.getCut(), self.pa.getDim())
                self.propagateSplitDownwards(parent, k, newNode, self.pa.getCut(), self.pa.getDim())

            self.save()                    # Guardo el nodo (u hoja) antiguo en disco
            self.save(newNode)             # Guardo el nuevo nodo (u hoja) en disco
            return newNode.getMbrPointer() # retorno el Nodo que debe insertarse en el padre

    # Gatilla split en hoja y retorna el mbrPointer de la nueva hoja
    def splitLeaf(self, lastSplit):
        #print("splitLeaf")
        mbrPointers = self.currentNode.getChildren() + [lastSplit]
        partitionData = self.pa.partition(self.currentNode.getMbr().expand(lastSplit), mbrPointers, self.m(), True) # leafMode = True
        self.currentNode.setData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newLeaf = self.newLeaf()
        newLeaf.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.save(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.save(newLeaf)          # Guardo el nuevo nodo (u hoja) en disco

        return newLeaf.getMbrPointer()

    def splitNodeByCut(self, nodeToDivide, cut, dim, k):
        #print("splitNodeByCut")
        mbrPointers = nodeToDivide.getChildren()
        partitionData = self.pa.partitionOnCut(mbrPointers, cut, dim)

        newNode = self.newNode() # Creo un hermano que contendra los mbrs de su corte respectivo

        nodeToDivide.setDataChildren(partitionData[0]) # Cambio el nodo actual a la nueva particion (se mantiene su mbr)
        newNode.setDataChildren(partitionData[1])

        # Dividiendo nodos pendientes e insertandoles en su lugar respectivo
        if self.pa.needsToSplitChilds():
            for child in self.pa.getRecursiveSplits():
                # Arbol hijo a dividir
                childTree = self.read(child.getPointer())

                if childTree.isALeaf():
                    continue

                splitChildTree = childTree.cutOnDimension(self.pa.getDim(), self.pa.getCut()) # resultado de la division
                self.save(splitChildTree)

                nodeToDivide.insert(childTree.getMbrPointer())
                self.propagateSplitDownwards(nodeToDivide, k - 1, childTree, cut, dim)

                newNode.insert(splitChildTree.getMbrPointer())
                self.propagateSplitDownwards(newNode, k - 1, splitChildTree, cut , dim)

        self.save(nodeToDivide)  # Guardo el nodo (u hoja) antiguo en disco
        self.save(newNode)       # Guardo el nuevo nodo (u hoja) en disco
        return newNode

    def propagateSplitDownwards(self, parent, k, nodeToDivide, cut, dim):
        #print("propagateSplitDownwards")
        if nodeToDivide.isANode() and self.pa.needsToSplitChilds():
            newNode  = self.splitNodeByCut(nodeToDivide, cut, dim, k)

            if parent.needToSplit():
                self.splitOneLevel(newNode.getMbrPointer(), parent, k)
            else:
                self.insertOneLevel(newNode.getMbrPointer(), parent, k)

def simpleTest():
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

def loadTest():
    d = 2
    M = 4
    E = 20
    r = 0.25

    rtree = RtreePlus(d = d, M = M, maxE = E, reset = False, initOffset = 0)

    print(rtree)

if __name__ == "__main__":
    simpleTest()
    loadTest()