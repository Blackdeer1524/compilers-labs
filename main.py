from src.analysis.analyzer import Analyzer
from src.scanning.scanner import Scanner


def main():
    s = Scanner(open("./test.txt"))
    a = Analyzer(s)
    res = a.parse()
    print("digraph {")
    print(res.to_graphviz().replace("\r", "\\n"))
    print("}")


if __name__ == "__main__":
    main()
