import os, time
import streamlit as st
from dotenv import load_dotenv

# Load .env
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# LangChain imports
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import (
    StructuredOutputParser, ResponseSchema
)
from langchain.chains import LLMChain

from modules import (
    auth, linting, test_generation,
    fallback_analysis, github_integration, analytics
)

# ——— build analysis_chain exactly as before ———
llm = ChatOpenAI(model="gpt-4", temperature=0.2, api_key=API_KEY)
schemas = [
    ResponseSchema(name="issue_detected", description="…"),
    ResponseSchema(name="suggested_fix", description="…"),
    ResponseSchema(name="confidence_score", description="…"),
    ResponseSchema(name="reasoning_steps", description="…", optional=True),
]
parser = StructuredOutputParser.from_response_schemas(schemas)
fmt_instr = parser.get_format_instructions()
prompt = PromptTemplate(
    input_variables=["code_snippet"],
    template=f"""
            You are an AI code analysis agent designed to detect bugs or inefficiencies in the provided code and suggest fixes. Analyze the following code snippet and provide:
             - A description of any issues detected (bugs, inefficiencies, or potential improvements).
             - A suggested fix or improvement.
             - A confidence score between 0 and 1 (for example, 0.82) indicating how certain you are of the fix.
             - A step-by-step reasoning for the suggested fix (if applicable).

            {{format_instructions}}""",
    partial_variables={"format_instructions": fmt_instr}
)
analysis_chain = LLMChain(llm=llm, prompt=prompt)

# ——— Streamlit UI ———
st.title("🌌 Self‑Healing Code Nexus v2.0")

# Simulate user identity
USER_ID = st.sidebar.text_input("User ID", value="alice")
tier = auth.get_subscription_level(USER_ID)
st.sidebar.success(f"Subscription tier: **{tier}**")

code = st.text_area("📝 Paste code here:", height=200)

if st.button("🔍 Scan & Heal"):
    if not code:
        st.warning("Please enter code first.")
        st.stop()

    # 1) Linting
    lint_report = ""
    if auth.feature_enabled("lint", tier):
        lint_report = linting.run_flake8_on_code(code)
        st.subheader("🧹 Lint Report")
        st.text(lint_report)

    # 2) AI Analysis (with fallback)
    raw_resp, lint_info = fallback_analysis.analyze_with_fallback(
        analysis_chain, code
    )
    parsed = parser.parse(raw_resp)
    conf = float(parsed["confidence_score"])
    st.subheader("🧠 AI Suggestion")
    st.json(parsed)

    # 3) Unit‑Test Generation
    if auth.feature_enabled("testgen", tier):
        st.subheader("🧪 Generated Tests")
        tests = test_generation.generate_tests(code)
        st.code(tests, language="python")

    # 4) Log analytics
    if auth.feature_enabled("analytics", tier):
        analytics.log_event(USER_ID, "analysis", conf)

    # 5) Show Deploy button and GitHub PR
    if auth.feature_enabled("autopr", tier):
        st.subheader("🔗 GitHub Auto‑PR")
        repo = st.text_input("Repo (owner/name)", placeholder="myorg/myrepo")
        path = st.text_input("File path in repo", placeholder="src/my_module.py")
        if st.button("✅ Create PR"):
            pr_url = github_integration.create_fix_pr(
                repo_full_name=repo,
                file_path=path,
                updated_code=code + "\n# FIX: " + parsed["suggested_fix"],
                token=GITHUB_TOKEN
            )
            st.success(f"PR created: {pr_url}")

    # 6) Real‑time collaboration (stub)
    if auth.feature_enabled("realtime", tier):
        st.info("🔄 Real‑time collaboration panel coming soon…")

    # 7) Show confidence history
    st.subheader("📊 Confidence over time")
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append(conf)
    st.line_chart(st.session_state.history)

st.write("---")
st.caption("© 2025 Self‑Healing Code Nexus")
