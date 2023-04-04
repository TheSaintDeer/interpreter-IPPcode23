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
        
        self.frame.append({text: None, 'type': None})
        return 0
            
    def definiteTemporaryFrame(self):
        self.definition = True
        self.frame.clear()
        return 0
        
    # def push(self):
    #     if self.definition:
    #         self.frame.append(self.temporaryFrame.copy())
    #         self.definition = False
    #         self.frame.clear()
    #         return 0
    #     else:
    #         return 55
        
    # def pop(self):
    #     try:
    #         self.temporaryFrame = self.localFrame.pop()
    #         self.defineTemporaryFrame = True
    #         return 0
    #     except:
    #         return 55
        
    def set(self, nameVar, value, type):
        if self.frame == False:
            return 55
        
        for i in self.frame:
            if nameVar in i:
                index = self.frame.index(i)
            
        self.frame[index][nameVar] = value
        self.frame[index]['type'] = type
        return 0
            
    def get(self, name):
        if self.definition == False:
            exit(55)
        
        for i in self.frame:
            if name in i:
                index = self.frame.index(i)
                break
        
        return self.frame[index][name], self.frame[index]['type']
    
    def clean(self):
        self.definition = False
        self.frame.clear()
        
    def fill(self, frame):
        self.definition = True
        self.frame = frame.copy()