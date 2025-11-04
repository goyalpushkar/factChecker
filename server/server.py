# ...existing code...
def has_matching_start(entries, word):
    return any(entry.startswith(word) for entry in entries)

# List with 3 values
sizes = ["small", "medium", "large"]

# Example usage
print("Available sizes:", sizes)

# Example usage
entries = ["apple pie", "banana split", "cherry tart"]
word = "apple"

if has_matching_start(entries, word):
    print(f"An entry starts with '{word}'.")
else:
    print(f"No entry starts with '{word}'.")
# ...existing code...
