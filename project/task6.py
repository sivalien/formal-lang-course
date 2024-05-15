from pyformlang.cfg import CFG, Variable, Terminal, Epsilon

from collections import defaultdict
from typing import Tuple


def cfg_to_weak_normal_form(grammar, start="S") -> CFG:
    elim_cfg = grammar.eliminate_unit_productions().remove_useless_symbols()
    return CFG(
        productions=set(
            elim_cfg._decompose_productions(
                elim_cfg._get_productions_with_only_single_terminals()
            )
        ),
        start_symbol=Variable(start),
    )


def cfpq_with_hellings(
    cfg,
    graph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[Tuple[int, int]]:
    prod_terminal, prod_epsilon, prod_mult = defaultdict(set), set(), defaultdict(set)
    for prod in cfg_to_weak_normal_form(cfg).productions:
        if len(prod.body) == 2:
            prod_mult[prod.head].add((prod.body[0], prod.body[1]))
        elif len(prod.body) == 1 and isinstance(prod.body[0], Terminal):
            prod_terminal[prod.head].add(prod.body[0])
        elif len(prod.body) == 1 and isinstance(prod.body[0], Epsilon):
            prod_epsilon.add(prod.body[0])

    r = {
        (n, start, end)
        for (start, end, label) in graph.edges.data("label")
        for n in prod_terminal
        if label in prod_terminal[n]
    }
    r.union({(n, node, node) for n in prod_epsilon for node in graph.nodes})

    r_copy = r.copy()
    temp = set()

    while len(r_copy) != 0:
        n1, v1, u1 = r_copy.pop()

        for n2, v2, u2 in r:
            if v1 == u2:
                for N_k in prod_mult:
                    if (n2, n1) in prod_mult[N_k] and (N_k, v2, v1) not in r:
                        r_copy.add((N_k, v2, u1))
                        temp.add((N_k, v2, u1))

    r.union(temp)

    return {
        (start, end)
        for (n, start, end) in r
        if Variable(n) == cfg.start_symbol
        and (start_nodes is None or start in start_nodes)
        and (final_nodes is None or end in final_nodes)
    }


def read_cfgrammar(path, start="S") -> CFG:
    with open(path, "r") as file:
        return CFG.from_text(file.read(), Variable(start))
