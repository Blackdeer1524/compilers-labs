from src.scanning.custom_scanner import Scanner
from src.analysis.generated_analyzer import SyntacticAnalyzer


def main():
    scanner = Scanner(open("./expr.txt"))
    syn_an = SyntacticAnalyzer(scanner)

    res = syn_an.parse()
    print("digraph {")
    print(res.to_graphviz().replace("\r", "\\n"))
    print("}")

if __name__ == "__main__":
    main()
