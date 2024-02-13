import cfpq_data
from networkx.drawing.nx_pydot import write_dot

from typing import Tuple


def get_graph_labels(graph):
    return set(map(lambda x: x[2], graph.edges.data("label")))


def get_graph_info_by_name(name: str):
    graph = cfpq_data.graph_from_csv(cfpq_data.download(name))
    return graph.number_of_nodes(), graph.number_of_edges(), get_graph_labels(graph)


def create_and_save_two_cycle_graph(
        path: str, count1: int, count2: int, labels: Tuple[str, str] = ('a', 'b')
):
    graph = cfpq_data.graphs.generators.labeled_two_cycles_graph(
        n=count1, m=count2, labels=labels
    )
    write_dot(G=graph, path=path)
