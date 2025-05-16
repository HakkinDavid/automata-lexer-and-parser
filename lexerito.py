import re
from typing import Dict, List, Tuple, Callable, Set


_range_re = re.compile(r"(\S)\.\.\.(\S)")
_split_re = re.compile(r",\s*")

_escapeMap = {"\\space": " "}                
_escapeMap.update({                          
    r'\"': '"',
    r"\'": "'",
    r'\#': '#'
})


def _token_to_pred(token: str) -> Callable[[str], bool]:
    token = token.strip()
    if token in _escapeMap:
        token = _escapeMap[token]            
    else:
        token = bytes(token, "utf-8").decode("unicode_escape") 

    m = _range_re.fullmatch(token)
    if m:
        ini, fin = map(ord, m.groups())
        return lambda c, ini=ini, fin=fin: ini <= ord(c) <= fin

    literal = token.strip('"')
    return lambda c, lit=literal: c == lit

def label_to_predicates(label: str):
    parts = _split_re.split(label)
    return [_token_to_pred(p) for p in parts if p]


_edge_re = re.compile(                       
    r'^(\w+)\s*->\s*(\w+)\s*\[label="((?:\\.|[^"])*)"\]'
)
_node_re = re.compile(r'^(\w+)\s*\[shape=(\w+)')



def load_dfa(dot_text: str):
    transitions: Dict[str, List[Tuple[Callable[[str], bool], str]]] = {}
    finals: Set[str] = set()
    for line in dot_text.splitlines():
        line = line.strip()
        if not line or line.startswith("//"):
            continue
        m_node = _node_re.match(line)
        if m_node:
            state, shape = m_node.groups()
            if shape == "doublecircle":
                finals.add(state)
            continue
        m_edge = _edge_re.match(line)
        if m_edge:
            src, dst, label = m_edge.groups()
            for pred in label_to_predicates(label):
                transitions.setdefault(src, []).append((pred, dst))
    return transitions, finals



TOKEN_ALIASES = {                            
    "EQ_EQ":       "OP_EQEQ",
    "SHIFT_LEFT":  "OP_LSHIFT",
    "SHIFT_RIGHT": "OP_RSHIFT",
    "SCOPE":       "OP_SCOPE",
    "ARROW":       "OP_ARROW",
}



class Lexer:
    def __init__(self, dfa_src: str):
        self.trans, self.finals = load_dfa(dfa_src)
        self.start_state = "q_0"

    def _step(self, state: str, ch: str):
        for pred, dst in self.trans.get(state, []):
            if pred(ch):
                return dst
        return None

    def _scan_string_or_char(self, text: str, i: int) -> Tuple[int, str, str]:
        """Devuelve (nueva_pos, tipo_token, lexema) o (i, '', '') si no aplica"""
        quote = text[i]
        if quote not in ('"', "'"):
            return i, '', ''
        j, n = i + 1, len(text)
        while j < n:
            if text[j] == '\\':              
                j += 2
                continue
            if text[j] == quote:             
                j += 1
                token_type = "STRING" if quote == '"' else "CHAR"
                return j, token_type, text[i:j]
            j += 1
        
        return i, '', ''

    def tokenize(self, text: str) -> List[Tuple[str, str]]:
        i, n = 0, len(text)
        tokens: List[Tuple[str, str]] = []
        while i < n:
            if text[i].isspace():
                i += 1
                continue

            
            new_pos, ttype, lexeme = self._scan_string_or_char(text, i)
            if new_pos != i:
                tokens.append((ttype, lexeme))
                i = new_pos
                continue

            state = self.start_state
            last_final = None
            j = i
            while j < n:
                nxt = self._step(state, text[j])
                if nxt is None:
                    break
                state = nxt
                j += 1
                if state in self.finals:
                    last_final = (j, state)

            if last_final is None:           
                tokens.append(("ERROR", text[i]))
                i += 1
            else:
                pos, fstate = last_final
                lexeme = text[i:pos]
                ttype = fstate[2:].upper()

                if fstate == "q_id":
                    ttype = "IDENTIFIER"
                elif fstate == "q_digit":
                    ttype = "NUMBER"

                
                ttype = TOKEN_ALIASES.get(ttype, ttype)  

                tokens.append((ttype, lexeme))
                i = pos
        return tokens



with open("design/lexer.auto", 'r', encoding='utf-8') as file:
    DOT_AUTOMATA = file.read()



if __name__ == "__main__":
    lx = Lexer(DOT_AUTOMATA)

    with open("cpp_test/" + input("Nombre del archivo C++: cpp_test/"), 'r') as file:
        code = file.read()

    for ttype, lexeme in lx.tokenize(code):
        print(f"{ttype:<15} {lexeme}")
