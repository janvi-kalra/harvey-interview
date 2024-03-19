import fitz
import os
from openai import OpenAI
import ast
import csv
import sys

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
csv.field_size_limit(sys.maxsize)

CLASSIFY_PROMPT = "You are an expert at classifying whether the provided text relates to the Termination, Indemnification, or Confidentiality of an acquisition. Given the section name and the section content, return Termination, Indemnification, Confidentiality, or None"


def clean(s):
    return s.strip("\n").replace("\n", " ")


def truncate_to_token_limit(text):
    # 1 token ~= 4 chars
    # gpt-3.5-turbo limit is 16385 tokens ~= 16385 * 4 characters
    # for safety, add 5,000 char buffer
    max_length = 16385 * 4 - 5000
    truncated_string = text[:max_length]
    return truncated_string


def classify(section_name, section_body):
    truncated_section_body = truncate_to_token_limit(section_body)
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "system",
            "content": CLASSIFY_PROMPT,
        }, {
            "role":
            "user",
            "content":
            f"section name: {section_name}. section content: {truncated_section_body}"
        }])
    result = completion.choices[0].message.content
    if result == "Termination" or result == "Indemnification" or result == "Confidentiality" or result == "None":
        return result
    return "None"


def get_next_section_name(lines, curr_line):
    # The next line in the CSV represents the next section
    if curr_line + 1 < len(lines):
        next_section_name = lines[curr_line + 1][1]
        return clean(next_section_name)
    # It is the last section in the TOC
    return None


def get_search_end(lines, curr_line, doc):
    # Search all pages until the next section.
    if curr_line + 1 < len(lines):
        # Search an extra page (+1) bc the next section might start on the same page as the current one
        return lines[curr_line + 1][2] + 1
    # If this is the last section in the TOC, search till the end of the document
    return doc.page_count


# Remove all text from the page before the section starts.
def trim_text(text, curr_section_name, next_section_name):
    parts = text.split(curr_section_name, 1)
    trimmed_text = parts[1] if len(parts) > 1 else parts[0]

    # If there is a section after the current one, remove all text with contents from the next section.
    if next_section_name:
        parts = trimmed_text.split(next_section_name, 1)
        trimmed_text = parts[0].strip()

    return trimmed_text


def add_section_bodies(pdf_path):
    doc = fitz.open(pdf_path)
    csv_file_path = os.path.join(
        'chunks',
        os.path.basename(pdf_path).replace('.Pdf', '.csv'))

    # First, read all the data from the CSV file
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read the header
        header.append(
            "Classification")  # Add 'Classification' column to the header
        lines = list(reader)  # Read all rows into a list

    updated_data = [header]

    for i, line in enumerate(lines):
        section_name = line[1]
        text = ""

        search_start = line[3]
        next_section_name = get_next_section_name(lines, i)
        search_end = get_search_end(lines, i, doc)

        for page_num in range(search_start, search_end):
            page = doc.load_page(page_num)
            text += page.get_text()

        text = trim_text(text, section_name, next_section_name)
        classification = classify(section_name, text)

        # Formatting ensures that line breaks in the PDF do not overflow beyond current cell.
        line[2] = f'"{text}"'
        line.append(classification)
        updated_data.append(line)

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_data)


def iterate_folder(folder_path):
    final_result = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)

            add_section_bodies(pdf_path)
    print(final_result)


# iterate_folder("dataset")

# Unit tests
filename_global = 'ALKURI GLOBAL ACQUISITION CORP._20210930_DEFM14A_19561988_4303635.Pdf'
pdf_path_global = f'dataset/{filename_global}'
add_section_bodies(pdf_path_global)
