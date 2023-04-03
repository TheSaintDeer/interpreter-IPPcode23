import argparse
import xml.etree.ElementTree as ET
import re
import copy
from interpretClasses.Instruction import Instruction
from interpretClasses.Frame import Frame
from interpretClasses.Error import Error


class Interpret:
    
    def __init__(self):
        
        self.error = Error()
        self.frame = {"GF": Frame(), "LF": Frame(), "TF": Frame()}
        self.frame["GF"].definiteTemporaryFrame()
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
        
        # self.XMLfile = input() if parametrs.source == None else parametrs.source
        # self.inputData = input() if parametrs.input == None else parametrs.input

        try:
            # self.XMLtree = ET.parse(XMLfile).getroot()
            self.XMLtree = ET.parse("in.xml").getroot()
        except FileNotFoundError:
            self.error.printError(11)
        except Exception as e:
            self.error.printError(31)
            
    def XMLtoInstr(self):
        
        if self.XMLtree.tag != "program":
            self.error.printError(32)
        
        if not("language" in self.XMLtree.attrib):
            self.error.printError(32)
            
        if self.XMLtree.attrib['language'].upper() != "IPPCODE23":
            self.error.printError(32)
            
        listLabel = list()
        # orderInstr = 0
        for instruction in self.XMLtree:
    
            if instruction.tag != "instruction":
                self.error.printError(32)
                
            if 'order' not in instruction.attrib:
                self.error.printError(32)
                
            if not (instruction.attrib['order'].isnumeric()):
                self.error.printError(32)
                
            if int(instruction.attrib['order']) < 1:
                self.error.printError(32)
                
            if 'opcode' not in instruction.attrib:
                self.error.printError(32)
            
            argOrder = 0
            for arg in instruction:
                argOrder += 1
                
                if arg.tag != "arg"+str(argOrder):
                    self.error.printError(32)
                    
                if 'type' not in arg.attrib:
                    self.error.printError(32)
                    
                if arg.attrib['type'] not in  ["var", "string", "int", "nil", "label", "type", "bool"]:
                    self.error.printError(32)
                
                if instruction.attrib['opcode'] == "LABEL":
                    if arg.text in listLabel:
                        self.error.printError(52)
                    self.listLabel.append(str(arg.text))
                    
            instr = Instruction(instruction.attrib['opcode'], instruction)
            self.listInstuction.append([int(instruction.attrib['order']), instr])
            # orderInstr += 1
            
        def sortByOrder(elem):
            return elem[0]

        self.listInstuction.sort(key=sortByOrder)

        prevIndex = -1
        for order in self.listInstuction:
            if int(order[0]) == prevIndex:
                self.error.printError(32)
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
                        if self.frame["LF"].definition:
                            self.frameStack.append(self.frame["LF"])
                        self.frame["LF"] = self.frame["TF"]
                        self.frame["TF"] = Frame()
                    else:
                        self.error.printError(55)
                        
                case "POPFRAME":
                    try:
                        self.frame["TF"] = self.frame["LF"]
                        self.frame["LF"] = self.frameStack.pop()
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
                        
                case "ADD":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 != typeSymb2 or typeSymb1 not in ["nil", "int"]:
                        self.error.printError(53)
                        
                    try:
                        result = int(valueSymb1) + int(valueSymb2)
                    except:
                        self.error.printError(32)

                    self.frame[frameVar].set(nameVar, str(result), "int")

                case "SUB":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 != typeSymb2 or typeSymb1 not in ["nil", "int"]:
                        self.error.printError(53)

                    try:
                        result = int(valueSymb1) - int(valueSymb2)
                    except:
                        self.error.printError(32)

                    self.frame[frameVar].set(nameVar, str(result), "int")
                    
                case "MUL":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 != typeSymb2 or typeSymb1 not in ["nil", "int"]:
                        self.error.printError(53)

                    try:
                        result = int(valueSymb1) * int(valueSymb2)
                    except:
                        self.error.printError(32)

                    self.frame[frameVar].set(nameVar, str(result), "int")
                
                case "IDIV":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 != typeSymb2 or typeSymb1 not in ["nil", "int"]:
                        self.error.printError(53)

                    if valueSymb2 == "0":
                        self.error.printError(57)

                    try:
                        result = int(int(valueSymb1) / int(valueSymb2))
                    except:
                        self.error.printError(32)

                    self.frame[frameVar].set(nameVar, str(result), "int")

                case "LT":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if "nil" in [valueSymb1, valueSymb2]:
                        self.error.printError(53)

                    if typeSymb1 == typeSymb2 and typeSymb1 in ["int", "string", "bool"]:
                        result = "true" if valueSymb1 < valueSymb2 else "false"
                        self.frame[frameVar].set(nameVar, str(result), "int")

                case "GT":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if "nil" in [valueSymb1, valueSymb2]:
                        self.error.printError(53)

                    if typeSymb1 == typeSymb2 and typeSymb1 in ["int", "string", "bool"]:
                        result = "true" if valueSymb1 > valueSymb2 else "false"
                        self.frame[frameVar].set(nameVar, str(result), "int")
                        
                case "EQ":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 == typeSymb2 and typeSymb1 in ["int", "string", "bool", "nil"]:
                        result = "true" if valueSymb1 < valueSymb2 else "false"
                        self.frame[frameVar].set(nameVar, str(result), "int")

                case "AND":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    condition1 = True if valueSymb1 == "true" else False
                    condition2 = True if valueSymb2 == "true" else False

                    result = condition1 and condition2
                    self.frame[frameVar].set(nameVar, str(result), "bool")

                case "OR":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    condition1 = True if valueSymb1 == "true" else False
                    condition2 = True if valueSymb2 == "true" else False

                    result = condition1 or condition2
                    self.frame[frameVar].set(nameVar, str(result), "bool")

                case "NOT":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)

                    condition1 = True if valueSymb1 == "true" else False

                    result = not condition1
                    self.frame[frameVar].set(nameVar, str(result), "bool")

                case "INT2CHAR":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    
                    if typeSymb1 != "int":
                        self.error.printError(53)

                    try:
                        self.frame[frameVar].set(nameVar, str(int(valueSymb1)), "string")
                    except:
                        self.error.printError(58)

                case "STRI2INT":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)
                    
                    if typeSymb1 != "string" or typeSymb2 != "int":
                        self.error.printError(53)

                    if int(valueSymb2) >= len(valueSymb1) or int(valueSymb2) < 0:
                        exit(58)

                    result = valueSymb1[int(valueSymb2)]
                    self.frame[frameVar].set(nameVar, ord(result), "int")


                case "READ":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    # if self.inputData:
                    #     readValue = self.inputData.readline()
                    #     readValue = readValue.strip()
                    # else:
                    readValue = input()
                        
                    self.frame[frameVar].set(nameVar, readValue, instr.arg2['text'])
                    
                case "WRITE":
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg1)
                    
                    valueSymb1 = re.sub(r"\\032", " ", valueSymb1)
                    valueSymb1 = re.sub(r"\\035", "#", valueSymb1)
                    valueSymb1 = re.sub(r"\\092", "\\\\", valueSymb1)
                    valueSymb1 = re.sub(r"\\010", "\\n", valueSymb1)

                    if not(valueSymb1 == "nil"):
                        print(valueSymb1, end="")
                        
                case "CONCAT":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)
                    
                    if typeSymb1 != typeSymb2 != "string":
                        self.error.printError(53)
                    
                    self.frame[frameVar].set(nameVar, valueSymb1+valueSymb2, "string")
                    
                case "STRLEN":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    
                    self.frame[frameVar].set(nameVar, str(len(valueSymb1)), "int")
                    
                case "GETCHAR":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    self.frame[frameVar].set(nameVar, valueSymb1[int(valueSymb2)], "string")
                    
                case "SETCHAR":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    newValue, newType = self.frame[frameVar].get(nameVar)
                    newValue[int(valueSymb1)] = valueSymb2
                    self.frame[frameVar].set(nameVar, newValue, newType)
                    
                case "TYPE":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    
                    self.frame[frameVar].set(nameVar, valueSymb1, "type")
                    
                case "LABEL":
                    pass
                
                case "JUMP":
                    for i in self.listInstuction:
                        if i[1].opcode == "LABEL":
                            if i[1].arg1['text'] == instr.arg1['text']:
                                order = self.listInstuction.index(i)
                    self.error.printError(52)
                                
                case "JUMPIFEQ":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 != typeSymb2 or "nil" in [typeSymb1, typeSymb2]:
                        self.error.printError(53) 
                    
                    if valueSymb1 == valueSymb2:
                        for i in self.listInstuction:
                            if i[1].opcode == "LABEL":
                                if i[1].arg1['text'] == instr.arg1['text']:
                                    order = self.listInstuction.index(i)
                        self.error.printError(52)
                                    
                case "JUMPIFNEQ":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)
                    
                    if typeSymb1 != typeSymb2 or "nil" in [typeSymb1, typeSymb2]:
                        self.error.printError(53) 
                    
                    if valueSymb1 != valueSymb2:
                        for i in self.listInstuction:
                            if i[1].opcode == "LABEL":
                                if i[1].arg1['text'] == instr.arg1['text']:
                                    order = self.listInstuction.index(i)
                        self.error.printError(52)
                                    
                case "EXIT":
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg1)
                    
                    if typeSymb1 == "":
                        exit(56)    

                    if typeSymb1 != "int":
                        exit(53)

                    if int(valueSymb1) < 0 or int(valueSymb1) > 49:
                        exit(57)

                    exit(int(valueSymb1))
                    
                case other:
                    self.error.printError(32)
                    
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