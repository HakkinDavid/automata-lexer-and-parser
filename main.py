from lexer import Lexer
from parser import ParserContext, Programa
from colorama import Fore, Back

\

if __name__ == "__main__":

    #Lexer

    lx = Lexer("design/lexer.auto")

    with open("cpp_test/" + input("Nombre del archivo C++: cpp_test/"), 'r') as file:
        code = file.read()

    print(Back.BLUE + "Archivo encontrado. Procesando con el lexer." + Back.BLACK)
    
    tokenized_code = lx.tokenize(code)

    print("Procesando con el parser.")
    
    ctx = ParserContext(tokenized_code)
    
    resultado = Programa().interpret(ctx)

    if resultado and ctx.pos == len(tokenized_code):
        print("El programa es sintácticamente válido.")
    else:
        print("Error: el programa no es sintácticamente válido o quedaron tokens sin consumir.")