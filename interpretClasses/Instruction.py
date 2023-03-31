class Instruction:
     
    def __init__(self, opcode, arguments):
        self.opcode = opcode
        
        try:
            self.arg1 = {"type": arguments[0].attrib['type'], "text": arguments[0].text.strip()} 
        except:
            pass
               
        try:     
            self.arg2 = {"type": arguments[1].attrib['type'], "text": arguments[1].text.strip()} 
        except:
            pass
        
        try:
            self.arg3 = {"type": arguments[2].attrib['type'], "text": arguments[2].text.strip()} 
        except:
            pass