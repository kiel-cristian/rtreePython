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

        # Algoritmo de particionamiento
        if partitionType == 0:
            self.pa = LinealPartition()
        elif partitionType == 1:
            self.pa = CuadraticPartition()

        # self.sa = MinAreaSelector()                # Algoritmo de seleccion de mejor nodo a insertar

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

    def newLeaf(self):
        return MLeaf(M = self.M(), d = self.d())

    def newNode(self):
        return MNode(M = self.M(), d = self.d())

    # Busqueda radial de objeto
    def search(self, r, mbrObject):
        pass

    # Inserta un mbrPointer en una hoja del Rtree, luego, maneja casos de desborde
    def insert(self, mbrPointer):
        # Bajo por el arbol hasta encontrar una hoja adecuada
        while self.currentNode.isANode():
            self.chooseTree(mbrPointer) # cambia currentNode

        if self.needToSplit():
            newLeafMbrPointer = self.split(self.newLeaf(), mbrPointer)
            self.adjust(newLeafMbrPointer) # Inicio ajuste hacia arriba del Rtree

    # AUXILIARES: SUJETAS A MODIFICACION

    # Analogo a insert, inserta nuevos nodos hacia arriba en Rtree, y sigue insertando en caso de desbordes
    def adjust(self, nodeMbrPointer):
        lastNodeMbrPointer = nodeMbrPointer

        while self.currentHeigth() > 0:
            self.chooseParent() # cambia currentNode y sube un nivel del arbol

            if self.needToSplit():
                lastNodeMbrPointer = self.split(self.newNode(), lastNodeMbrPointer)
            else:
                self.currentNode.insert(lastNodeMbrPointer)
                self.saveTree(self.currentNode)
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

            self.nfh.saveNewTree(newRoot)
            self.root = newRoot

        self.goToRoot()
        return

    def currentHeigth(self):
        return self.k

    # Insert masivo leyendo datos de archivos, deberia servir para experimentos
    def loadRtreeData(self):
        pass

    # Baja un nivel en el arbol y prepara cache y nodo actual
    def seekNode(self, pointer):
        self.cache = [self.currentNode] + self.cache
        self.k = self.k + 1

        self.currentNode = self.nfh.readTree(pointer)
        return

    def chooseParent(self):
        if self.k > 0:
            self.currentNode = self.cache[0]
            self.k = self.k - 1
            self.cache = self.cache[1:]
        else:
            raise RtreeHeightError("Ya esta en la raiz")

    # Escoge un nodo u hoja para proceder con la insercion
    def chooseTree(self, mbrPointer):
        childrenMbrs   = self.currentNode.getChildrenMbrs()
        bestMbrPointer = self.sa.select(mbrPointer, childrenMbrs) #PENDIENTE
        self.seekNode(bestMbrPointer.getPointer())

    # Maneja split
    def split(self, newRtree, mbrPointer):
        currentMbr   = self.currentNode.getMbr()
        children     = self.currentNode.getChildren() # Tuplas (Mbr,Puntero) de la hoja seleccionada

        currentMbr.expand(mbrPointer.getMbr()) # expandimos el mbr del nodo (u hoja) seleccionado, para simular insercion
        partitionData = self.pa.partition(currentMbr, childrenMbrs + [mbrPointer]) # efectuamos la particion de elementos agregando el elemento a insertar

        self.currentNode.setSplitData(partitionData[0][0], partitionData[0][1:]) # Guardo en el nodo (u hoja) antiguo la primera particion
        newRtree.setSplitData(partitionData[1][0], partitionData[1][1:])         # Guardo en un nuevo nodo (u hoja) la segunda particion

        self.saveTree(self.currentNode)  # Guardo el nodof (u hoja) antiguo en disco
        self.saveNewTree(newRtree)       # Guardo el nuevo nodo (u hoja) en disco

        treeMbrPointer = newRtree.getMbrPointer()
        return treeMbrPointer

if __name__=="__main__":
    d = 2
    M = 100
    rtree = Rtree(d = d, M = 100, maxE = 10**6, reset = True, initOffset = 0, partitionType = 0)

    rtree.insert(randomMbrPointer(d))
    # rtree.loadRtreeData()