from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EarleyItem:
    lhs: str

    rule: list[str]
    rule_pos: int

    parent_index: int

    def current(self) -> Optional[str]:
        if self.rule_pos >= len(self.rule):
            return None
        return self.rule[self.rule_pos]

    def __repr__(self) -> str:
        formatted_rule = (
            " ".join(self.rule[: self.rule_pos])
            + "•"
            + " ".join(self.rule[self.rule_pos :])
        )
        return f"{self.__class__.__name__}[{self.lhs}→{formatted_rule}, {self.parent_index}]"

    def __hash__(self):
        return hash(str(self))


class EarleyParser:
    def __init__(
        self,
        grammar: dict[str, list[list[str]]],
        axiom: str,
        is_epsilon: set[str],
        s: str,
    ):
        self.grammar = grammar
        self.is_epsilon = is_epsilon
        self.s = s + "$"

        self.earley_sets: list[set[EarleyItem]] = [set() for _ in range(len(s) + 1)]
        self.earley_sets[0].add(EarleyItem("S'", [axiom], 0, 0))

    def parse(self):
        for i in range(len(self.s)):
            a_next = self.s[i]

            Q = self.earley_sets[i]
            while True:
                Q_prime: set[EarleyItem] = set()
                for x in Q:
                    c = x.current()
                    if c is None:  # completer
                        parent_set = self.earley_sets[x.parent_index]
                        for parent_item in parent_set:
                            c_parent = parent_item.current()
                            if c_parent is not None and c_parent == x.lhs:
                                Q_prime.add(
                                    EarleyItem(
                                        parent_item.lhs,
                                        parent_item.rule,
                                        parent_item.rule_pos + 1,
                                        parent_item.parent_index,
                                    )
                                )
                    elif c == a_next:  # scanner
                        self.earley_sets[i + 1].add(
                            EarleyItem(x.lhs, x.rule, x.rule_pos + 1, x.parent_index)
                        )
                    elif c.isupper():  # predictor
                        # c is some non-terminal
                        for rule in self.grammar[c]:
                            Q_prime.add(EarleyItem(c, rule, 0, i))
                        if c in self.is_epsilon:
                            Q_prime.add(
                                EarleyItem(
                                    x.lhs, x.rule, x.rule_pos + 1, x.parent_index
                                )
                            )
                prev_len = len(self.earley_sets[i])
                self.earley_sets[i].update(Q_prime)
                if prev_len == len(self.earley_sets[i]):
                    break
                Q = Q_prime
        
        for i in self.earley_sets:
            print(i)


if __name__ == "__main__":
    parser = EarleyParser({"E": [["E", "+", "E"], ["n"]]}, "E", set(), "n+n")
    parser.parse()
