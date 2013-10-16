'''
Created on 09-10-2013

@author: Ian
'''
import io
import random
import struct
import Rtree
import Mbr


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
    # generateData()
  f = open("Resultados.txt", 'w')
  for M in [50,100]:
    mTree = Rtree(2 ** 2,M)
    f.write("d meanPartitionsPerNode meanInsertTime meanTotalNodes meanInternalNodes\n")
    # Construyo el Rtree con los elementos
    for s in range (10 ** 5):
      m = Mbr(2 ** 2)
      m.setPoint([random.random() for _ in range(2 ** 2)])
      mTree.insert(m)
    f.write("%d %f %f %f %f\n" % (mTree.d, mTree.getMeanNodePartitions(), mTree.meanInsertionTime, mTree.meanTotalNodes, mTree.meanInternalNodes))
#   f = open("Resultados.txt", 'w+')
#   for d in [2,4,8,16]:
#     for M in [50,100]:
#       mTree = Rtree(2 ** d,M)
#       f.write("d meanPartitionsPerNode meanInsertTime meanTotalNodes meanInternalNodes\n")
#       # Construyo el Rtree con los elementos
#       for s in range (10 ** 5):
#         m = Mbr(2 ** d)
#         m.setPoint([random.random() for _ in range(2 ** d)])
#         mTree.insert(m)
#       f.write("%d %f %f %f %f\n" % (mTree.d, mTree.getMeanNodePartitions(), mTree.meanInsertionTime, mTree.meanTotalNodes, mTree.meanInternalNodes))
#       f.write("d meanVisited meanQueryTime\n")
#       # Construyo los elementos de consulta
#       for radio in [0.25, 0.50, 0.75]:
#         for n in range (1,6):
#           for s in range (n * 10 ** 3):
#             obj = [random.random() for _ in range(2 ** d)]
#             mTree.search(radio * (d ** 0.5), obj)
#           f.write("%d %f %f\n" % (mTree.d, mTree.computeMeanNodes(), mTree.meanSearchTime))
