import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import time
import pandas as pd
import numpy as np

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4", temperature=0.2, api_key=api_key)

# Define output schema for structured response
response_schemas = [
    ResponseSchema(name="issue_detected", description="Description of the bug or inefficiency in the code"),
    ResponseSchema(name="suggested_fix", description="Proposed solution or code fix"),
    ResponseSchema(name="confidence_score", description="Confidence level of the fix (0-1)"),
    ResponseSchema(name="reasoning_steps", description="Step-by-step reasoning for the suggested fix", optional=True),
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()

# Prompt template for code analysis and fix suggestion
prompt_template = """
You are an AI code analysis agent designed to detect bugs or inefficiencies in the provided code and suggest fixes. Analyze the following code snippet and provide:
- A description of any issues detected (bugs, inefficiencies, or potential improvements).
- A suggested fix or improvement.
- A confidence score (0-1) indicating how certain you are of the fix.
- A step-by-step reasoning for the suggested fix (if applicable).

Code snippet:
{code_snippet}

{format_instructions}
"""

prompt = PromptTemplate(
    input_variables=["code_snippet"],
    template=prompt_template,
    partial_variables={"format_instructions": format_instructions}
)

# Create the analysis chain
analysis_chain = LLMChain(llm=llm, prompt=prompt)


# Function to analyze code and get suggestions
def analyze_code(code_snippet):
    response = analysis_chain.run(code_snippet=code_snippet)
    return output_parser.parse(response)


# Function to apply fix
def apply_fix(original_code, suggested_fix, confidence_score):
    if confidence_score < 0.7:
        st.warning(f"⚠️ Low confidence score ({confidence_score}). Proceed with caution!")
    fixed_code = original_code + "\n# Applied fix: " + suggested_fix
    return fixed_code


# Custom CSS for a futuristic theme
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #fff;
        font-family: 'Courier New', monospace;
    }
    .stButton>button {
        background-color: #00ffcc;
        color: #0f0c29;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        transition: transform 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.1);
        background-color: #00cc99;
    }
    .stTextArea>label {
        color: #00ffcc;
        font-size: 18px;
    }
    .stCodeBlock {
        background-color: #1a1a3d;
        padding: 10px;
        border-radius: 5px.
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit UI
st.title("🌌 Self-Healing Code Nexus")
st.subheader("Empower your code with AI magic! ✨")

# Animated intro
with st.spinner("Initializing AI Matrix... 🚀"):
    time.sleep(1)
st.write("Upload or type your code, and let the Nexus heal it! 🛠️")

# Sidebar for creativity
st.sidebar.title("Nexus Control Panel")
st.sidebar.write("🌠 Customize your experience:")
theme = st.sidebar.selectbox("Choose a vibe", ["Cyberpunk", "Space Odyssey", "Neon Dream"])
st.sidebar.write("Powered by xAI's Grok 3")

# Input code
code_input = st.text_area("📝 Drop your code here:", height=200,
                          placeholder="e.g., def divide_numbers(a, b): return a / b")

if st.button("🔍 Activate Code Scan"):
    if code_input:
        with st.spinner("Scanning code in the AI Matrix... 🌌"):
            time.sleep(1)  # Simulate processing
            analysis_result = analyze_code(code_input)

        st.subheader("🧠 Analysis Report")
        st.json(analysis_result, expanded=True)

        issue = analysis_result["issue_detected"]
        fix = analysis_result["suggested_fix"]
        confidence = float(analysis_result["confidence_score"])
        reasoning = analysis_result.get("reasoning_steps", "No detailed steps provided.")

        st.subheader("🔧 Fix Details")
        st.write(f"**Issue Detected:** {issue}")
        st.write(f"**Suggested Fix:** {fix}")
        st.write(f"**Confidence Score:** {confidence} ⭐")

        # Collapsible step-by-step explanation
        with st.expander("📋 Step-by-Step Reasoning"):
            st.write(reasoning)

        # Canvas panel for visual dashboard
        st.subheader("📊 Code Health Dashboard")
        if 'confidence_history' not in st.session_state:
            st.session_state.confidence_history = []
        st.session_state.confidence_history.append(confidence)
        chart_data = pd.DataFrame({
            'Analysis': range(1, len(st.session_state.confidence_history) + 1),
            'Confidence': st.session_state.confidence_history
        })
        st.bar_chart(chart_data.set_index('Analysis'))

        # Approval button with animation
        if st.button("✅ Deploy Fix"):
            with st.spinner("Deploying fix to the Nexus... ⚡"):
                time.sleep(1)  # Simulate deployment
                updated_code = apply_fix(code_input, fix, confidence)
                st.session_state.updated_code = updated_code
                st.success("Fix deployed successfully! 🎉")

# Save and Load feature
st.subheader("💾 Code Management")
col1, col2 = st.columns(2)
with col1:
    if st.button("💾 Save Code"):
        if 'updated_code' in st.session_state:
            with open("healed_code.py", "w") as f:
                f.write(st.session_state.updated_code)
            st.success("Code saved as 'healed_code.py'!")
        else:
            st.warning("No updated code to save!")

with col2:
    if st.button("📂 Load Code"):
        try:
            with open("healed_code.py", "r") as f:
                st.session_state.updated_code = f.read()
                st.session_state.code_input = st.session_state.updated_code
                st.success("Code loaded successfully!")
        except FileNotFoundError:
            st.error("No saved code found!")

# Display updated code with creative flair
if 'updated_code' in st.session_state:
    st.subheader("🌟 Healed Code Matrix")
    st.code(st.session_state.updated_code, language="python")

# Footer
st.write("---")
st.write("Created with ❤️ by your AI companion | v1.1 | 12:10 PM PDT, April 19, 2025")
