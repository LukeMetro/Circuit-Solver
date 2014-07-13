
'''
Luke Metro - lmetro - Section C - 15-112 Term Project
Solver.py

Class that takes the circuitElementDict from MainGUI and uses it to 
solve the circuit via a graph data structure.
Implementation of graph based off of code found at
http://www.python.org/doc/essays/graphs/
'''
from ComponentClasses import *
import tkMessageBox
import copy
from History import History


class Solver(object):

    def __init__(self, data):
        self.rawData = data

    def displayPopup(self):
        if(self.isCompleteCircuit() == True):
            try:
                self.createGraph()
                #Verify circuit and solve if valid
                #(Note: return value of isCompleteCircuit may have changed
                # with the shorting out of components, so re-test that)
                if(self.isCompleteCircuit() and self.verifyCircuit()):
                    self.eliminateExtraneous()
                    self.simplifyAndKeepHistory()
                    self.generateSolution()
                    self.createPopup()
                    del self #Delete solver object after info has been displayed
            except:
                tkMessageBox.showerror("No solution available.", 
                    "Sorry, your circuit could not be solved.\n" + \
                    "Please rebuild it in a different way and try again")

    #Actually create the popup to display the solution data to the user
    def createPopup(self):
        #Initialize resltString and sort resistor names alphanumerically
        resultString, sortedKeyList = '', sorted(self.solutionDict.keys())
        for key in sortedKeyList:
            if ('Resistor' in key): #Only output data for resistors
                resistance = self.solutionDict[key].resistance
                voltage = self.solutionDict[key].voltage
                current = self.solutionDict[key].current
                rPrefix, resistance = self.getPrefixAndAdjustValue(resistance)
                vPrefix, voltage = self.getPrefixAndAdjustValue(voltage)
                cPrefix, current = self.getPrefixAndAdjustValue(current)
                resultString += "%s:\t%.2f%svolts\t%.2f%samps\t%.2f%sohms\n"%\
                (key, voltage, vPrefix, current, cPrefix, resistance, rPrefix)
        thevResistance = self.solutionDict[self.voltageSourceKey].resistance
        tPrefix, thevResistance = self.getPrefixAndAdjustValue(thevResistance)
        resultString += "\nThevenin Resistance of Circuit is:   %.2f%sohms" % \
            (thevResistance, tPrefix)
        resultString +=\
'''\n\n(Voltages given as voltage across an element)\n
NOTE: If the data for a resistor isn't displayed, it is shorted out,
and thus electrically insignificant.
(No electrons pass through it, thus current = 0A and voltage = 0V)\n'''
        tkMessageBox.showinfo("Solution Data for Circuit", resultString)

        
    #Return the prefix to reduce number to 3 nondecimal digits
    #And adjust number to display accordingly
    def getPrefixAndAdjustValue(self, value):
        #Micro is the minimum supported prefix
        #Input will not be accepted below microamps/volts, so
        #Lower prefixes are unneccesary
        #Subtract 0.1 to offet loss of precision with floats
        if(10**(-6)-.1 <= abs(value) < 10**(-3)-.1):
            prefix = "micro"
            value /= 10.0**(-6)
        elif(abs(value) < 10.0**0 - .1):
            prefix = "milli"
            value /= 10.0**(-3)
        elif(abs(value) < 10**3 - .1):
            prefix = "" #no prefix
            #Don't change value
        elif(abs(value) < 10**6 - .1):
            prefix = "kilo"
            value /= 10.0**3
        elif(abs(value) < 10**9 - .1):
            prefix = "mega"
            value /= 10.0**6
        #Maximum supported prefix is Mega-
        #Input will not be accepted above the Megaamp/Megavolt level,
        #So higher prefixes are unneccesary
        return prefix, value

    #Create Struct class as way to hold data
    class Struct(): pass

    #Calculate current/voltage values for each component in self.rawData
    #Basically, reverse-construct the circuit using History object
    def generateSolution(self):
        self.solutionDict = dict() #Hold solved values for circuit
        #Find data for first item & initialize variables
        totalCurrent = self.getFullySimplifiedSolutionData()
        originalCurrent, lastOperation = totalCurrent, None
        #Loop from most recent to 2nd-to-last item in self.history
        for i in xrange(len(self.history) - 1, 0, -1):
            thisOperation = self.history[i].operation
            thisKey = self.history[i].deletedKey
            lastKey = self.history[i].presentKey
            self.solutionDict[thisKey] = self.Struct()
            self.solutionDict[thisKey].resistance = \
                self.history[i].data[thisKey].resistance
            if(thisOperation == 'Series'):
                self.makeSolutionForSeries(totalCurrent, thisKey, lastKey, i)
            else: #thisOperation == 'Parallel'
                totalCurrent = self.makeSolutionForParallel(totalCurrent, 
                    thisKey, lastKey)
            if(lastOperation == 'Series' and thisOperation == 'Parallel'):
                self.solutionDict[thisKey].current = \
                    (self.solutionDict[lastKey].current/ \
                    self.solutionDict[thisKey].resistance) * \
                    self.solutionDict[lastKey].resistance
            lastOperation = thisOperation#For next iteration of loop
            self.calculateVoltages(thisKey, lastKey)#Uses current just found


    #Calculate voltages via Ohm's Law (Voltage = Current * Resistance) 
    def calculateVoltages(self, thisKey, lastKey):
        self.solutionDict[lastKey].voltage = \
            self.solutionDict[lastKey].current * \
            self.solutionDict[lastKey].resistance
        self.solutionDict[thisKey].voltage = \
            self.solutionDict[thisKey].current * \
            self.solutionDict[thisKey].resistance

    #Updates self.solutionDict for parallel resistors and returns totalCurrent
    def makeSolutionForParallel(self, totalCurrent, thisKey, lastKey):
        numerator = (-1) * self.solutionDict[lastKey].resistance * \
            self.solutionDict[thisKey].resistance
        denominator = self.solutionDict[lastKey].resistance - \
            self.solutionDict[thisKey].resistance
        self.solutionDict[lastKey].resistance = numerator/denominator
        self.solutionDict[lastKey].current = \
            self.solutionDict[lastKey].voltage/ \
            self.solutionDict[lastKey].resistance
        self.solutionDict[thisKey].current = totalCurrent - \
            self.solutionDict[lastKey].current
        totalCurrent -= self.solutionDict[thisKey].current
        return totalCurrent

    #Updates self.solutionDict for series resistors
    def makeSolutionForSeries(self, totalCurrent, thisKey, lastKey, i):
        self.solutionDict[lastKey].resistance -= \
            self.solutionDict[thisKey].resistance
        #Check for series connection between current & last resistor
        if(len(self.history[i].graph[thisKey]) == 1):
            self.solutionDict[thisKey].current = \
                self.solutionDict[lastKey].current
        else:
            self.solutionDict[thisKey].current = totalCurrent


    #Get solution information for current version of self.graph/self.data
    #i.e. get solution information for voltage source and resistor in fully
    #simplified circuit
    def getFullySimplifiedSolutionData(self):
        for key in self.graph:
            if('Resistor' in key):
                #Create struct to hold data
                self.solutionDict[key] = self.Struct()
                #Get resistance from self.data
                self.solutionDict[key].resistance = self.data[key].resistance
                #Since it's only one resistor, voltage == voltage of source
                self.solutionDict[key].voltage = \
                    self.data[self.voltageSourceKey].voltage
                #Calculate current through resistor
                self.solutionDict[key].current = self.solutionDict[key].voltage
                self.solutionDict[key].current /= self.data[key].resistance
                #Create voltage source struct
                self.solutionDict[self.voltageSourceKey] = self.Struct()
                #Get voltage of source
                self.solutionDict[self.voltageSourceKey].voltage = \
                    self.data[self.voltageSourceKey].voltage
                #Current through voltage source equals the current through
                #The one resistor (Kirchoff's Current Law)
                self.solutionDict[self.voltageSourceKey].current = \
                    self.solutionDict[key].current
                #Set resistance for voltage source to be combined resistance
                #Of entire circuit (aka Thevenin Resistance or resistance seen)
                self.solutionDict[self.voltageSourceKey].resistance = \
                    self.data[key].resistance
                #Return total current to be used in calculations
                return self.solutionDict[self.voltageSourceKey].current

    #Go through graph, find elements that have nothing connecting into them
    #Or connect to nothing, and delete them. Recursively repeat until done.
    def eliminateExtraneous(self):
        noPathSet = set()
        isolationSet = set(self.graph.keys())
        for key in self.graph:
            if(self.graph[key] == set()):
                noPathSet.add(key)
            #If there is no path from a voltage source to an element,
            #It is electrically useless. 
            if(not self.doesPathExist(self.voltageSourceKey, key)):
                noPathSet.add(key)
            #Delete components that have connections from isolation list
            saveList = set()
            for innerKey in isolationSet:
                if(innerKey in self.graph[key]):
                    saveList.add(innerKey)
            for innerKey in saveList:
                isolationSet.remove(innerKey)
        #Delete components from graph
        unionDeleteSet = noPathSet | isolationSet
        self.deleteItems(unionDeleteSet)
        if(unionDeleteSet != set()):
            self.eliminateExtraneous()#Recurse if necessary

    def deleteItems(self, deleteSet):
        for item in deleteSet:
            del self.graph[item]
        #Delete references to deleted items in graph
        for key in self.graph:
            for item in deleteSet:
                if(item in self.graph[key]):
                    self.graph[key].remove(item)

    #Go through circuit and find equivalent resistances and keep
    #A history of the operations (Recursive function)
    def simplifyAndKeepHistory(self):
        self.history = [History(copy.deepcopy(self.data),
            copy.deepcopy(self.graph), None, None, None)]
        self.combineSeries()
        self.combineParallel()

    '''
    Loop through components and combine resistors in series
    2 resistors are in series iff a resistor is only in the contents
    of one key in the graph dict
    '''
    def combineSeries(self):
        rToDelete = rToKeep = None
        for key in self.graph:
            for innerKey in self.graph:
                #Only combine resistors
                if('Resistor' in key and 'Resistor' in innerKey):
                    if(self.graph[key] == set([innerKey])):
                        appearanceCount = 0
                        for innerMostKey in self.graph:
                            if innerKey in self.graph[innerMostKey]:
                                appearanceCount += 1
                        if(appearanceCount == 1):
                            rToDelete, rToKeep = innerKey, key
                    if(rToDelete != None):
                        break#Break out of inner loop once series are found
            if(rToDelete != None):
                #Update history list
                self.history.append(History(copy.deepcopy(self.data),
                    copy.deepcopy(self.graph), rToDelete, rToKeep, 'Series'))
                self.graph[rToKeep] = copy.deepcopy(self.graph[rToDelete])
                del self.graph[rToDelete]
                self.data[rToKeep].resistance+=self.data[rToDelete].resistance
                del self.data[rToDelete]
                #Recursively combine resistors until complete
                self.combineParallel(); self.combineSeries()
                break

    '''
    Loop through components and combine resistors in parallel.
    Two resistors are in parallel iff
    1) They lead into the same components
    2) There is a component that leads into both of them
    (ex: output for 1 is [2,3,4] and output for 2 is [1,3,4])
    '''
    def combineParallel(self):
        criteria1, criteria2 = False, True
        #Nested loop to test each resistor with each other resistor
        for outerKey in self.graph:
            for innerKey in self.graph:
                #Check if keys are two different resistors
                if('Resistor' in outerKey and 'Resistor' in innerKey and
                    outerKey != innerKey):
                    if(self.graph[outerKey] == self.graph[innerKey]):
                        criteria1 = True
                        for innerMostKey in self.graph:
                            if(self.isParallelCriteria1True(outerKey, 
                                innerKey, innerMostKey)):
                                criteria1 = False
                if(criteria1 == criteria2 == True):
                    break
                else: #Reset criteria
                    criteria1, criteria2 = False, True
            if(criteria1 == criteria2 == True):
                self.doParallelCombineOperation(innerKey, outerKey)
                #Recursively try to combine more resistors
                self.combineSeries(); self.combineParallel()
                break #Exit outer loop

    #Determine if criteria 1 for resistors being in parallel is true
    def isParallelCriteria1True(self, outerKey, innerKey, innerMostKey):
        return ((innerKey in self.graph[innerMostKey] and 
            outerKey not in self.graph[innerMostKey]) or
            (outerKey in self.graph[innerMostKey] and
            innerKey not in self.graph[innerMostKey]))


    def doParallelCombineOperation(self, resistor1, resistor2):
        #Update history list
        self.history.append(History(copy.deepcopy(self.data),
            copy.deepcopy(self.graph), resistor1, resistor2, 'Parallel'))
        r1resistance = self.data[resistor1].resistance
        r2resistance = self.data[resistor2].resistance
        #Adjust value of resistance in self.data
        self.data[resistor2].resistance = (r1resistance*r2resistance)
        self.data[resistor2].resistance /= (r1resistance+r2resistance)
        del self.data[resistor1]
        #Remove resistor 1 and referencees to it from graph
        for key in self.graph:
            if(resistor1 in self.graph[key]):
                self.graph[key].remove(resistor1)
        del self.graph[resistor1]

    #Check to see if circuit is both complete (current can flow from
    #One end of the terminal to another) and it only utilizes a single
    #Voltage Source
    def verifyCircuit(self):
        if(self.voltageSourceCount != 1):
            tkMessageBox.showerror("Too Many Voltage Sources",
                "Solving is only supported for a single voltage source.\n"+
                "Rebuild your circuit and try again.")
            return False
        elif(not self.doesPathToSelfExist(self.voltageSourceKey)):
            tkMessageBox.showerror("Invalid Circuit",
                "Path does not exist from positive to negative terminal\n" +
                "of voltage source. Rebuild your circuit and try again.")
            return False
        else:
            return True #Circuit is valid and ready to be solved

    #Check to see if a node has a path to itself in a map
    #ORIGINAL CODE, based off of graph representation from python essay
    def doesPathToSelfExist(self, node):
        #First, find other nodes that connect into given node
        candidates = set() 
        for key in self.graph:
            if node in self.graph[key]:
                candidates.add(key)
        #For each candidate, check to see if a path exists from 
        #Initial node to candidate
        for candidate in candidates:
            if(self.doesPathExist(node, candidate) == True):
                return True
        return False #Only reached if True is never returned


    #Create an Adjacency map of the circuit with direction being
    #The flow of current throughout the circuit
    def createGraph(self):
        self.graph = dict()
        self.combineWires()
        self.shortOutResistors()
        self.data = copy.deepcopy(self.rawData)
        #Store appropriate data that will make graph
        self.voltageSourceKey = self.getVoltageSourceKey()
        self.voltageSource = self.data[self.voltageSourceKey]
        self.startTerminal = (self.voltageSource.outLinkX, 
            self.voltageSource.outLinkY)
        self.endTerminal = (self.voltageSource.inLinkX, 
            self.voltageSource.inLinkY)
        self.addToGraph(self.voltageSourceKey, self.startTerminal)

    #Delete from self.rawData resistors that are fully enclosed by a wire node
    #(Current will instead pass through the wire and resistors will be 
    # electrically insignificant)
    def shortOutResistors(self):
        deletionSet = set()
        for outerKey in self.rawData:
            if('Wire' in outerKey):
                connectionCoords = self.rawData[outerKey].connectionCoords
                for innerKey in self.rawData:
                    if('Resistor' in innerKey):
                        enterCoords = (self.rawData[innerKey].inLinkX, 
                            self.rawData[innerKey].inLinkY)
                        exitCoords = (self.rawData[innerKey].outLinkX, 
                            self.rawData[innerKey].outLinkY)
                        if(enterCoords in connectionCoords and
                            exitCoords in connectionCoords):
                            deletionSet.add(innerKey)
        #Delete appropriate items
        for item in deletionSet:
            del self.rawData[item]




    #Combine wires so that 2 touching wires become one large wire
    #After this method runs, there will be no adjacent wires in the graph
    def combineWires(self):
        deletionSet = set()
        for outerKey in self.rawData:
            for innerKey in self.rawData:
                #Only combine wires, and don't combine anything with itself
                if(('Wire' in outerKey) and ('Wire' in innerKey) and
                    innerKey != outerKey and innerKey not in deletionSet):
                    outerCoords = set(self.rawData[outerKey].connectionCoords)
                    innerCoords = set(self.rawData[innerKey].connectionCoords)
                    intersect = outerCoords & innerCoords
                    if(intersect != set()):
                        self.rawData[innerKey].connectionCoords =  \
                            outerCoords | innerCoords
                        deletionSet.add(outerKey)
        #Delete wires that were absorbed into other wires
        for item in deletionSet:
            del self.rawData[item]

    #Recursive function that adds components to graph
    #Unitl graph is fully constructed
    def addToGraph(self, startKey, startCoords):
        if(startKey not in self.graph):
            self.graph[startKey] = set()
        for key in self.rawData:
            #Don't connect an item to itself
            if(key != startKey):
                if(isinstance(self.data[key], Wire)):
                    self.wireAddOperation(startKey, key)
                elif(not isinstance(self.data[startKey], Wire)):
                    self.nonWireAddOperation(startKey, key, startCoords)

    def nonWireAddOperation(self, start, to, startCoords):
        enterCoords = (self.data[to].inLinkX, self.data[to].inLinkY)
        exitCoords = (self.data[to].outLinkX, self.data[to].outLinkY)
        if(startCoords == enterCoords):
            self.graph[start].add(to)
            if(not isinstance(self.data[to], VoltageSource)):
                self.addToGraph(to, exitCoords)


    def wireAddOperation(self, nonWireKey, wireKey):
        #All coordinates that the wire encompasses
        connectionCoords = self.data[wireKey].connectionCoords
        nonWireExitCoords = (self.data[nonWireKey].outLinkX,
                            self.data[nonWireKey].outLinkY)
        if(nonWireExitCoords in connectionCoords):
            for key in self.data:
                if((key != nonWireKey) and (key != wireKey)):
                    #Wires have been combined, so 2 wires cannot be touching
                    if(not isinstance(self.data[key], Wire)):
                        enterCoords = (self.data[key].inLinkX, 
                            self.data[key].inLinkY)
                        exitCoords = (self.data[key].outLinkX, 
                            self.data[key].outLinkY)
                        if(enterCoords in connectionCoords):
                            self.graph[nonWireKey].add(key)
                            if(not isinstance(self.data[key], VoltageSource)):
                                self.addToGraph(key, exitCoords)

    #Uses find_path to determine if a path exists (ORIGINAL CODE)
    def doesPathExist(self, start, end):
        path = self.find_path(self.graph, start, end)
        if(path == None):
            return False
        else:
            return True

    #Taken from python graphs essay
    #Finds a path between 2 nodes. If none exists, return empty brackets
    def find_path(self, graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not graph.has_key(start):
            return None
        for node in graph[start]:
            if node not in path:
                newpath = self.find_path(graph, node, end, path)
                if newpath: return newpath
        return None #Base case, path not found

    #Get the key of the circuit's voltage source
    def getVoltageSourceKey(self):
        for key in self.data:
            if(isinstance(self.data[key], VoltageSource)):
                return key

    #Check to see if circuit is valid. If it isn't, display an error message
    def isCompleteCircuit(self):
        #Check to see that there is something powering the circuit
        self.voltageSourceCount, resistorCount = 0, 0
        for key in self.rawData:
            if(isinstance(self.rawData[key], VoltageSource)): 
                self.voltageSourceCount += 1
            elif(isinstance(self.rawData[key], Resistor)): 
                resistorCount += 1
        if(resistorCount == self.voltageSourceCount == 0):
            tkMessageBox.showwarning("No circuit",
                "You forgot to create a circuit!")
            return False
        elif(self.voltageSourceCount == 0):
            tkMessageBox.showwarning("Incomplete Circuit - Add a Voltage Source",
                "The current through each resistor is 0 Amps.\n"+
                "The voltages at all nodes of the circuit are 0V.")
            return False
        elif(resistorCount == 0):
            tkMessageBox.showwarning("Incomplete Circuit", 
                "Current isn't flowing through any resistors." + 
                " Values cannot be calculated.")
            return False
        return True #Only if false is never reached



