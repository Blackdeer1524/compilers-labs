from src.analysis.task_transitions import (
    E1Node,
    FNode,
    InitNode,
    ENode,
    EOFNode,
    KeywordAsteriskNode,
    KeywordLeftParenNode,
    KeywordPlusNode,
    KeywordRightParenNode,
    NumberNode,
    T1Node,
    TNode,
)
from src.scanning.task_scanner import Scanner
from src.analysis.task_analyzer import SyntacticAnalyzer


def to_string(node: InitNode | ENode | E1Node | TNode | FNode | T1Node) -> str:
    match node:
        case InitNode() as node:
            match node.value:
                case (ENode() as enode, EOFNode()):
                    return to_string(enode)
                case None:
                    return ""
        case ENode() as node:
            match node.value:
                case (TNode() as tnode, E1Node() as e1node):
                    return to_string(tnode) + to_string(e1node)
                case None:
                    return ""
        case E1Node():
            match node.value:
                case tuple((KeywordPlusNode(), TNode() as tnode, E1Node() as e1node)):
                    return "+" + to_string(tnode) + to_string(e1node)
                case None:
                    return ""
        case TNode():
            match node.value:
                case (FNode() as fnode, T1Node() as t1node):
                    return to_string(fnode) + to_string(t1node)
                case None:
                    return ""
        case FNode():
            match node.value:
                case (
                    KeywordLeftParenNode(),
                    ENode() as enode,
                    KeywordRightParenNode(),
                ):
                    return "(" + to_string(enode) + ")"
                case (NumberNode() as nnode,):
                    return str(nnode.value.value)
                case None:
                    return ""
        case T1Node():
            match node.value:
                case (KeywordAsteriskNode(), FNode() as fnode, T1Node() as t1node):
                    return "*" + to_string(fnode) + to_string(t1node)
                case None:
                    return ""


def main():
    scanner = Scanner(open("./expr.txt"))
    syn_an = SyntacticAnalyzer(scanner)

    res = syn_an.parse()
    print(eval(to_string(res)))


if __name__ == "__main__":
    main()
