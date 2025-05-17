# Este módulo implementa un parser para analizar una secuencia de tokens

from typing import List, Tuple  # Se importa para usar anotaciones de tipo con listas de tuplas

# Clase que maneja el contexto del análisis sintáctico
class ParserContext:
    def __init__(self, tokens: List[Tuple[str, str]]):  # Constructor que recibe una lista de tokens
        self.tokens = tokens  # Guarda los tokens
        self.pos = 0  # Inicializa la posición del puntero de análisis en 0

    def current_token(self):  # Devuelve el token actual o None si ya se terminó
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):  # Avanza al siguiente token
        self.pos += 1

    def match(self, expected_type: str, expected_value: str = None) -> bool:  # Verifica si el token actual coincide con tipo y opcionalmente valor
        tok = self.current_token()
        if tok is None:
            print(f"❌ Error: esperado {expected_type} pero no hay más tokens.")
            return False
        if tok[0] != expected_type:
            print(f"❌ Error: esperado {expected_type}, pero se encontró {tok[0]} ('{tok[1]}') en la posición {self.pos}.")
            return False
        if expected_value and tok[1] != expected_value:
            print(f"❌ Error: esperado valor '{expected_value}', pero se encontró '{tok[1]}' en la posición {self.pos}.")
            return False
        print(f"✅ Match: {expected_type} '{tok[1]}'")
        self.advance()
        return True

# Clase base para cualquier expresión del lenguaje (regla no terminal)
class AbstractExpression:
    def interpret(self, context: ParserContext) -> bool:
        raise NotImplementedError  # Debe implementarse en subclases

# Representa la estructura principal del programa
class Programa(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Programa>")
        return (
            Librerias().interpret(context) and  # Primero analiza librerías
            FuncionPrincipal().interpret(context)  # Luego la función principal
        )

# Representa las librerías (por ejemplo, #include<string>)
class Librerias(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Librerías>")
        while context.match("LIBRARY"):  # Consume todos los tokens LIBRARY
            pass
        return True

# Representa la función principal int main(void) { ... }
class FuncionPrincipal(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <FuncionPrincipal>")
        if not context.match("INT"):
            return False
        if not context.match("MAIN"):
            return False
        if not context.match("SYM", "("):
            return False
        if not context.match("VOID"):
            return False
        if not context.match("SYM", ")"):
            return False
        if not context.match("SYM", "{"):
            return False

        print("▶ Dentro de main: analizando <Declaraciones>")
        Declaraciones().interpret(context)  # Procesa declaraciones dentro del cuerpo de main

        print("▶ Dentro de main: analizando <Enunciados>")
        Enunciados().interpret(context)  # Procesa enunciados (como for, cout, etc.)

        if not context.match("SYM", "}"):
            return False
        return True

# Representa una serie de declaraciones de variables
class Declaraciones(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Declaraciones>")
        while Declaracion().interpret(context):  # Mientras siga habiendo declaraciones
            pass
        return True

# Representa una declaración individual
class Declaracion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Declaración>")
        pos_backup = context.pos  # Guarda la posición para volver atrás si falla
        tipos_validos = ["INT", "STRING", "CHAR", "FLOAT", "LONG", "DOUBLE"]
        if context.current_token() and context.current_token()[0] in tipos_validos:
            tipo = context.current_token()[0]
            context.advance()
            if tipo == "LONG":
                if not context.match("INT"):
                    context.pos = pos_backup
                    return False
            if not context.match("IDENTIFIER"):
                context.pos = pos_backup
                return False
            if not context.match("EQ"):
                context.pos = pos_backup
                return False
            valor_esperado = {  # Determina qué tipo de literal se espera
                "INT": "INT_LITERAL",
                "FLOAT": "FLOAT_LITERAL",
                "DOUBLE": "FLOAT_LITERAL",
                "CHAR": "CHAR_LITERAL",
                "STRING": "STR_LITERAL",
            }.get(tipo, "INT_LITERAL")
            if not context.match(valor_esperado):
                context.pos = pos_backup
                return False
            if not context.match("SYM", ";"):
                context.pos = pos_backup
                return False
            return True
        elif context.match("IDENTIFIER", "std"):  # Caso para std::string ...
            if not context.match("SCOPE", "::"):
                context.pos = pos_backup
                return False
            if not context.match("STRING"):
                context.pos = pos_backup
                return False
            if not context.match("IDENTIFIER"):
                context.pos = pos_backup
                return False
            if not context.match("EQ"):
                context.pos = pos_backup
                return False
            if not context.match("STR_LITERAL"):
                context.pos = pos_backup
                return False
            if not context.match("SYM", ";"):
                context.pos = pos_backup
                return False
            return True
        return False

# Representa una serie de enunciados (como for, cout)
class Enunciados(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Enunciados>")
        while ForLoop().interpret(context) or CoutPrint().interpret(context):  # Procesa todos los enunciados
            pass
        return True

# Representa un ciclo for completo
class ForLoop(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ForLoop>")
        pos_backup = context.pos
        if not context.match("FOR"):
            context.pos = pos_backup
            return False
        if not context.match("SYM", "("):
            return False
        if not Declaracion().interpret(context):
            return False
        if not context.match("IDENTIFIER"):
            return False
        if not context.match("LT"):
            return False
        if not context.match("IDENTIFIER"):
            return False
        if not context.match("DOT"):
            return False
        if not context.match("IDENTIFIER", "length"):
            return False
        if not context.match("SYM", "(") or not context.match("SYM", ")"):
            return False
        if not context.match("SYM", ";"):
            return False
        if not context.match("IDENTIFIER"):
            return False
        if not context.match("OP_SYM", "+") or not context.match("OP_SYM", "+"):
            return False
        if not context.match("SYM", ")"):
            return False
        if not context.match("SYM", "{"):
            return False
        if not CoutPrint().interpret(context):  # Se espera una impresión cout dentro del for
            return False
        if not context.match("SYM", "}"):
            return False
        return True

# Representa un enunciado de impresión tipo std::cout << abc[i] << std::endl;
class CoutPrint(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <CoutPrint>")
        pos_backup = context.pos
        if not context.match("IDENTIFIER", "std"):
            context.pos = pos_backup
            return False
        if not context.match("SCOPE", "::"):
            return False
        if not context.match("COUT"):
            return False
        if not context.match("SHIFT_LEFT"):
            return False
        if not context.match("IDENTIFIER"):
            return False
        if not context.match("LBRACK"):
            return False
        if not context.match("IDENTIFIER"):
            return False
        if not context.match("RBRACK"):
            return False
        if not context.match("SHIFT_LEFT"):
            return False
        if not context.match("IDENTIFIER", "std"):
            return False
        if not context.match("SCOPE", "::"):
            return False
        if not context.match("IDENTIFIER", "endl"):
            return False
        if not context.match("SYM", ";"):
            return False
        return True


__all__ = ["parser"]