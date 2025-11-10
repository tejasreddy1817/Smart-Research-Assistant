import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from agents.search_agent import SearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.summarizer_agent import SummarizerAgent
from agents.validator_agent import ValidatorAgent
from agents.formatter_agent import FormatterAgent
import os


st.set_page_config(page_title="Smart Research Assistant", layout="wide")

st.title("Smart Research Assistant (LangGraph-style Multi-Agent)")
st.write("Enter a research topic and run the workflow. Uses OpenAI if you provide `OPENAI_API_KEY` in env.")

# Sidebar config
with st.sidebar:
    st.header("Options")
    use_web = st.checkbox("Attempt live web search (requires SERPAPI_KEY)", value=False)
    use_openai = st.checkbox("Use OpenAI for summarization (requires OPENAI_API_KEY)", value=False)
    show_raw = st.checkbox("Show intermediate agent outputs", value=True)
    max_docs = st.number_input("Max documents to fetch (search agent)", min_value=1, max_value=10, value=3)
    run_btn = st.button("Run Workflow")

# Debug line (you can remove later)
st.sidebar.write("Loaded SERPAPI_KEY:", os.getenv("SERPAPI_KEY"))
topic = st.text_input("Research topic", "")

# Agents (simple orchestrator)
search_agent = SearchAgent()
analysis_agent = AnalysisAgent()
summarizer_agent = SummarizerAgent(use_openai=use_openai and bool(os.getenv("OPENAI_API_KEY")))
validator_agent = ValidatorAgent()
formatter_agent = FormatterAgent()

if run_btn and topic.strip():
    st.header(f"Results for: {topic}")
    with st.spinner("Running Search Agent..."):
        docs = search_agent.run(topic, max_results=int(max_docs), use_web=use_web)
    if show_raw:
        st.subheader("Search Agent: Retrieved documents")
        for i, d in enumerate(docs, 1):
            st.markdown(f"**Doc {i} — {d['title']}**")
            st.write(d["content"][:800] + ("..." if len(d["content"])>800 else ""))
            st.write("---")

    with st.spinner("Running Analysis Agent..."):
        analysis = analysis_agent.run(docs)
    if show_raw:
        st.subheader("Analysis Agent: Findings")      
        st.json(analysis)

    with st.spinner("Running Summarizer Agent..."):
        summary = summarizer_agent.run(topic, docs, analysis)
    st.subheader("Final Structured Summary")
    st.markdown(summary)

    with st.spinner("Running Validator Agent..."):
        val_report = validator_agent.run(summary, docs, analysis)
    if show_raw:
        st.subheader("Validator Report")
        st.write(val_report)

    with st.spinner("Formatting output..."):
        md = formatter_agent.to_markdown(topic, summary, analysis)
        st.download_button("Download Summary (Markdown)", md, file_name=f"{topic.replace(' ','_')}_summary.md")
        st.write("---")
        st.subheader("Markdown Preview")
        st.markdown(md)
else:
    st.info("Enter a topic and click **Run Workflow**.")
