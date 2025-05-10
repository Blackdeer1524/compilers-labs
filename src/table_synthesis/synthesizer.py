from src.analysis.ast import *

class SemanticsAnalyzer:
    def __init__(self):
        self.errors: list[str] = []
    
    def collect_error(self, mes: str):
        ...

    def is_axiom(self, node: AxiomNode) -> bool:
        return node.value is not None

    def collect_nonterm(self, node: NonTermNode) -> str:
        if node.value is None: 
            self.collect_error(f"expected {node.node_name} not to be None")
            return "ERROR"
        return node.value.value

    def collect_rule(self, node: RuleNode) -> str:
        match node.value:
            case None:
                self.collect_error()
            case (TermNode(), RuleTailNode()): ...
            case (NonTermNode(), RuleTailNode()): ...
            case KeywordNode(kind="epsilon"): ...
            case KeywordNode(kind=unexpected): ...
            



    def process_node(self, node: ProductionNode):
        if node.value is None:
            self.collect_error("")
            return 

        (axiom, nonterm, kw_is, rule, alt_rule, kw_end, next_prod) = node.value

        if kw_is.value is None:
            self.collect_error(f"expected {kw_is.node_name} not to be None")
            return
        
        if kw_end.value is None:
            self.collect_error(f"expected {kw_end.node_name} not to be None")
            return

        is_axiom = self.is_axiom(axiom)
        nt = collect_nonterm(nonterm)
        self.collect_rule(rule)


    




def process_prods(node: ProductionNode):
