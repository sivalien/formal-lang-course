import pytest
import networkx as nx

from project.graph import (
    get_graph_info_by_name,
    create_and_save_two_cycle_graph,
    get_graph_labels,
)


def test_get_graph_info_by_name_wc():
    assert get_graph_info_by_name("wc") == (332, 269, {"a", "d"})


def test_get_graph_info_by_name_skos():
    labels = {
        "comment",
        "contributor",
        "creator",
        "definition",
        "description",
        "disjointWith",
        "domain",
        "example",
        "first",
        "inverseOf",
        "isDefinedBy",
        "label",
        "range",
        "rest",
        "scopeNote",
        "seeAlso",
        "subClassOf",
        "subPropertyOf",
        "title",
        "type",
        "unionOf",
    }
    assert get_graph_info_by_name("skos") == (144, 252, labels)


def test_create_and_save_two_cycle_graph(tmp_path):
    path = tmp_path / "test_graph.dot"
    count1 = 3
    count2 = 4
    labels = ("x", "y")
    edges = {
        ("1", "0"),
        ("1", "2"),
        ("2", "3"),
        ("3", "0"),
        ("0", "4"),
        ("4", "5"),
        ("5", "6"),
        ("6", "7"),
        ("0", "7"),
    }

    create_and_save_two_cycle_graph(path, count1, count2, labels)

    graph = nx.Graph(nx.nx_pydot.read_dot(path))

    assert get_graph_labels(graph) == {"x", "y"}
    assert set(graph.nodes) == {"0", "1", "2", "3", "4", "5", "6", "7"}
    assert set(graph.edges) == edges
