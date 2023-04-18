# Implementační dokumentace k 2. úloze do IPP 2022/2023
# Jméno a příjmení: Ivan Golikov
# Login: xgolik00

import argparse
import xml.etree.ElementTree as ET
import re
from interpretClasses.Instruction import Instruction
from interpretClasses.Frame import Frame
import sys


class Interpret:
    
    def __init__(self):
        
        self.frame = {"GF": Frame(), "LF": Frame(), "TF": Frame()}
        self.frame["GF"].definiteTemporaryFrame()
        self.frameStack = list()
        self.dataStack = list()
        self.listInstuction = list()
        
        self.XMLfile = None
        self.inputData = None
        self.XMLtree = None

        self.stats = None
        self.maxCountVar = 0
        
    def parseArguments(self):
        
        parser = argparse.ArgumentParser(description="XML interpreter")
        parser.add_argument("--source", help = "file XML")
        parser.add_argument("--input", help = "file for input")
        parser.add_argument("--stats", help = "file for input")
        parser.add_argument("--insts", help = "count instruction", nargs='?')
        parser.add_argument("--eol", help = "end of line", nargs='?')
        parser.add_argument("--print", help = "write to statistic")
        parser.add_argument("--vars", help = "maximum number of initialized variables", nargs='?')
        parser.add_argument("--hot", help = "the most frequently used instruction", nargs='?')
        parametrs = parser.parse_args()
        
        self.XMLfile = parametrs.source if parametrs.source else input()
        self.inputData = open(parametrs.input, "r") if parametrs.input else None
        self.stats = open(parametrs.stats, "w") if parametrs.stats else None

        try:
            self.XMLtree = ET.parse(self.XMLfile).getroot()
        except FileNotFoundError:
            exit(11)
        except Exception as e:
            exit(31)
            
    def XMLtoInstr(self):
        
        if self.XMLtree.tag != "program":
            exit(32)
        
        if not("language" in self.XMLtree.attrib):
            exit(32)
            
        if self.XMLtree.attrib['language'].upper() != "IPPCODE23":
            exit(32)
            
        listLabel = list()
        for instruction in self.XMLtree:
    
            if instruction.tag != "instruction":
                exit(32)
                
            if 'order' not in instruction.attrib:
                exit(32)
                
            if not (instruction.attrib['order'].isnumeric()):
                exit(32)
                
            if int(instruction.attrib['order']) < 1:
                exit(32)
                
            if 'opcode' not in instruction.attrib:
                exit(32)
            
            instr = Instruction(instruction.attrib['opcode'])
            for arg in instruction:
                if 'type' not in arg.attrib:
                    exit(32)
                    
                if arg.attrib['type'] not in  ["var", "string", "int", "nil", "label", "type", "bool", "float"]:
                    exit(32)
                
                if instruction.attrib['opcode'] == "LABEL":
                    if arg.text in listLabel:
                        exit(52)
                    listLabel.append(str(arg.text))
                    
                instr.setArg(arg)
                    
            try:
                instr.controlArg()
            except:
                exit(32)
                
            self.listInstuction.append([int(instruction.attrib['order']), instr])
            
        # function for sorting
        def sortByOrder(elem):
            return elem[0]

        self.listInstuction.sort(key=sortByOrder)

        # check for duplicate order number
        prevIndex = -1
        for order in self.listInstuction:
            if int(order[0]) == prevIndex:
                exit(32)
            prevIndex = int(order[0])
            
    def interpreting(self):
        
        order = 0
        returnPoint = list()
        currentCountVar = 0
        
        while order < len(self.listInstuction):
            instr = self.listInstuction[order][1]
            instr.incrementUses()
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
                        exit(55)
                        
                case "POPFRAME":
                    if self.frame["TF"].definition:
                        currentCountVar -= len(self.frame["TF"].frame)
                    
                    if self.frame["LF"].definition:
                        self.frame["TF"] = self.frame["LF"]
                    else:
                        exit(55)
                    
                    if self.frameStack:
                        self.frame["LF"] = self.frameStack.pop()
                    else:
                        self.frame["LF"] = Frame()

                case "DEFVAR":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    self.frame[frameVar].newVar(nameVar)
                    
                    currentCountVar += 1
                    self.maxCountVar = currentCountVar if currentCountVar > self.maxCountVar else self.maxCountVar
                    
                case "CALL":
                    returnPoint.append(order)
                    
                    found = False
                    for i in self.listInstuction:
                        if i[1].opcode == "LABEL":
                            if i[1].arg1['text'] == instr.arg1['text']:
                                order = self.listInstuction.index(i)
                                found = True
                                break
                    if not found:
                        exit(52)
                        
                case "RETURN":
                    try:
                        order = returnPoint.pop()
                    except:
                        exit(56)
                        
                case "PUSHS":
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg1)
                    self.dataStack.append([valueSymb1, typeSymb1])
                    
                case "POPS":
                    if self.dataStack:
                        popData = self.dataStack.pop()
                        frameVar, nameVar = self.__splitting(instr.arg1['text'])
                        self.frame[frameVar].set(nameVar, popData[0], popData[1])
                    else:
                        exit(56)
                        
                case "ADD":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 != typeSymb2 or typeSymb1 not in ["int", "float"]:
                        exit(53)
                        
                    if "float" in [typeSymb1, typeSymb2]:
                        try:
                            result = float(valueSymb1) + float(valueSymb2)
                        except:
                            exit(53)
                        self.frame[frameVar].set(nameVar, str(result), "float")
                    else:
                        try:
                            result = int(valueSymb1) + int(valueSymb2)
                        except:
                            exit(53)
                        self.frame[frameVar].set(nameVar, str(result), "int")

                case "SUB":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 != typeSymb2 or typeSymb1 not in ["int", "float"]:
                        exit(53)

                    if "float" in [typeSymb1, typeSymb2]:
                        try:
                            result = float(valueSymb1) - float(valueSymb2)
                        except:
                            exit(53)
                        self.frame[frameVar].set(nameVar, str(result), "float")
                    else:
                        try:
                            result = int(valueSymb1) - int(valueSymb2)
                        except:
                            exit(53)
                        self.frame[frameVar].set(nameVar, str(result), "int")
                    
                case "MUL":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 != typeSymb2 or typeSymb1 not in ["int", "float"]:
                        exit(53)

                    if "float" in [typeSymb1, typeSymb2]:
                        try:
                            result = float(valueSymb1) * float(valueSymb2)
                        except:
                            exit(53)
                        self.frame[frameVar].set(nameVar, str(result), "float")
                    else:
                        try:
                            result = int(valueSymb1) * int(valueSymb2)
                        except:
                            exit(53)
                        self.frame[frameVar].set(nameVar, str(result), "int")
                
                case "IDIV":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 != typeSymb2 or typeSymb1 not in ["int", "float"]:
                        exit(53)

                    if int(valueSymb2) == 0:
                        exit(57)

                    if "float" in [typeSymb1, typeSymb2]:
                        try:
                            result = int(float(valueSymb1) / float(valueSymb2))
                        except:
                            exit(53)
                        self.frame[frameVar].set(nameVar, str(result), "int")
                    else:
                        try:
                            result = int(int(valueSymb1) / int(valueSymb2))
                        except:
                            exit(53)
                        self.frame[frameVar].set(nameVar, str(result), "int")

                case "LT":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 == typeSymb2 and typeSymb1 in ["int", "string", "bool", "float"]:
                        result = "true" if valueSymb1 < valueSymb2 else "false"
                        self.frame[frameVar].set(nameVar, result, "bool")
                    else:
                        exit(53)

                case "GT":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 == typeSymb2 and typeSymb1 in ["int", "string", "bool", "float"]:
                        result = "true" if valueSymb1 > valueSymb2 else "false"
                        self.frame[frameVar].set(nameVar, result, "bool")
                    else:
                        exit(53)

                case "EQ":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 == typeSymb2 and typeSymb1 in ["int", "string", "bool", "float"] or "nil" in [typeSymb1, typeSymb2]:
                        result = "true" if valueSymb1 == valueSymb2 else "false"
                        self.frame[frameVar].set(nameVar, result, "bool")
                    else:
                        exit(53)

                case "AND":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 != "bool" or typeSymb2 != "bool":
                        exit(53)

                    condition1 = True if valueSymb1 == "true" else False
                    condition2 = True if valueSymb2 == "true" else False

                    result = condition1 and condition2
                    self.frame[frameVar].set(nameVar, str(result).lower(), "bool")

                case "OR":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 != "bool" or typeSymb2 != "bool":
                        exit(53)

                    condition1 = True if valueSymb1 == "true" else False
                    condition2 = True if valueSymb2 == "true" else False

                    result = condition1 or condition2
                    self.frame[frameVar].set(nameVar, str(result).lower(), "bool")

                case "NOT":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)

                    if typeSymb1 != "bool":
                        exit(53)

                    condition1 = True if valueSymb1 == "true" else False

                    result = not condition1
                    self.frame[frameVar].set(nameVar, str(result).lower(), "bool")

                case "INT2CHAR":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    
                    if typeSymb1 != "int":
                        exit(53)

                    try:
                        self.frame[frameVar].set(nameVar, chr(int(valueSymb1)), "string")
                    except:
                        exit(58)

                case "STRI2INT":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)
                    
                    if typeSymb1 != "string" or typeSymb2 != "int":
                        exit(53)

                    if int(valueSymb2) >= len(valueSymb1) or int(valueSymb2) < 0:
                        exit(58)

                    result = valueSymb1[int(valueSymb2)]
                    self.frame[frameVar].set(nameVar, ord(result), "int")

                case "READ":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    typeVar = instr.arg2['text']
                    
                    if typeVar not in ["int", "float", "string", "bool"]:
                        exit(32)
                    
                    if self.inputData:
                        readValue = self.inputData.readline()
                        readValue = readValue.strip()
                    else:
                        readValue = input()
                        
                    if typeVar == "bool":
                        if readValue == "":
                            readValue = ""
                        elif readValue.lower() == "true":
                            readValue = "true"
                        else:
                            readValue = "false"
                            
                    if typeVar == "int":
                        try:
                            int(readValue)
                        except:
                            if not (readValue == ""):
                                readValue = ""
                            
                    if typeVar == "float":
                        try:
                            readValue = str(float.fromhex(readValue))
                        except:
                            if not (readValue == ""):
                                readValue = ""
                        
                    self.frame[frameVar].set(nameVar, readValue, typeVar)
                    
                case "WRITE":
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg1)
                    
                    if valueSymb1 != "":
                    
                        if typeSymb1 == "string":
                            valueSymb1 = re.sub(r"\\032", " ", valueSymb1)
                            valueSymb1 = re.sub(r"\\035", "#", valueSymb1)
                            valueSymb1 = re.sub(r"\\092", "\\\\", valueSymb1)
                            valueSymb1 = re.sub(r"\\010", "\\n", valueSymb1)
                            
                        if typeSymb1 == "float":
                            valueSymb1 = str(float.hex(float(valueSymb1)))

                        if not(typeSymb1 in ["nil", None]):
                            print(valueSymb1, end="")
                        
                case "CONCAT":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)
                    
                    if typeSymb1 != "string":
                        exit(53)
                    
                    if typeSymb2 != "string":
                        exit(53)
                        
                    self.frame[frameVar].set(nameVar, valueSymb1+valueSymb2, "string")
                    
                case "STRLEN":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    
                    if typeSymb1 != "string":
                        exit(53)
                    
                    self.frame[frameVar].set(nameVar, str(len(valueSymb1)), "int")
                    
                case "GETCHAR":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)
                    
                    if typeSymb1 != "string":
                        exit(53)
                        
                    if typeSymb2 != "int":
                        exit(53)
                        
                    if len(typeSymb1) <= int(valueSymb2):
                        exit(58) 
                        
                    self.frame[frameVar].set(nameVar, valueSymb1[int(valueSymb2)], "string")
                    
                case "SETCHAR":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)
                    
                    if typeSymb1 != "int":
                        exit(53)
                        
                    if typeSymb2 != "string":
                        exit(53)
                        
                    newValue, newType = self.frame[frameVar].get(nameVar)
                    
                    if len(newValue) <= int(valueSymb1):
                        exit(58) 
                        
                    newValue = list(newValue)
                    newValue[int(valueSymb1)] = valueSymb2
                    newValue = "".join(newValue)
                    self.frame[frameVar].set(nameVar, newValue, newType)
                    
                case "TYPE":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    
                    self.frame[frameVar].set(nameVar, typeSymb1, "type")
                    
                case "LABEL":
                    pass
                
                case "JUMP":
                    found = False
                    for i in self.listInstuction:
                        if i[1].opcode == "LABEL":
                            if i[1].arg1['text'] == instr.arg1['text']:
                                order = self.listInstuction.index(i)
                                found = True
                                break
                    if not found:
                        exit(52)
                                
                case "JUMPIFEQ":
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 != typeSymb2 and "nil" not in [typeSymb1, typeSymb2]:
                        exit(53) 
                    
                    if valueSymb1 == valueSymb2:
                        found = False
                        for i in self.listInstuction:
                            if i[1].opcode == "LABEL":
                                if i[1].arg1['text'] == instr.arg1['text']:
                                    order = self.listInstuction.index(i)
                                    found = True
                                    break
                        if not found:
                            exit(52)
                                    
                case "JUMPIFNEQ":
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)
                    
                    if typeSymb1 != typeSymb2 and "nil" not in [typeSymb1, typeSymb2]:
                        exit(53) 
                    
                    if valueSymb1 != valueSymb2:
                        found = False
                        for i in self.listInstuction:
                            if i[1].opcode == "LABEL":
                                if i[1].arg1['text'] == instr.arg1['text']:
                                    order = self.listInstuction.index(i)
                                    found = True
                                    break
                        if not found:
                            exit(52)
                                    
                case "EXIT":
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg1)
                    
                    if typeSymb1 == "":
                        exit(56)    

                    if typeSymb1 != "int":
                        exit(53)

                    if int(valueSymb1) < 0 or int(valueSymb1) > 49:
                        exit(57)

                    exit(int(valueSymb1))
                    
                case "DPRINT":
                    pass
                                    
                case "BREAK":
                    pass
                
                case "INT2FLOAT":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    
                    if valueSymb1 == "":
                        exit(56)
                        
                    if typeSymb1 != "int":
                        exit(53)
                    
                    self.frame[frameVar].set(nameVar, str(float(valueSymb1)), "float")
                
                case "FLOAT2INT":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    
                    if valueSymb1 == "":
                        exit(56)
                        
                    if typeSymb1 != "float":
                        exit(53)
                        
                    self.frame[frameVar].set(nameVar, str(int(float(valueSymb1))), "int")
                    
                case "DIV":
                    frameVar, nameVar = self.__splitting(instr.arg1['text'])
                    valueSymb1, typeSymb1 = self.__workSymb(instr.arg2)
                    valueSymb2, typeSymb2 = self.__workSymb(instr.arg3)

                    if typeSymb1 != typeSymb2 or typeSymb1 not in ["nil", "int", "float"]:
                        exit(53)

                    if int(float(valueSymb2)) == 0:
                        exit(57)

                    if "float" in [typeSymb1, typeSymb2]:
                        try:
                            result = float(valueSymb1) / float(valueSymb2)
                        except:
                            exit(53)
                        self.frame[frameVar].set(nameVar, str(result), "float")
                    else:
                        try:
                            result = int(int(valueSymb1) + int(valueSymb2))
                        except:
                            exit(53)
                        self.frame[frameVar].set(nameVar, str(result), "int")
                    
                case "CLEARS":
                    self.dataStack.clear()
                
                case "ADDS":
                    value2 = self.dataStack.pop() # [vlaue, type]
                    value1 = self.dataStack.pop()

                    if value1[1] != value2[1] or value1[1] not in ["int", "float"]:
                        exit(53)
                        
                    if "float" in [value1[1], value2[1]]:
                        try:
                            result = float(value1[0]) + float(value2[0])
                        except:
                            exit(53)
                        self.dataStack.append([str(result), "float"])
                    else:
                        try:
                            result = int(value1[0]) + int(value2[0])
                        except:
                            exit(53)
                        self.dataStack.append([str(result), "int"])
                
                case "SUBS":
                    value2 = self.dataStack.pop()
                    value1 = self.dataStack.pop()

                    if value1[1] != value2[1] or value1[1] not in ["int", "float"]:
                        exit(53)
                        
                    if "float" in [value1[1], value2[1]]:
                        try:
                            result = float(value1[0]) - float(value2[0])
                        except:
                            exit(53)
                        self.dataStack.append([str(result), "float"])
                    else:
                        try:
                            result = int(value1[0]) - int(value2[0])
                        except:
                            exit(53)
                        self.dataStack.append([str(result), "int"])
                
                case "MULS":
                    value2 = self.dataStack.pop()
                    value1 = self.dataStack.pop()

                    if value1[1] != value2[1] or value1[1] not in ["nil", "int", "float"]:
                        exit(53)
                        
                    if "float" in [value1[1], value2[1]]:
                        try:
                            result = float(value1[0]) * float(value2[0])
                        except:
                            exit(53)
                        self.dataStack.append([str(result), "float"])
                    else:
                        try:
                            result = int(value1[0]) * int(value2[0])
                        except:
                            exit(53)
                        self.dataStack.append([str(result), "int"])
                
                case "IDIVS":
                    value2 = self.dataStack.pop()
                    value1 = self.dataStack.pop()

                    if value1[1] != value2[1] or value1[1] not in ["nil", "int", "float"]:
                        exit(53)

                    if int(value2[0]) == 0:
                        exit(57)
                        
                    if "float" in [value1[1], value2[1]]:
                        try:
                            result = int(float(value1[0]) / float(value2[0]))
                        except:
                            exit(53)
                    else:
                        try:
                            result = int(int(value1[0]) / int(value2[0]))
                        except:
                            exit(53)
                    self.dataStack.append([str(result), "int"])
                case "DIVS":
                    value2 = self.dataStack.pop()
                    value1 = self.dataStack.pop()

                    if value1[1] != value2[1] or value1[1] not in ["nil", "int", "float"]:
                        exit(53)

                    if int(value2[0]) == 0:
                        exit(57)
                        
                    if "float" in [value1[1], value2[1]]:
                        try:
                            result = float(value1[0]) / float(value2[0])
                        except:
                            exit(53)
                        self.dataStack.append([result, "float"])
                    else:
                        try:
                            result = int(int(value1[0]) / int(value2[0]))
                        except:
                            exit(53)
                        self.dataStack.append([result, "int"])
                
                case "LTS":
                    value2 = self.dataStack.pop()
                    value1 = self.dataStack.pop()

                    if value1[1] == value2[1] and value1[1] in ["int", "string", "bool", "float"]:
                        result = "true" if value1[0] < value2[0] else "false"
                        self.dataStack.append([result, "bool"])
                    else:
                        exit(53)
                
                case "GTS":
                    value2 = self.dataStack.pop()
                    value1 = self.dataStack.pop()

                    if value1[1] == value2[1] and value1[1] in ["int", "string", "bool", "float"]:
                        result = "true" if value1[0] > value2[0] else "false"
                        self.dataStack.append([result, "bool"])
                    else:
                        exit(53)
                
                case "EQS":
                    value2 = self.dataStack.pop()
                    value1 = self.dataStack.pop()
                    
                    if value1[1] == value2[1] and value1[1] in ["int", "string", "bool", "float"] or "nil" in [value1[1], value2[1]]:
                        result = "true" if value1[0] == value2[0] else "false"
                        self.dataStack.append([result, "bool"])
                    else:
                        exit(53)
                
                case "ANDS":
                    value2 = self.dataStack.pop()
                    value1 = self.dataStack.pop()

                    if value1[1] != "bool" or value2[1] != "bool":
                        exit(53)

                    condition1 = True if value1[0] == "true" else False
                    condition2 = True if value2[0] == "true" else False

                    result = condition1 and condition2
                    self.dataStack.append([str(result).lower(), "bool"])
                
                case "ORS":
                    value2 = self.dataStack.pop()
                    value1 = self.dataStack.pop()

                    if value1[1] != "bool" or value2[1] != "bool":
                        exit(53)

                    condition1 = True if value1[0] == "true" else False
                    condition2 = True if value2[0] == "true" else False

                    result = condition1 or condition2
                    self.dataStack.append([str(result).lower(), "bool"])
                
                case "NOTS":
                    value1 = self.dataStack.pop()

                    if value1[1] != "bool":
                        exit(53)

                    condition1 = True if value1[0] == "true" else False

                    result = not condition1
                    self.dataStack.append([str(result).lower(), "bool"])
                
                case "INT2CHARS":
                    value1 = self.dataStack.pop()
                    
                    if value1[1] != "int":
                        exit(53)

                    try:
                        self.dataStack.append([chr(int(value1[0])), "string"])
                    except:
                        exit(58)
                
                case "STRI2INTS":
                    value2 = self.dataStack.pop()
                    value1 = self.dataStack.pop()
                    
                    if value1[1] != "string" or value2[1] != "int":
                        exit(53)

                    if int(value2[0]) >= len(value1[0]) or int(value2[0]) < 0:
                        exit(58)

                    result = value1[0][int(value2[0])]
                    self.dataStack.append([ord(result), "int"])
                
                case "JUMPIFEQS":
                    value2 = self.dataStack.pop()
                    value1 = self.dataStack.pop()

                    if value1[1] != value2[1] and "nil" not in [value1[1], value2[1]]:
                        exit(53) 
                    
                    if value1[0] == value2[0]:
                        found = False
                        for i in self.listInstuction:
                            if i[1].opcode == "LABEL":
                                if i[1].arg1['text'] == instr.arg1['text']:
                                    order = self.listInstuction.index(i)
                                    found = True
                                    break
                        if not found:
                            exit(52)
                
                case "JUMPIFNEQS":
                    value2 = self.dataStack.pop()
                    value1 = self.dataStack.pop()

                    if value1[1] != value2[1] and "nil" not in [value1[1], value2[1]]:
                        exit(53) 
                    
                    if value1[0] != value2[0]:
                        found = False
                        for i in self.listInstuction:
                            if i[1].opcode == "LABEL":
                                if i[1].arg1['text'] == instr.arg1['text']:
                                    order = self.listInstuction.index(i)
                                    found = True
                                    break
                        if not found:
                            exit(52)
                
                case "INT2FLOATS":
                    value1 = self.dataStack.pop()
                    
                    if value1[0] != "":
                        exit(56)
                    
                    if value1[1] != "int":
                        exit(53)
                    
                    self.dataStack.append([str(float(value1[0])), "float"])
                
                case "FLOAT2INTS":
                    value1 = self.dataStack.pop()
                                        
                    if value1[0] != "":
                        exit(56)
                        
                    if value1[1] != "float":
                        exit(53)
                    
                    self.dataStack.append([str(int(float(value1[0]))), "int"])
                
                case other:
                    exit(32)
                    
        self.__writeStats()
                    
    def __workSymb(self, argument):
        if argument['type'] == "var":
            
            frameSymb, nameSymb = self.__splitting(argument['text'])
            frame = self.frame[frameSymb]
            
            return frame.get(nameSymb)
        
        else:
            if argument['type'] == "float":
                return str(float.fromhex(argument['text'])), "float"
            return argument['text'], argument['type']
        
        
    def __splitting(self, text):
        try:
            frame, name = text.split('@')
        except:
            exit(55)
            
        if frame not in ["GF", "LF", "TF"]:
            exit(52)
            
        return frame, name
    
    def __writeStats(self):
        if self.stats:
            for arg in sys.argv[1:]:
                if arg == "--insts":
                    insts = [instr[1].opcode for instr in self.listInstuction if instr[1].opcode not in ["LABEL", "DPRINT", "BREAK"]]
                    self.stats.write(str(len(insts))+"\n")
                    
                elif arg == "--hot":
                    hots = [instr[1].numberOfUses for instr in self.listInstuction]
                    index = hots.index(max(hots))
                    self.stats.write(self.listInstuction[index][1].opcode+"\n")
                    
                elif arg == "--vars":
                    self.stats.write(str(self.maxCountVar)+"\n")
                    
                elif re.search("^--print=", arg):
                    try:
                        prints = arg.split('=')
                    except:
                        exit(10)
                    self.stats.write(prints[1]+"\n")
                    
                elif arg == "--eol":              
                    self.stats.write("\n")
                    
                elif re.search("^--frequent=|--source=|--input=|--stats=", arg):
                    pass
                else:
                    exit(10)