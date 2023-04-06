class Instruction:
     
    def __init__(self, opcode):
        self.opcode = opcode
        self.arg1 = None
        self.arg2 = None
        self.arg3 = None
        
    def setArg(self, argument):
        if argument.tag == "arg1":
            try:
                self.arg1 = {"type": argument.attrib['type'], "text": argument.text.strip()} 
            except:
                pass
               
        if argument.tag == "arg2":
            try:     
                self.arg2 = {"type": argument.attrib['type'], "text": argument.text.strip()} 
            except:
                pass
        
        if argument.tag == "arg3":
            try:
                self.arg3 = {"type": argument.attrib['type'], "text": argument.text.strip()} 
            except:
                pass
            
    def controlArg(self):
        
        if self.opcode in ["CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK", "CLEARS"]:
            if self.arg1 != None or self.arg2 != None or self.arg3 != None:
                exit(32)
        
        if self.opcode in ["DEFVAR", "CALL", "PUSHS", "POPS", "WRITE", "LABEL", "JUMP", "EXIT", "DPRINT"]:
            if self.arg1 == None or self.arg2 != None or self.arg3 != None:
                exit(32)
                
        if self.opcode in ["MOVE", "NOT", "INT2CHAR", "READ", "STRLEN", "TYPE", "INT2FLOAT", "FLOAT2INT"]:
            if self.arg1 == None or self.arg2 == None or self.arg3 != None:
                exit(32)
                
        if self.opcode in ["ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR", "JUMPIFEQ", "JUMPIFNEQ", "DIV"]:
            if self.arg1 == None or self.arg2 == None or self.arg3 == None:
                exit(32)