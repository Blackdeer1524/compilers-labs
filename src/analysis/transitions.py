from src.analysis.ast import (
    NON_TERMINAL,
    TERMINAL,
    InitNode,
    AxiomNode,
    EOFNode,
    NonTermNode,
    KeywordAxiomNode,
    KeywordEndNode,
    KeywordEpsilonNode,
    KeywordIsNode,
    KeywordOrNode,
    ProductionNode,
    TermNode,
    RuleAltNode,
    RuleNode,
    RuleTailNode,
)
from src.scanning.scanner import Token, Keyword, Ident, EOF, QuotedStr


def transitions(
    current: NON_TERMINAL | TERMINAL, token: Token
) -> list[NON_TERMINAL | TERMINAL] | str | None:
    match current:
        case InitNode():
            match token:
                case Keyword(value="axiom"):
                    (prod, eof) = (ProductionNode(), EOFNode())
                    current.value = (prod, eof)
                    current.pos = token.start
                    return [prod, eof]
                case Ident():
                    (prod, eof) = (ProductionNode(), EOFNode())
                    current.value = (prod, eof)
                    current.pos = token.start
                    return [prod, eof]
                case QuotedStr():
                    return f"unexpected token: {token}"
                case Keyword(value="or"):
                    return f"unexpected token: {token}"
                case Keyword(value="is"):
                    return f"unexpected token: {token}"
                case Keyword(value="epsilon"):
                    return f"unexpected token: {token}"
                case Keyword(value="end"):
                    return f"unexpected token: {token}"
                case Keyword(value=other):
                    return f"unknown keyword: {other}"
                case EOF():
                    (prod, eof) = (ProductionNode(), EOFNode())
                    current.value = (prod, eof)
                    current.pos = token.start
                    return [prod, eof]
        case ProductionNode():
            match token:
                case Keyword(value="axiom"):
                    res = (
                        AxiomNode(),
                        NonTermNode(),
                        KeywordIsNode(),
                        RuleNode(),
                        RuleAltNode(),
                        KeywordEndNode(),
                        ProductionNode(),
                    )
                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Ident():
                    res = (
                        AxiomNode(),
                        NonTermNode(),
                        KeywordIsNode(),
                        RuleNode(),
                        RuleAltNode(),
                        KeywordEndNode(),
                        ProductionNode(),
                    )
                    current.value = res
                    current.pos = token.start
                    return list(res)
                case QuotedStr():
                    return f"unexpected token: {token}"
                case Keyword(value="or"):
                    return f"unexpected token: {token}"
                case Keyword(value="is"):
                    return f"unexpected token: {token}"
                case Keyword(value="epsilon"):
                    return f"unexpected token: {token}"
                case Keyword(value="end"):
                    return f"unexpected token: {token}"
                case Keyword(value=other):
                    return f"unknown keyword: {other}"
                case EOF():
                    current.pos = token.start
                    return []
        case RuleNode():
            match token:
                case Keyword(value="axiom"):
                    return f"unexpected token: {token}"
                case Ident():
                    nt = NonTermNode()
                    tail = RuleTailNode()
                    current.value = (nt, tail)
                    current.pos = token.start
                    return [nt, tail]
                case QuotedStr():
                    t = TermNode()
                    tail = RuleTailNode()
                    current.value = (t, tail)
                    current.pos = token.start
                    return [t, tail]
                case Keyword(value="or"):
                    return f"unexpected token: {token}"
                case Keyword(value="is"):
                    return f"unexpected token: {token}"
                case Keyword(value="epsilon"):
                    current.value = KeywordEpsilonNode()
                    current.pos = token.start
                    return [current.value]
                case Keyword(value="end"):
                    return f"unexpected token: {token}"
                case Keyword(value=other):
                    return f"unknown keyword: {other}"
                case EOF():
                    return f"unexpected token: {token}"
        case RuleTailNode():
            match token:
                case Keyword(value="axiom"):
                    return f"unexpected token: {token}"
                case Ident():
                    current.value = (NonTermNode(), RuleTailNode())
                    current.pos = token.start
                    return list(current.value)
                case QuotedStr():
                    current.value = (TermNode(), RuleTailNode())
                    current.pos = token.start
                    return list(current.value)
                case Keyword(value="or"):
                    current.pos = token.start
                    return []
                case Keyword(value="is"):
                    return f"unexpected token: {token}"
                case Keyword(value="epsilon"):
                    return f"unexpected token: {token}"
                case Keyword(value="end"):
                    current.pos = token.start
                    return []
                case Keyword(value=other):
                    return f"unknown keyword: {other}"
                case EOF():
                    return f"unexpected token: {token}"
        case RuleAltNode():
            match token:
                case Keyword(value="axiom"):
                    return f"unexpected token: {token}"
                case Ident():
                    return f"unexpected token: {token}"
                case QuotedStr():
                    return f"unexpected token: {token}"
                case Keyword(value="or"):
                    current.value = (KeywordOrNode(), RuleNode(), RuleAltNode())
                    current.pos = token.start
                    return [current.value[0], current.value[1], current.value[2]]
                case Keyword(value="is"):
                    return f"unexpected token: {token}"
                case Keyword(value="epsilon"):
                    return f"unexpected token: {token}"
                case Keyword(value="end"):
                    current.pos = token.start
                    return []
                case Keyword(value=other):
                    return f"unknown keyword: {other}"
                case EOF():
                    return f"unexpected token: {token}"
        case AxiomNode():
            match token:
                case Keyword(value="axiom"):
                    current.value = KeywordAxiomNode()
                    current.pos = token.start
                    return [current.value]
                case Ident():
                    current.pos = token.start
                    return []
                case QuotedStr():
                    return f"unexpected token: {token}"
                case Keyword(value="or"):
                    return f"unexpected token: {token}"
                case Keyword(value="is"):
                    return f"unexpected token: {token}"
                case Keyword(value="epsilon"):
                    return f"unexpected token: {token}"
                case Keyword(value="end"):
                    return f"unexpected token: {token}"
                case Keyword(value=other):
                    return f"unknown keyword: {other}"
                case EOF():
                    return f"unexpected token: {token}"
        case KeywordAxiomNode():
            if type(token) != Keyword or token.value != "axiom":
                return f"expected `axiom, {token} found"
            current.value = token
            current.pos = token.start
            return None
        case KeywordOrNode():
            if type(token) != Keyword or token.value != "or":
                return f"expected `or, {token} found"
            current.value = token
            current.pos = token.start
            return None
        case KeywordIsNode():
            if type(token) != Keyword or token.value != "is":
                return f"expected `is, {token} found"
            current.value = token
            current.pos = token.start
            return None
        case KeywordEpsilonNode():
            if type(token) != Keyword or token.value != "epsilon":
                return f"expected `epsilon, {token} found"
            current.value = token
            current.pos = token.start
            return None
        case KeywordEndNode():
            if type(token) != Keyword or token.value != "end":
                return f"expected `end, {token} found"
            current.value = token
            current.pos = token.start
            return None
        case NonTermNode():
            if type(token) != Ident:
                return f"expected NonTerm, but {type(token)} found"
            current.value = token
            current.pos = token.start
            return None
        case TermNode():
            if type(token) != QuotedStr:
                return f"expected Term, but {type(token)} found"
            current.value = token
            current.pos = token.start
            return None
        case EOFNode():
            if type(token) != EOF:
                return f"expected EOF, but {type(token)} found"
            current.value = token
            current.pos = token.start
            return None
