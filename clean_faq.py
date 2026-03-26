'''
i checked faq_stc.md file and i find , 
    need to remove all before this "# Quick Solutions" and 
    remove all after this "#### popular pages",,, 

for file faq_we.md , 
    need to remove all before "### Prepaid Mobile" and 
    remove all after this "Compare" ,,

'''


import os
import re

# =========================
# Paths
# =========================
INPUT_DIR = "data/raw"
OUTPUT_DIR = "Data_cleaned"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# Regex extraction
# =========================
def extract_with_regex(text, start_marker, end_marker):
    pattern = re.escape(start_marker) + r"(.*?)" + re.escape(end_marker)
    match = re.search(pattern, text, re.DOTALL)

    if match:
        return start_marker + match.group(1)
    else:
        print(f"⚠️ Regex failed: {start_marker} → {end_marker}")
        return ""


# =========================
# Cleaning logic
# =========================
def clean_file(file_name):
    input_path = os.path.join(INPUT_DIR, file_name)

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Apply rules
    if "stc" in file_name.lower():
        cleaned = extract_with_regex(
            content,
            "# Quick Solutions",
            "#### popular pages"
        )
        output_name = "faq_stc_cleaned.md"

    elif "we" in file_name.lower():
        cleaned = extract_with_regex(
            content,
            "### Prepaid Mobile",
            "Compare"
        )
        output_name = "faq_we_cleaned.md"

    else:
        cleaned = content
        output_name = f"{file_name}_cleaned.md"

    # Fallback
    if not cleaned:
        print(f"⚠️ Fallback used for {file_name}")
        cleaned = content

    # Save cleaned file
    output_path = os.path.join(OUTPUT_DIR, output_name)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned)

    print(f"✅ Saved cleaned file → {output_path}")


# =========================
# Run
# =========================
for file in os.listdir(INPUT_DIR):
    if file.endswith(".md"):
        clean_file(file)

print("\n🎯 Cleaning completed successfully.")