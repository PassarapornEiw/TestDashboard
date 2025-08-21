import base64

# File paths
input_file = "dashboard_server.py"
encoded_output = "1908252153.txt"

# Encode file content to base64
with open(input_file, "rb") as f:
    encoded_str = base64.b64encode(f.read()).decode("utf-8")

# Save encoded content to a .txt file
with open(encoded_output, "w", encoding="utf-8") as f:
    f.write(encoded_str)

encoded_output
