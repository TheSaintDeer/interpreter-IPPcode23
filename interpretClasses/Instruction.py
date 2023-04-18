# Implementační dokumentace k 2. úloze do IPP 2022/2023
# Jméno a příjmení: Ivan Golikov
# Login: xgolik00

class Instruction:
     
    def __init__(self, opcode):
        self.opcode = opcode.upper()
        self.arg1 = None
        self.arg2 = None
        self.arg3 = None
        self.numberOfUses = 0
        
    # determining the location of all arguments for a command
    def setArg(self, argument):
        try:
            text = argument.text.strip()
        except:
            text = ""
            
        if argument.tag == "arg1":
            self.arg1 = {"type": argument.attrib['type'], "text": text} 
               
        if argument.tag == "arg2":
            self.arg2 = {"type": argument.attrib['type'], "text": text} 
        
        if argument.tag == "arg3":
            self.arg3 = {"type": argument.attrib['type'], "text": text} 
            
    # checking that no argument is missing or extra
    def controlArg(self):
        
        if self.opcode in ["CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK", "CLEARS", "ADDS", "SUBS", "MULS", "IDIVS", "DIVS", "LTS", "GTS", "EQS", "ANDS", "ORS", "NOTS", "INT2CHARS", "STRI2INTS", "INT2FLOATS", "FLOAT2INTS"]:
            if self.arg1 != None or self.arg2 != None or self.arg3 != None:
                exit(32)
        
        if self.opcode in ["DEFVAR", "CALL", "PUSHS", "POPS", "WRITE", "LABEL", "JUMP", "EXIT", "DPRINT", "JUMPIFEQS", "JUMPIFNEQS"]:
            if self.arg1 == None or self.arg2 != None or self.arg3 != None:
                exit(32)
                
        if self.opcode in ["MOVE", "NOT", "INT2CHAR", "READ", "STRLEN", "TYPE", "INT2FLOAT", "FLOAT2INT"]:
            if self.arg1 == None or self.arg2 == None or self.arg3 != None:
                exit(32)
                
        if self.opcode in ["ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR", "JUMPIFEQ", "JUMPIFNEQ", "DIV"]:
            if self.arg1 == None or self.arg2 == None or self.arg3 == None:
                exit(32)
                
    def incrementUses(self):
        self.numberOfUses += 1