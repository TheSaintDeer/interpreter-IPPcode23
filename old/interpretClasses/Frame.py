import copy

class Frame:
    
    def __init__(self):
        self.globalFrame = list()
        
        self.localFrame = list()
        
        self.temporaryFrame = list()
        self.defineTemporaryFrame = False
        
    def createVar(self, text):
        try:
            frame, value = text.split('@')
        except:
            return 55
        
        if frame == "GF":
            for i in self.globalFrame:
                if value in i:
                    return 55
            
            self.globalFrame.append({value: None, 'type': None})
            return 0
        
        elif frame == "LF":
            
            for i in self.localFrame[0]:
                if value in i:
                    return 55
            
            self.localFrame[0].append({value: None, 'type': None})
            return 0
            
        elif frame == "TF":
            if self.defineTemporaryFrame == False:
                return 55
            
            for i in self.temporaryFrame:
                if value in i:
                    return 55
            
            self.temporaryFrame.append({value: None, 'type': None})
            return 0
            
    def definitionTemporaryFrame(self):
        self.defineTemporaryFrame = True
        self.temporaryFrame.clear()
        
    def push(self):
        if self.defineTemporaryFrame:
            self.localFrame.append(self.temporaryFrame.copy())
            self.defineTemporaryFrame = False
            self.temporaryFrame.clear()
            return 0
        else:
            return 55
        
    def pop(self):
        try:
            self.temporaryFrame = self.localFrame.pop()
            self.defineTemporaryFrame = True
            return 0
        except:
            return 55
        
    def set(self, var, symb):
        try:
            frameVar, nameVar = var.split('@')
            typeSymb, valueSymb = symb.split('@')
        except:
            return 55
        
        if frameVar == "GF":
            
            for i in self.globalFrame:
                if nameVar in i:
                    index = self.globalFrame.index(i)
                
            self.globalFrame[index][nameVar] = valueSymb
            self.globalFrame[index]['type'] = typeSymb
        
        elif frameVar == "LF":
            
            for i in self.localFrame[0]:
                if nameVar in i:
                    index = self.localFrame[0].index(i)
            
            self.localFrame[0][index][nameVar] = valueSymb
            self.localFrame[0][index]['type'] = typeSymb
            
        elif frameVar == "TF":
             
            if self.defineTemporaryFrame == False:
                return 55
            
            for i in self.temporaryFrame:
                if nameVar in i:
                    index = self.temporaryFrame.index(i)
                
            self.temporaryFrame[index][nameVar] = valueSymb
            self.temporaryFrame[index]['type'] = typeSymb
            
    def get(self, frame, name):
        if frame == "GF":
            for i in self.globalFrame:
                if name in i:
                    index = self.globalFrame.index(i)
                    break
            return self.globalFrame[index][name], self.globalFrame[index]['type']
                
        elif frame == "LF":
            for i in self.localFrame[-1]:
                if name in i:
                    index = self.localFrame[-1].index(i)
                    break
                
            return self.localFrame[-1][index][name], self.localFrame[-1][index]['type']
            
        elif frame == "TF":
            if self.defineTemporaryFrame == False:
                exit(55)
            
            for i in self.temporaryFrame:
                if name in i:
                    index = self.temporaryFrame.index(i)
                    break
            
            return self.temporaryFrame[index][name], self.temporaryFrame[index]['type']