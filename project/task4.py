from project.task3 import FiniteAutomaton, intersect_automata


def reachability_with_constraints(
    fa: FiniteAutomaton, constraints_fa: FiniteAutomaton
) -> dict[int, set[int]]:
    intersection = intersect_automata(fa, constraints_fa, lbl=False)
    res = {state: set() for state in fa.start_states}

    if intersection.is_empty():
        return res

    from_states, to_states = intersection.get_transitive_closure().nonzero()
    n = len(constraints_fa)

    for from_state, to_state in zip(from_states, to_states):
        if (
            from_state in intersection.start_states
            and to_state in intersection.final_states
        ):
            res[fa.get_state_by_index(from_state // n)].add(
                fa.get_state_by_index(to_state // n)
            )

    return res
