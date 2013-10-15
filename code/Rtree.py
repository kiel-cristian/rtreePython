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

    def resetRoot(self):
        # Se construye una raiz vacia
        self.currentNode = self.newNode()

        # Creo dos hojas para mantener invariante de la raiz
        leaf1 = self.newLeaf()
        leaf2 = self.newLeaf()

        # Guardo el nodo raiz en disco
        self.save()

        # Guardo dos hojas de la raiz en disco
        self.save(leaf1)
        self.save(leaf2)

        # Agrego las hojas al nodo raiz
        self.currentNode.insert(leaf1.getMbrPointer())
        self.currentNode.insert(leaf2.getMbrPointer())

        # Guardo el nodo raiz en disco nuevamente, ya que, se agregaron las hojas en su estructura
        self.save()

        self.setAsRoot() # convertir nodo actual en raiz

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
        if self.meanInsertionTime == None: 
          self.meanInsertionTime = t1-t0 
        else:
          self.meanInsertionTime = (self.meanInsertionTime*self.insertionsCount + (t1-t0))/(self.insertionsCount+1)
          self.insertionsCount = self.insertionsCount +1
        self.computeMeanNodes()
        self.goToRoot()



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