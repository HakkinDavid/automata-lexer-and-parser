import re
from typing import Dict, List, Tuple, Callable, Set
from colorama import Fore, Back, Style


class Lexer:
    mapa_escapes = {"\\\\space": " ", "\\\"": "\"", "\\\\comma": ","}
    regex_rango = re.compile(r"(\S)\.\.\.(\S)")
    regex_separador = re.compile(r",\s*")
    regex_transicion = re.compile(r'^(\w+)\s*->\s*(\w+)\s*\[label="((?:\\.|[^"\\])*)"\]')
    regex_nodo = re.compile(r'^(\w+)\s*\[shape=(\w+)')
    mapa_tokens_finales = {
        "q_id": "IDENTIFIER",
        "q_digit": "INT_LITERAL",
        "q_float_digit": "FLOAT_LITERAL",
        "q_char_close": "CHAR_LITERAL",
        "q_string_close": "STR_LITERAL",
        "q_inc_gt": "LIBRARY",
    }

    def __init__(self, dfa_src: str):
        self.transiciones, self.estados_finales = self.cargar_afd(dfa_src)
        self.estado_inicial = "q_0"

    def token_a_predicado(self, token: str) -> Callable[[str], bool]:
        if token in self.mapa_escapes:
            target = self.mapa_escapes[token]
            return lambda c: c == target
        m = self.regex_rango.fullmatch(token)
        if m:
            ini, fin = map(ord, m.groups())
            return lambda c, ini=ini, fin=fin: ini <= ord(c) <= fin
        literal = token
        return lambda c, lit=literal: c == lit

    def etiqueta_a_predicados(self, etiqueta: str) -> List[Callable[[str], bool]]:
        partes = self.regex_separador.split(etiqueta)
        return [self.token_a_predicado(p) for p in partes if p]

    def cargar_afd(self, dot_text: str):
        transiciones: Dict[str, List[Tuple[Callable[[str], bool], str]]] = {}
        estados_finales: Set[str] = set()
        for line in dot_text.splitlines():
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            m_nodo = self.regex_nodo.match(line)
            if m_nodo:
                estado, shape = m_nodo.groups()
                if shape == "doublecircle":
                    estados_finales.add(estado)
                continue
            m_trans = self.regex_transicion.match(line)
            if m_trans:
                src, dst, label = m_trans.groups()
                for pred in self.etiqueta_a_predicados(label):
                    transiciones.setdefault(src, []).append((pred, dst))
        return transiciones, estados_finales

    def transicion(self, estado: str, ch: str):
        for pred, dst in self.transiciones.get(estado, []):
            if pred(ch):
                return dst
        return None

    def tokenize(self, texto: str) -> List[Tuple[str, str]]:
        i, n = 0, len(texto)
        tokens: List[Tuple[str, str]] = []
        while i < n:
            if texto[i].isspace():
                i += 1
                continue
            estado = self.estado_inicial
            ultimo_final = None
            j = i
            while j < n:
                siguiente = self.transicion(estado, texto[j])
                if siguiente is None or siguiente == "q_0":
                    break
                estado = siguiente
                j += 1
                if estado in self.estados_finales:
                    ultimo_final = (j, estado)
            if ultimo_final is None:
                tokens.append(("ERROR", texto[i]))
                i += 1
            else:
                pos, estado_final = ultimo_final
                lexema = texto[i:pos]
                ttype = self.mapa_tokens_finales.get(estado_final, estado_final[2:].upper())
                tokens.append((ttype, lexema))
                i = pos

        errores_encontrados = []
        for token_idx, (ttype, lexema) in enumerate(tokens):
            if ttype == "ERROR":
                err_local = lexema if token_idx+1 >= len(tokens) else lexema + " " + tokens[token_idx+1][1]
                print(Fore.RED + f"{ttype} cerca del lexema {err_local}. Revisa que tu código sea correcto.")
                errores_encontrados.append(err_local)
            else:
                print(Fore.GREEN + f"{ttype:<15} {lexema}")
        if len(errores_encontrados) > 0:
            print(Back.RED + f"Abortando. El lexer ha detectado los siguientes errores:", errores_encontrados)
            exit(0)
        print(Back.GREEN + f"Programa validado por el lexer.")
        return tokens

if __name__ == "__main__":
    with open("design/lexer.auto", 'r') as file:
        DOT_AUTOMATA = file.read()
    lx = Lexer(DOT_AUTOMATA)

    with open("cpp_test/" + input("Nombre del archivo C++: cpp_test/"), 'r') as file:
        code = file.read()

    print(Back.BLUE + "Archivo encontrado. Procesando con el lexer." + Back.BLACK)
    
    tokenized_code = lx.tokenize(code)