from pprint import pprint
from src.analysis.analyzer import Analyzer
from src.scanning.scanner import Scanner
from src.table_synthesis.synthesizer import SemanticsAnalyzer


def main():
    s = Scanner(open("./test.txt"))
    a = Analyzer(s)
    res = a.parse()
    # print("digraph {")
    # print(res.to_graphviz().replace("\r", "\\n"))
    # print("}")

    sa = SemanticsAnalyzer()
    pprint(sa.process_productions(res))


if __name__ == "__main__":
    main()
