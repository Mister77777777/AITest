import pytest
from autotestdesign.core.whitebox.state_machine import (
    StateMachine, Transition, parse_dsl, generate_all_states_cases, generate_all_transitions_cases,
)


def test_parse_dsl_simple():
    dsl = """
    S1 --login--> S2
    S2 --logout--> S1
    S2 --error--> S3
    """
    sm = parse_dsl(dsl, start_state="S1")
    assert sorted(sm.states) == ["S1", "S2", "S3"]
    assert len(sm.transitions) == 3


def test_state_machine_rejects_empty():
    with pytest.raises(ValueError):
        parse_dsl("", start_state="S1")


def test_all_states_coverage_reaches_every_state():
    sm = StateMachine(
        start_state="S1",
        states=["S1", "S2", "S3"],
        transitions=[
            Transition("S1", "login", "S2"),
            Transition("S2", "logout", "S1"),
            Transition("S2", "error", "S3"),
        ],
    )
    cases = generate_all_states_cases(sm, requirement_id="REQ-001")
    visited = {sm.start_state}
    for tc in cases:
        for step in tc.steps:
            for state in sm.states:
                if step.endswith(f"-> {state}"):
                    visited.add(state)
    assert visited == set(sm.states)


def test_all_transitions_coverage_includes_every_transition():
    sm = StateMachine(
        start_state="S1",
        states=["S1", "S2", "S3"],
        transitions=[
            Transition("S1", "login", "S2"),
            Transition("S2", "logout", "S1"),
            Transition("S2", "error", "S3"),
        ],
    )
    cases = generate_all_transitions_cases(sm, requirement_id="REQ-001")
    events = set()
    for tc in cases:
        for step in tc.steps:
            for t in sm.transitions:
                if f"--{t.event}-->" in step:
                    events.add(t.event)
    assert events == {"login", "logout", "error"}
    assert all(c.technique == "STT" for c in cases)
