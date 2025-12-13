import re
import sys

input = sys.stdin.read()

# Replace Numeric(x, y) → Numeric_x_y_
pattern = r"Numeric\((\d+),\s*(\d+)\)"
replacement = r"Numeric_\1_\2_"

result = re.sub(pattern, replacement, input, flags=re.IGNORECASE)

print(result)
