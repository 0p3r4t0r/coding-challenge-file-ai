import sys
import re


ER_DIAGRAM_HEADER = "### Entity-Relationship Diagram"
AUTO_GENERATED_TEXT = """
This diagram is auto-generated on commit by [update_readme.py](./scripts/entity-relationship-diagrams/update_readme.py)
using [paracelsus](https://github.com/tedivm/paracelsus).

DO NOT EDIT IT MANUALLY
"""


input = sys.stdin.read()
mermaid_markdown = f"```mermaid\n{input}```"


updated_content = ""
with open("README.md", "r") as readme:
    content = readme.read()

    if ER_DIAGRAM_HEADER not in content:
        raise Exception(f"README must contain the header {ER_DIAGRAM_HEADER}")

    upper, lower = content.split(ER_DIAGRAM_HEADER)

    upper = upper.rstrip("\n")
    lower = lower.replace(AUTO_GENERATED_TEXT, "")
    lower = re.sub(r"```mermaid.*?```", "", lower, flags=re.DOTALL)
    lower = lower.lstrip("\n")

    updated_content = f"{upper}\n\n{ER_DIAGRAM_HEADER}\n{AUTO_GENERATED_TEXT}\n\n{mermaid_markdown}\n\n\n{lower}"


with open("README.md", "w") as readme:
    readme.write(updated_content)
