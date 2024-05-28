from project.lang.project.languageVisitor import languageVisitor
from project.lang.project.languageLexer import languageLexer
from project.lang.project.languageParser import languageParser

from antlr4 import *
from antlr4.InputStream import InputStream


class CounterVisitor(languageVisitor):
    def __init__(self):
        super().__init__()
        self.__counter = 0

    def enterEveryRule(self, rule):
        self.__counter += 1

    @property
    def counter(self):
        return self.__counter


class TreeToProgVisitor(languageVisitor):
    def __init__(self):
        super().__init__()
        self.__result = []

    def enterEveryRule(self, rule):
        self.__result.append(rule.get_text())

    def compute_result(self):
        return "".join(self.__result)


def prog_to_tree(program: str) -> tuple[ParserRuleContext, bool]:
    parser = languageParser(CommonTokenStream(languageLexer(InputStream(program))))
    return parser.prog(), parser.getNumberOfSyntaxErrors() == 0


def nodes_count(tree: ParserRuleContext) -> int:
    visitor = CounterVisitor()
    tree.accept(visitor)
    return visitor.counter


def tree_to_prog(tree: ParserRuleContext) -> str:
    visitor = TreeToProgVisitor()
    tree.accept(visitor)
    return visitor.compute_result()
