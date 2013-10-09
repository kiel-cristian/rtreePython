from math import log
import sys
import struct
from FileHandler import *
from MRtree import *
from PartitionAlgorithm import *

#  ERRORS
class RtreeHeightError(Exception):
    def __init__(self):
        self.value = "height error"
    def __str__(self):
        return repr(self.value)

class Rtree(object):
    # d          : dimension de vectores del arbol
    # M          : capacidad maxima de nodos y hojas
    # maxE       : cantidad maxima de elementos que almacenara el Rtree
    # reset      : cuando es True, se construye un nuevo arbol, si no, se carga de disco
    # initOffset : offset desde se cargara nodo raiz
    def __init__(self, d, M = 100, maxE = 100000, reset = False, initOffset = 0, partitionType = 0):
        self.nfh = RtreeFileHandler( loadDataFile    = "data" + str(d) + "D.bin",
                                dataFile        = "rtree" + str(d) + "D.bin",
                                d               = d,
                                M               = M,
                                initOffset      = initOffset)

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
            self.currentNode.setAsRoot()

            # Creo dos hojas para mantener invariante de la raiz
            leaf1 = self.newLeaf()
            leaf2 = self.newLeaf()

            # Agrego las hojas al nodo raiz
            self.currentNode.insert(leaf1)
            self.currentNode.insert(leaf2)

            # Guardo el nodo raiz en disco
            self.nfh.saveTree(self.currentNode)

            # Guardo dos hojas de la raiz en disco
            self.nfh.saveNewTree(leaf1)
            self.nfh.saveNewTree(leaf2)

            # Guardo una referencia al nodo raiz
            self.root = self.currentNode
        else:
            # Se carga la raiz de disco
            self.currentNode = self.nfh.readTree(initOffset)
            self.currentNode.setAsRoot(initOffset)
            self.root = self.currentNode
            
        #Metricas
        self.meanInsertionTime = None
        self.insertionsCount = 0
        self.meanTotalNodes = 0
        self.meanInternalNodes = 0
        self.meanSearchTime = None:
        self.searchCount = 0
        
    def getMeanNodePartitions(self):
      ##TODO
      pass

    # Capacidad minima de nodos y hojas
    def m(self):
        return self.nfh.m

    # Capacidad maxima de nodos y hojas
    def M(self):
        return self.nfh.M

    def d(self):
        return self.nfh.d

    def needToSplit(self):
        return self.currentNode.needsToSplit()

    def isNode(self, p):
        return self.nfh.isNode(p)

    def newLeaf(self):
        return MLeaf(M = self.M(), d = self.d())

    def newNode(self):
        return MNode(M = self.M(), d = self.d())

    def computeMeanNodes(self):
      ##TODO
      self.meanTotalNodes=0
      self.meanInternalNodes = 0    

    # Busqueda radial de objeto
    def search(self, r, mbrObject):
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
        while self.currentNode.isNode():
            self.chooseNode(mbr)

        if self.needToSplit():
            nodeMbr      = self.currentNode.getMbr()
            childrenMbrs = self.currentNode.getChildrenMbrs()

            results = self.pa.partition()
            
        t1 = time()
        if self.meanInsertionTime == None: 
          self.meanInsertionTime = t1-t0 
        else:
          self.meanInsertionTime = (self.meanInsertionTime*self.insertionsCount + (t1-t0))/(self.insertionsCount+1)
          self.insertionsCount = self.insertionsCount +1
        self.computeMeanNodes()

    # AUXILIARES: SUJETAS A MODIFICACION

    # Insert masivo leyendo datos de archivos, deberia servir para experimentos
    def loadRtreeData(self):
        pass

    # Baja un nivel en el arbol y prepara cache y nodo actual
    def seekNode(self, pointer):
        pass

    # Escoge un nodo u hoja para insertar
    def chooseTree(self, mbrPointer):
        pass

    # Maneja split
    def splitNode(self):
        pass

if __name__=="__main__":
    d = 2
    M = 100
    rtree = Rtree(d = d, M = 100, maxE = 10**6, reset = True)
    # rtree.loadRtreeData()
