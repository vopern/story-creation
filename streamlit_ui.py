import os
import streamlit.components.v1 as components
import tempfile
import streamlit as st
import dotenv
from openai import OpenAI
import pandas as pd
import networkx as nx
from pyvis.network import Network
from belief_state import BeliefState
from agentic_helpers import QuestionAgent3, generate_story


st.set_page_config(page_title="Story Creation", layout="wide")
st.title("Multi-Turn Text-to-Story Generation")

dotenv.load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("MODEL_ID")

if "belief_state" not in st.session_state:
    st.session_state.belief_state = BeliefState(client, model)

if "agent" not in st.session_state:
    st.session_state.agent = QuestionAgent3(client, model)


# === Sidebar Chat Layout ===
with st.sidebar:
    st.title("💬 What story do you want to tell?")

    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.agent.messages.append({"role": "user", "content": user_input})
        st.session_state.belief_state.update_from_text_input(question=st.session_state.agent.get_last_question(), answer=user_input)
        st.session_state.agent.generate_question()

    with st.container():
        for msg in st.session_state.agent.get_chat():
            if msg["role"] == "system":
                st.info(msg["content"])
            else:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

st.markdown("""
### Edit Story Details

Enhance your story by directly editing the details below. 
Submit your changes to update the storyline prompt.
""")

tabs = st.tabs(["Storyline", "Characters", "Relations"])
with tabs[0]:
    default_storyline = [{"Act": 1, "Description": "Setup / Inciting Incident", "Content": None},
                         {"Act": 2, "Description": "Confrontation / Complications", "Content": None},
                         {"Act": 3, "Description": "Climax & Resolution", "Content": None}]
    st.session_state.storyline_df = pd.DataFrame(st.session_state.belief_state.state.get('storyline', default_storyline))
    st.subheader("Storyline")
    edited_storyline = st.data_editor(
        st.session_state.storyline_df,
        num_rows='fixed',
        use_container_width=True,
        key='storyline_edit'
    )
    st.session_state.storyline_df = edited_storyline

    submit_storyline = st.button('Submit storyline')

with tabs[1]:
    st.session_state.character_df = pd.DataFrame(st.session_state.belief_state.state.get('characters', []))
    st.subheader("Characters")
    edited_characters = st.data_editor(
        st.session_state.character_df,
        num_rows="dynamic",
        use_container_width=True,
        key='character_edit'
    )
    st.session_state.character_df = edited_characters

    submit_characters = st.button('Submit characters')

with tabs[2]:
    st.session_state.relation_df = pd.DataFrame(st.session_state.belief_state.state.get('relations', []))
    st.subheader("Relations")
    edited_relations = st.data_editor(
        st.session_state.relation_df,
        num_rows="dynamic",
        use_container_width=True,
        key='relation_edit'
    )
    st.session_state.relation_df = edited_relations

    submit_relations = st.button('Submit relations')

    # Create and visualize graph
    G = nx.Graph()
    for _, row in st.session_state.relation_df.dropna().iterrows():
        G.add_edge(row["character_1"], row["character_2"], label=row.get("description", ""))

    # Generate graph with pyvis
    net = Network(notebook=False, height="600px", width="100%", directed=False)
    net.from_nx(G)
    net.force_atlas_2based()  # spring-like layout

    # Save and display the graph
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        net.save_graph(tmp_file.name)
        tmp_file_path = tmp_file.name

    with open(tmp_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    components.html(html_content, height=300, scrolling=True)

    # Clean up tmp file
    os.remove(tmp_file_path)

if submit_characters:
    st.session_state.belief_state.update_from_structured_data(st.session_state.character_df.dropna(), key='characters')
    st.session_state.belief_state.parse_state('characters')

if submit_relations:
    st.session_state.belief_state.update_from_structured_data(st.session_state.relation_df.dropna(), key='relations')
    st.session_state.belief_state.parse_state('relations')

if submit_storyline:
    st.session_state.belief_state.update_from_structured_data(st.session_state.storyline_df.dropna(), key='storyline')
    st.session_state.belief_state.parse_state('storyline')

st.markdown("---")
with st.expander("🔍 Merged Story Prompt"):
    st.text(st.session_state.belief_state.prompt)

init_generation = st.button('Generate Story')

if init_generation:
    story = generate_story(client, st.session_state.belief_state.prompt)
    st.markdown("---")
    st.markdown("📖 **Story**")
    st.markdown("---")
    st.markdown(story)



