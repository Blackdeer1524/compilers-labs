from collections import deque
from typing import Deque

from src.analysis.bootstrapped_transitions import NON_TERMINAL, TERMINAL, InitNode, transitions
from src.scanning.scanner import ScanError, Scanner


class SyntacticAnalyzer:
    def __init__(self, s: Scanner):
        self.scanner = s

    def parse(self):
        init = InitNode()
        d: Deque[tuple[TERMINAL | NON_TERMINAL, int]] = deque([(init, 0)])
        for token in self.scanner:
            if len(d) == 0:
                raise RuntimeError(
                    "stack is exhausted, but there are still tokens left!"
                )
            while len(d) > 0:
                cur_node, depth = d.pop()
                match token:
                    case ScanError():
                        raise RuntimeError(f"scanner error: {token}")
                    case _:
                        rule = transitions(cur_node, token)
                        match rule:
                            case None:
                                break
                            case str():
                                raise RuntimeError(rule)
                            case list():
                                for v in reversed(rule):
                                    d.append((v, depth + 1))
        return init
