# pip install langgraph streamlit
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
import streamlit as st


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
        "treatment_prescribed": "Immediate ICU/Senior Doctor attention",
        "medication": "After treatment",
        "summary": "EMERGENCY case: Heart Rate %dbpm & Oxygen %d%%"
        % (state["heart_rate"], state["oxygen"]),
    }


def urgent(state: MedicalTriage):
    return {
        "cond_result": "urgent",
        "treatment_prescribed": "Fast-track doctor assessment",
        "medication": "After treatment",
        "summary": "URGENT case: Pain Level %d/10" % state["pain_level"],
    }


def priority(state: MedicalTriage):
    return {
        "cond_result": "priority",
        "treatment_prescribed": "Nurse evaluation then doctor",
        "medication": "After treatment",
        "summary": "PRIORITY case: Fever %.1fF" % state["temperature"],
    }


def routine(state: MedicalTriage):
    return {
        "cond_result": "routine",
        "treatment_prescribed": "Standard procedure",
        "medication": "After treatment",
        "summary": "ROUTINE case: Stable vitals",
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

# Streamlit App
st.set_page_config(page_title="Medical Triage System", layout="wide")

st.title("Medical Decision Support System")
st.markdown("---")

# Main input form
st.header("Patient Vitals Input")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Vital Signs")
    heart_rate = st.number_input(
        "Heart Rate (bpm)", min_value=40, max_value=180, value=80
    )
    oxygen = st.number_input(
        "Oxygen Saturation (%)", min_value=70, max_value=100, value=98
    )

with col2:
    st.subheader("Symptoms")
    pain_level = st.number_input(
        "Pain Level (0-10)", min_value=0, max_value=10, value=0
    )
    temperature = st.number_input(
        "Temperature (F)", min_value=95.0, max_value=108.0, value=98.6, step=0.1
    )

# Analyze button
if st.button("Generate Triage Report", type="primary"):
    with st.spinner("Analyzing patient vitals..."):
        initial_state = {
            "heart_rate": int(heart_rate),
            "oxygen": int(oxygen),
            "pain_level": int(pain_level),
            "temperature": float(temperature),
        }
        results = workflow.invoke(initial_state)

        # Quick metrics
        st.markdown("---")
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Condition", results["cond_result"].upper())
        with metric_col2:
            wait_time = (
                "IMMEDIATE" if results["cond_result"] == "emergency" else "PRIORITY"
            )
            st.metric("Wait Time", wait_time)
        with metric_col3:
            status = "Stable" if results["cond_result"] == "routine" else "Urgent Care"
            if "Stable" in status:
                st.success(status)
            else:
                st.error(status)

        # Detailed report
        st.markdown("## Detailed Medical Report")
        col_report1, col_report2 = st.columns(2)

        with col_report1:
            st.error(f"**Condition:** {results['cond_result'].upper()}")
            st.info(f"**Treatment Plan:** {results['treatment_prescribed']}")
        with col_report2:
            st.warning(f"**Medication:** {results['medication']}")
            st.success(f"**Clinical Summary:** {results['summary']}")

# Instructions
with st.expander("Triage Criteria"):
    st.markdown("""
    **EMERGENCY:** HR >120 or O2 <92%  
    **URGENT:** Pain >=8/10  
    **PRIORITY:** Temp >101F  
    **ROUTINE:** Stable vitals
    """)

# CLI test (optional)
if __name__ == "__main__":
    initial_state = {
        "heart_rate": 130,
        "oxygen": 96,
        "temperature": 102.3,
        "pain_level": 6,
    }
    results = workflow.invoke(initial_state)
    print("\n=== MEDICAL TRIAGE REPORT ===")
    print(f"Condition: {results['cond_result'].upper()}")
    print(f"Treatment: {results['treatment_prescribed']}")
    print(f"Medication: {results['medication']}")
    print(f"Summary: {results['summary']}")
