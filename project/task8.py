from pyformlang.finite_automaton import State, Symbol
from pyformlang.cfg import Epsilon, CFG
from pyformlang.regular_expression import Regex
from pyformlang.rsa import Box, RecursiveAutomaton
import networkx as nx

from collections import defaultdict

from project.task2 import graph_to_nfa
from project.task3 import FiniteAutomaton, intersect_automata


def cfg_to_rsm(cfg: CFG) -> RecursiveAutomaton:
    productions = defaultdict(list)

    for production_item in cfg.productions:
        if len(production_item.body) == 0:
            body_regex = Epsilon().to_text()
        else:
            body_regex = " ".join(var.value for var in production_item.body)
        productions[Symbol(production_item.head)].append(body_regex)

    regexes = {
        Box(Regex("|".join(regex_list)).to_epsilon_nfa().to_deterministic(), symbol)
        for symbol, regex_list in productions.items()
    }

    return RecursiveAutomaton(productions.keys(), Symbol("S"), regexes)


def ebnf_to_rsm(ebnf: str) -> RecursiveAutomaton:
    productions = defaultdict(list)

    for line in ebnf.splitlines():
        line = line.strip()
        if "->" in line:
            head, body = line.split("->")
            body = body.strip() if body.strip() != "" else Epsilon().to_text()
            productions[Symbol(head.strip())].append(body)

    regexes = {
        Box(Regex("|".join(regex_list)).to_epsilon_nfa().to_deterministic(), symbol)
        for symbol, regex_list in productions.items()
    }
    return RecursiveAutomaton(productions.keys(), Symbol("S"), regexes)


def cfpq_with_tensor(
    rsm: RecursiveAutomaton | CFG,
    graph: nx.MultiDiGraph,
    final_nodes: set[int] = None,
    start_nodes: set[int] = None,
) -> set[tuple[int, int]]:

    if not isinstance(rsm, RecursiveAutomaton):
        rsm = cfg_to_rsm(rsm)

    start_nodes = graph.nodes if start_nodes is None else start_nodes
    final_nodes = graph.nodes if final_nodes is None else final_nodes

    rsm_matrix = rsm_to_matrix(rsm)[0]
    automaton = FiniteAutomaton(graph_to_nfa(graph, start_nodes, final_nodes))

    prev_nnz = 0
    result = set()
    while True:
        closure = list(
            zip(
                *intersect_automata(rsm_matrix, automaton)
                .get_transitive_closure()
                .nonzero()
            )
        )

        curr_nnz = len(closure)
        if curr_nnz == prev_nnz:
            break
        prev_nnz = curr_nnz

        for i, j in closure:
            if (
                rsm_matrix.get_index(i) in rsm_matrix.start_states
                and rsm_matrix.get_index(j) in rsm_matrix.final_states
            ):
                var = rsm_matrix.indexes_dict()[i].value[0]
                automaton.add_label_if_not_exist(var)
                automaton.set_true(var, i, j)
                result.add((i, j))

    return result


def rsm_to_matrix(rsm: RecursiveAutomaton) -> tuple:
    automaton = FiniteAutomaton()
    states = set()

    for v, p in rsm.boxes.items():
        for s in p.dfa.states:
            states.add(State((v, s.value)))

            if s in p.dfa.start_states:
                automaton.start_states.add(State((v, s.value)))

            if s in p.dfa.final_states:
                automaton.final_states.add(State((v, s.value)))

    automaton.set_state_to_index(
        {
            value: index
            for index, value in enumerate(sorted(states, key=lambda x: x.value[1]))
        }
    )

    epsilon_symbols = set()

    for v, p in rsm.boxes.items():
        for src, transition in p.dfa.to_dict().items():
            for label, dst in transition.items():
                label = label.value

                if isinstance(dst, Epsilon):
                    epsilon_symbols.add(label)

                automaton.add_label_if_not_exist(label)
                for target in {dst} if not isinstance(dst, set) else dst:
                    automaton.set_true(
                        label,
                        automaton.get_index(State((v, src.value))),
                        automaton.get_index(State((v, target.value))),
                    )

    return automaton, epsilon_symbols