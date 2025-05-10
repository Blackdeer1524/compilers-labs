from dataclasses import dataclass
from typing import Literal, Optional
from scanning.scanner import Ident, QuotedStr
from src.analysis.ast import *
from text.processors import Position

RULE_T = list[Ident | QuotedStr | Literal["epsilon"]]


@dataclass
class ProductionInfo:
    lhs: Ident | None
    rhs: list[RULE_T]
    is_axiom: bool


class SemanticsAnalyzer:
    def __init__(self):
        self.errors: list[str] = []

    def store_error(self, mes: str, pos: Position | None):
        self.errors.append(f"[{pos if pos is not None else '???'}] {mes}")

    def is_axiom(self, node: AxiomNode) -> bool:
        return node.value is not None

    def collect_nonterm(self, node: NonTermNode) -> Optional[Ident]:
        if node.value is None:
            self.store_error(f"expected {node.node_label} not to be None", node.pos)
            return None
        return node.value

    def collect_term(self, node: TermNode) -> Optional[QuotedStr]:
        if node.value is None:
            self.store_error(f"expected {node.node_label} not to be None", node.pos)
            return None
        return node.value

    def collect_rule_tail(self, node: RuleTailNode) -> RULE_T:
        match node.value:
            case None:
                return []
            case KeywordNode(kind="epsilon"):
                return ["epsilon"]
            case KeywordNode(kind=unknown):
                self.store_error(f"unexpected keyword: {unknown}", node.pos)
                return []
            case RuleNode() as rule:
                return self.collect_rule(rule)

    def collect_rule(self, node: RuleNode) -> RULE_T:
        match node.value:
            case None:
                self.store_error(f"expected a rule {node.pos}", node.pos)
                return []
            case (TermNode() as term, RuleTailNode() as tail):
                term = self.collect_term(term)
                if term is None:
                    return self.collect_rule_tail(tail)
                return [term] + self.collect_rule_tail(tail)
            case (NonTermNode() as non_term, RuleTailNode() as tail):
                non_term = self.collect_nonterm(non_term)
                if non_term is None:
                    return self.collect_rule_tail(tail)
                return [non_term] + self.collect_rule_tail(tail)
            case KeywordNode(kind="epsilon"):
                return ["epsilon"]
            case KeywordNode(kind=unknown):
                self.store_error(f"unexpected keyword: {unknown}", node.pos)
                return []

    def collect_alt_rules(self, node: RuleAltNode) -> list[RULE_T]:
        match node.value:
            case None:
                return []
            case (
                KeywordNode() as kw_is,
                RuleNode() as rule,
                RuleAltNode() as alt_rules,
            ):
                if kw_is.kind != "is":
                    self.store_error(
                        f'expected "is" keyword, but {kw_is.kind} found', kw_is.pos
                    )
                if kw_is.value is None:
                    self.store_error(
                        f"expected {kw_is.node_label} not to be None", kw_is.pos
                    )
                return [self.collect_rule(rule)] + self.collect_alt_rules(alt_rules)

    def process_node(self, node: ProductionNode) -> list[ProductionInfo]:
        if node.value is None:
            return []

        (axiom, nonterm, kw_is, rhs, alt_rules, kw_end, next_prod) = node.value

        is_axiom = self.is_axiom(axiom)
        lhs = self.collect_nonterm(nonterm)
        if kw_is.value is None:
            self.store_error(f"expected {kw_is.node_label} not to be None", kw_is.pos)
        rhs = [self.collect_rule(rhs)] + self.collect_alt_rules(alt_rules)
        if kw_end.value is None:
            self.store_error(f"expected {kw_end.node_label} not to be None", kw_end.pos)

        res = ProductionInfo(lhs, rhs, is_axiom)
        return [res] + self.process_node(next_prod)
