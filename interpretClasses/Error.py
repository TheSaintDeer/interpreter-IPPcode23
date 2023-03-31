import sys

class Error:
    
    __typeError = {
                10: "Bad argument\n",
                11: "Input error\n",
                12: "Output error\n",
                31: "XML format\n",
                32: "Bad XML structure\n",
                52: "Semantic error\n",
                53: "Bad type of operand\n",
                54: "Missing variable\n",
                55: "Missing frame\n",
                56: "Missing value\n",
                57: "Bad value of a operand\n",
                58: "Bad string operation\n",
                99: "Interpret error\n"
                }
    
    def printError(self, errCode):
        sys.stderr.write(self.__typeError[errCode])
        exit(errCode)