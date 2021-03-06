class MbrError(Exception):
    def __init__(self):
        super(MbrError, self).__init__()
        self.value = "mbr error"
    def __str__(self):
        return repr(self.value)
class MbrDataListLengthError(MbrError):
    pass
class MbrPointDimensionError(MbrError):
    pass

class MbrApi(object):
    def __init__(self):
        pass
    def getMin(self,d):
        pass
    def getMax(self,d):
        pass
    def distanceTo(self, o):
        pass
    def returnExpandedMBR(self, o):
        pass
    def getArea(self):
        pass
    def deadSpace(self, o):
        pass
    def setRange(self, o):
        pass
    def areIntersecting(self,o):
        pass
    def getCenter(self):
        pass