# uncompyle6 version 3.6.3
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.5 (default, Nov  7 2019, 10:50:52)
# [GCC 8.3.0]
# Embedded file name: ulang\parser\lrparser.py
from rply.errors import ParsingError


class LRParser:
    __module__ = __name__
    __qualname__ = "LRParser"

    def __init__(self, lrparser):
        self.lr_table = lrparser.lr_table
        self.error_handler = lrparser.error_handler

    def parse(self, tokenizer, state=None):
        from rply.token import Token

        lookahead = None
        lookaheadstack = []
        statestack = [0]
        symstack = [Token("$end", "$end")]
        current_state = 0
        while True:
            if self.lr_table.default_reductions[current_state]:
                t = self.lr_table.default_reductions[current_state]
                current_state = self._reduce_production(t, symstack, statestack, state)
                continue
            else:
                if lookahead is None:
                    if lookaheadstack:
                        lookahead = lookaheadstack.pop()
                else:
                    try:
                        lookahead = next(tokenizer)
                    except StopIteration:
                        lookahead = None

                    if lookahead is None:
                        lookahead = Token("$end", "$end")
            ltype = lookahead.gettokentype()
            if ltype in self.lr_table.lr_action[current_state]:
                t = self.lr_table.lr_action[current_state][ltype]
                if t > 0:
                    statestack.append(t)
                    current_state = t
                    symstack.append(lookahead)
                    lookahead = None
                    continue
                else:
                    if t < 0:
                        current_state = self._reduce_production(
                            t, symstack, statestack, state
                        )
                        continue
                    else:
                        n = symstack[(-1)]
                    return n
            elif self.error_handler is not None:
                if state is None:
                    self.error_handler(lookahead)
                else:
                    self.error_handler(state, lookahead)
                lookahead = None
                continue
            else:
                raise ParsingError(None, lookahead.getsourcepos())

    def _reduce_production(self, t, symstack, statestack, state):
        p = self.lr_table.grammar.productions[(-t)]
        pname = p.name
        plen = p.getlength()
        start = len(symstack) + (-plen - 1)
        if not start >= 0:
            raise AssertionError
        else:
            targ = symstack[start + 1:]
            start = len(symstack) + -plen
            if not start >= 0:
                raise AssertionError
            del symstack[start:]
            del statestack[start:]
            if state is None:
                value = p.func(targ)
            else:
                value = p.func(state, targ)
        symstack.append(value)
        current_state = self.lr_table.lr_goto[statestack[(-1)]][pname]
        statestack.append(current_state)
        return current_state

# okay decompiling ./pyc/ulang.parser.lrparser.pyc
