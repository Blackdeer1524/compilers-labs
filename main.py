from pprint import pprint
from src.scanning.scanner import Scanner
from src.analysis.analyzer import SyntacticAnalyzer
from src.table_synthesis.semantics import SemanticsAnalyzer
from src.table_synthesis.synthesizer import Synthesizer, render_table
from src.table_synthesis.compiler import generate_transitions
from src.table_synthesis.stream import Stream


def main():
    scanner = Scanner(open("./test.txt"))
    syn_an = SyntacticAnalyzer(scanner)

    res = syn_an.parse()
    # print("digraph {")
    # print(res.to_graphviz().replace("\r", "\\n"))
    # print("}")

    sem_an = SemanticsAnalyzer()
    match sem_an.process_productions(res):
        case tuple((axiom, infos)):
            synth = Synthesizer()
            table = synth.process(axiom, infos)
            # print(render_table(table))
            # 
            # print("# ====================")

            s = Stream()
            generate_transitions(s, table, infos)
            print(s.emit())
        case list() as errors:
            pprint(errors)
    

if __name__ == "__main__":
    main()
