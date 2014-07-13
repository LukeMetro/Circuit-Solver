'''
Luke Metro - Lmetro - Section B - 15-112 Term Project
Main GUI for the circuit editor/solver
Includes the capability to generate data from which an adjacecy map 
of the circuit can be created
'''
from Tkinter import *
from PIL import ImageTk, Image
from ComponentClasses import * #Import data structures for component data
from Solver import Solver
from Editor import Editor
import tkMessageBox
import copy


class MainGUI(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def run(self):
        self.root = Tk()
        self.canvas = Canvas(self.root, width = self.width,
                             height = self.height)
        self.canvas.pack()
        self.root.resizable(width = 0, height = 0)
        self.initData() #Init data for the program to run
        self.initGUI()
        self.root.title("Circuit Solver")
        self.root.mainloop() #This call BLOCKS

    def initData(self):
        self.getImageAssets()
        self.createComponentList()
        self.circuitElementDict = dict() #Dictionary of elements in the circuit

    #Create a component list used to create the drag-and-drop buttons
    def createComponentList(self):
        #list of dictionaries with 'name' & 'image' index
        self.componentList = []
        self.componentList.append({"name": "Resistor",
                                   "image": self.resistorImages[0]})
        self.componentList.append({"name": "Voltage Source",
                                   "image": self.voltageImages[0]})
        self.componentList.append({"name": "Wire",
                                   "image": self.wireImages[0]})
        
    def initGUI(self):
        self.drawGridLines()
        self.drawDesignModeButtons()
        self.drawSolveButton()
        #Set method outside of main event loop to preserve bindings
        self.root.after(10, self.drawStartInstructionText)
        self.setBindings()

    #Create popup that will give the user instructions on how to operate the program
    def drawStartInstructionText(self):
        instructionText = \
'''
Drag-and-drop voltage sources, resistors, and wires from the 
top ribbon to add them to your circuit. Place components with
their arrows pointing in the direcion of current. 
Make a complete circuit, and hit solve!

PROTIPS: 

To edit the value of a component, double click on it and an editor 
windowwill appear. (NOTE: Resistors default to 1 kiloohm and 
Voltage Sources default to 1 Volt.)

To delete a component, press BACKSPACE while you are dragging it.

To rotate a component, while you are dragging it, press the arrow 
key in the direction in which you want the component to go. 
(The current arrow will be pointing in the same direction as 
the arrow key that you select.)
'''
        tkMessageBox.showinfo("Instructions", instructionText)


    #Open Solver Window
    def drawSolveButton(self):
        self.solveButtonWidth, self.solveButtonHeight = 50,25
        self.solveTopX  = self.solveButtonWidth
        self.solveTopY = self.height - self.solveButtonHeight
        self.solveButton = Button(self.root, text="Solve!",
                                  command = self.onSolveButtonPress,
                                  bg = "#33e5b5")
        smallButton_window = self.canvas.create_window(0, self.height,
                                            window = self.solveButton,
                                            anchor = SW)

    def onSolveButtonPress(self):
        solver = Solver(copy.deepcopy(self.circuitElementDict))
        solver.displayPopup() #Display popup w/ all circuit info
        del solver #Not needed for subsequent calculations

    #Create "Buttons" from which users will be able to drag and drop
    #Components onto their circuit
    def drawDesignModeButtons(self):
        bgColor, buttonColor = "#4285f4", "white"
        self.canvas.create_rectangle(0, 0, self.width, self.lineStartHeight,
                                     fill = bgColor, outline = bgColor)
        self.drawTopInstructionText()
        buttonLength, margin, topOffset = 125, 10, 25 #pixels
        for i in xrange(len(self.componentList)):
            self.canvas.create_rectangle(buttonLength*i + margin, topOffset,
                                         buttonLength*(i+1)-margin,
                                         self.lineStartHeight-margin,
                                         fill=buttonColor,
                                         outline = buttonColor)
            imageIndex = i
            #loop around to first component if array is to go out of bounds
            imageCx = (buttonLength*i + buttonLength*(i+1))/2
            imageCy = self.lineStartHeight/2
            self.canvas.create_image(imageCx, imageCy,
                    image=self.componentList[imageIndex]["image"],
                    tags = ("select component",
                    self.componentList[imageIndex]["name"]),
                    anchor = CENTER)
            
    def drawTopInstructionText(self):
        self.instructionTextHeight = 12
        self.instructionTextStart = (6, 6)
        font = "Helvetica %d bold" %self.instructionTextHeight
        ribbonText = "Click and drag a component to add it to your circuit:"
        self.canvas.create_text(self.instructionTextStart, text=ribbonText,
                                font=font, anchor = NW)
    

    '''Bind mouse presses to enable dragging-and-dropping of components
       drag-and-drop functionality based off code from demo found at
       http://bit.ly/181UUe4 (Bryan Oakley)'''
    #Set key/mouse bindings of the Main GUI
    def setBindings(self):
        self.dragData = {'x': 0, 'y': 0, 'item': None} #initialize dragData
        self.canvas.tag_bind("component", "<ButtonPress-1>",
                             self.onComponentButtonPress)
        self.canvas.tag_bind("component", "<ButtonRelease-1>",
                             self.onComponentButtonRelease)
        self.canvas.tag_bind("component", "<B1-Motion>",
                             self.onComponentMotion)
        self.canvas.tag_bind("component", "<Double-Button-1>",
                             self.onComponentDoubleClick)
        self.root.bind("<Key>", self.keyPressedInactive)
        self.canvas.tag_bind("select component", "<ButtonPress-1>",
                             self.onSelectComponentButtonPress)
        self.canvas.tag_bind("select component", "<ButtonRelease-1>",
                             self.onComponentButtonRelease)
        self.canvas.tag_bind("select component", "<B1-Motion>",
                             self.onComponentMotion)

    #On double-click of item, generate a popup that allows the user to
    #Edit the value of the selected component.
    def onComponentDoubleClick(self, event):
        self.getDraggedItemData(event)
        selected = self.circuitElementDict[self.dragData['dataKey']]
        if(not isinstance(selected, Wire)):#Wires cannot be edited   
            edit = Editor(selected, self.root)
            edit.displayPopup()

    #When "select component" button is pressed, draw a component on top of
    #the button and allow the user to drag that component around
    def onSelectComponentButtonPress(self, event):
        #Draw new component
        selectedItem = self.canvas.find_closest(event.x, event.y)[0]
        itemTags = self.canvas.gettags(selectedItem)
        if("Resistor" in itemTags):
            self.drawResistor(event.x, event.y)
        elif("Voltage Source" in itemTags):
            self.drawVoltageSource(event.x, event.y)
        elif("Wire" in itemTags):
            self.drawWire(event.x, event.y)
        self.getDraggedItemData(event) #Get dragged item data
        #Set keybinding to enable rotation and deletion of element
        self.root.bind("<Key>", self.keyPressedActive)

    #Begin the dragging of a component
    def onComponentButtonPress(self, event):
        #Set keybinding to enable rotation & deletion of element
        self.root.bind("<Key>", self.keyPressedActive)
        self.getDraggedItemData(event)

    #Get identifier (i.e. "Resistor 4") about element currently being dragged
    def getDraggedItemData(self, event):
        #dragData idea from Oakley post
        closeItems = self.canvas.find_closest(event.x, event.y)
        #Ensure that it is item and not, say, a gridline or background rect
        #being dragged
        for i in xrange(len(closeItems)):
            if("component" in self.canvas.gettags(closeItems[i])):
                self.dragData['item'] = closeItems[i]
                break
        self.dragData['x'] = event.x
        self.dragData['y'] = event.y
        #Get dict key of selected item by looping through items
        #(Original Code)
        for key in self.circuitElementDict:
            element = self.circuitElementDict[key]
            if(event.x >= element.topX and event.x <= element.bottomX and
               event.y >= element.topY and event.y <= element.bottomY):
                self.dragData['dataKey'] = element.name


    #Rotate if 'r' key is pressed while dragging component
    #Original Code
    def keyPressedActive(self, event):
        arrowKeysyms = set(['Right', 'Left', 'Up', 'Down'])
        if(event.keysym == "BackSpace"):
            #If user hits backspace while dragging object, delete it
            self.canvas.delete(self.dragData['item'])
            #Also delete component data from dictionary
            del self.circuitElementDict[self.dragData['dataKey']]
        elif(event.keysym in arrowKeysyms):
            self.rotateUntilSatisfactory(event)

    #Rotate the item counterclockwise until it corresponds to the
    #Proper position for the arrow key
    def rotateUntilSatisfactory(self, event):
        #Do not rotate if not in valid circuit drawing area
        if(event.y <= self.lineStartHeight):
            return #Don't attempt rotation and get out of function
        if(event.keysym == 'Right'):
            finalPosition = 0
        elif(event.keysym == 'Up'):
            finalPosition = 1
        elif(event.keysym == 'Left'):
            finalPosition = 2
        else: #event.keysym == 'Down'
            finalPosition = 3
        #Get orientation and rotate item until orientation matches
        #Desired orientation
        orientation = int(self.canvas.gettags(self.dragData['item'])[2])
        while(orientation != finalPosition):
            self.rotateItem(event)
            orientation = int(self.canvas.gettags(self.dragData['item'])[2])

    
    #Rotate item on press of arrow key
    def rotateItem(self, event):
        tags = self.canvas.gettags(self.dragData['item'])
        orientation = int(tags[2])
        element = self.circuitElementDict[self.dragData['dataKey']] #alias
        cX = (element.topX + element.bottomX)/2
        cY = (element.topY + element.bottomY)/2
        self.drawImageAfterRotation(cX, cY, orientation, tags)
        self.dragData['item'] =self.canvas.find_closest(event.x, event.y)[0]
        self.resetCornerCoords(element, cX, cY)
        #Edit connection coords if element is a wire
        if(isinstance(element, Wire)):
            self.wireRotate(element)   
        else: #For non-wire elements, 
            self.nonWireRotate(element, cX, cY, orientation)   
        self.snapToGrid() #Snap rotated component to grid
        self.root.bind("<Key>", self.keyPressedInactive) #Remove binding

    #Draw new image after rotation
    def drawImageAfterRotation(self, cX, cY, orientation, tags):
        addToDict = False #Don't add a new resistor to dict
        orientTotal = 4 #Number of total orientations
        #Delete selected item and replace it with rotated item
        self.canvas.delete(self.dragData['item'])
        if("Resistor" in tags):
            self.drawResistor(cX, cY, (orientation+1)%orientTotal, addToDict)
        elif("Voltage Source" in tags):
            self.drawVoltageSource(cX, cY,
                                   (orientation+1)%orientTotal,
                                   addToDict)
        elif("Wire" in tags):
            self.drawWire(cX, cY, (orientation+1)%orientTotal,
                          addToDict)

    #Reset corner coords of element in rotation operation
    def resetCornerCoords(self, element, cX, cY):
        distTopX, distTopY = element.topX - cX, cY - element.topY
        distBottomX, distBottomY = element.bottomX - cX, cY - element.bottomY
        element.topX = cX + distBottomY
        element.bottomY = cY + distBottomX
        element.bottomX = cX + distTopY
        element.topY = cY + distTopX

    #rotation operation for Wire elements
    def wireRotate(self, element):
        #Determine which side the wire is running along
        xLength = abs(element.topX - element.bottomX)
        yLength = abs(element.topY  - element.bottomY)
        #Offset loss of precision in rotation by adding 1
        startX, endX = -1 -element.imageWidth/2, +element.imageWidth/2 + 1
        newCy = (element.topY + element.bottomY)/2
        newCx = (element.topX + element.bottomX)/2
        element.connectionCoords = []
        if(xLength > yLength): #Laid out horizontally
            for i in xrange(startX, endX):
                element.connectionCoords.append((i + newCx, newCy))
        else: #laid out vertically
            for i in xrange(startX, endX):
                element.connectionCoords.append((newCx, i + newCy))


    #rotation operation for non-Wire elements
    def nonWireRotate(self, element, cX, cY, orientation):
        distInLinkX, distInLinkY = element.inLinkX - cX, cY - element.inLinkY
        distOutLinkX, distOutLinkY = element.outLinkX - cX, cY - element.outLinkY#Changed
        element.inLinkX = cX + distOutLinkY
        element.outLinkY = cY + distOutLinkX
        element.outLinkX = cX + distInLinkY
        element.inLinkY = cY +  distInLinkX
        #Adjust properly for sign changes on even rotations
        if(orientation%2 == 0): 
            element.inLinkX, element.outLinkX = \
                element.outLinkX, element.inLinkX
            element.inLinkY, element.outLinkY = \
                element.outLinkY, element.inLinkY

    #Do nothing if key is pressed while component is not being dragged
    def keyPressedInactive(self, event):
        pass

    #End the dragging of a component
    def onComponentButtonRelease(self, event):
        self.snapToGrid()
        #Reset drag data (Code from Brian Oakley's post)
        self.dragData['item'] = None
        self.dragData['x'] = 0
        self.dragData['y'] = 0
        self.dragData['dataKey'] = None #Original Code
        #Bind Key press so that nothing will happen if "r" is pressed
        self.root.bind("<Key>", self.keyPressedInactive)

    def snapToGrid(self):
        #Fit center of component to intersection of gridlines
        #(ORIGINAL CODE)
        try:
            itemX, itemY = self.canvas.coords(self.dragData['item'])
            #If dragged component would overlap top bar, then delete it, or
            #If dragged component would cover the solve button, delete it.
            topBoundary  = self.lineStartHeight + self.lineStep/2
            if(itemY <= topBoundary or 
                (itemY >= self.solveTopY and itemX <= self.solveTopX)):
                self.canvas.delete(self.dragData['item'])
                del self.circuitElementDict[self.dragData['dataKey']]
            else:
                deltaX, deltaY = itemX % self.lineStep, itemY % self.lineStep
                if(deltaX > self.lineStep / 2):
                    deltaX = self.lineStep - deltaX
                else:
                    deltaX *= -1
                if(deltaY > self.lineStep / 2):
                    deltaY = self.lineStep - deltaY
                else:
                    deltaY *= -1
                deltaX, deltaY = int(deltaX), int(deltaY)
                self.canvas.move(self.dragData['item'], deltaX, deltaY)
                #Adjust element data to reflect the snapping
                self.changeDictLocationData(deltaX, deltaY)
                self.smoothConnectionPoints()
        #Catch error from double clicking and do nothing, as no movement is 
        #Made on a double-click
        except: pass
    

    #Smooth the coords in the dict so that connection points exactly align to
    #intersections of the gridlines (so adjacency map can be generated)
    def smoothConnectionPoints(self):
        element = self.circuitElementDict[self.dragData['dataKey']] #alias
        if(isinstance(element, Wire)): #Only round the non-changing axis
            for i in xrange(len(element.connectionCoords)):
                x, y = element.connectionCoords[i]
                x = self.gridLineRound(x)
                y = self.gridLineRound(y)
                element.connectionCoords[i] = (x, y)
        else:
            element.inLinkX = self.gridLineRound(element.inLinkX)
            element.inLinkY = self.gridLineRound(element.inLinkY)
            element.outLinkX = self.gridLineRound(element.outLinkX)
            element.outLinkY = self.gridLineRound(element.outLinkY)

    def gridLineRound(self, num):
        gridLineStep = 25
        return int(gridLineStep * round(float(num)/gridLineStep))
        
    #Change the location data in the circuitElementDict to match
    #What is displayed on the editor
    def changeDictLocationData(self, deltaX, deltaY):
        #If user deletes component before they drop it on the circuit,
        #It won't be in the dict. Prevent key error w/ if statement.
        if(self.dragData['dataKey'] in self.circuitElementDict):
            element = self.circuitElementDict[self.dragData['dataKey']] #alias
            element.topX += deltaX
            element.bottomX += deltaX
            element.topY += deltaY
            element.bottomY += deltaY
            if(isinstance(element, Wire)):
                for i in xrange(len(element.connectionCoords)):
                    x, y = element.connectionCoords[i]
                    x += deltaX
                    y += deltaY
                    element.connectionCoords[i] = (x, y)
            else: #Not a wire
                element.inLinkX += deltaX
                element.outLinkX += deltaX
                element.inLinkY += deltaY
                element.outLinkY += deltaY

    #Handle the dragging of a component
    def onComponentMotion(self, event):
        #compute how much object has moved
        deltaX = event.x - self.dragData['x']
        deltaY = event.y - self.dragData['y']
        #move the object commensurately
        self.canvas.move(self.dragData['item'], deltaX, deltaY)
        #record new position of object
        self.dragData['x'] = event.x
        self.dragData['y'] = event.y
        deltaX, deltaY = int(deltaX), int(deltaY)
        #Update component object to reflect new coordinates
        self.changeDictLocationData(deltaX, deltaY)
        
    #Load and save images needed for the program
    #Rotation angles are in degrees
    def getImageAssets(self):
        resistorFile = "Resistor.png"
        resistorImage = Image.open(resistorFile)
        self.resistorImages = [ImageTk.PhotoImage(resistorImage),
                               ImageTk.PhotoImage(resistorImage.rotate(90)),
                               ImageTk.PhotoImage(resistorImage.rotate(180)),
                               ImageTk.PhotoImage(resistorImage.rotate(270))]
        voltageFile= "Voltage Source.png"
        voltageImage = Image.open(voltageFile)
        self.voltageImages = [ImageTk.PhotoImage(voltageImage),
                               ImageTk.PhotoImage(voltageImage.rotate(90)),
                               ImageTk.PhotoImage(voltageImage.rotate(180)),
                               ImageTk.PhotoImage(voltageImage.rotate(270))]
        wireFile = "Wire.png"
        wireImage = Image.open(wireFile)
        self.wireImages = [ImageTk.PhotoImage(wireImage),
                               ImageTk.PhotoImage(wireImage.rotate(90)),
                               ImageTk.PhotoImage(wireImage.rotate(180)),
                               ImageTk.PhotoImage(wireImage.rotate(270))]

    def drawWire(self, X, Y, orientation = 0, create = True):
        self.canvas.create_image(X, Y, image = self.wireImages[orientation],
                                 tags = ("component", "Wire", orientation),
                                 anchor = CENTER)
        if(create == True):
            newWire = Wire(X, Y)
            self.circuitElementDict[newWire.name] = newWire
    
    def drawVoltageSource(self, X, Y, orientation = 0, create = True):
        self.canvas.create_image(X, Y, image=self.voltageImages[orientation],
                            tags = ("component", "Voltage Source", orientation),
                            anchor = CENTER)
        if(create == True):
            defaultVoltage = 1.0#1 Volt (float)
            newVoltageSource = VoltageSource(defaultVoltage, X, Y) #Default: DC source of 1V
            self.circuitElementDict[newVoltageSource.name] = newVoltageSource
        
    def drawResistor(self, X, Y, orientation = 0, create = True):
        #Image is a partially-transparent PNG to preserve gridlines
        self.canvas.create_image(X, Y, image=self.resistorImages[orientation],
                                 tags = ("component", "Resistor", orientation),
                                 anchor = CENTER)
        #Create new resistor with default value of 1 kilohm
        if(create == True):
            defaultResistance = 1000.0 #1 kilohm (float)
            newResistor = Resistor(defaultResistance, X, Y)
            self.circuitElementDict[newResistor.name] = newResistor
        
    #Draw gridlines to control placement of elements
    def drawGridLines(self):
        #set background color to white
        self.lineStartHeight = 100
        self.canvas.create_rectangle(0, 0, self.width, self.height,
                                fill = "white", outline = "white")
        self.lineStep = 25
        lineColor = "#bebebe"
        for row in xrange(0, self.width, self.lineStep):
            self.canvas.create_line(row, self.lineStartHeight,
                                    row, self.height, fill=lineColor)
        for col in xrange(self.lineStartHeight, self.height, self.lineStep):
            self.canvas.create_line(0, col, self.width, col, fill=lineColor)
