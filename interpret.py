# Implementační dokumentace k 2. úloze do IPP 2022/2023
# Jméno a příjmení: Ivan Golikov
# Login: xgolik00

from interpretClasses.main import Interpret

if __name__ == "__main__":
    interpret = Interpret()

    interpret.parseArguments()
    interpret.XMLtoInstr()
    interpret.interpreting()