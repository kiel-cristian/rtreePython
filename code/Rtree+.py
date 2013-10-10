# encoding: utf-8
from SelectionManager import *
from RtreeApi import *

class RtreePlus(RtreeApi):
    # d          : dimension de vectores del arbol
    # M          : capacidad maxima de nodos y hojas
    # maxE       : cantidad maxima de elementos que almacenara el RtreePlus
    # reset      : cuando es True, se construye un nuevo arbol, si no, se carga de disco
    # initOffset : offset desde se cargara nodo raiz
    def __init__(self, d, M = 100, maxE = 100000, reset = False, initOffset = 0, partitionType = 0):
        super(RtreePlus, self).__init__(d = d, M = M, maxE = maxE, reset = reset, initOffset = initOffset, partitionType = partitionType)
        self.sa = RtreePlusSelection()  # Algoritmo de seleccion de mejor nodo a insertar en base a crecimiento minimo de area

    # Busqueda radial de objeto
    def search(self, r, mbrObject):
        pass

        t0 = time()
      
        ##TODO
      
        t1 = time()
        if self.meanSearchTime == None: 
            self.meanSearchTime = t1-t0
        else:
            self.meanSearchTime = (self.meanSearchTime*self.searchCount + (t1-t0))/(self.searchCount+1)
            self.searchCount = self.searchCount +1

    def insert(self, mbrPointer):      
        t0 = time()

        # Bajo por el arbol hasta encontrar una hoja adecuada
        while self.currentNode.isANode():
            self.chooseTree(mbrPointer) # cambia currentNode

        if self.needToSplit():
            newLeafMbrPointer = self.split(self.newLeaf(), mbrPointer)
            self.adjust(newLeafMbrPointer) # Inicio ajuste hacia arriba del RtreePlus
        else:
            self.currentNode.insert(mbrPointer)
            self.nfh.saveTree(self.currentNode) # se guarda nodo en disco
            self.goToRoot()

        t1 = time()
        if self.meanInsertionTime == None: 
          self.meanInsertionTime = t1-t0 
        else:
          self.meanInsertionTime = (self.meanInsertionTime*self.insertionsCount + (t1-t0))/(self.insertionsCount+1)
          self.insertionsCount = self.insertionsCount +1
        self.computeMeanNodes()

    # Analogo a insert, inserta nuevos nodos hacia arriba en RtreePlus, y sigue insertando en caso de desbordes
    def adjust(self, nodeMbrPointer):
        lastNodeMbrPointer = nodeMbrPointer

        while self.currentHeigth() > 0:
            self.chooseParent() # cambia currentNode y sube un nivel del arbol

            if self.needToSplit():
                lastNodeMbrPointer = self.split(self.newNode(), lastNodeMbrPointer)
            else:
                self.currentNode.insert(lastNodeMbrPointer)
                self.nfh.saveTree(self.currentNode)
                self.goToRoot()
                break

        # Se necesita crear una nueva raiz
        if self.currentHeigth() == 0 and self.needToSplit():
            brotherMbrPointer = self.split(self.newNode(), lastNodeMbrPointer)

            self.currentNode.unsetRoot()

            newRoot = self.newNode()
            newRoot.setAsRoot()

            newRoot.insert(thisMbrPointer)
            newRoot.insert(self.currentNode)

            self.nfh.saveTree(newRoot)
            self.root = newRoot

        self.goToRoot()
        return

if __name__=="__main__":
    d = 2
    M = 100
    rtree = RtreePlus(d = d, M = 100, maxE = 10**6, reset = True, initOffset = 0, partitionType = 0)

    objects = [randomMbrPointer(d) for i in range(200)]

    for o in objects:
        rtree.insert(o)