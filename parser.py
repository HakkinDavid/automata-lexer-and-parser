from typing import List, Tuple  # Importa los tipos necesarios para anotaciones (listas de tuplas)

# Clase que mantiene el contexto actual del análisis: tokens y posición
class ParserContext:
    def __init__(self, tokens: List[Tuple[str, str]]):
        self.tokens = tokens  # Lista de tokens
        self.pos = 0  # Índice actual del token en análisis

    def current_token(self):
        # Retorna el token actual o None si ya no hay más
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        # Avanza al siguiente token
        self.pos += 1

    def match(self, expected_type: str, expected_value: str = None) -> bool:
        # Verifica si el token actual coincide con el tipo (y valor opcional) esperado
        tok = self.current_token()
        if tok is None:
            print(f"ℹ️ Se esperaba {expected_type} pero no hay más tokens")
            return False
        
        if tok[0] != expected_type:
            print(f"ℹ️ Se esperaba {expected_type}, pero se encontró {tok[0]} ('{tok[1]}') en la posición {self.pos}")
            return False
        
        # Permitir cualquier valor para LIBRARY si no se especifica expected_value
        if expected_type == "LIBRARY":
            print(f"✅ Match (LIBRARY): {tok[1]}")
            self.advance()
            return True
        #cambio mas reciente
        
        if expected_value and tok[1] != expected_value:
            print(f"ℹ️ Se esperaba valor '{expected_value}', pero se encontró '{tok[1]}' en la posición {self.pos}")
            return False
        print(f"✅ Encontrado {expected_type} '{tok[1]}'")
        self.advance()
        return True

# Interfaz base para todas las reglas del parser
class AbstractExpression:
    def interpret(self, context: ParserContext) -> bool:
        raise NotImplementedError  # Cada subclase debe implementar esta función

#Funciones de utilidad para el parser-------------------------------------------------------------
def match_identificador_indexado(context: ParserContext) -> bool:
    pos = context.pos
    if context.match("IDENTIFIER") and context.match("LBRACK") and context.match("IDENTIFIER") and context.match("RBRACK"):
        print("✅ Encontrado IDENTIFIER con índice (array access)")
        return True
    context.pos = pos
    return False

# Utilidad para reconocer llamadas como abc.length()
def match_llamada_miembro(context: ParserContext) -> bool:
    print("▶ Analizando <match_llamada_miembro>")
    pos = context.pos
    if context.match("IDENTIFIER") and context.match("DOT") and context.match("IDENTIFIER"):
        if context.match("SYM", "(") and context.match("SYM", ")"):
            print("✅ Encontrado llamada a método tipo objeto.metodo()")
            return True
    context.pos = pos
    return False
#fin de funciones de utilidad-----------------------------------------------------


# Representa la regla <Programa> ------------------------------------------------------------------------------------
class Programa(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Programa>")
        return (
            Librerias().interpret(context) and
            DeclaracionTemplate().interpret(context) and
            DeclaracionCompuesta().interpret(context) and
            Funciones().interpret(context) and
            FuncionPrincipal().interpret(context)
        )

# Representa la regla <Librerías>
class Librerias(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Librerías>")
        # Acepta múltiples tokens LIBRARY
        while context.match("LIBRARY"):
            pass
        # Acepta opcionalmente: using namespace std;
        if context.match("USING"):
          if not context.match("NAMESPACE"): return False
          if not context.match("IDENTIFIER", "std"): return False
          if not context.match("SYM", ";"): return False
        return True
    
# representa la regla Template--------------------------------------------------------------

class DeclaracionTemplate(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <DeclaracionTemplate>")
        any_success = False

        while True:
            pos = context.pos

            # Solo intentar si empieza con TEMPLATE
            if not context.match("TEMPLATE"):
                context.pos = pos
                break  # No es template, salimos del ciclo

            print("🔁 Inicio de bloque TEMPLATE")
            if not context.match("LT"): # <
                context.pos = pos
                return False
            
            # template < typename <id> >
            if not context.match("TYPENAME"):
                context.pos = pos
                return False
            if not context.match("IDENTIFIER"): #id
                context.pos = pos
                return False
            if not context.match("GT"): # >
                context.pos = pos
                return False

            # <id> <identifier>
            if not context.match("IDENTIFIER"):
                context.pos = pos
                return False
            if not context.match("IDENTIFIER"):
                context.pos = pos
                return False

            if not context.match("SYM", "("):
                context.pos = pos
                return False
            if not ListaParametrosTemplate().interpret(context):
                context.pos = pos
                return False
            if not context.match("SYM", ")"):
                context.pos = pos
                return False

            if not context.match("SYM", "{"):
                context.pos = pos
                return False
            
            # Opción: solo retorno
            if Retorno().interpret(context):
                pass  # válido también

            # Opción: enunciados + retorno
            elif Enunciados().interpret(context):
                Retorno().interpret(context)  # opcional
            else:
                context.pos = pos
                return False

            if not context.match("SYM", "}"):
                context.pos = pos
                return False


        return True 


class ListaParametrosTemplate(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ListaParametrosTemplate>")
        if not ParametroTemplate().interpret(context):
            return False
        while context.match("SYM", ","):
            if not ParametroTemplate().interpret(context):
                return False
        return True

class ParametroTemplate(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ParametroTemplate>")
        return context.match("IDENTIFIER") and context.match("IDENTIFIER")

class EnunciadosTemplate(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <EnunciadosClass>")
        while True:
            pos = context.pos
            if not EnunciadoTemplate().interpret(context):
                context.pos = pos
                break
        return True  # ε es válido

class EnunciadoTemplate(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <EnunciadoClass>")
        pos = context.pos

        if Asignacion().interpret(context) and context.match("SYM", ";"):
            return True
        if Entrada().interpret(context) and context.match("SYM", ";"):
            return True
        if Salida().interpret(context) and context.match("SYM", ";"):
            return True
        if Seleccion().interpret(context):
            return True
        if Iteracion().interpret(context):
            return True
        if Retorno().interpret(context) and context.match("SYM", ";"):
            return True

        context.pos = pos
        return False


#Estructuras y clases-------------------------------------------------------------
# Representa la regla <DeclaracionCompuesta>
class DeclaracionCompuesta(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <DeclaracionCompuesta>")
 
        # union <id> { <miembros_union> }
        if context.match("UNION"):
            if context.match("IDENTIFIER"):
                if context.match("SYM", "{"):
                    if MiembrosUnion().interpret(context):
                        if context.match("SYM", "}"):
                            context.match("SYM", ";")
      

           # struct <id> <herencia> { <miembros_union> }
        if context.match("STRUCT"):
            if context.match("IDENTIFIER"):
                if context.match("SYM", "{"):
                    if MiembrosUnion().interpret(context):
                        if context.match("SYM", "}"):
                            context.match("SYM", ";")
                            

        # class <id> <herencia> { <miembros_class> }
        if context.match("CLASS"):
            if context.match("IDENTIFIER"):
                if context.match("SYM", "{"):
                    if MiembrosClass().interpret(context):
                        if context.match("SYM", "}"):
                            context.match("SYM", ";")
                               
        return True # ε (opcional)


class Visibilidad(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Visibilidad>")
        pos = context.pos

        if context.match("PUBLIC") or context.match("PRIVATE") or context.match("PROTECTED"): # COLON 
            if context.match("COLON", ":"):  # public, private, protected 
                return True

        context.pos = pos
        return False
    
class MiembrosClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <MiembrosClass>")
        
        
        while True:
            
            pos = context.pos
            
            print("Buscando miembros de clase pos", pos)

            # Caso: <visibilidad> <miembro_class>
            if (Visibilidad().interpret(context)==True):
                print("Visibilidad encontrada")
                if (MiembroClass().interpret(context)==True):
                    print("Miembro encontrado en miembro class 1")
                    continue  # sigue con más miembros
                else:
                    #context.pos = pos
                    break
            
            context.pos = pos
            print("Buscando miembros de clase en la posición", context.pos)

            # Caso: <miembro_class>
            if (MiembroClass().interpret(context)==True):
                print("Miembro encontrado en miembros class 2")
                continue  # sigue con más miembros

            print("⚠️ No se encontró un miembro de clase válido", context.pos)    
            break

        return True  # siempre válido (ε permitido)


class MiembroClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <MiembroClass>")
        pos = context.pos

        if DeclaracionClass().interpret(context):
            return True

        if FuncionesClass().interpret(context):
            return True
        #context.pos = pos
        return False


class MiembrosUnion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <MiembrosUnion>")
        while Declaracion().interpret(context):
            pass
        return True

class FuncionesClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <FuncionesClass>")
        while True:
            if (FuncionClass().interpret(context) == False):
                break
        return False  # ε es válido

#funcion de clase fue la ultima

class FuncionClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <FuncionClass>")
        pos = context.pos

           #COnstructor 
        if context.match("IDENTIFIER"):
            if context.match("SYM", "("):
                if context.match("SYM", ")"):
                    if context.match("SYM", ";"):
                        return True
                
        context.pos = pos

           #COnstructor 
        if context.match("IDENTIFIER"):
            if context.match("SYM", "("):
                if context.match("SYM", ")"):
                    if context.match("SYM", "{"): 
                        if context.match("SYM", "}"):
                            return True
        context.pos = pos
        
        # Destructor
        if context.match("IDENTIFIER"):
            if context.match("SYM", "("):
                    EnunciadosClass().interpret(context)
                    RetornoClass().interpret(context)
                    if context.match("SYM", ")") and context.match("SYM", "{"):
                        return context.match("SYM", "}")
                    

        context.pos = pos

        # Opcional: <modificador_función>
        ModificadorFuncion().interpret(context)

        context.pos = pos

        # <tipo_función> <nombre_class_función>(...)
        if TipoFuncion().interpret(context):
            print("Tipo de función encontrado")
            if NombreClassFuncion().interpret(context):
                if context.match("SYM", "("):
                    Parametros().interpret(context)
                    if context.match("SYM", ")") and context.match("SYM", "{"):
                        EnunciadosClass().interpret(context)
                        RetornoClass().interpret(context)
                        if context.match("SYM", "}"):
                            return True

        print("⚠️ No se encontró una función válida", pos)
        context.pos = pos
        print("⚠️ No se encontró una función válida", pos)
        return False

class NombreClassFuncion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <NombreClassFuncion>")
        pos = context.pos

        # Caso: <identifier>
        if context.match("IDENTIFIER"):
            return True

        # Caso: operator <operador_valido>
        if context.match("OPERATOR"):
            if OperadorValido().interpret(context):
                return True

        context.pos = pos
        return False
    
class OpcionesClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <OpcionesClass>")
        pos = context.pos

        # this
        if context.match("THIS"):
            return True

        # * this
        if context.match("SYM", "*"):
            if context.match("THIS"):
                return True
            context.pos = pos

        # this -> <identifier>
        if context.match("THIS"):
            if context.match("ARROW") and context.match("IDENTIFIER"):
                return True
            context.pos = pos

        # (* this) . <identifier>
        if context.match("SYM", "("):
            if context.match("SYM", "*") and context.match("THIS") and context.match("SYM", ")"):
                if context.match("DOT") and context.match("IDENTIFIER"):
                    return True
            context.pos = pos

        # <identifier>
        if context.match("IDENTIFIER"):
            return True

        context.pos = pos
        return False

class ValorEnumClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ValorEnumClass>")
        pos = context.pos

        if context.match("IDENTIFIER"):
            # opción con asignación: <identifier> = <expresion_class>
            if context.match("EQ"):
                if ExpresionClass().interpret(context):
                    return True
            return True  # solo <identifier>

        context.pos = pos
        return False

class ListaValoresClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ListaValoresClass>")
        if ValorEnumClass().interpret(context):
            if context.match("SYM", ","):
                return self.interpret(context)  # llamada recursiva
            return True  # una sola entrada
        return False

class OperadorValido(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <OperadorValido>")
        pos = context.pos

        # Operadores de un solo símbolo
        if context.match("SYM", "+"):
            return True
        if context.match("SYM", "-"):
            return True
        if context.match("SYM", "*"):
            return True
        if context.match("SYM", "/"):
            return True
        if context.match("SYM", "<"):
            return True
        if context.match("SYM", ">"):
            return True

        # Operadores dobles: == y !=
        if context.match("SYM", "="):
            if context.match("SYM", "="):
                return True
            context.pos = pos  # restaurar si solo encontró uno

        if context.match("SYM", "!"):
            if context.match("SYM", "="):
                return True
            context.pos = pos

        # Operador: []
        if context.match("LBRACK"):
            if context.match("RBRACK"):
                return True
            context.pos = pos

        # Operador: ()
        if context.match("LPAREN"):
            if context.match("RPAREN"):
                return True
            context.pos = pos

        context.pos = pos
        return False

class EnunciadosClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <EnunciadosClass>")
        while True:
            pos = context.pos
            if not EnunciadoClass().interpret(context):
                context.pos = pos
                break
        return True  # ε es válido

class EnunciadoClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <EnunciadoClass>")
        pos = context.pos

        if AsignacionClass().interpret(context) and context.match("SYM", ";"):
            return True
        if Entrada().interpret(context) and context.match("SYM", ";"):
            return True
        if Salida().interpret(context) and context.match("SYM", ";"):
            return True
        if Seleccion().interpret(context):
            return True
        if Iteracion().interpret(context):
            return True
        if LlamadaFuncion().interpret(context) and context.match("SYM", ";"):
            return True
        if SwitchClass().interpret(context):
            return True
        if Corrutina().interpret(context) and context.match("SYM", ";"):
            return True
        if context.match("GOTO") and context.match("IDENTIFIER") and context.match("SYM", ";"):
            return True
        if context.match("IDENTIFIER") and context.match("SYM", ":"):
            if self.interpret(context):  # llamada recursiva
                return True
        if context.match("THROW"):
            if ExpresionClass().interpret(context) and context.match("SYM", ";"):
                return True
            context.pos = pos
        if context.match("TRY"):
            if context.match("SYM", "{"):
                if EnunciadosClass().interpret(context) and context.match("SYM", "}"):
                    if context.match("CATCH") and context.match("SYM", "("):
                        if Tipo().interpret(context) and context.match("IDENTIFIER") and context.match("SYM", ")"):
                            if context.match("SYM", "{") and EnunciadosClass().interpret(context) and context.match("SYM", "}"):
                                return True
        if DeclaracionClass().interpret(context):
            return True
        if DeclaracionTipo().interpret(context): 
            return True
        if BloqueTryClass().interpret(context):
            return True

        context.pos = pos
        return False


class DeclaracionClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <DeclaracionClass>")
        pos = context.pos

        # enum <identifier> { <lista_valores> } ;
        if context.match("ENUM"):
            if context.match("IDENTIFIER") and context.match("SYM", "{"):
                if ListaValoresClass().interpret(context) and context.match("SYM", "}"):
                    if context.match("SYM", ";"):
                        return True
            context.pos = pos
            return False

        # <constructor> -> <identifier>(<parámetros>){...}
        if context.match("CONSTRUCTOR"):  # debes mapear esta palabra clave en tu lexer
            if context.match("SYM", "->") and context.match("IDENTIFIER"):
                if context.match("SYM", "("):
                    Parametros().interpret(context)
                    if context.match("SYM", ")") and context.match("SYM", "{"):
                        EnunciadosClass().interpret(context)
                        if context.match("SYM", "}"):
                            return True
            context.pos = pos
            return False

        # <destructor> -> ~<identifier>(){...}
        if context.match("DESTRUCTOR"):  # debes mapear esta palabra clave también
            if context.match("SYM", "->") and context.match("SYM", "~") and context.match("IDENTIFIER"):
                if context.match("SYM", "(") and context.match("SYM", ")") and context.match("SYM", "{"):
                    EnunciadosClass().interpret(context)
                    if context.match("SYM", "}"):
                        return True
            context.pos = pos
            return False

        # Comunes: <modificador> <tipo> <identifier>
        if Modificador().interpret(context):
            if Tipo().interpret(context):
                if context.match("IDENTIFIER"):
                    
                    # <modificador> <tipo> <identifier> ;
                    if context.match("SYM", ";"):
                        return True

                    # <modificador> <tipo> <identifier> = <opciones_class> ;
                    if context.match("EQ"):
                        if OpcionesClass().interpret(context) and context.match("SYM", ";"):
                            return True

                        # <modificador> <tipo> <identifier> = <identifier>.<identifier>(<argumentos>) ;
                        if context.match("IDENTIFIER") and context.match("DOT") and context.match("IDENTIFIER"):
                            if context.match("SYM", "("):
                                Argumentos().interpret(context)  # puede ser ε
                                if context.match("SYM", ")") and context.match("SYM", ";"):
                                    return True

        context.pos = pos
        return False


class Modificador(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Modificador>")
        pos = context.pos

        modificadores = [
            "CONST", "INLINE", "MUTABLE", "REGISTER", "ALIGNAS", "THREAD_LOCAL",
            "VOLATILE", "TYPEDEF",
            "DECLTYPE", "CONSTEXPR", "CONSTEVAL", "CONSTINIT"  # meta_programación
        ]

        context.match("MODIFICADOR")  # Si el lexer separa tipos, esto puede ser más limpio

        for mod in modificadores:
            if context.match(mod):
                return True

        context.pos = pos
        return True  # ε es válido

class DeclaracionTipo(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <DeclaracionTipo>")
        pos = context.pos

        if not Modificador().interpret(context):
            return False

        tipo = None
        if context.match("INT"):
            tipo = "INT"
        elif context.match("FLOAT"):
            tipo = "FLOAT"
        elif context.match("DOUBLE"):
            tipo = "DOUBLE"
        elif context.match("CHAR"):
            tipo = "CHAR"
        elif context.match("BOOL"):
            tipo = "BOOL"
        elif context.match("STRING"):
            tipo = "STRING"
        elif context.match("SHORT"):
            tipo = "SHORT"
        elif context.match("LONG"):
            tipo = "LONG"
        elif context.match("SIGNED"):
            tipo = "SIGNED"
        else:
            context.pos = pos
            return False

        if not context.match("IDENTIFIER"):  # variable name
            context.pos = pos
            return False

        if not context.match("EQ"):
            context.pos = pos
            return False

        if tipo in ["INT", "SHORT", "LONG", "SIGNED"]:
            if not ExpresionEntero().interpret(context):
                context.pos = pos
                return False
        elif tipo in ["FLOAT", "DOUBLE"]:
            if not ExpresionDecimal().interpret(context):
                context.pos = pos
                return False
        elif tipo == "CHAR":
            if not context.match("CHAR_LITERAL"):
                context.pos = pos
                return False
        elif tipo == "BOOL":
            if not context.match("TRUE") and not context.match("FALSE"):
                if not ExpresionComparacionBooleana().interpret(context):
                    context.pos = pos
                    return False
        elif tipo == "STRING":
            if not context.match("STR_LITERAL"):
                context.pos = pos
                return False

        return context.match("SYM", ";")

class BloqueTryClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <BloqueTryClass>")
        pos = context.pos

        if context.match("TRY") and context.match("SYM", "{"):
            if EnunciadosClass().interpret(context) and context.match("SYM", "}"):
                if BloquesCatchClass().interpret(context):
                    return True

        context.pos = pos
        return False

class BloquesCatchClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <BloquesCatch>")
        pos = context.pos

        if context.match("CATCH"):
            if context.match("SYM", "("):
                if Tipo().interpret(context) and context.match("IDENTIFIER") and context.match("SYM", ")"):
                    if context.match("SYM", "{") and EnunciadosClass().interpret(context) and context.match("SYM", "}"):
                        BloquesCatchClass().interpret(context)  # Recursión opcional
                        return True
        else:
            return True  # ε

        context.pos = pos
        return False

class AsignacionClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <AsignacionClass>")
        pos = context.pos

        if AsignacionInt().interpret(context) and context.match("SYM", ";"):
            return True
        if AsignacionOtherClass().interpret(context):
            return True

        context.pos = pos
        return False

class AsignacionOtherClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <AsignacionOtherClass>")
        pos = context.pos

        if context.match("IDENTIFIER"):
            if context.match("EQ"):
                if ExpresionesClass().interpret(context) and context.match("SYM", ";"):
                    return True

        context.pos = pos
        return False


class ExpresionesClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ExpresionesClass>")
        pos = context.pos

        # <expresión_class> <operador_aritmético> <expresión_class>
        if ExpresionClass().interpret(context):
            if OperadorAritmetico().interpret(context):
                if ExpresionClass().interpret(context):
                    return True
        context.pos = pos

        # ( <expresión_class> <operador_aritmético> <expresión_class> )
        if context.match("SYM", "("):
            if ExpresionClass().interpret(context):
                if OperadorAritmetico().interpret(context):
                    if ExpresionClass().interpret(context) and context.match("SYM", ")"):
                        return True
        context.pos = pos
                

        if ExpresionClass().interpret(context):
            return True
        return False

class ExpresionClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ExpresionClass>")
        pos = context.pos

        # <identifier>
        if context.match("IDENTIFIER"):
            return True

        # <entero>
        if context.match("INT_LITERAL"):
            return True

        # <decimal>
        if context.match("FLOAT_LITERAL"):
            return True

        # nullptr
        if context.match("NULLPTR"):
            return True

        # <conversión> <tipo> ( <expresión_class> )
        if Conversion().interpret(context):
            if Tipo().interpret(context) and context.match("SYM", "("):
                if self.interpret(context) and context.match("SYM", ")"):
                    return True
                context.pos = pos

#        # <expresión_class> <operador_aritmético> <expresión_class>
        if self.interpret(context):
            if OperadorAritmetico().interpret(context):
                if self.interpret(context):
                    return True
            context.pos = pos
#
 #       # ( <expresión_class> <operador_aritmético> <expresión_class> )
        if context.match("SYM", "("):
            if self.interpret(context):
                if OperadorAritmetico().interpret(context):
                    if self.interpret(context) and context.match("SYM", ")"):
                        return True
            context.pos = pos

        # this
        if context.match("THIS"):
            return True

        # * this
        if context.match("SYM", "*") and context.match("THIS"):
            return True

        # this -> <identifier>
        if context.match("THIS"):
            if context.match("ARROW") and context.match("IDENTIFIER"):
                return True
            context.pos = pos

        # (* this) . <identifier>
        if context.match("SYM", "("):
            if context.match("SYM", "*") and context.match("THIS") and context.match("SYM", ")"):
                if context.match("DOT") and context.match("IDENTIFIER"):
                    return True
            context.pos = pos

        context.pos = pos
        return False

class Conversion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Conversión>")
        return (
            context.match("CONST_CAST") or
            context.match("DYNAMIC_CAST") or
            context.match("STATIC_CAST") or
            context.match("REINTERPRET_CAST")
        )

class SwitchClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <SwitchClass>")
        pos = context.pos

        if context.match("SWITCH") and context.match("SYM", "("):
            if context.match("IDENTIFIER") and context.match("SYM", ")"):
                if context.match("SYM", "{"):
                    if CasosClass().interpret(context) and context.match("SYM", "}"):
                        return True

        context.pos = pos
        return False

class CasosClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <CasosClass>")
        pos = context.pos

        # case <tipo_casos> : <enunciados_switch_class> <casos_class>
        if context.match("CASE"):
            if TipoCasos().interpret(context) and context.match("SYM", ":"):
                if EnunciadosSwitchClass().interpret(context):
                    CasosClass().interpret(context)  # recursivo
                    return True
            context.pos = pos

        # default : <enunciados_switch_class>
        if context.match("DEFAULT") and context.match("SYM", ":"):
            if EnunciadosSwitchClass().interpret(context):
                return True
            context.pos = pos

        # ε
        return True

class TipoCasos(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <TipoCasos>")
        return (
            context.match("STRING_LITERAL") or  # <cadena>
            context.match("INT_LITERAL") or     # <entero>
            context.match("FLOAT_LITERAL")      # <decimal>
        )


class EnunciadosSwitchClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <EnunciadosSwitchClass>")
        while True:
            pos = context.pos
            if not EnunciadoSwitchClass().interpret(context):
                context.pos = pos
                break
        return True  # ε

class EnunciadoSwitchClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <EnunciadoSwitchClass>")
        pos = context.pos

        if AsignacionClass().interpret(context) and context.match("SYM", ";"):
            return True
        if Entrada().interpret(context) and context.match("SYM", ";"):
            return True
        if Salida().interpret(context) and context.match("SYM", ";"):
            return True
        if Seleccion().interpret(context):
            return True
        if SwitchClass().interpret(context):
            return True
        if Iteracion().interpret(context):
            return True
        if LlamadaFuncion().interpret(context) and context.match("SYM", ";"):
            return True
        if context.match("BREAK") and context.match("SYM", ";"):
            return True
        if context.match("CONTINUE") and context.match("SYM", ";"):
            return True

        context.pos = pos
        return False

class ModificadorFuncionClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ModificadorFuncionClass>")
        return any(context.match(tok) for tok in [
            "NOEXCEPT", "REQUIRES", "TEMPLATE", "STATIC_ASSERT", "VIRTUAL", "FRIEND"
        ])


class RetornoClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Retorno>")
        pos = context.pos

        if context.match("RETURN"):
            if ExpresionClass().interpret(context) and context.match("SYM", ";"):
                return True

        # ε permitido
        context.pos = pos
        return True
    




#Aqui empieza el main------------------------------------------------------------------------------------
# Representa la función principal int main(void) { ... }
class FuncionPrincipal(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <FuncionPrincipal>")
        pos = context.pos

        if not context.match("INT"):
            return False
        if not context.match("MAIN"):
            return False
        if not context.match("SYM", "("):
            return False
        if not context.match("VOID", "void"):
            print("⚠️ Se recomienda void")
        if not context.match("SYM", ")"):
            return False
        if not context.match("SYM", "{"):
            return False

        print("▶ Dentro de main: analizando <Enunciados>")
        Enunciados().interpret(context)

        # Aquí validamos: return 0;
        print("▶ Dentro del main: Verificando return 0;")
        if not context.match("RETURN"):
            print("⚠️ Se recomienda 'return'")
        if not context.match("INT_LITERAL", "0"):
            print("⚠️ Se recomienda '0'")
        if not context.match("SYM", ";"):
            print("⚠️ Se recomienda ';'")
        # No es necesario verificar el return, ya que puede ser void pero es recomendable

        if not context.match("SYM", "}"):
            print("⚠️ Se recomienda cierre '}'")
            context.pos = pos
            return False

        return True


# Representa una <Declaración> de variable
class Declaracion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Declaración>")
        pos_backup = context.pos
        tipos_validos = ["INT", "STRING", "CHAR", "FLOAT", "LONG", "DOUBLE"]

        # Verifica si el tipo es uno de los esperados
        for tipo in tipos_validos:
            print(f"Buscando tipo: {tipo}")
            if context.match(tipo):
                print(f"Tipo encontrado: {tipo}")
                break
        else:
            tipo = None

        if tipo:
            if tipo == "LONG":  # Caso especial para long int
                if not context.match("INT"):
                    context.pos = pos_backup
                    return False
            if not context.match("IDENTIFIER"):
                context.pos = pos_backup
                return False
            # Declaración sin inicialización
            if context.match("SYM", ";"):
                return True
            # Declaración con inicialización
            if not context.match("EQ"):
                context.pos = pos_backup
                return False
            valor_esperado = {
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

        # Declaración tipo std::string abc = "abc";
        if context.match("IDENTIFIER", "std"):
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

# Representa una lista de <enunciado> dentro de un bloque
class Enunciados(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Enunciados>")
        success = False
        while Enunciado().interpret(context):
            success = True
        return success  # Devuelve True si al menos se interpretó uno


# Representa un <enunciado>
class Enunciado(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Enunciado>")
        pos = context.pos

        # throw <expresión> ;
        if context.match("THROW"):
            if Expresion().interpret(context) and context.match("SYM", ";"):
                return True
            context.pos = pos

        # goto <identifier> ;
        if context.match("GOTO"):
            if context.match("IDENTIFIER") and context.match("SYM", ";"):
                return True
            context.pos = pos

        # <identifier> : <enunciado>
        if context.match("IDENTIFIER"):
            if context.match("SYM", ":"):
                if self.interpret(context):
                    return True
            context.pos = pos

        # try { <enunciados> } catch ( <tipo> <identifier> ) { <enunciados> }
        if BloqueTry().interpret(context):
            return True

        # asm("string") ;
        if context.match("ASM"):
            if context.match("SYM", "(") and context.match("STRING_LITERAL") and context.match("SYM", ")") and context.match("SYM", ";"):
                return True
            context.pos = pos

        # delete <identifier>
        if context.match("DELETE"):
            if context.match("IDENTIFIER"):
                return True
            context.pos = pos

        # sizeof(<identifier>)
        if context.match("SIZEOF"):
            if context.match("SYM", "(") and context.match("IDENTIFIER") and context.match("SYM", ")"):
                return True
            context.pos = pos
        return (
            Declaracion().interpret(context) or #check
            (Asignacion().interpret(context) and context.match("SYM", ";")) or
            Entrada().interpret(context) or
            Salida().interpret(context)  or
            Seleccion().interpret(context) or 
            Iteracion().interpret(context) or
            (LlamadaFuncion().interpret(context) and context.match("SYM", ";")) or
            Switch().interpret(context) or
            (Corrutina().interpret(context) and context.match("SYM", ";"))
        )
    
class BloqueTry(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <BloqueTry>")
        pos = context.pos

        if context.match("TRY"):
            if context.match("SYM", "{") and Enunciados().interpret(context) and context.match("SYM", "}"):
                if BloquesCatch().interpret(context):
                    return True

        context.pos = pos
        return False

class BloquesCatch(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <BloquesCatch>")
        pos = context.pos

        if context.match("CATCH"):
            if context.match("SYM", "("):
                if Tipo().interpret(context) and context.match("IDENTIFIER") and context.match("SYM", ")"):
                    if context.match("SYM", "{") and Enunciados().interpret(context) and context.match("SYM", "}"):
                        # Llamada recursiva para más bloques catch
                        BloquesCatch().interpret(context)
                        return True
        else:
            # Épsilon (ε) válido
            return True

        context.pos = pos
        return False

class Tipo(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Tipo>")
        pos = context.pos

        tipos_simples = [
            "INT", "FLOAT", "DOUBLE", "CHAR", "STRING", "BOOL", "SHORT", "LONG", "SIGNED",
            "UNSIGNED", "WCHAR_T", "CHAR8_T", "CHAR16_T", "CHAR32_T", "AUTO"
        ]

        if any(context.match(tipo) for tipo in tipos_simples):
            # manejar combinaciones como 'short int', 'long int', etc.
            context.match("INT")  # opcional
            return True

        context.pos = pos

        # decltype ( <expresion> )
        if context.match("DECLTYPE") and context.match("SYM", "("):
            if Expresion().interpret(context) and context.match("SYM", ")"):
                return True

        context.pos = pos
        return False

class Corrutina(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Corrutina>")
        pos = context.pos

        if context.match("CO_AWAIT"):
            if Expresion().interpret(context):
                return True

        if context.match("CO_YIELD"):
            if Expresion().interpret(context):
                return True

        if context.match("CO_RETURN"):
            if Expresion().interpret(context):
                return True

        context.pos = pos
        return False
    
# Agrupa todas las variantes de <asignacion>
class Asignacion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("\u25b6 Analizando <Asignacion>")
        return (
            AsignacionInt().interpret(context) or
            AsignacionOther().interpret(context) 
        )

# <asignacion-int> -> <nombre> = <expresiones> ; | <nombre>++ ; | <nombre>-- ;
class AsignacionInt(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <AsignacionInt>")
        pos = context.pos

        # Caso 1: x_ = <expresión> ;
        if context.match("IDENTIFIER"):
            if context.match("EQ"):
                if Expresiones().interpret(context):
                    return True
            # Post-incremento: x_++ ;
            elif context.match("OP_SYM", "+") and context.match("OP_SYM", "+"):
                return True
            # Post-decremento: x_-- ;
            elif context.match("MINUS", "-") and context.match("MINUS", "-"):
                return True
            context.pos = pos  # restaurar si no fue post incremento válido

        # Caso 2: ++x_ ;
        context.pos = pos
        if context.match("OP_SYM", "+") and context.match("OP_SYM", "+"):
            if context.match("IDENTIFIER"):
                return True

        # Caso 3: --x_ ;
        context.pos = pos
        if context.match("MINUS", "-") and context.match("MINUS", "-"):
            if context.match("IDENTIFIER"):
                return True

        context.pos = pos
        return False

# El resto sigue la misma estructura
class AsignacionOther(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <AsignacionOther>")
        pos = context.pos

        # <identifier> = <expresiones> ;
        if context.match("IDENTIFIER"):
            if context.match("EQ"):
                if Expresiones().interpret(context):
                    if context.match("SYM", ";"):
                        return True

        context.pos = pos
        return False


#Entrada y salida-------------------------------------------------------------
# Representa entrada: cin >> variable; o std::cin >> variable;
# Representa entrada: cin >> variable; o std::cin >> variable;
class Entrada(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Entrada>")
        pos_backup = context.pos

        # Opción: std::cin
        if context.match("IDENTIFIER", "std"):
            if not context.match("SCOPE", "::") or not context.match("CIN"):
                context.pos = pos_backup
                return False
        # Opción directa: cin
        elif not context.match("CIN"):
            return False

        if not context.match("SHIFT_RIGHT"): return False
        if not context.match("IDENTIFIER"): return False
        if not context.match("SYM", ";"): return False
        return True

class Salida(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Salida>")
        pos_backup = context.pos

        # Aceptar std::cout o cout
        if context.match("IDENTIFIER", "std"):
            if not context.match("SCOPE", "::") or not context.match("COUT"):
                context.pos = pos_backup
                return False
        elif not context.match("COUT"):
            context.pos = pos_backup
            return False

        print("▶ Manejando múltiples elementos con <<")

        while context.match("SHIFT_LEFT"):
            # 1. std::endl
            std_pos = context.pos
            if context.match("IDENTIFIER", "std"):
                if context.match("SCOPE", "::") and context.match("IDENTIFIER", "endl"):
                    print("✅ Encontrado std::endl")
                    continue
                else:
                    context.pos = std_pos  # rollback si std sin endl

            # 2. arreglo[index]
            if match_identificador_indexado(context):
                continue

            # 3. string literal
            if context.match("STR_LITERAL"):
                continue

            # 4. identificador simple
            if context.match("IDENTIFIER"):
                continue

            # Si no coincide nada válido, error
            context.pos = pos_backup
            return False

        # Finaliza con ;
        if not context.match("SYM", ";"):
            context.pos = pos_backup
            return False

        return True


class Seleccion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Seleccion>")
        pos = context.pos
        if context.match("IF"):
            print("✅ Encontrado IF")
            if context.match("SYM", "("):
                print("✅ Encontrado SYM '(' — ahora analizamos condiciones")
                if Condiciones().interpret(context):
                    print("✅ Condiciones interpretadas correctamente")
                    if context.match("SYM", ")") and context.match("SYM", "{"):
                        print("✅ Abriendo bloque '{' — interpretando enunciados del if")
                        Enunciados().interpret(context)
                        if context.match("SYM", "}"):
                            print("✅ Cierre de bloque '}' — revisando else")
                            BloquesElse().interpret(context)
                            return True
        print("⚠️ Se esperaba un bloque if válido")
        context.pos = pos
        return False


class BloquesElse(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        if context.match("ELSE"):
            if context.match("IF"):
                if context.match("SYM", "(") and Condiciones().interpret(context) and context.match("SYM", ")"):
                    if context.match("SYM", "{"):
                        Enunciados().interpret(context)
                        if context.match("SYM", "}"):
                            return BloquesElse().interpret(context)
                        return False
            elif context.match("SYM", "{"):
                Enunciados().interpret(context)
                return context.match("SYM", "}")
        return True

# Representa una declaración dentro de un for (...)
class DeclaracionFor(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <DeclaracionFor>")
        pos = context.pos
        tipos_validos = ["INT", "STRING", "CHAR", "FLOAT", "LONG", "DOUBLE"]
        for tipo in tipos_validos:
            if context.match(tipo):
                if tipo == "LONG" and not context.match("INT"):
                    context.pos = pos
                    return False
                if context.match("IDENTIFIER") and context.match("EQ") and Expresiones().interpret(context):
                    return True
        context.pos = pos
        return False


class Iteracion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Iteracion>")
        pos = context.pos

        # while (...)
        if context.match("WHILE") and context.match("SYM", "("):
            if Condiciones().interpret(context) and context.match("SYM", ")") and context.match("SYM", "{"):
                Enunciados().interpret(context)
                return context.match("SYM", "}")

        context.pos = pos

        # for (...)
        if context.match("FOR") and context.match("SYM", "("):
            if DeclaracionFor().interpret(context) and context.match("SYM", ";") and \
               Condiciones().interpret(context) and context.match("SYM", ";") and \
               AsignacionInt().interpret(context):
                if context.match("SYM", ")") and context.match("SYM", "{"):
                    Enunciados().interpret(context)
                    return context.match("SYM", "}")

        context.pos = pos
        return False
# Representa la regla <Condiciones>

class Condiciones(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Condiciones>")
        return Condicion().interpret(context)
    
class OperadorRelacional(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <OperadorRelacional>")
        tok = context.current_token()
        if tok and tok[0] in {"GT", "LT", "EQ_EQ", "NEQ", "GTE", "LTE"}:
            print(f"✅ Encontrado REL_OP '{tok[1]}'")
            context.advance()
            return True
        print(f"ℹ️ Se esperaba REL_OP, pero se encontró {tok}")
        return False

class OperadorLogico(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <OperadorLogico1>")
        tok = context.current_token()
        if tok and tok[0] in {"AND", "OR"}:
            print(f"✅ Encontrado LOGIC_OP '{tok[1]}'")
            context.advance()
            return True
        return False

# Ajustamos Condicion.match_atomic para aceptar llamadas a métodos
class Condicion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Condicion>")
        pos = context.pos

        if (self.match_atomic(context) and
            OperadorRelacional().interpret(context) and
            self.match_atomic(context)):
            print("▶ Analizando <despues match_atomic>")
            if OperadorLogico().interpret(context):
                print("▶ Analizando <Operador Logico2222222222222>")
                return self.interpret(context)
            return True

        context.pos = pos
        return False

    def match_atomic(self, context: ParserContext) -> bool:
        return (
            print("▶ Analizando <Dentro de MatchAtomic>"),
            match_llamada_miembro(context) or
            context.match("INT_LITERAL") or
            context.match("FLOAT_LITERAL") or
            context.match("CHAR_LITERAL") or
            context.match("BOOL_LITERAL") or
            context.match("IDENTIFIER")
        )

class Expresiones(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Expresiones>")
        pos = context.pos

        # 1. ( <expresión> <operador_aritmético> <expresión> )
        if context.match("SYM", "("):
            if Expresion().interpret(context):
                if OperadorRelacional().interpret(context):
                    if Expresion().interpret(context) and context.match("SYM", ")"):
                        if context.match("OP_SYM", "?"):
                            if context.match("IDENTIFIER"):
                                if context.match("COLON", ":"):
                                    if context.match("IDENTIFIER"):
                                        return True
        context.pos = pos

        # 2. <expresión> <operador_aritmético> <expresión>
        if Expresion().interpret(context):
            if OperadorAritmetico().interpret(context):
                if Expresion().interpret(context):
                    return True
        context.pos = pos  # rollback

        # 3. ( <expresión> <operador_aritmético> <expresión> )
        if context.match("SYM", "("):
            if Expresion().interpret(context):
                if OperadorAritmetico().interpret(context):
                    if Expresion().interpret(context):
                        if context.match("SYM", ")"):
                            return True
        context.pos = pos  # rollback

        # 4. <expresión>
        if Expresion().interpret(context):
            return True

        # 5. <conversión> <tipo> ( <expresión> )
        if Conversion().interpret(context):
            if Tipo().interpret(context) and context.match("SYM", "("):
                if Expresion().interpret(context) and context.match("SYM", ")"):
                    return True
        context.pos = pos

        # 6. <expresion_ternaria>
        if ExpresionTernaria().interpret(context):
            return True
        context.pos = pos

        # 7. <expresion_ternaria>
        if ExpresionDecimal().interpret(context):
            return True
        context.pos = pos
        
        # 8. <expresion_ternaria>
        if ExpresionBooleana().interpret(context):
            return True
        context.pos = pos


        # 9. ( <expresión> <operador_aritmético> <expresión> )
        if context.match("SYM", "("):
            if Expresion().interpret(context):
                if OperadorRelacional().interpret(context):
                    if Expresion().interpret(context) and context.match("SYM", ")"):
                        return True
        context.pos = pos

        return False

class Expresion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Expresion>")
        pos = context.pos

        # 1. <identifier>
        if context.match("IDENTIFIER"):
            return True

        # 2. <entero>
        if context.match("INT_LITERAL"):
            return True

        # 3. <decimal>
        if context.match("FLOAT_LITERAL"):
            return True

        # 4. nullptr
        if context.match("NULLPTR"):
            return True
        
        context.pos = pos
        return False


# Representa una expresión ternaria
class ExpresionTernaria(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ExpresionTernaria>")
        pos = context.pos

        if Expresion().interpret(context):
            if context.match("SYM", "?"):
                if Expresion().interpret(context):
                    if context.match("SYM", ":"):
                        if Expresion().interpret(context):
                            return True

        context.pos = pos
        return False

class ExpresionDecimal(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ExpresionDecimal>")
        pos = context.pos

        if context.match("FLOAT_LITERAL"):
            return True

        context.pos = pos
        if context.match("FLOAT_LITERAL"):
            if OperadorAritmetico().interpret(context) and context.match("FLOAT_LITERAL"):
                return True

        context.pos = pos
        if context.match("SYM", "("):
            if context.match("FLOAT_LITERAL") and OperadorAritmetico().interpret(context) and context.match("FLOAT_LITERAL"):
                if context.match("SYM", ")"):
                    return True

        context.pos = pos
        return False

class ExpresionBooleana(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ExpresionBooleana>")
        pos = context.pos

        if context.match("TRUE") or context.match("FALSE"):
            return True

        if ExpresionComparacionBooleana().interpret(context):
            return True

        context.pos = pos
        return False

class ExpresionComparacionBooleana(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ExpresionComparacionBooleana>")
        pos = context.pos

        # entero <op_rel> entero
        if context.match("INT_LITERAL"):
            if OperadorRelacional().interpret(context) and context.match("INT_LITERAL"):
                return True

        context.pos = pos

        # decimal <op_rel> decimal
        if context.match("FLOAT_LITERAL"):
            if OperadorRelacional().interpret(context) and context.match("FLOAT_LITERAL"):
                return True

        context.pos = pos
        return False
# Representa un operador aritmético

class Switch(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("\u25b6 Analizando <Switch>")
        pos = context.pos
        if context.match("SWITCH") and context.match("SYM", "(") and context.match("IDENTIFIER") and context.match("SYM", ")") and context.match("SYM", "{"):
            Casos().interpret(context)
            return context.match("SYM", "}")
        context.pos = pos
        return False

class Casos(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        while context.match("CASE"):
            if context.match("STR_LITERAL") or context.match("INT_LITERAL"):
                if context.match("SYM", ":"):
                    Enunciados().interpret(context)
        if context.match("DEFAULT") and context.match("SYM", ":"):
            Enunciados().interpret(context)
        return True

class LlamadaFuncion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <LlamadaFuncion>")
        pos_backup = context.pos
        if not context.match("IDENTIFIER"): return False
        if not context.match("SYM", "("): return False
        # puede aceptar parámetros
        while True:
            if context.match("IDENTIFIER"):
                if not context.match("SYM", ","):
                    break
            else:
                break
        if not context.match("SYM", ")"): return False
        if not context.match("SYM", ";"): return False
        return True
    
class ModificadorVariable(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ModificadorVariable>")
        return any(context.match(tok) for tok in [
            "INLINE", "MUTABLE", "REGISTER", "ALIGNAS", "THREAD_LOCAL", "VOLATILE", "UNSIGNED", "CONST", "TYPEDEF"
        ])


class ExpresionEntero(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ExpresionEntero>")
        pos = context.pos

        if context.match("INT_LITERAL"):
            # Caso: <entero>
            return True

        context.pos = pos
        if context.match("INT_LITERAL"):
            if OperadorAritmetico().interpret(context) and context.match("INT_LITERAL"):
                return True
        context.pos = pos
        if context.match("SYM", "("):
            if context.match("INT_LITERAL") and OperadorAritmetico().interpret(context) and context.match("INT_LITERAL"):
                if context.match("SYM", ")"):
                    return True

        context.pos = pos
        return False


class OperadorAritmetico(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <OperadorAritmetico>")
        return (
            context.match("SYM", "+") or
            context.match("SYM", "-") or
            context.match("SYM", "*") or
            context.match("SYM", "/") or
            context.match("SYM", "%")
        )
    
class OperadorRelacional(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <OperadorRelacional>")
        tok = context.current_token()
        if tok and tok[0] in {"GT", "LT", "EQ_EQ", "NEQ", "GTE", "LTE"}:
            print(f"✅ Encontrado REL_OP '{tok[1]}'")
            context.advance()
            return True
        print(f"ℹ️ Se esperaba REL_OP, pero se encontró {tok}")
        return False

class OperadorLogico(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <OperadorLogico1>")
        tok = context.current_token()
        if tok and tok[0] in {"AND", "OR"}:
            print(f"✅ Encontrado LOGIC_OP '{tok[1]}'")
            context.advance()
            return True
        return False

#Fin del Main------------------------------------------------------------------------------------

#Iincio de funciones

# Clase para <argumentos>
class Argumentos(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Argumentos>")
        pos = context.pos

        # Caso base: ε (vacío)
        if context.current_token() == ("SYM", ")"):  # Se detecta cierre inmediato del paréntesis
            print("Argumentos: vacío")
            return True

        # Caso: <expresion>
        if Expresion().interpret(context):
            # Revisa si hay una coma para más argumentos
            if context.match("SYM", ","):
                if not self.interpret(context):  # Llamada recursiva
                    context.pos = pos
                    return False
            return True

        context.pos = pos
        return False


# Representa una lista de funciones al final del programa
class Funciones(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("\u25b6 Analizando <Funciones>")
        while Funcion().interpret(context):
            pass
        return True

class Funcion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("\u25b6 Analizando <Funcion>")
        pos = context.pos

        if TipoFuncion().interpret(context) and context.match("IDENTIFIER") and context.match("SYM", "("):
            Parametros().interpret(context)
            if context.match("SYM", ")") and context.match("SYM", "{"):
                Enunciados().interpret(context)
                Retorno().interpret(context)
                return context.match("SYM", "}")
        context.pos = pos
        return False

class ModificadorFuncion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ModificadorFuncion>")
        return( 
            context.match("NOEXCEPT") or 
            context.match("REQUIRES") or 
            context.match("TEMPLATE") or 
            context.match("STATIC_ASSERT") or 
            context.match("VIRTUAL")
        )


class TipoFuncion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        return (
            context.match("VOID") or
            context.match("INT") or
            context.match("FLOAT") or
            context.match("DOUBLE") or
            context.match("CHAR") or
            context.match("STRING") or
            context.match("BOOL")
        )

class Parametros(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("\u25b6 Analizando <Parametros>")
        pos = context.pos
        if TipoFuncion().interpret(context) and context.match("IDENTIFIER"):
            while context.match("SYM", ","):
                if not (TipoFuncion().interpret(context) and context.match("IDENTIFIER")):
                    context.pos = pos
                    return False
            return True
        return True  # ε (vacío)

class Retorno(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("\u25b6 Analizando <Retorno>")
        pos = context.pos
        if context.match("RETURN"):
            if Expresiones().interpret(context):
                context.match("SYM", ";")
                return True
            context.pos = pos
            return False
        return True  # ε
    

# Fin de la clase ParserContext ------------------------------------------------------------------------------------------------------------------------