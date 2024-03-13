from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    State,
    Symbol,
)
from networkx.classes.reportviews import NodeView
from networkx import MultiDiGraph
from scipy.sparse import dok_matrix, kron
from typing import Iterable

from project.task2 import regex_to_dfa, graph_to_nfa


class FiniteAutomaton:
    def __init__(self, fa=None) -> None:
        self.matrices = {}
        if fa is None:
            self.start_states = set()
            self.final_states = set()
            self.state_to_index = {}
            return

        self.start_states = fa.start_states
        self.final_states = fa.final_states

        self.state_to_index = {state: index for index, state in enumerate(fa.states)}
        self.n_states = len(fa.states)

        for from_state, transitions in fa.to_dict().items():
            for symbol, to_states in transitions.items():
                if symbol not in self.matrices.keys():
                    self.matrices[symbol] = dok_matrix(
                        (self.n_states, self.n_states), dtype=bool
                    )
                if isinstance(fa, DeterministicFiniteAutomaton):
                    self.matrices[symbol][
                        self.state_to_index[from_state], self.state_to_index[to_states]
                    ] = True
                else:
                    for to_state in to_states:
                        self.matrices[symbol][
                            self.state_to_index[from_state],
                            self.state_to_index[to_state],
                        ] = True

    def to_nfa(self) -> NondeterministicFiniteAutomaton:
        nfa = NondeterministicFiniteAutomaton()

        for state in self.start_states:
            nfa.add_start_state(state)

        for state in self.final_states:
            nfa.add_final_state(state)

        for label, matrix in self.matrices.items():
            n, m = matrix.shape
            for from_state in range(n):
                for to_state in range(m):
                    if matrix[from_state, to_state]:
                        nfa.add_transition(State(from_state), label, State(to_state))

        return nfa

    def accepts(self, word: Iterable[Symbol]) -> bool:
        return self.to_nfa().accepts(word)

    def is_empty(self) -> bool:
        return len(self.matrices) == 0


def intersect_automata(
    automaton1: FiniteAutomaton, automaton2: FiniteAutomaton
) -> FiniteAutomaton:
    res = FiniteAutomaton()

    for state1, index1 in automaton1.state_to_index.items():
        for state2, index2 in automaton2.state_to_index.items():
            index = len(automaton2.state_to_index) * index1 + index2
            res.state_to_index[index] = index

            if state1 in automaton1.start_states and state2 in automaton2.start_states:
                res.start_states.add(State(index))

            if state1 in automaton1.final_states and state2 in automaton2.final_states:
                res.final_states.add(State(index))

    labels = [label for label in automaton1.matrices if label in automaton2.matrices]
    for label in labels:
        res.matrices[label] = kron(
            automaton1.matrices[label], automaton2.matrices[label], "csr"
        )

    return res


def paths_ends(
    graph: MultiDiGraph, start_nodes: set[int], final_nodes: set[int], regex: str
) -> list[tuple[NodeView, NodeView]]:
    intersection = intersect_automata(
        FiniteAutomaton(regex_to_dfa(regex)),
        FiniteAutomaton(graph_to_nfa(graph, start_nodes, final_nodes)),
    )
    return zip(intersection.start_states, intersection.final_states)
