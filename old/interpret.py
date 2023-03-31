# Implementační dokumentace k 2. úloze do IPP 2022/2023
# Jméno a příjmení: Ivan Golikov
# Login: xgolik00

import re
import argparse
import sys
from unicodedata import name
import xml.etree.ElementTree as ET
import collections
from interpretClasses import Error, Frame, Instruction

def workSymb(arg, frames):
    if arg['type'] == "var":
        try:
            frameSymb, nameSymb = arg['text'].split('@')
        except:
            exit(55)
        
        if frameSymb in ["GF", "LF", "TF"]:
            try:
                return frames.get(frameSymb, nameSymb)
            except:
                err.printErr(55)
    
    else:
        return arg['text'], arg['type']

err = Error.Error()
frame = Frame.Frame()

# parsing argument
# parser = argparse.ArgumentParser(description="XML interpreter")
# parser.add_argument("--source", help = "file XML")
# parser.add_argument("--input", help = "file for input")
# parametrs = parser.parse_args()

# args = parser.parse_args()

# # open xml file
# XMLfile = input() if parametrs.source == None else parametrs.source

# handle input way
# inputData = input() if parametrs.input == None else parametrs.input

# if parametrs.input:
#     inputFile = open(parametrs.input, "r")

# parsing xml file
try:
    # root = ET.parse(XMLfile).getroot()
    root = ET.parse("in.xml").getroot()
except FileNotFoundError:
    err.printErr(11)
except Exception as e:
    err.printErr(31)

    
# control structure of xml file
if root.tag != "program":
    err.printErr(32)
    
if not("language" in root.attrib):
    err.printErr(32)
    
if root.attrib['language'].upper() != "IPPCODE23":
    err.printErr(32)

# making the list with all instruction 
listInstuction = []
listLabel = []
orderInstr = 0
for instruction in root:
    
    if instruction.tag != "instruction":
        err.printErr(32)
        
    if 'order' not in instruction.attrib:
        err.printErr(32)
        
    if not (instruction.attrib['order'].isnumeric()):
        err.printErr(32)
        
    if int(instruction.attrib['order']) < 1:
        err.printErr(32)
        
    if 'opcode' not in instruction.attrib:
        err.printErr(32)
    
    argOrder = 0
    for arg in instruction:
        argOrder += 1
        
        if arg.tag != "arg"+str(argOrder):
            err.printErr(32)
            
        if 'type' not in arg.attrib:
            err.printErr(32)
            
        if arg.attrib['type'] not in  ["var", "string", "int", "nil", "label", "type", "bool"]:
            err.printErr(32)
        
        if instruction.attrib['opcode'] == "LABEL":
            if arg.text in listLabel:
                err.printErr(52)
            listLabel.append(str(arg.text))
            
    instr = Instruction.Instruction(instruction.attrib['opcode'], instruction)
    listInstuction.append([int(instruction.attrib['order']), instr])
    orderInstr += 1
    
# sorting dictionary
def sortByOrder(elem):
    return elem[0]

listInstuction.sort(key=sortByOrder)

prevIndex = -1
for order in listInstuction:
    if int(order[0]) == prevIndex:
        err.printErr(32)
    prevIndex = int(order[0])
    

# start instructions
order = 0
returnPoint = list()
dataStack = list()

while order < len(listInstuction):
    instr = listInstuction[order][1]
    order += 1
    
    match instr.opcode:
            
        case "MOVE":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            frame.set(instr.arg1['text'], str(typeSymb1)+"@"+str(valueSymb1))
        
        case "CREATEFRAME":
            frame.definitionTemporaryFrame()
        
        case "PUSHFRAME":
            if frame.push():
                err.printErr(55)
            
        case "POPFRAME":
            if frame.pop():
                err.printErr(55)
            
        case "DEFVAR":
            if frame.createVar(instr.arg1['text']):
                err.printErr(55)
            
        case "CALL":
            returnPoint.append(order)
            for i in listInstuction:
                if i[1].opcode == "LABEL":
                    if i[1].arg1['text'] == instr.arg1['text']:
                        order = listInstuction.index(i)
                        
        case "RETURN":
            order = returnPoint.pop()
            
        case "PUSHS":
            valueVar, typeVar = workSymb(instr.arg1, frame)
            dataStack.append([valueVar, typeVar])
            
        case "POPS":
            if dataStack:
                pops = dataStack.pop()
                frame.set(instr.arg1['text'], pops[0]+"@"+pops[1])
            else:
                err.printErr(56)
            
        case "ADD":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            if (typeSymb1 == "nil" and typeSymb2 != "nil") or (typeSymb1 != "nil" and typeSymb2 == "nil") or typeSymb1 != "int" or typeSymb2 != "int":
                err.printErr(53)
                
            try:
                result = int(valueSymb1) + int(valueSymb2)
            except:
                err.printErr(32)
                
            frame.set(instr.arg1['text'], "int@"+str(result))
            
        case "SUB":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            if (typeSymb1 == "nil" and typeSymb2 != "nil") or (typeSymb1 != "nil" and typeSymb2 == "nil") or typeSymb1 != "int" or typeSymb2 != "int":
                err.printErr(53)
                
            try:
                result = int(valueSymb1) - int(valueSymb2)
            except:
                err.printErr(32)
                
            frame.set(instr.arg1['text'], "int@"+str(result))
            
        case "MUL":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            if (typeSymb1 == "nil" and typeSymb2 != "nil") or (typeSymb1 != "nil" and typeSymb2 == "nil") or typeSymb1 != "int" or typeSymb2 != "int":
                err.printErr(53)
                
            try:
                result = int(valueSymb1) * int(valueSymb2)
            except:
                err.printErr(32)
                
            frame.set(instr.arg1['text'], "int@"+str(result))
            
        case "IDIV":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            if (typeSymb1 == "nil" and typeSymb2 != "nil") or (typeSymb1 != "nil" and typeSymb2 == "nil") or typeSymb1 != "int" or typeSymb2 != "int":
                err.printErr(53)
                
            if valueSymb2 == "0":
                err.printErr(57)
                
            try:
                result = int(int(valueSymb1) / int(valueSymb2))
            except:
                err.printErr(32)
            
            frame.set(instr.arg1['text'], "int@"+str(result))
            
        case "LT":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            if typeSymb1 == typeSymb2 and typeSymb1 in ["int", "string", "bool"]:
                result = "True" if valueSymb1 < valueSymb2 else "False"
                frame.set(instr.arg1['text'], "bool@"+result)
                
        case "GT":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            if typeSymb1 == typeSymb2 and typeSymb1 in ["int", "string", "bool"]:
                result = "True" if valueSymb1 > valueSymb2 else "False"
                frame.set(instr.arg1['text'], "bool@"+result)
                
        case "EQ":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            if (typeSymb1 == "nil" and typeSymb2 != "nil") or (typeSymb1 != "nil" and typeSymb2 == "nil"):
                err.printErr(53)
            
            if typeSymb1 == typeSymb2 and typeSymb1 in ["int", "string", "bool"]:
                result = "True" if valueSymb1 == valueSymb2 else "False"
                frame.set(instr.arg1['text'], "bool@"+result)
                
        case "AND":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            condition1 = True if valueSymb1 == "True" else False
            condition2 = True if valueSymb2 == "True" else False

            result = condition1 and condition2
            frame.set(instr.arg1['text'], "bool@"+result)
            
        case "OR":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            condition1 = True if valueSymb1 == "True" else False
            condition2 = True if valueSymb2 == "True" else False

            result = condition1 or condition2
            frame.set(instr.arg1['text'], "bool@"+result)
        
        case "NOT":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            
            condition1 = True if valueSymb1 == "True" else False

            result = not condition1
            frame.set(instr.arg1['text'], "bool@"+result)
            
        case "INT2CHAR":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            
            if typeSymb1 != "int":
                exit(53)
            
            try:
                frame.set(instr.arg1['text'], "string@"+chr(int(valueSymb1)))
            except:
                exit(58)
                
        case "STRI2INT":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            if typeSymb1 != "string" or typeSymb2 != "int":
                exit(53)

            if int(valueSymb2) >= len(valueSymb1) or int(valueSymb2) < 0:
                exit(58)

            result = valueSymb1[int(valueSymb2)]
            frame.set(instr.arg1['text'], "int@"+ord(result))
            
        case "READ":
            # if parametrs.input:
            #     readValue = inputFile.readline()
            #     readValue = readValue.strip()
            # else:
            readValue = input()
                
            frame.set(instr.arg1['text'], instr.arg2['text']+"@"+readValue)
            
        case "WRITE":
            valueSymb1, typeSymb1 = workSymb(instr.arg1, frame)
            
            valueSymb1 = re.sub(r"\\032", " ", valueSymb1)
            valueSymb1 = re.sub(r"\\035", "#", valueSymb1)
            valueSymb1 = re.sub(r"\\092", "\\\\", valueSymb1)
            valueSymb1 = re.sub(r"\\010", "\\n", valueSymb1)

            if not(valueSymb1 == "nil"):
                print(valueSymb1, end="")
                
        case "CONCAT":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            if typeSymb1 != typeSymb2 != "string":
                err.printErr(53)
            
            frame.set(instr.arg1['text'], "string@"+valueSymb1+valueSymb2)
            
        case "STRLEN":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            
            frame.set(instr.arg1['text'], "int@"+len(valueSymb1))
            
        case "GETCHAR":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            frame.set(instr.arg1['text'], "string@"+valueSymb1[int(valueSymb2)])
            
        case "SETCHAR":
            valueVar, typeVar = workSymb(instr.arg1, frame)
            
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            valueVar[int(valueSymb2)] = valueSymb2
            frame.set(instr.arg1['text'], typeVar+"@"+valueVar)
            
        case "TYPE":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            
            frame.set(instr.arg1['text'], "type@"+valueSymb1)
            
        case "LABEL":
            pass
        
        case "JUMP":
            for i in listInstuction:
                if i[1].opcode == "LABEL":
                    if i[1].arg1['text'] == instr.arg1['text']:
                        order = listInstuction.index(i)
            err.printErr(52)
                        
        case "JUMPIFEQ":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            if (typeSymb1 == "nil" and typeSymb2 != "nil") or (typeSymb1 != "nil" and typeSymb2 == "nil"):
                err.printErr(53)
            
            if valueSymb1 == valueSymb2 and typeSymb1 in ["int", "string", "bool"] and typeSymb2 in ["int", "string", "bool"]:
                for i in listInstuction:
                    if i[1].opcode == "LABEL":
                        if i[1].arg1['text'] == instr.arg1['text']:
                            order = listInstuction.index(i)
                err.printErr(52)
                            
        case "JUMPIFNEQ":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            valueSymb2, typeSymb2 = workSymb(instr.arg3, frame)
            
            if (typeSymb1 == "nil" and typeSymb2 != "nil") or (typeSymb1 != "nil" and typeSymb2 == "nil"):
                err.printErr(53)
            
            if valueSymb1 != valueSymb2 and typeSymb1 in ["int", "string", "bool"] and typeSymb2 in ["int", "string", "bool"]:
                for i in listInstuction:
                    if i[1].opcode == "LABEL":
                        if i[1].arg1['text'] == instr.arg1['text']:
                            order = listInstuction.index(i)
                err.printErr(52)
                            
        case "EXIT":
            valueSymb1, typeSymb1 = workSymb(instr.arg2, frame)
            
            if typeSymb1 == "":
                exit(56)    

            if typeSymb1 != "int":
                exit(53)

            if int(valueSymb1) < 0 or int(valueSymb1) > 49:
                exit(57)

            exit(int(valueSymb1))
            
        case other:
            err.printErr(32)
                
pass