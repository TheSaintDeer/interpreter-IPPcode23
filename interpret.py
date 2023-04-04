from interpretClasses.main import Interpret

if __name__ == "__main__":
    interpret = Interpret()

    interpret.parseArguments()
    interpret.XMLtoInstr()
    interpret.interpreting()