from langchain.chat_models import ChatOpenAI
from modules.linting import run_flake8_on_code
from modules.linting import apply_black
import os
import json

# primary vs fallback LLMs
_primary_llm = ChatOpenAI(model="gpt-4", temperature=0.2, api_key=os.getenv("OPENAI_API_KEY"))
_fallback_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, api_key=os.getenv("OPENAI_API_KEY"))

def analyze_with_fallback(prompt_chain, code_snippet: str):
    # 1) static lint first
    lint_report = run_flake8_on_code(code_snippet)

    # 2) format code to standard style
    formatted = apply_black(code_snippet)

    # 3) call primary LLM
    primary = prompt_chain.run(code_snippet=formatted)

    # Debug log (remove in prod)
    print(f"Primary LLM output: {primary}")

    # Validate primary response
    if not primary.strip():
        print("Primary LLM returned an empty response.")
        fallback = _fallback_llm.call_as_llm(prompt_chain.prompt.format(code_snippet=formatted))
        return fallback, lint_report

    try:
        parsed = json.loads(primary)
    except json.JSONDecodeError as e:
        print(f"Primary LLM response was not valid JSON: {e}")
        fallback = _fallback_llm.call_as_llm(prompt_chain.prompt.format(code_snippet=formatted))
        return fallback, lint_report

    # Check confidence score
    if float(parsed.get("confidence_score", 0)) < 0.7:
        fallback = _fallback_llm.call_as_llm(prompt_chain.prompt.format(code_snippet=formatted))
        return fallback, lint_report

    return primary, lint_report
