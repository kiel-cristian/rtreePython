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
        super(Rtree, self).__init__(d = d, M = M, maxE = maxE, reset = reset, initOffset = initOffset, partitionType = partitionType)
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
            self.adjust() # ajusta mbrs hasta la raiz

        t1 = time()
        if self.meanInsertionTime == None: 
          self.meanInsertionTime = t1-t0 
        else:
          self.meanInsertionTime = (self.meanInsertionTime*self.insertionsCount + (t1-t0))/(self.insertionsCount+1)
          self.insertionsCount = self.insertionsCount +1
        self.computeMeanNodes()
        self.goToRoot()

    # Propaga el split hasta donde sea necesario
    def propagateSplit(self, splitMbrPointer):        
        lastSplit = splitMbrPointer
        lastNode = self.currentNode

        while self.currentHeigth() >= 0:
            if self.currentHeigth() > 0:
                self.chooseParent() # cambia currentNode y sube un nivel del arbol

                self.updateChild(lastNode.getMbrPointer())

                if self.needToSplit():
                    lastSplit = self.split(self.newNode(), lastSplit)
                    lastNode  = self.currentNode
                else:
                    self.adjust()
                    break
            else:
                # Nueva raiz
                self.updateChild(lastNode.getMbrPointer())
                
                lastSplit = self.split(self.newNode(), lastSplit)

                self.makeNewRoot(lastSplit)

    # Ajusta mbrs de todos los nodos hasta llegar a la raiz
    def adjust(self):
        while self.currentHeigth() > 0:
            childMbrPointer = self.currentNode.getMbrPointer()

            self.chooseParent() # cambia currentNode y sube un nivel del arbol

            self.updateChild(childMbrPointer) # actualiza el nodo actual con la nueva version de su nodo hijo

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