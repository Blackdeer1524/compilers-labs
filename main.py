from pprint import pprint
from src.scanning.scanner import Scanner
from src.analysis.analyzer import SyntacticAnalyzer
from src.table_synthesis.semantics import SemanticsAnalyzer


def main():
    scanner = Scanner(open("./test.txt"))
    syn_an = SyntacticAnalyzer(scanner)

    res = syn_an.parse()
    # print("digraph {")
    # print(res.to_graphviz().replace("\r", "\\n"))
    # print("}")

    sem_an = SemanticsAnalyzer()
    pprint(sem_an.process_productions(res))


if __name__ == "__main__":
    main()
