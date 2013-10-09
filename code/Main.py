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
  for d in range(1, 9):
    mTree = Rtree(2**d)
    for n in range (1, 11):
      m = Mbr(2**d)
      m.setPoint([random.random() for _ in range(0,2**d)])
      mTree.insert(m)
#     for obj in 
#     mTree.rangeQuery(obj,radio,mTree.root)
  pass