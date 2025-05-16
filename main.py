from lexer import Lexer
from parser import Parser
from colorama import Fore, Back

if __name__ == "__main__":
    lx = Lexer("design/lexer.auto")

    with open("cpp_test/" + input("Nombre del archivo C++: cpp_test/"), 'r') as file:
        code = file.read()

    print(Back.BLUE + "Archivo encontrado. Procesando con el lexer." + Back.BLACK)
    
    tokenized_code = lx.tokenize(code)