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


def evaluate(node: InitNode | ENode | E1Node | TNode | FNode | T1Node) -> int | float:
    match node:
        case InitNode() as node:
            match node.value:
                case (ENode() as enode, EOFNode()):
                    return evaluate(enode)
                case None:
                    return 0
        case ENode() as node:
            match node.value:
                case (TNode() as tnode, E1Node() as e1node):
                    return evaluate(tnode) + evaluate(e1node)
                case None:
                    return 0
        case E1Node():
            match node.value:
                case tuple((KeywordPlusNode(), TNode() as tnode, E1Node() as e1node)):
                    return evaluate(tnode) + evaluate(e1node)
                case None:
                    return 0
        case TNode():
            match node.value:
                case (FNode() as fnode, T1Node() as t1node):
                    return evaluate(fnode) * evaluate(t1node)
                case None:
                    return 1
        case FNode():
            match node.value:
                case (
                    KeywordLeftParenNode(),
                    ENode() as enode,
                    KeywordRightParenNode(),
                ):
                    return evaluate(enode)
                case (NumberNode() as nnode,):
                    return nnode.value.value
                case None:
                    return 0
        case T1Node():
            match node.value:
                case (KeywordAsteriskNode(), FNode() as fnode, T1Node() as t1node):
                    return evaluate(fnode) * evaluate(t1node)
                case None:
                    return 1


def main():
    scanner = Scanner(open("./expr.txt"))
    syn_an = SyntacticAnalyzer(scanner)

    res = syn_an.parse()
    print(evaluate(res))


if __name__ == "__main__":
    main()
