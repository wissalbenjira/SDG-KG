import streamlit as st
import pandas as pd

def sim_space(ds, qs):
    return 1.0 if ds == qs else 0.5 if qs in ds else 0.0

def sim_time(dt, qt):
    return 1.0 if qt.split("-")[0] in dt else 0.5 if qt[:4] in dt else 0.0

def sim_context(dc, qc):
    return 1.0 if qc.lower() in dc.lower() else 0.5 if any(qc.lower() in d.lower() for d in dc.split(',')) else 0.0

weights = {"s": 0.25, "t": 0.25, "c": 0.2, "r": 0.15, "p": 0.15}

def run():
    st.title("Define a Use Case")

    # Étape 1 : choix du scénario
    st.header("Describe your use case")
    predefined_use_cases = [
        "...",
        "How women struggle with the convenient access to public transports in Hauts-de-Seine area since the 2017 French elections",
        "How elderly people in Paris access healthcare services since COVID",
        "Access to education for children in rural areas since 2015"
    ]
    selected_scenario = st.selectbox("Choose a predefined use case:", predefined_use_cases)

    if selected_scenario == "How women struggle with the convenient access to public transports in Hauts-de-Seine area since the 2017 French elections":
        st.success("Use case selected ✅")

        st.header("Query Parameters")
        indicator = "11.2.1"
        space = "92 - Hauts-de-Seine"
        time_param = "Since 2017"
        context = "Women"

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📊 Indicator", indicator)
        col2.metric("🗺️ Space", space)
        col3.metric("⏱️ Time", time_param)
        col4.metric("🧍 Context", context)

        step2_confirm = st.checkbox("✅ These parameters are correct", key="step2")

        if step2_confirm:
            st.header("Relevant Data Sources")

            datasets = {
                "INSEE": {"D_s": "92", "D_t": "2017-2022", "D_c": "Women, Age", "D_r": 0.90, "D_p": 0.95},
                "WorldPop": {"D_s": "FR", "D_t": "2015-2021", "D_c": "Age, Women", "D_r": 0.80, "D_p": 0.85},
                "Open Data Paris": {"D_s": "75", "D_t": "2018-2023", "D_c": "Sex, Transport, Disability", "D_r": 0.83, "D_p": 0.86}
            }

            Q = {"q_s": "92", "q_t": "2017-2024", "q_c": "Women"}

            st.subheader("Top scores (overview)")
            score_preview = []
            for name, data in datasets.items():
                sim_s = sim_space(data["D_s"], Q["q_s"])
                sim_t = sim_time(data["D_t"], Q["q_t"])
                sim_c = sim_context(data["D_c"], Q["q_c"])
                r = data["D_r"]
                p = data["D_p"]

                tsm = round((weights["s"] * sim_s + weights["t"] * sim_t + weights["c"] * sim_c +
                             weights["r"] * r + weights["p"] * p) / sum(weights.values()), 3)

                score_preview.append((name, tsm))

            score_preview = sorted(score_preview, key=lambda x: x[1], reverse=True)
            for name, score in score_preview:
                st.markdown(f"**{name}** — TSM Score: `{score}`")

            step3_confirm = st.checkbox("Show TSM calculation details")

            if step3_confirm:
                st.header("TSM Calculation Details")
                details = []
                for name, data in datasets.items():
                    sim_s = sim_space(data["D_s"], Q["q_s"])
                    sim_t = sim_time(data["D_t"], Q["q_t"])
                    sim_c = sim_context(data["D_c"], Q["q_c"])
                    r = data["D_r"]
                    p = data["D_p"]
                    tsm = round((weights["s"] * sim_s + weights["t"] * sim_t + weights["c"] * sim_c +
                                 weights["r"] * r + weights["p"] * p) / sum(weights.values()), 3)

                    details.append({
                        "Source": name,
                        "Spatial Sim": sim_s,
                        "Temporal Sim": sim_t,
                        "Context Sim": sim_c,
                        "Reliability": r,
                        "Completeness": p,
                        "Final TSM Score": tsm
                    })

                df = pd.DataFrame(details)
                st.dataframe(df.style.format(precision=2), use_container_width=True)

                st.header("Select the database to use")
                score_labels = [f"{name} ({score:.2f})" for name, score in score_preview]
                label_to_name = {f"{name} ({score:.2f})": name for name, score in score_preview}
                options = ["-- Select --"] + score_labels
                db_display_choice = st.selectbox("Choose from available datasets:", options)

                db_choice = label_to_name.get(db_display_choice)
                if db_choice:
                    st.success(f"You selected **{db_choice}** as the source for indicator **{indicator}**.")
