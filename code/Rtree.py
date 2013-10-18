# encoding: utf-8
from SelectionManager import *
from RtreeApi import *
from MbrGenerator import *

class Rtree(RtreeApi):
    # d          : dimension de vectores del arbol
    # M          : capacidad maxima de nodos y hojas
    # maxE       : cantidad maxima de elementos que almacenara el Rtree
    # reset      : cuando es True, se construye un nuevo arbol, si no, se carga de disco
    # initOffset : offset desde se cargara nodo raiz
    def __init__(self, d, M = 100, maxE = 100000, reset = False, initOffset = 0, partitionType = 0):
        super(Rtree, self).__init__(d = d, M = M, maxE = maxE, reset = reset, initOffset = initOffset, dataFile = "rtree")
        self.sa = RtreeSelection()  # Algoritmo de seleccion de mejor nodo a insertar en base a crecimiento minimo de area
        # Algoritmo de particionamiento
        if partitionType == 0:
            self.pa = LinealPartition()
        elif partitionType == 1:
            self.pa = CuadraticPartition()

    def insert(self, mbrPointer):
        t0 = time()

        # Bajo por el arbol hasta encontrar una hoja adecuada
        while self.currentNode.isANode():
            next = self.chooseTree(mbrPointer)
            self.seekNode(next) # cambia currentNode

        if self.needToSplit():
            newLeafMbrPointer = self.split(self.newLeaf(), mbrPointer)
            self.propagateSplit(newLeafMbrPointer) # propago hacia el padre el split
        else:
            self.insertChild(mbrPointer)
            self.propagateAdjust() # ajusta mbrs hasta la raiz

        t1 = time()
        self.incrementMeanInsertionTime(t1-t0)
        self.computeMeanNodes()
        self.goToRoot()

    # Maneja split
    def split(self, newRtree, mbrPointer):
        currentMbr   = self.currentNode.getMbr()
        children     = self.currentNode.getChildren() # Tuplas (Mbr,Puntero) de la hoja seleccionada

        currentMbr.expand(mbrPointer.getMbr()) # expandimos el mbr del nodo (u hoja) seleccionado, para simular insercion
        partitionData = self.pa.partition(currentMbr, children + [mbrPointer], self.m()) # efectuamos la particion de elementos agregando el elemento a insertar

        self.currentNode.setData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newRtree.setData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.save(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.save(newRtree)          # Guardo el nuevo nodo (u hoja) en disco

        treeMbrPointer = newRtree.getMbrPointer()
        return treeMbrPointer

    # Propaga el split hasta donde sea necesario
    def propagateSplit(self, splitMbrPointer):
        lastSplit = splitMbrPointer
        lastNode = self.currentNode

        while self.currentHeigth() >= 0:
            self.chooseParent() # cambia currentNode y sube un nivel del arbol

            self.updateChild(lastNode.getMbrPointer())

            if self.needToSplit():
                lastSplit = self.split(self.newNode(), lastSplit)

                # Se llego a la raiz
                if self.currentHeigth() == 0:
                    self.makeNewRoot(lastSplit)
                    break
                lastNode  = self.currentNode
            else:
                self.insertChild(lastSplit)
                break
        self.propagateAdjust()
        self.goToRoot()

def simpleTest():
    d = 2
    M = 25
    E = 10**4
    r = 0.25
    rtree = Rtree(d = d, M = M, maxE = E, reset = True, initOffset = 0, partitionType = 1)
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
    M = 25
    E = 10**4
    r = 0.25
    rtree = Rtree(d = d, M = M, maxE = E, reset = False, initOffset = 0, partitionType = 1)

    print(rtree)

if __name__ == "__main__":
    simpleTest()
    loadTest()