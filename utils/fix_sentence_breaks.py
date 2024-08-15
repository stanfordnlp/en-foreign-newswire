import os
import re

def check_for_missing_newlines(directory):
    # Pattern to match a period followed by a tab and a non-whitespace character,
    # excluding cases where the word starts with a quote or is part of a list/enumeration.
    sentence_pattern = re.compile(r'\.\t[^\d\s\'\"]')
    list_pattern = re.compile(r'^\d+\.')

    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    if sentence_pattern.search(line):
                        # Check the line before to ensure it's not a list/enumeration item
                        if i == 0 or not list_pattern.match(lines[i-1].strip()):
                            print(f"Issue found in file {filename} on line {i + 1}:")
                            print(f"Context:\n{lines[i-1].strip() if i > 0 else ''}\n{line.strip()}\n{lines[i+1].strip() if i < len(lines) - 1 else ''}")
                            print("-" * 40)

if __name__ == "__main__":
    directory = "/path/to/your/directory"
    check_for_missing_newlines(directory)
