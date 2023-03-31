import argparse
import xml.etree.ElementTree as ET
from interpretClasses import Instruction, Frame, Error


class Interpret:
    
    def __init__(self):
        
        self.error = Error.Error()
        self.frame = {"GF": Frame.Frame(), "LF": Frame.Frame(), "TF": Frame.Frame()}
        # self.GF = Frame.Frame()
        # self.LF = Frame.Frame()
        # self.TF = Frame.Frame()
        self.frameStack = list()
        self.dataStack = list()
        self.listInstuction = list()
        
        self.XMLfile = None
        self.inputData = None
        self.XMLtree = None
        
    def parseArguments(self):
        
        parser = argparse.ArgumentParser(description="XML interpreter")
        parser.add_argument("--source", help = "file XML")
        parser.add_argument("--input", help = "file for input")
        parametrs = parser.parse_args()
        
        self.XMLfile = input() if parametrs.source == None else parametrs.source
        self.inputData = input() if parametrs.input == None else parametrs.input

        try:
            # root = ET.parse(XMLfile).getroot()
            self.XMLtree = ET.parse("in.xml").getroot()
        except FileNotFoundError:
            self.error.printError(11)
        except Exception as e:
            self.error.printError(31)
            
    def XMLtoInstr(self):
        
        if self.root.tag != "program":
            self.error.printErr(32)
        
        if not("language" in self.root.attrib):
            self.error.printErr(32)
            
        if self.root.attrib['language'].upper() != "IPPCODE23":
            self.error.printErr(32)
            
        listLabel = list()
        # orderInstr = 0
        for instruction in self.root:
    
            if instruction.tag != "instruction":
                self.error.printErr(32)
                
            if 'order' not in instruction.attrib:
                self.error.printErr(32)
                
            if not (instruction.attrib['order'].isnumeric()):
                self.error.printErr(32)
                
            if int(instruction.attrib['order']) < 1:
                self.error.printErr(32)
                
            if 'opcode' not in instruction.attrib:
                self.error.printErr(32)
            
            argOrder = 0
            for arg in instruction:
                argOrder += 1
                
                if arg.tag != "arg"+str(argOrder):
                    self.error.printErr(32)
                    
                if 'type' not in arg.attrib:
                    self.error.printErr(32)
                    
                if arg.attrib['type'] not in  ["var", "string", "int", "nil", "label", "type", "bool"]:
                    self.error.printErr(32)
                
                if instruction.attrib['opcode'] == "LABEL":
                    if arg.text in listLabel:
                        self.error.printErr(52)
                    self.listLabel.append(str(arg.text))
                    
            instr = Instruction.Instruction(instruction.attrib['opcode'], instruction)
            self.listInstuction.append([int(instruction.attrib['order']), instr])
            # orderInstr += 1
            
        def sortByOrder(elem):
            return elem[0]

        self.listInstuction.sort(key=sortByOrder)

        prevIndex = -1
        for order in self.listInstuction:
            if int(order[0]) == prevIndex:
                self.error.printErr(32)
            prevIndex = int(order[0])
            
    def interpreting(self):
        
        order = 0
        returnPoint = list()
        
        while order < len(self.listInstuction):
            instr = self.listInstuction[order][1]
            order += 1
            
            match instr.opcode:
                
                case "MOVE":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    self.frame[frameVar].set(nameVar, valueSymb1, typeSymb1)
                    
                case "CREATEFRAME":
                    self.frame["TF"].definiteTemporaryFrame()
                    
                case "PUSHFRAME":
                    if self.frame["TF"].definition:
                        self.frameStack.append(self.frame["TF"].copy())
                        self.frame["TF"].clean()
                    else:
                        self.error.printError(55)
                        
                case "POPFRAME":
                    try:
                        self.frame["TF"].fill(self.frame["LF"].pop())
                    except:
                        self.error.printError(55)

                case "DEFVAR":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    if self.frame[frameVar].newVar(nameVar):
                        self.error.printError(55)
                    
                case "CALL":
                    returnPoint.append(order)
                    
                    for i in self.listInstuction:
                        if i[1].opcode == "LABEL":
                            if i[1].arg1['text'] == instr.arg1['text']:
                                order = self.listInstuction.index(i)
                                
                case "RETURN":
                    order = returnPoint.pop()
                    
                case "PUSHS":
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg1)
                    self.dataStack.append([valueSymb1, typeSymb1])
                    
                case "POPS":
                    if self.dataStack:
                        popData = self.dataStack.pop()
                        frameVar, nameVar = self.__splitting(instr.arg1['text'])
                        self.frame[frameVar].set(nameVar, popData[0], popData[1])
                    else:
                        self.error.printError(56)
                        
                
                
                case other:
                    self.error.printErr(32)
                    
    def __workSymb(self, argument):
        if argument['type'] == "var":
            
            frameSymb, nameSymb = self.__splitting(argument['text'])
            frame = self.frame[frameSymb]
            
            try:
                return frame.get(nameSymb)
            except:
                self.error.printError(55)
        
        else:
            return argument['text'], argument['type']
        
        
    def __splitting(self, text):
        try:
            frame, name = text.split('@')
        except:
            self.error.printError(55)
            
        return frame, name