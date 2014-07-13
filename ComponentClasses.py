'''
Luke Metro - Lmetro - Section B - 15-112 Term Project
File that contains classes that are used to represent circuit components
'''

class Resistor(object):
    count = 1
    def __init__(self, resistance, cX, cY):
        self.imageWidth, self.imageHeight = 100, 50 #Pixels
        #Compute coordinates of connection points of resistor
        #(Resistor is placed horizontally by default)
        self.inLinkX, self.inLinkY = cX - self.imageWidth/2, cY
        self.outLinkX, self.outLinkY = cX + self.imageWidth/2, cY
        self.topX, self.topY = cX - self.imageWidth/2, cY - self.imageHeight/2
        self.bottomX, self.bottomY = cX + self.imageWidth/2, cY + self.imageHeight/2
        self.name = "Resistor %d" % Resistor.count
        self.resistance = resistance
        Resistor.count += 1

    def __hash__(self):
        return hash(self.name)


class VoltageSource(object):
    count = 1
    def __init__(self, voltage,  cX, cY):
        self.imageWidth, self.imageHeight = 100, 50
        #Compute coordsinates of connection points of voltage source
        #(Voltage source is placed horizontally by default)
        self.inLinkX, self.inLinkY = cX - self.imageWidth/2, cY
        self.outLinkX, self.outLinkY = cX + self.imageWidth/2, cY
        self.topX, self.topY = cX - self.imageWidth/2, cY - self.imageHeight/2
        self.bottomX, self.bottomY = cX + self.imageWidth/2, cY + self.imageHeight/2
        self.name = "Voltage Source %d" % VoltageSource.count
        self.voltage = voltage #Value of voltage 
        VoltageSource.count += 1

    def __hash__(self):
        return hash(self.name)

class Wire(object):
    count = 1
    def __init__(self, cX, cY):
        #Wire goes along width of image file, and runs across cY
        self.imageWidth, self.imageHeight = 100, 50
        startX, endX = -self.imageWidth/2, +self.imageWidth/2 + 1
        #Add one to endX to offset non-inclusiveness of xrange
        #Compute coordinates of connection range of wire
        self.connectionCoords = []
        for point in xrange(startX, endX): #Offset non-inclusiveness of xrange
            self.connectionCoords.append((cX + point, cY))
        #Make connectionCoords only include multiples of 25
        for i in xrange(len(self.connectionCoords)):
            (x, y) = self.connectionCoords[i]
            self.connectionCoords[i] = (roundToGrid(x), roundToGrid(y))
        self.connectionCoords = list(set(self.connectionCoords)) #eliminate redundancies
        self.name = "Wire %d" % Wire.count
        self.topX, self.topY = cX - self.imageWidth/2, cY - self.imageHeight/2
        self.bottomX, self.bottomY = cX + self.imageWidth/2, cY + self.imageHeight/2
        Wire.count += 1

    def __hash__(self):
        return hash(self.name)

#Round connectionCoords to only include multiples of 25
def roundToGrid(num):
    gridLine = 25 #Distance between gridLines
    return int(gridLine * round(float(num)/gridLine))
