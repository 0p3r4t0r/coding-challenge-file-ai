import sys
import re


ER_DIAGRAM_HEADER = "### Entity-Relationship Diagram"


input = sys.stdin.read()
mermaid_markdown = f'```mermaid\n{input}```'


updated_content = ''
with open("../README.md", "r") as readme:
    content = readme.read()

    if ER_DIAGRAM_HEADER not in content:
        raise Exception(f'README must contain the header {ER_DIAGRAM_HEADER}')

    upper, lower = content.split(ER_DIAGRAM_HEADER)

    upper = upper.rstrip('\n')
    lower = re.sub(r"```mermaid.*?```", "", lower, flags=re.DOTALL)
    lower = lower.lstrip('\n')

    updated_content = f'{upper}\n\n{ER_DIAGRAM_HEADER}\n\n{mermaid_markdown}\n\n\n{lower}'


with open("../README.md", "w") as readme:
    readme.write(updated_content)
