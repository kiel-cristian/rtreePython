# encoding: utf-8
from SelectionManager import *
from RtreeApi import *

class Rtree(RtreeApi):
    # d          : dimension de vectores del arbol
    # M          : capacidad maxima de nodos y hojas
    # maxE       : cantidad maxima de elementos que almacenara el Rtree
    # reset      : cuando es True, se construye un nuevo arbol, si no, se carga de disco
    # initOffset : offset desde se cargara nodo raiz
    def __init__(self, d, M = 100, maxE = 100000, reset = False, initOffset = 0, partitionType = 0):
        super(Rtree, self).__init__(d = d, M = M, maxE = maxE, reset = reset, initOffset = initOffset, partitionType = partitionType, dataFile = "r+tree")
        self.sa = RtreeSelection()  # Algoritmo de seleccion de mejor nodo a insertar en base a crecimiento minimo de area

    def insert(self, mbrPointer):
        t0 = time()

        # Bajo por el arbol hasta encontrar una hoja adecuada
        while not self.currentNode.isALeaf():
            next = self.chooseTree(mbrPointer)
            self.seekNode(next) # cambia currentNode

        if self.needToSplit():
            newLeafMbrPointer = self.split(self.newLeaf(), mbrPointer)
            self.propagateSplit(newLeafMbrPointer) # propago hacia el padre el split
        else:
            self.update(mbrPointer)
            self.propagateAdjust() # ajusta mbrs hasta la raiz

        t1 = time()
        self.incrementMeanInsertionTime(t1-t0)
        self.computeMeanNodes()
        self.goToRoot()

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

        treeMbrPointer = newRtree.getMbrPointer()
        return treeMbrPointer

if __name__=="__main__":
    d = 2
    M = 100
    rtree = Rtree(d = d, M = 25, maxE = 10**6, reset = True, initOffset = 0, partitionType = 0)

    objects = [randomMbrPointer(d) for i in range(70)]

    for o in objects:
        rtree.insert(o)
    print(rtree)

    r = 0.25
    print(randomRadialMbr(d,r))
    print("Search Results")
    randomMbr = randomRadialMbr(d,r)
    results = rtree.search(randomMbr)
    for m in results:
        print("d: " + str(randomMbr.distanceTo(m)))
        print("\t" + (str(m)))