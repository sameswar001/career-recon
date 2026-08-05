"""Compiles the career-recon StateGraph.

Wires researcher and gap_analyst as a parallel fan-out from START, joining
at writer, then writer -> critic -> (loop back to writer | human_review),
then human_review -> (finalize | writer). All nodes are stubs at this
stage — this file exists to prove the graph's shape (fan-out/fan-in,
conditional routing, cycles) before any real node logic is written.
"""

from langgraph.graph import END, START, StateGraph
from nodes.critic import critic_node, route_after_critic
from nodes.gap_analyst import gap_analyst_node
from nodes.human_review import human_review_node, route_after_human_review
from nodes.researcher import researcher_node
from nodes.writer import writer_node
from state import AgentState


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("researcher", researcher_node)
    graph.add_node("gap_analyst", gap_analyst_node)
    graph.add_node("writer", writer_node)
    graph.add_node("critic", critic_node)
    graph.add_node("human_review", human_review_node)

    graph.add_edge(START, "researcher")
    graph.add_edge(START, "gap_analyst")
    graph.add_edge("researcher", "writer")
    graph.add_edge("gap_analyst", "writer")
    graph.add_edge("writer", "critic")
    graph.add_conditional_edges(
        "critic", route_after_critic,
        {"writer": "writer", "human_review": "human_review"},
    )
    graph.add_conditional_edges(
        "human_review", route_after_human_review,
        {"finalize": END, "writer": "writer"},
    )

    return graph.compile()
