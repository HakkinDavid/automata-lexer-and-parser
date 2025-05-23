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

    # Parser

    print(Back.BLACK + Fore.WHITE + "Procesando con el parser.")
    
    ctx = ParserContext(tokenized_code)
    
    resultado = Programa().interpret(ctx)

    if resultado and ctx.pos == len(tokenized_code):
        print(Back.GREEN + "El programa es sintácticamente válido.")
    else:
        print(Back.RED + "Error: el programa no es sintácticamente válido.")
        if (ctx.pos < len(tokenized_code)):
            print("Quedaron tokens sin consumir.", tokenized_code[ctx.pos:])