'''
Luke Metro - lmetro - 15-112 Term Project - Section B

Editor.py

Using a component object as input, this class will generate a popup that will
enable the user to edit the value of a component.
(i.e. Resistance & Voltage)
'''
from Tkinter import *
from ComponentClasses import *
import tkMessageBox

class Editor(object):

    def __init__(self, component, parent):
        self.component = component
        self.parent = parent

    #Create popup that user can use to edit the value of selected component
    def displayPopup(self):
        if(isinstance(self.component, Resistor)):
            self.displayResistorPopup()
        elif(isinstance(self.component, VoltageSource)):
            self.displayVoltageSourcePopup()

    def displayResistorPopup(self):
        resistance = originalResistance = self.component.resistance
        prefix, resistance = self.getPrefixAndAdjustValue(resistance)
        text = "  %s has a resistance of %.2f %sohms  " % (self.component.name,
            resistance, prefix)
        text +="\n Input new value below (in Ohms):  "
        newValue = self.getComponentValue(text)
        #If user doesn't enter input, getComponentValue returns None
        if(isinstance(newValue, float)):
            self.component.resistance = newValue

    def displayVoltageSourcePopup(self):
        voltage = originalVoltage = self.component.voltage
        prefix, voltage = self.getPrefixAndAdjustValue(voltage)
        text = "  Voltage across %s is %.2f %svolts  " % (self.component.name,
            voltage, prefix)
        text += "\n  Input new value below (in Volts):  "
        newValue = self.getComponentValue(text)
        #If user doesn't enter input, getComponentValue returns None
        if(isinstance(newValue, float)):
            self.component.voltage = newValue

    #Create popup to get a floating-point number value, check its
    #validity (make sure it's an actual number) and return it
    def getComponentValue(self, message):
        self.message = message #So that message can be used in submit method
        self.window = Toplevel(self.parent)
        Label(self.window, text=message).pack()
        self.field = Entry(self.window)
        self.field.pack()
        OK = Button(self.window, text = "OK", command = self.submit)
        OK.pack()
        self.parent.wait_window(self.window)#Blocking call
        try:
            if(self.returnValue != 0):
                return self.returnValue
            else:
                tkMessageBox.showerror("Invalid Input", "You cannot have a "+
                    "value of 0!\n(PROTIP: Use a wire instead.)")
        except: #User closes out of input window
            return None

#Define function to collect input
    def submit(self):
        value = self.field.get()
        try:
            value = float(value)
            self.window.destroy() #Close popup
            self.returnValue = value
        except: #User enters non-numeric input
            self.window.destroy() #Close popup
            tkMessageBox.showerror("Invalid Input", 
                "You did not input a valid number.")
            #Recursively call function until user enters valid input
            self.getComponentValue(self.message)

    #Return the prefix to reduce number to 3 nondecimal digits
    #And adjust number to display accordingly
    def getPrefixAndAdjustValue(self, value):
        #Micro is the minimum supported prefix
        #Input will not be accepted below microamps/volts, so
        #Lower prefixes are unneccesary
        if(10**(-6) <= abs(value) < 10**(-3)):
            prefix = "micro"
            value /= 10.0**(-6)
        elif(abs(value) < 10.0**0):
            prefix = "milli"
            value /= 10.0**(-3)
        elif(abs(value) < 10**3):
            prefix = "" #no prefix
            #Don't change value
        elif(abs(value) < 10**6):
            prefix = "kilo"
            value /= 10.0**3
        elif(abs(value) < 10**9):
            prefix = "mega"
            value /= 10.0**6
        #Maximum supported prefix is Mega-
        #Input will not be accepted above the Megaamp/Megavolt level,
        #So higher prefixes are unneccesary
        return prefix, value



