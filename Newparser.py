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
            print(f"ℹ️ Se esperaba {expected_type} pero no hay más tokens.")
            return False
        
        if tok[0] != expected_type:
            print(f"ℹ️ Se esperaba {expected_type}, pero se encontró {tok[0]} ('{tok[1]}') en la posición {self.pos}.")
            return False
        
        # Permitir cualquier valor para LIBRARY si no se especifica expected_value
        if expected_type == "LIBRARY":
            print(f"✅ Match (LIBRARY): {tok[1]}")
            self.advance()
            return True
        #cambio mas reciente
        
        if expected_value and tok[1] != expected_value:
            print(f"ℹ️ Se esperaba valor '{expected_value}', pero se encontró '{tok[1]}' en la posición {self.pos}.")
            return False
        print(f"✅ Match: {expected_type} '{tok[1]}'")
        self.advance()
        return True   

# Interfaz base para todas las reglas del parser
class AbstractExpression:
    def interpret(self, context: ParserContext) -> bool:
        raise NotImplementedError  # Cada subclase debe implementar esta función

def match_identificador_indexado(context: ParserContext) -> bool:
    pos = context.pos
    if context.match("IDENTIFIER") and context.match("LBRACK") and context.match("IDENTIFIER") and context.match("RBRACK"):
        print("✅ Match: IDENTIFIER con índice (array access)")
        return True
    context.pos = pos
    return False


# Utilidad para reconocer llamadas como abc.length()
def match_llamada_miembro(context: ParserContext) -> bool:
    print("▶ Analizando <match_llamada_miembro>")
    pos = context.pos
    if context.match("IDENTIFIER") and context.match("DOT") and context.match("IDENTIFIER"):
        if context.match("SYM", "(") and context.match("SYM", ")"):
            print("✅ Match: llamada a método tipo objeto.metodo()")
            return True
    context.pos = pos
    return False

# Inicio Programa----------------------------------------------------------------------

# Representa la regla <Programa>
class Programa(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Programa>")
        print("Version 3AM")
        return (
            Librerias().interpret(context) and
            EspacioNombres().interpret(context) and
            DeclaracionCompuesta().interpret(context) and
            DeclaracionTemplate().interpret(context) and
            FuncionPrincipal().interpret(context) and
            Funciones().interpret(context) 
        )

#Arriba del main-----------------------------------------------------------------
# Representa la regla <Librerías> REVISAR POR EL ######
class Librerias(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Librerías>")
        print("test")
        # Acepta múltiples tokens LIBRARY
        while context.match("LIBRARY"):
            pass
        # Acepta la librería estándar
        return True
    
# Representa la regla <Librerías> 
class EspacioNombres(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Namespaces>")
        if context.match("USING"):
          print("se entro a using")      
          if not context.match("NAMESPACE"): return False
          if not context.match("IDENTIFIER", "std"): return False
          if not context.match("SYM", ";"): return False
        print("despues del if")
        # Acepta la librería estándar
        return True   



# Representa la regla <DeclaracionCompuesta>
class DeclaracionCompuesta(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <DeclaracionCompuesta>")
        pos = context.pos

        # union <id> { <miembros_union> }
        if context.match("UNION"):
            if context.match("IDENTIFIER"):
                if context.match("SYM", "{"):
                    if MiembrosUnion().interpret(context):
                        if context.match("SYM", "}"):
                            return True
        context.pos = pos

        # struct <id> <herencia>? { <miembros_union> }
        if context.match("STRUCT"):
            if context.match("IDENTIFIER"):
                Herencia().interpret(context)  # opcional
                if context.match("SYM", "{"):
                    if MiembrosUnion().interpret(context):
                        if context.match("SYM", "}"):
                            return True
        context.pos = pos

        # class <id> <herencia>? { <miembros_class> }
        if context.match("CLASS"):
            if context.match("IDENTIFIER"):
                Herencia().interpret(context)  # opcional
                if context.match("SYM", "{"):
                    if MiembrosClass().interpret(context):
                        if context.match("SYM", "}"):
                            return True
        context.pos = pos

        return False

class Herencia(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Herencia>")
        pos = context.pos

        if context.match("SYM", ":"):
            if context.match("VISIBILIDAD"):  # public, private, protected
                if context.match("IDENTIFIER"):  # clase base
                    return True

        context.pos = pos
        return True  # ε (opcional)

class Visibilidad(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Visibilidad>")
        pos = context.pos

        if context.match("PUBLIC") or context.match("PRIVATE") or context.match("PROTECTED"):
            return True

        context.pos = pos
        return False
    
class MiembrosClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <MiembrosClass>")
        while MiembroClass().interpret(context):
            pass
        return True

class MiembroClass(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <MiembroClass>")
        pos = context.pos

        # Caso: visibilidad seguida de otro miembro
        if Visibilidad().interpret(context):
            return MiembroClass().interpret(context)

        # Caso: declaración simple
        if DeclaracionFunc().interpret(context):
            return True

        # Caso: función dentro de clase
        if FuncionClass().interpret(context):
            return True

        context.pos = pos
        return False

class MiembrosUnion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <MiembrosUnion>")
        while Declaracion().interpret(context):
            pass
        return True

    
class DeclaracionTemplate(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <DeclaracionTemplate>")
        pos = context.pos

        if not context.match("TEMPLATE"): return False
        if not context.match("LT"): return False
        
        # template < template <id> >
        if not context.match("TEMPLATE"): 
            context.pos = pos
            return False
        if not context.match("LT"):
            context.pos = pos
            return False
        if not Id().interpret(context):  # <id>
            context.pos = pos
            return False
        if not context.match("GT"): 
            context.pos = pos
            return False
        if not context.match("GT"):  # cerrar ambos '<'
            context.pos = pos
            return False

        # <id> <identifier>
        if not Id().interpret(context):
            context.pos = pos
            return False
        if not context.match("IDENTIFIER"):
            context.pos = pos
            return False

        if not context.match("SYM", "("): return False
        if not ListaParametrosTemplate().interpret(context):
            context.pos = pos
            return False
        if not context.match("SYM", ")"): return False

        if not context.match("SYM", "{"): return False
        if not EnunciadosFuncion().interpret(context): return False
        if not context.match("SYM", "}"): return False

        return True

class Id(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Id>")
        tok = context.current_token()
        if tok and tok[0] == "IDENTIFIER" and tok[1].islower():
            context.advance()
            return True
        return False

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
        return Id().interpret(context) and context.match("IDENTIFIER")


#Dentro del main-----------------------------------------------------------------
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
            print("❌ Faltó void")
        if not context.match("SYM", ")"):
            return False
        if not context.match("SYM", "{"):
            return False

        print("▶ Dentro de main: analizando <Enunciados>")
        Enunciados().interpret(context)

        # Aquí validamos: return 0;
        print("▶ Dentro del main: Verificando return 0;")
        if not context.match("RETURN"):
            print("❌ Faltó 'return'")
        if not context.match("INT_LITERAL", "0"):
            print("❌ Faltó '0'")
        if not context.match("SYM", ";"):
            print("❌ Faltó ';'")
        # No es necesario verificar el return, ya que puede ser void pero es recomendable

        if not context.match("SYM", "}"):
            print("❌ Faltó cierre '}'")
            context.pos = pos
            return False
    
        print("▶ Fin de la función principal")

        return True

# Representa una lista de funciones al final del programa
class Funciones(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("\u25b6 Analizando <Funciones>")
        while Funcion().interpret(context):
            pass
        return True

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

        # Orden de evaluación de estructuras conocidas
        return (
            Declaracion().interpret(context) or
            (Asignacion().interpret(context) and context.match("SYM", ";")) or
            (Entrada().interpret(context) and context.match("SYM", ";")) or
            (Salida().interpret(context) and context.match("SYM", ";")) or
            Seleccion().interpret(context) or
            Iteracion().interpret(context) or
            (LlamadaFuncion().interpret(context) and context.match("SYM", ";")) or
            Switch().interpret(context) or
            (Corrutina().interpret(context) and context.match("SYM", ";"))
        )

    
# Clases necesatios para declaracion-------------------------------------------------------------------
class Declaracion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <Declaración>")
        pos = context.pos

        # enum <identifier> { <lista_valores> }
        if context.match("ENUM"):
            if context.match("IDENTIFIER") and context.match("SYM", "{"):
                if ListaValores().interpret(context):
                    if context.match("SYM", "}"):
                        if context.match("SYM", ";"):
                            return True
        context.pos = pos

        # <declaracion_tipo>
        if DeclaracionTipo().interpret(context):
            return True
        context.pos = pos

        # Opcional: <modificador>
        Modificador().interpret(context)  # no falla si es ε

        # <tipo>
        tipo_tokens = [
            "INT", "FLOAT", "DOUBLE", "CHAR", "BOOL", "STRING",
            "SHORT", "LONG", "SIGNED", "IDENTIFIER"  # incluye clases
        ]
        for tipo in tipo_tokens:
            if context.match(tipo):
                break
        else:
            context.pos = pos
            return False

        # <identifier>
        if not context.match("IDENTIFIER"):
            context.pos = pos
            return False

        # Casos de declaración:
        # 1. Arreglo: int x[5];
        if context.match("LBRACK"):
            if context.match("INT_LITERAL") and context.match("RBRACK"):
                return context.match("SYM", ";")
            context.pos = pos
            return False

        # 2. Asignación con identificador simple
        if context.match("EQ"):
            if context.match("IDENTIFIER"):
                return context.match("SYM", ";")

            # 3. Asignación con llamada a función: x = Clase().metodo()
            if context.match("IDENTIFIER"):
                if context.match("DOT"):
                    if context.match("IDENTIFIER") and context.match("SYM", "("):
                        Argumentos().interpret(context)  # puede ser ε
                        if context.match("SYM", ")"):
                            return context.match("SYM", ";")
            context.pos = pos
            return False

        # 4. Declaración simple: int x;
        if context.match("SYM", ";"):
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

class ListaValores(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ListaValores>")
        if not ValorEnum().interpret(context):
            return False
        while context.match("SYM", ","):
            if not ValorEnum().interpret(context):
                return False
        return True


class ValorEnum(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <ValorEnum>")
        pos = context.pos
        if context.match("IDENTIFIER"):
            if context.match("EQ"):
                if not Expresion().interpret(context):
                    context.pos = pos
                    return False
            return True
        return False

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


# Fin Representa la regla <DeclaracionFunc>-----------------------------------------------

# Agrupa todas las variantes de <asignacion> y sus clases necesarias-------------------------------
class Asignacion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("\u25b6 Analizando <Asignacion>")
        return (
            AsignacionInt().interpret(context) or
            AsignacionOther().interpret(context) 
        )


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
        return AsignacionInt().interpret(context)
    
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
                    print("✅ Match: std::endl")
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
            print("✅ Match: IF")
            if context.match("SYM", "("):
                print("✅ Match: SYM '(' — ahora analizamos condiciones")
                if Condiciones().interpret(context):
                    print("✅ Condiciones interpretadas correctamente")
                    if context.match("SYM", ")") and context.match("SYM", "{"):
                        print("✅ Abriendo bloque '{' — interpretando enunciados del if")
                        Enunciados().interpret(context)
                        if context.match("SYM", "}"):
                            print("✅ Cierre de bloque '}' — revisando else")
                            BloquesElse().interpret(context)
                            return True
        print("❌ Falló el bloque if")
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
               AsignacionFor().interpret(context):
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
            print(f"✅ Match: REL_OP '{tok[1]}'")
            context.advance()
            return True
        print(f"ℹ️ Se esperaba REL_OP, pero se encontró {tok}")
        return False

class OperadorLogico(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        print("▶ Analizando <OperadorLogico1>")
        tok = context.current_token()
        if tok and tok[0] in {"AND", "OR"}:
            print(f"✅ Match: LOGIC_OP '{tok[1]}'")
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
        return Expresion().interpret(context)

class Expresion(AbstractExpression):
    def interpret(self, context: ParserContext) -> bool:
        pos = context.pos
        if context.match("IDENTIFIER") or context.match("INT_LITERAL"):
            if context.match("ARITH_OP"):
                return Expresion().interpret(context)
            return True
        if context.match("SYM", "("):
            if Expresion().interpret(context) and context.match("ARITH_OP") and Expresion().interpret(context):
                return context.match("SYM", ")")
        context.pos = pos
        return False

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


#Funciones-------------------------------------------------------------------------------------------
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
            if Expresion().interpret(context):
                context.match("SYM", ";")
                return True
            context.pos = pos
            return False
        return True  # ε
# Fin de la clase ParserContext