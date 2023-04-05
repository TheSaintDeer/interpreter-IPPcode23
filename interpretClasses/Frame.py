class Frame:
    
    def __init__(self):
        self.frame = list()
        self.definition = False
        
    def newVar(self, text):
        if self.definition == False:
            return 55
        
        for i in self.frame:
            if text in i:
                return 55
        
        self.frame.append({text: None, text+'type': None})
        return 0
            
    def definiteTemporaryFrame(self):
        self.definition = True
        self.frame.clear()
        return 0
        
    def set(self, nameVar, value, type):
        if self.frame == False:
            return 55
        
        for i in self.frame:
            if nameVar in i:
                index = self.frame.index(i)
            
        self.frame[index][nameVar] = value
        self.frame[index][nameVar+'type'] = type
        return 0
            
    def get(self, name):
        if self.definition == False:
            exit(55)
        
        for i in self.frame:
            if name in i:
                index = self.frame.index(i)
                break
        
        return self.frame[index][name], self.frame[index][name+'type']
    
    def clean(self):
        self.definition = False
        self.frame.clear()
        
    def fill(self, frame):
        self.definition = True
        self.frame = frame.copy()