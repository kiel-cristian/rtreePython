# encoding: utf-8
from math import log
import sys
import struct
from FileHandler import *
from MRtree import *
from PartitionAlgorithm import *

#  ERRORS
class RtreeHeightError(Exception):
    def __init__(self, value = "error de altura"):
        self.value = value
    def __str__(self):
        return (str(type(self))) + " " + repr(self.value)

class RtreeApi(object):
    # d          : dimension de vectores del arbol
    # M          : capacidad maxima de nodos y hojas
    # maxE       : cantidad maxima de elementos que almacenara el Rtree
    # reset      : cuando es True, se construye un nuevo arbol, si no, se carga de disco
    # initOffset : offset desde se cargara nodo raiz
    def __init__(self, d, M = 100, maxE = 100000, reset = False, initOffset = 0, partitionType = 0):
        self.nfh = RtreeFileHandler( loadDataFile    = "data" + str(d) + "D.bin",
                                     dataFile        = str(type(self)) + str(d) + "D.bin",
                                     d               = d,
                                     M               = M,
                                     initOffset      = initOffset)
    
        # Algoritmo de particionamiento
        if partitionType == 0:
            self.pa = LinealPartition()
        elif partitionType == 1:
            self.pa = CuadraticPartition()

        self.cache = []                             # cache: lista de nodos visitados
        self.k = 0                                  # k: nodos en cache
        self.H = log(maxE, self.M()) -1             # H: altura maxima del arbol

        # Inicializacion de la raiz
        if reset:
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
            self.currentNode.insert(leaf1)
            self.currentNode.insert(leaf2)

            # Guardo el nodo raiz en disco nuevamente, ya que, se agregaron las hojas en su estructura
            self.save()

            self.setAsRoot() # convertir nodo actual en raiz
        else:
            # Se carga la raiz de disco
            self.getRoot(initOffset)
            
        #Metricas
        self.meanInsertionTime = None
        self.insertionsCount = 0
        self.meanTotalNodes = 0
        self.meanInternalNodes = 0
        self.meanSearchTime = None
        self.searchCount = 0
        
    def getMeanNodePartitions(self):
      ##TODO
      pass

    # Fija punteros auxiliares de la estructura a la  raiz
    def goToRoot(self):
        self.cache = []
        self.k     = 0
        self.currentNode = self.root

    def setAsRoot(self, offset = 0):
        self.currentNode.setAsRoot(offset)
        self.root = self.currentNode

    def loadRoot(self, offset = 0):
        self.currentNode = self.nfh.readTree(offset)
        self.makeRoot(offset)

    # Crea una nueva raiz recibiendo mbrPointer del hermano recien creado
    def makeNewRoot(self, childMbrPointer):
        newRoot = self.newNode()
        newRoot.setAsRoot(0) # raiz siempre en comienzo del archivo

        newRoot.insert(self.currentNode)
        newRoot.insert(childMbrPointer)

        child = self.nfh.readTree(childMbrPointer.getPointer())

        self.nfh.swapTrees(newRoot, child)

        self.currentNode = newRoot
        self.root        = newRoot

    # Capacidad minima de nodos y hojas
    def m(self):
        return self.nfh.m

    # Capacidad maxima de nodos y hojas
    def M(self):
        return self.nfh.M

    def d(self):
        return self.nfh.d

    def needToSplit(self):
        return self.currentNode.needToSplit()

    def newLeaf(self):
        return MLeaf(M = self.M(), d = self.d())

    def newNode(self):
        return MNode(M = self.M(), d = self.d())

    def computeMeanNodes(self):
        ##TODO
        self.meanTotalNodes=0
        self.meanInternalNodes = 0 

    # Busqueda radial de objeto
    def search(self, radialMbr):
        t0 = time()

        results = []
        results = self.searchR(radialMbr = radialMbr, results = results)
      
        t1 = time()
        if self.meanSearchTime == None: 
            self.meanSearchTime = t1-t0
        else:
            self.meanSearchTime = (self.meanSearchTime*self.searchCount + (t1-t0))/(self.searchCount+1)
            self.searchCount = self.searchCount +1
        return results

    def searchR(self, radialMbr, results):
        selections = self.chooseTreeForSearch(radialMbr)

        if self.currentNode.isANode():
            for s in  selections:
                self.seekNode(s)
                results = results + self.searchR(radialMbr, results)
        else:
            for s in selections:
                results = results + [s]
        
        if self.currentHeigth() > 0:
            self.chooseParent()
        return results

    # Insercion de un mbrPointer
    def insert(self, mbrPointer):
        pass

    # Analogo a insert, inserta nuevos nodos hacia arriba en Rtree, y sigue insertando en caso de desbordes
    def adjust(self, nodeMbrPointer):
        pass

    def currentHeigth(self):
        return self.k

    # Guarda el nodo actual en disco
    def save(self,tree = None):
        if tree != None:
            self.nfh.saveTree(tree)
        else:
            self.nfh.saveTree(self.currentNode)

    # Actualiza nodo actual insertando nuevo hijo y guardando posteriormente en disco
    def update(self, newChild):
        self.currentNode.insert(newChild)
        self.save()
        
    # Actualiza nodo actual con la nueva version de uno de sus hijos (mbr,pointer)
    def updateChild(self, mbrPointer):
        self.currentNode.updateChild(mbrPointer)
        self.save()

    # Baja un nivel en el arbol y prepara cache y nodo actual
    def seekNode(self, mbrPointer):
        pointer = mbrPointer.getPointer()
        self.cache = [self.currentNode] + self.cache
        self.k = self.k + 1

        self.currentNode = self.nfh.readTree(pointer)
        return

    # Escoger el padre del nodo actual
    def chooseParent(self):
        if self.k > 0:
            self.currentNode = self.cache[0]
            self.k = self.k - 1
            self.cache = self.cache[1:]
        else:
            raise RtreeHeightError("Ya esta en la raiz")

    # Escoge los nodos que intersectan con el mbr para proceder con la insercion
    def chooseTree(self, mbrPointer):
        childrenMbrs = self.currentNode.getChildren()
        return self.sa.select(mbrPointer, childrenMbrs)

    # Escoge los nodos segun criterio de busqueda
    def chooseTreeForSearch(self, mbrO):
        childrenMbrs = self.currentNode.getChildren()
        return self.sa.radialSelect(mbrO, childrenMbrs)

    # Maneja split
    def split(self, newRtree, mbrPointer):
        currentMbr   = self.currentNode.getMbr()
        children     = self.currentNode.getChildren() # Tuplas (Mbr,Puntero) de la hoja seleccionada

        currentMbr.expand(mbrPointer.getMbr()) # expandimos el mbr del nodo (u hoja) seleccionado, para simular insercion
        partitionData = self.pa.partition(currentMbr, children + [mbrPointer]) # efectuamos la particion de elementos agregando el elemento a insertar

        self.currentNode.setSplitData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newRtree.setSplitData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.nfh.saveTree(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.nfh.saveTree(newRtree)       # Guardo el nuevo nodo (u hoja) en disco

        treeMbrPointer = newRtree.getMbrPointer()
        return treeMbrPointer

    # Advertencia : USAR SOLO CON ARBOLES PEQUEÑOS!
    def __str__(self):
        def toStr(tree, s = "", l = 0, i = 0):
            s = s + "{ l:" + str(l) + ", i :" + str(i) + "} ->" + str(tree) + "\n"

            if tree.isANode():
                children = tree.getChildren()
                for i in range(tree.elems):
                    child = children[i]
                    childTree = self.nfh.readTree(child.getPointer())
                    s = toStr(childTree, s, l + 1, i)
            else:
                children = tree.getChildren()
                for i in range(tree.elems):
                    child = children[i]
                    s = s + "{ child, l:" + str(l) + ", i :" + str(i) + "} ->" + str(child) + "\n"
            return s
        return toStr(self.currentNode)

if __name__=="__main__":
    d = 2
    M = 100
    rApi = RtreeApi(d = d, M = 100, maxE = 10**6, reset = True, initOffset = 0, partitionType = 0)
    print(rApi)