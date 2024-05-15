import networkx as nx
from scipy.sparse import dok_matrix
from pyformlang.rsa import RecursiveAutomaton
from pyformlang.cfg import CFG
from project.task2 import graph_to_nfa
from project.task3 import (
    FiniteAutomaton,
    intersect_automata,
)
from project.task8 import rsm_to_matrix, cfg_to_rsm


def cfpq_with_gll(
    rsm: RecursiveAutomaton | CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    rsm = rsm if isinstance(rsm, RecursiveAutomaton) else cfg_to_rsm(rsm)

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
