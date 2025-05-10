from collections import defaultdict
from typing import DefaultDict
from scanning.scanner import Ident, QuotedStr
from src.table_synthesis.semantics import RULE_T, ProductionInfo

class SynthError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Synthesizer:
    def __init__(self):
        self.productions: dict[str, ProductionInfo] = {}

        self.accepts_epsilon: set[str] = set()
        self.seen: set[str] = set()

        self.first_sets: DefaultDict[str, set[str]] = defaultdict(set)
        self.follow_sets: DefaultDict[str, set[str]] = defaultdict(set)
        self.table: dict[str, DefaultDict[str, RULE_T | None]] = defaultdict(lambda: defaultdict(lambda: None))

    
    def calculate_first_sets(self, nonterm: str):
        if nonterm in self.seen:
            return

        self.seen.add(nonterm)
        self.first_sets[nonterm] = set()
        for rule in self.productions[nonterm].rhs:
            match rule:
                case "epsilon": 
                    self.accepts_epsilon.add(nonterm)
                case list():
                    for item in rule:
                        match item:
                            case Ident():
                                if item.value not in self.first_sets:
                                    assert item.value in self.productions
                                    self.calculate_first_sets(item.value)
                                
                                for f in self.first_sets[item.value]:
                                    self.table[nonterm][f] = rule
                                
                                self.first_sets[nonterm].update(self.first_sets[item.value])
                                

                                if item.value not in self.accepts_epsilon:
                                    break
                            case QuotedStr():
                                self.first_sets[nonterm].add(item.value)
                                break
                        
    def calculate_follow_sets(self):
        while True:
            updated = False
            for nonterm, info in self.productions.items():
                for rule in info.rhs:
                    match rule:
                        case "epsilon": continue
                        case list(): 
                            for i in range(len(rule)-1):
                                cur =  rule[i]
                                match cur:
                                    case Ident():
                                        broke_the_loop = False
                                        for after in rule[i+1:]:
                                            match after:
                                                case QuotedStr():
                                                    prev_len = len(self.follow_sets[cur.value])
                                                    self.follow_sets[cur.value].add(after.value)
                                                    if len(self.follow_sets[cur.value]) != prev_len:
                                                        updated = True
                                                    broke_the_loop = True
                                                    break
                                                case Ident(): 
                                                    prev_len = len(self.follow_sets[cur.value])

                                                    assert after.value in self.productions
                                                    self.follow_sets[cur.value].update(self.first_sets[after.value])

                                                    if len(self.follow_sets[cur.value]) != prev_len:
                                                        updated = True
                                                    if after.value not in self.accepts_epsilon:
                                                        broke_the_loop = True
                                                        break
                                        if not broke_the_loop and rule[-1] in self.accepts_epsilon:
                                            prev_len = len(self.follow_sets[cur.value])
                                            self.follow_sets[cur.value].update(self.follow_sets[nonterm])
                                            if len(self.follow_sets[cur.value]) != prev_len:
                                                updated = True
                                    case QuotedStr():
                                        continue
                            last = rule[-1]        

                            prev_len = len(self.follow_sets[last.value])
                            self.follow_sets[last.value].update(self.follow_sets[nonterm])
                            if len(self.follow_sets[last.value]) != prev_len:
                                updated = True
            if not updated:
                break
                            
    def process(self, productions: dict[str, ProductionInfo]) -> list[str]:
        self.productions = productions
        
        errors: list[str] = []
        for nonterm, rules in self.productions.items():
            for rule in rules.rhs:
                match rule:
                    case "epsilon": continue
                    case list():
                        for item in rule:
                            match item:
                                case Ident():
                                    if item.value not in self.productions:
                                        errors.append(f"found an undefined non terminal: {item.value}")
                                case QuotedStr(): 
                                    continue
        if len(errors) > 0:
            return errors

        for nonterm in productions:
            self.calculate_first_sets(nonterm)
        self.calculate_follow_sets()

        

        


            
        


            


        

        