#This class creates a start screen where the user can select the window size,
#And then launch the circuit editor
from MainGUI import MainGUI
from Tkinter import *

class StartScreen(object):
    def __init__(self):
        #Fixed height and width
        self.width = 300
        self.height = 300
        
    def run(self):
        self.root = Tk()
        self.root.wm_title("Start Screen")
        self.canvas = Canvas(self.root, width=self.width, height = self.height)
        self.canvas.pack()
        self.root.resizable(width = 0, height = 0)
        self.drawStartScreen() #Draw elements on canvas
        self.root.mainloop()

    #Place information on startScreen
    def drawStartScreen(self):
        self.drawIntroText()
        self.drawButtons()

    #Display introduction to the end user
    def drawIntroText(self):
        self.screenWidth = self.canvas.winfo_screenwidth()
        self.screenHeight = self.canvas.winfo_screenheight()
        textX, textY = self.width/2, 35
        messageFont = "Helvetica 13"
        introString = "Welcome to the super circuit solver!\n"
        introString += "Pick your desired window size:\n"
        introString +="(Your screen resolution is %dx%d)"\
                       %(self.screenWidth, self.screenHeight)
        self.canvas.create_text(textX, textY, text = introString,
                           font = messageFont)

    def drawButtons(self):
        buttonWidth = 40
        buttonHeightOffset = 100
        buttonHeightDifference = 30
        smallCaption = "Small (600px-by-400px)"
        smallButton = self.generateSizeButton(smallCaption, self.smallPressed)
        smallButton_window = self.canvas.create_window(self.width/2,
                                     buttonHeightOffset, window = smallButton)
        #Only draw medium button if screen resolution can support it
        if(self.screenWidth > 900 and self.screenHeight > 600):
            buttonHeightOffset += buttonHeightDifference
            mediumCaption = "Medium (900px-by-600px)"
            mediumButton = self.generateSizeButton(mediumCaption,
                                                   self.mediumPressed)
            mediumButton_window = self.canvas.create_window(self.width/2,
                                    buttonHeightOffset, window = mediumButton)
        #Only draw large button if screen resolution can support it
        if(self.screenWidth > 1200 and self.screenHeight > 800):
            buttonHeightOffset += buttonHeightDifference
            largeCaption = "Large (1200px-by-800px)"
            largeButton = self.generateSizeButton(largeCaption,
                                                  self.largePressed)
            largeButton_window = self.canvas.create_window(self.width/2,
                                    buttonHeightOffset, window = largeButton)
        #Only draw XL Button if screen resolution can support it
        if(self.screenWidth > 1500 and self.screenHeight > 1000):
            buttonHeightOffset += buttonHeightDifference
            XLCaption = "XL (1500px-by-1000px)"
            XLButton = self.generateSizeButton(XLCaption, self.XLPressed)
            XLButton_window = self.canvas.create_window(self.width/2,
                                    buttonHeightOffset, window = XLButton)

    #Generate and return a button to select window size
    def generateSizeButton(self, caption, command):
        buttonWidth = 40
        return Button(self.root, text=caption, command=command, bg= "white",
                      width = buttonWidth, relief = GROOVE)

    #Exit start screen and open circuit solver
    def startSolver(self, width, height):
        self.root.destroy()
        gui = MainGUI(width, height)
        gui.run()

    #Create a small window whenever corresponding button is pressed
    def smallPressed(self):
        width, height = 600, 400 #pixels
        self.startSolver(width, height)

    #Create a medium window whenever corresponding button is pressed
    def mediumPressed(self):
        width, height = 900, 600 #pixels
        self.startSolver(width, height)

    #Create a large window whenever corresponding button is pressed
    def largePressed(self):
        width, height = 1200, 800 #pixels
        self.startSolver(width, height)

    #Create an extra large window whenever corresponding button is pressed
    def XLPressed(self):
        width, height = 1500, 1000 #pixels
        self.startSolver(width, height)

screen = StartScreen()
screen.run()
