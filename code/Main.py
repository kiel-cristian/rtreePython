'''
Created on 09-10-2013

@author: Ian
'''
import io
import random
import struct
from Rtree import *
from MbrPointer import *
from MbrGenerator import *
import datetime

def generateObjects(name, numElems, dimension):
    f = io.open(name, 'wb')
    randElems = [random.random() for _ in range(numElems * dimension)]
    buf = struct.pack('1i', dimension) + struct.pack('1i', numElems) + struct.pack('%sd' % len(randElems), *randElems)
    f.write(buf)
    print("Done[" + str(numElems) + "," + str(dimension) + "]")

def generateData():
    num = 0;
    for d in range(1, 9):
        for n in range (1, 11):
            generateObjects("data" + str(num), n * (10 ** 5), 2 ** d)
            num = num + 1

if __name__ == '__main__':
#     mTree = Rtree(d=2, M=100, maxE=10 ** 6, reset=True, initOffset=0, partitionType=0)
#     for s in range (100):
#         mTree.insert(gen.next(d = 2))
#         for s in range (10):
#             mTree.search(gen.nextRadial(d = 2, r = 0.25 * (2 ** 0.5)))
    for j in range(1, 11):
        k = 1
        for partitionType in [0, 1]:
    #       for d in [2, 4, 8, 16]:
          for d in [4, 8, 16]:
              for M in [50, 100]:
                  gen = MbrGenerator()
                  mTree = Rtree(d=d, M=M, maxE=10 ** 6, reset=True, initOffset=0, partitionType=partitionType)
                  f = open("Resultados.txt", 'w+')
                  f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "\n")
                  f.write("d=%d M=%d partitionType=%d\n" % (d, M, partitionType))
                  f.write("meanPartitionsPerNode meanInsertTime meanTotalNodes meanInternalNodes\n")
                  # Construyo el Rtree con los elementos
                  for s in range (10 ** 5):
                      mTree.insert(gen.next(d=d))
                  f.write("%f %f %f %f\n" % (mTree.getMeanNodePartitions(), mTree.meanInsertionTime, mTree.meanTotalNodes, mTree.meanInternalNodes))
                  f.write("meanVisited meanQueryTime\n")
                  print("Insercion n:%d" % k)
                  k += 1
                  f.close()
                  fileName = "../searchs/" + str(mTree.treeType) + " M" + str(mTree.M()) + " d" + str(mTree.d()) + " busqueda.bin"
                  # Construyo los elementos de consulta
                  for radio in [0.25, 0.50, 0.75]:
                      for n in range (1, 6):
                          f = open("Resultados.txt", 'w+')
                          fb = open(fileName, 'w+')
                          for s in range (n * 10 ** 3):
                              mTree.search(gen.nextRadial(d=d, r=radio * (d ** 0.5)), fb,False, True)
                          f.write("%f %f\n" % (mTree.getMeanVisitedNodes(), mTree.meanSearchTime))
                          f.close()
                          fb.close()
                          print("Busqueda n:%d %f" % (n, radio))
        print("Repeticion n:%d" % j)