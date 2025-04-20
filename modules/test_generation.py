from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import os

# initialize a smaller LLM or re‑use GPT‑4 if budget allows
_tester = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

_template = PromptTemplate(
    input_variables=["code_snippet"],
    template="""
Generate pytest unit tests for the following Python functions. Ensure edge cases are covered.

```python
{code_snippet}
""" )

def generate_tests(code_snippet: str) -> str:
    """Return a .py file’s worth of pytest functions as text."""
    prompt = _template.format(code_snippet=code_snippet)
    return _tester.call_as_llm(prompt)