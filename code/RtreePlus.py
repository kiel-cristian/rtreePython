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
        self.sa = RtreePlusSelection()  # Algoritmo de seleccion de mejor nodo a insertar en base a interseccion de areas

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

        self.insertR(parentNode = self.currentNode, mbrPointer = mbrPointer, currentNode = self.currentNode, level = 0, parents = [])

        t1 = time()
        if self.meanInsertionTime == None: 
          self.meanInsertionTime = t1-t0 
        else:
          self.meanInsertionTime = (self.meanInsertionTime*self.insertionsCount + (t1-t0))/(self.insertionsCount+1)
          self.insertionsCount = self.insertionsCount +1
        self.computeMeanNodes()

    def insertR(self, mbrPointer, parentNode, currentNode, level, parents):
        # Bajo por todos los nodos adecuados
        if currentNode.isANode():
            trees = self.chooseTree(currentNode, mbrPointer)

            if len(trees) == 0:
                self.insertAnyLeaf(mbrPointer, parentNode = parentNode, currentNode = currentNode, level = level)
            else:
                for next in trees:
                    self.insertR(mbrPointer = mbrPointer, parentNode = currentNode, currentNode = self.seekNode(next), level = level + 1)
        # Al encontrar una hoja
        else:
            if currentNode.needsToSplit():
                newLeafMbrPointer = self.split(self.newLeaf(), mbrPointer)
                self.propagateSplit(node = parentNode, newMbrPointer = newLeafMbrPointer, oldMbrPointer = currentNode.getMbrPointer(), level = level)
            else:
                currentNode.insert(mbrPointer)
                self.nfh.saveTree(currentNode)
                self.adjust(node = parentNode, oldMbrPointer = currentNode.getMbrPointer(), level = level)

    def insertAnyLeaf(self, mbrPointer, parentNode, currentNode, level):
        if currentNode.isANode():
            next = self.chooseAnyTree(currentNode)

            self.insertAnyLeaf(mbrPointer = mbrPointer, parentNode = currentNode, currentNode = self.seekNode(next))
        else:
            if currentNode.needsToSplit():
                newLeafMbrPointer = self.split(self.newLeaf(), mbrPointer)
                self.propagateSplit(node = parentNode, newMbrPointer = newLeafMbrPointer, oldMbrPointer = currentNode.getMbrPointer(), level = level)
            else:
                currentNode.insert(mbrPointer)
                self.nfh.saveTree(currentNode)
                self.adjust(node = parentNode, oldMbrPointer = currentNode.getMbrPointer(), level = level)

    def chooseAnyTree(self,currentNode):
        return self.sa.selectAny(currentNode)

    # Ajusta Mbr de todos los nodos padre hasta la raiz
    def adjust(self, node, oldMbrPointer, level):
        if level > 0:
            node.updateChild(oldMbrPointer)
            self.saveTree(node)
            parent = self.chooseParent(level)
            self.adjust(node = parent, oldMbrPointer = node.getMbrPointer(), level = level - 1)

    # Analogo a insert, inserta nuevos nodos hacia arriba en RtreePlus, y sigue insertando en caso de desbordes
    def propagateSplit(self, node, newMbrPointer, oldMbrPointer, level):
        lastNodeMbrPointer = oldMbrPointer

        if level > 0:
            parent = self.chooseParent(level)
            node.updateChild(oldMbrPointer)
            self.nfh.saveTree(node)

            if node.needsToSplit():
                brotherMbrPointer = self.split(self.newNode(), newMbrPointer)

                self.propagateSplit(node = parent, newMbrPointer = brotherMbrPointer, oldMbrPointer = node.getMbrPointer())
            else:
                node.insert(newMbrPointer)
                self.nfh.saveTree(node)
                self.adjust(node = parent, oldMbrPointer = node.getMbrPointer(), level = level - 1)


            self.updateHere(oldMbrPointer)

            if newMbrPointer != None and self.needToSplit():
                brotherMbrPointer = self.split(self.newNode(), oldMbrPointer)
                self.adjust(self, newMbrPointer = brotherMbrPointer, oldMbrPointer = self.getCurrentMbrPointer())

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