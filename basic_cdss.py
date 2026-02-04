# pip install langgraph langchain
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal


# Creating class
class MedicalTriage(TypedDict):
    heart_rate: int
    oxygen: int
    pain_level: int
    temperature: float
    cond_result: str
    treatment_prescribed: str
    medication: str
    summary: str


# Defining graph
graph = StateGraph(MedicalTriage)


# Defining nodes
def collect_vitals(state: MedicalTriage):
    return state


def check_condition(
    state: MedicalTriage,
) -> Literal["emergency", "urgent", "priority", "routine"]:
    if state["heart_rate"] > 120 or state["oxygen"] < 92:
        return "emergency"
    elif state["pain_level"] >= 8:
        return "urgent"
    elif state["temperature"] > 101:
        return "priority"
    else:
        return "routine"


def emergency(state: MedicalTriage):
    return {
        "cond_result": "emergency",
        "treatment_prescribed": "Immediate ICU/ Senior Doctor attention",
        "medication": "After treatment",
        "summary": f"EMERGENCY case: Heart Rate is {state['heart_rate']} & Oxygen level is {state['oxygen']} %",
    }


def urgent(state: MedicalTriage):
    return {
        "cond_result": "urgent",
        "treatment_prescribed": "Fast-track doctor assessment",
        "medication": "After treatment",
        "summary": f"URGENT case: Pain Level is {state['pain_level']} /10",
    }


def priority(state: MedicalTriage):
    return {
        "cond_result": "priority",
        "treatment_prescribed": "First do evalutaion by nurse, then consult doctor",
        "medication": "After treatment",
        "summary": f"PRIORITY case: Fever is {state['temperature']:.1f}°C",
    }


def routine(state: MedicalTriage):
    return {
        "cond_result": "routine",
        "treatment_prescribed": "Standard Procudure",
        "medication": "After treatment",
        "summary": f"ROUTINE case: Stable vitals",
    }


# Adding nodes
graph.add_node("vitals", collect_vitals)
graph.add_node("emergency", emergency)
graph.add_node("urgent", urgent)
graph.add_node("priority", priority)
graph.add_node("routine", routine)

# Adding edges
graph.add_edge(START, "vitals")
graph.add_conditional_edges(
    "vitals",
    check_condition,
    {
        "emergency": "emergency",
        "urgent": "urgent",
        "priority": "priority",
        "routine": "routine",
    },
)
graph.add_edge("emergency", END)
graph.add_edge("urgent", END)
graph.add_edge("priority", END)
graph.add_edge("routine", END)

# Compiling graph
workflow = graph.compile()

# Initialising graph
initial_state = {"heart_rate": 130, "oxygen": 96, "temperature": 102.3, "pain_level": 6}
results = workflow.invoke(initial_state)
print("\n=== MEDICAL TRIAGE REPORT ===")
print(f"Condition: {results['cond_result']}")
print(f"Treatment: {results['treatment_prescribed']}")
print(f"Medication: {results['medication']}")
print(f"Summary: {results['summary']}")
print("============================")
