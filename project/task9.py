from networkx import DiGraph

from project.task8 import cfg_to_rsm

from pyformlang.rsa import RecursiveAutomaton
from pyformlang.cfg import CFG
from pyformlang.finite_automaton import State, Symbol

import networkx as nx

from typing import *
from copy import deepcopy
from itertools import product
import pyformlang


def cfpq_with_gll(
    rsm: RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    if isinstance(rsm, CFG):
        rsm = cfg_to_rsm(rsm)

    if start_nodes is None:
        start_nodes = graph.nodes

    if final_nodes is None:
        final_nodes = graph.nodes

    rsm_start_nonterm = "S"
    if rsm.initial_label.value is not None:
        rsm_start_nonterm = rsm.initial_label.value

    rsm_start = rsm.boxes[rsm.initial_label].dfa.start_state.value

    res = set()

    stack_start_states = set()
    for sn in start_nodes:
        stack_start_states.add((rsm_start_nonterm, sn))

    stack = dict()
    for state in stack_start_states:
        stack[state] = set()

    visited = set()
    for v in start_nodes:
        visited.add((v, (v, rsm_start_nonterm)))

    start_dfa = rsm.boxes[rsm_start_nonterm].dfa.to_dict()
    start_dfa.setdefault(State(rsm_start), dict())

    to_visit = deepcopy(visited)

    while len(to_visit) > 0:

        v, (node, label) = to_visit.pop()
        cond = (node, label)

        if node in start_nodes and label == rsm_start and v in final_nodes:
            res.add((node, v))
        for rsm_state_, stack_state_ in stack.setdefault(cond, set()):
            s = (v, stack_state_)
            if s not in visited:
                visited.add(s)
                to_visit.add(s)

        for symbol, _ in start_dfa.items():
            if symbol in rsm.labels:
                stack_state_ = (v, symbol.value)
                s = (v, stack_state_)
                if s not in visited:
                    visited.add(s)
                    to_visit.add(s)

    return res
