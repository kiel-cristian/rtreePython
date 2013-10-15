# encoding: utf-8
from SelectionManager import *
from RtreeApi import *

class RtreePlus(RtreeApi):
    # d          : dimension de vectores del arbol
    # M          : capacidad maxima de nodos y hojas
    # maxE       : cantidad maxima de elementos que almacenara el RtreePlus
    # reset      : cuando es True, se construye un nuevo arbol, si no, se carga de disco
    # initOffset : offset desde se cargara nodo raiz
    def __init__(self, d, M = 100, maxE = 100000, reset = False, initOffset = 0, partitionType = 2):
        super(RtreePlus, self).__init__(d = d, M = M, maxE = maxE, reset = reset, initOffset = initOffset, partitionType = partitionType)
        self.sa = RtreePlusSelection() # Algoritmo de seleccion de mejor nodo a insertar en base a interseccion de areas
        self.visitedNodes = {}
        self.pendingSplits = {}

        for h in self.H:
            self.pendingSplits[h] = {}
            self.visitedNodes[h]  = {}

    def chooseAnyTree(self):
        return self.sa.selectAny(self.currentNode)

    def setLastInsertHeight(self):
        self.lastInsertH = self.k

    def lastInsertHeight(self):
        return self.lastInsertH

    def insert(self, mbrPointer):
        t0 = time()

        self.insertR(mbrPointer)
        self.goToRoot()

        t1 = time()
        if self.meanInsertionTime == None:
          self.meanInsertionTime = t1-t0
        else:
          self.meanInsertionTime = (self.meanInsertionTime*self.insertionsCount + (t1-t0))/(self.insertionsCount+1)
          self.insertionsCount = self.insertionsCount +1
        self.computeMeanNodes()

    def markNodeAsVisited(self, node):
        self.visitedNodes[self.currentHeigth()][next.getMbrPointer()] = True

    def insertR(self, mbrPointer):
        # Bajo por todos los nodos adecuados
        if self.currentNode.isANode():
            trees = self.chooseTree(self.currentNode, mbrPointer)

            if len(trees) == 0:
                self.insertAnyLeaf(mbrPointer)
            else:
                for next in trees:
                    self.seekNode(next)

                    self.markNodeAsVisited(next)
                    self.insertR(mbrPointer)
                    # self.adjustOneLevel()
        # Al encontrar una hoja
        else:
            if self.currentNode.needToSplit():
                newLeafMbrPointer = self.split(self.newLeaf(), mbrPointer, plusMode = True) # split en las hojas del r+tree es distinto al de los nodos
                # se deben insertar los valores de los objetos en donde intersecten segun las nuevas subsecciones
                self.splitOneLevel(newLeafMbrPointer)
            else:
                self.update(mbrPointer) # inserta el objeto en la hoja actual y guarda en disco
                self.adjustOneLevel() #inicia proceso de ajuste

    def insertAnyLeaf(self, mbrPointer):
        while self.currentNode.isANode():
            next = self.chooseAnyTree()
            self.seekNode(next)

        if self.currentNode.needToSplit():
            newLeafMbrPointer = self.split(self.newLeaf(), mbrPointer, plusMode = True)
            self.propagateSplit(newLeafMbrPointer)
        else:
            self.update(mbrPointer)
            self.propagateAdjust()

    # Ajusta Mbr del nodo padre del nodo actual
    def adjustOneLevel(self):
        if self.currentHeigth() > 0:
            childMbrPointer = self.currentNode.getMbrPointer()

            self.chooseParent() # cambia currentNode y sube un nivel del arbol

            self.updateChild(childMbrPointer) # actualiza el nodo actual con la nueva version de su nodo hijo

    # Analogo a insert, inserta nuevos nodos hacia arriba en RtreePlus hasta el nivel del padre
    def splitOneLevel(self, splitMbrPointer):
        lastSplit = splitMbrPointer
        lastNode = self.currentNode

        # if self.currentHeigth() > 0:

        if self.currentHeigth() > 0:
        self.chooseParent() # cambia currentNode y sube un nivel del arbol

        self.updateChild(lastNode.getMbrPointer())

        if self.needToSplit():
            self.pendingSplits[self.currentHeigth()] = self.pendingSplits[self.currentHeigth()] + [lastSplit]
        else:
            self.update(lastSplit)

    def doPendingSplits(self):
        pendingSplitsLen = len(self.pendingSplits[self.currentHeigth()])

        self.pa.partitionPlus()

        currentMbr   = self.currentNode.getMbr()
        children     = self.currentNode.getChildren() # Tuplas (Mbr,Puntero) de la hoja seleccionada

        currentMbr.expand(mbrPointer.getMbr()) # expandimos el mbr del nodo (u hoja) seleccionado, para simular insercion
        partitionData = self.pa.partition(currentMbr, children + [mbrPointer], self.m(), leafMode) # efectuamos la particion de elementos agregando el elemento a insertar

        self.currentNode.setData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newRtree.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.nfh.saveTree(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.nfh.saveTree(newRtree)       # Guardo el nuevo nodo (u hoja) en disco

        treeMbrPointer = newRtree.getMbrPointer()
        return treeMbrPointer


        for split in self.pendingSplits[self.currentHeigth()]:

            self.pa.partitions()


    def splitNode(self, mbrPointers):
        partitionData = self.pa.partition(self.currentNode.getMbr(), mbrPointers, self.m())
        self.currentNode.setData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newNode = self.newNode()
        newNode.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.nfh.saveTree(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.nfh.saveTree(newNode)          # Guardo el nuevo nodo (u hoja) en disco

        newMbrPointer = newNode.getMbrPointer()
        self.propagateSplitUpwards(newMbrPointer)

        if self.pa.needsToSplitChilds():
            self.propagateSplitDownwards(self.pa.getRecursiveSplits(), self.pa.getCut(), self.pa.getDim())

    def splitLeaf(self, mbrPointers):
        partitionData = self.pa.partition(self.currentNode.getMbr(), mbrPointers, self.m(), True) # leafMode = True
        self.currentNode.setData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newLeaf = self.newLeaf()
        newLeaf.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.nfh.saveTree(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.nfh.saveTree(newLeaf)          # Guardo el nuevo nodo (u hoja) en disco

        newMbrPointer = newLeaf.getMbrPointer()
        self.propagateSplitUpwards(newMbrPointer)

    # Maneja split
    def split(self, newRtree, mbrPointer, leafMode = False):
        currentMbr   = self.currentNode.getMbr()
        children     = self.currentNode.getChildren() # Tuplas (Mbr,Puntero) de la hoja seleccionada

        currentMbr.expand(mbrPointer.getMbr()) # expandimos el mbr del nodo (u hoja) seleccionado, para simular insercion
        partitionData = self.pa.partition(currentMbr, children + [mbrPointer], self.m(), leafMode) # efectuamos la particion de elementos agregando el elemento a insertar

        self.currentNode.setData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newRtree.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.nfh.saveTree(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.nfh.saveTree(newRtree)       # Guardo el nuevo nodo (u hoja) en disco

        if self.pa.needsToSplitChilds():
            self.splitChildren(self.pa.getRecursiveSplits(), self.pa.getCut(), self.pa.getDim())

        return newRtree.getMbrPointer()

    def splitOnCut(self, cut, dim):
        partitionData = self.pa.partitionOnCut(self.currentNode.getMbr(), self.currentNode.getChildren())

    def splitChildren(self, children, cut, dim):
        for child in children:
            self.seekNode(child.getPointer())

            if self.currentNode.isANode():
                self.split(self.newNode(), )

if __name__=="__main__":
    d = 2
    M = 100
    rtree = RtreePlus(d = d, M = 100, maxE = 10**6, reset = True, initOffset = 0, partitionType = 0)

    objects = [randomMbrPointer(d) for i in range(200)]

    for o in objects:
        rtree.insert(o)