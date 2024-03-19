import fitz
import os
from openai import OpenAI
import ast
import csv
import sys
import re

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
csv.field_size_limit(sys.maxsize)

CLASSIFY_PROMPT = "As a specialist in legal document analysis, your task is to determine the specific category that a given text segment belongs to. The categories are Termination, Indemnification, Confidentiality, or None. Given the section title and section content, return Termination, Indemnification, Confidentiality, or None. Weigh the section title more in your classification decision. Utilize your expertise to make accurate and clear categorizations based on the legal terminology and context presented in each text segment."

# Csv Columns
Section_Name_Index = 1
Zero_Indexed_Page_Number_Index = 3
Classification_Index = 4
Section_Text_Index = 5


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
            f"section title: {section_name}. section content: {truncated_section_body}"
        }])
    result = completion.choices[0].message.content
    if "Termination" in result:
        return 'Termination'
    if "Indemnification" in result:
        return 'Indemnification'
    if "Confidentiality" in result:
        return 'Confidentiality'
    return "None"


def get_next_section_name(lines, curr_line):
    # The next line in the CSV represents the next section
    if curr_line + 1 < len(lines):
        next_section_name = lines[curr_line + 1][Section_Name_Index]
        return next_section_name
    # Is the last section in the TOC
    return None


def get_search_end(lines, curr_line, doc):
    # Search all pages until the start of the next section.
    if curr_line + 1 < len(lines):
        # Search an extra page (+1) bc the next section might start on the same page as the current one
        return int(lines[curr_line + 1][Zero_Indexed_Page_Number_Index]) + 1
    # If this is the last section in the TOC, search till the end of the document
    return doc.page_count


# Remove all text from the page before the section starts.
def trim_search_start_page(text, curr_section_name):
    # Using regex to split to take case sensitivity into account
    parts = re.split(f'({re.escape(curr_section_name)})', text, maxsplit=1)
    return parts[2] if len(parts) > 2 else parts[0]


# If there is a section after the current one, remove all text with contents from the next section.
def trim_search_end_page(text, next_section_name):
    if next_section_name:
        # Using regex to split to take case sensitivity into account
        parts = re.split(f'({re.escape(next_section_name)})', text, maxsplit=1)
        return parts[0].strip()
    return text


def add_section_bodies(pdf_path):
    doc = fitz.open(pdf_path)
    csv_file_path = os.path.join(
        'chunks',
        os.path.basename(pdf_path).replace('.Pdf', '.csv'))

    # Read all the data from the CSV file
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)
        lines = list(reader)

    updated_data = [header]

    for i, line in enumerate(lines):
        # if (i != 4):
        #     updated_data.append(line)
        #     continue
        section_name = line[Section_Name_Index]
        text = ""

        search_start = int(line[Zero_Indexed_Page_Number_Index])
        next_section_name = get_next_section_name(lines, i)
        search_end = get_search_end(lines, i, doc)

        for page_num in range(search_start, search_end):
            # print(
            #     f"searching for section_name {section_name}: search_start {search_start + 1} search_end {search_end}"
            # )
            page = doc.load_page(page_num)
            page_text = page.get_text()
            if page_num == search_start:
                page_text = trim_search_start_page(page_text, section_name)
            if page_num == search_end - 1:
                page_text = trim_search_end_page(page_text, next_section_name)

            text += page_text

        # print(f'TEXT: \n {text}')

        classification = classify(section_name, text)

        # Formatting ensures that line breaks in the PDF do not overflow beyond current cell.
        line[Section_Text_Index] = f'"{text}"'
        line[Classification_Index] = classification
        updated_data.append(line)

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_data)


def iterate_folder(folder_path):
    i = 0
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            add_section_bodies(pdf_path)
            i += 1
            print(f"Completed {pdf_path}: {i}/100")


iterate_folder("dataset")

# # Unit tests
# filename_global = 'Archaea Energy Inc._20221114_DEFM14A_20445339_4545162.Pdf'
# pdf_path_global = f'dataset/{filename_global}'
# add_section_bodies(pdf_path_global)
