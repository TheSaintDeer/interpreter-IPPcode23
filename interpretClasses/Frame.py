# Implementační dokumentace k 2. úloze do IPP 2022/2023
# Jméno a příjmení: Ivan Golikov
# Login: xgolik00

class Frame:
    
    def __init__(self):
        self.frame = list()
        self.definition = False
        
    # method needed to create a new variable
    def newVar(self, text):
        if self.definition == False:
            exit(55)
        
        # checking for the presence of a variable with the same name
        for i in self.frame:
            if text in i:
                exit(52)
        
        self.frame.append({text: "", text+'type': ""})
            
    def definiteTemporaryFrame(self):
        self.definition = True
        self.frame.clear()
        
    # set value and type for given variable
    def set(self, nameVar, value, type):
        if self.definition == False:
            exit(55)
        
        found = False
        for i in self.frame:
            if nameVar in i:
                index = self.frame.index(i)
                found = True
                break
        
        if not found:
            exit(54)
            
        self.frame[index][nameVar] = value
        self.frame[index][nameVar+'type'] = type
        return 0
            
    # get the value and type of the given variable
    def get(self, name):
        if self.definition == False:
            exit(55)
        
        found = False
        for i in self.frame:
            if name in i:
                index = self.frame.index(i)
                found = True
                break
            
        if not found:
            exit(54)
        
        return self.frame[index][name], self.frame[index][name+'type']
    
    def clean(self):
        self.definition = False
        self.frame.clear()
        
    def fill(self, frame):
        self.definition = True
        self.frame = frame.copy()