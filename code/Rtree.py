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
        super(Rtree, self).__init__(d = d, M = M, maxE = maxE, reset = reset, initOffset = initOffset, partitionType = partitionType, dataFile = "rtree")
        self.sa = RtreeSelection()  # Algoritmo de seleccion de mejor nodo a insertar en base a crecimiento minimo de area

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

        self.nfh.saveTree(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.nfh.saveTree(newRtree)       # Guardo el nuevo nodo (u hoja) en disco

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

    # Ajusta mbrs de todos los nodos hasta llegar a la raiz
    def propagateAdjust(self):
        while self.currentHeigth() > 0:
            childMbrPointer = self.currentNode.getMbrPointer()

            self.chooseParent() # cambia currentNode y sube un nivel del arbol

            self.updateChild(childMbrPointer) # actualiza el nodo actual con la nueva version de su nodo hijo

if __name__=="__main__":
    d = 2
    M = 100
    rtree = Rtree(d = d, M = 3, maxE = 10**6, reset = True, initOffset = 0, partitionType = 0)

    objects = [randomMbrPointer(d) for i in range(13)]
    print("Data generada")

    for o in objects:
        rtree.insert(o)

    print(rtree)
    #print("propagateSplit")rtree.printTree()

    r = 0.25
    print(randomRadialMbr(d,r))
    print("Search Results")
    randomMbr = randomRadialMbr(d,r)
    results = rtree.search(randomMbr)
    for m in results:
        print("d: " + str(randomMbr.distanceTo(m)))
        print("\t" + (str(m)))