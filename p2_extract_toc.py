import fitz
import os
from openai import OpenAI
import ast
import csv
from part1_results import TOC_PAGES_PART_ONE_MAPPING

# Part 2: On the TOC pages in a document, use an LLM to convert the unstructured data into structured content.

EXTRACT_TOC_PROMPT = "Given a string of a document's Table of Contents, you are an expert at converting it into a structured list (Section Header, Page Number) tuples that represent the table of contents."

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def clean(s):
    return s.lower().strip("\n").replace("\n", " ")


# issue #1:
# issue #2: dups of mergers. create a dictionary of section names that you've already seen. and get the second or third one according to fmap.


def find_zero_indexed_page_start(toc_page, section_name):
    links = toc_page.get_links()
    for link in links:
        if link['kind'] == fitz.LINK_GOTO:
            link_text = toc_page.get_text("text", clip=link['from'])
            if clean(link_text) == clean(section_name):
                toc_page_num = link['page']
                return toc_page_num
    return None


def extract_toc(pdf_path, toc_pages):
    doc = fitz.open(pdf_path)
    csv_file_path = os.path.join(
        'chunks',
        os.path.basename(pdf_path).replace('.Pdf', '.csv'))
    with open(csv_file_path, mode='w', newline='',
              encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(
            ['Document', 'Section Header', 'Section Text', 'Page Number'])

    for page_num in toc_pages:
        page = doc.load_page(page_num)
        page_content = page.get_text()

        completion = client.chat.completions.create(model="gpt-4",
                                                    messages=[{
                                                        "role":
                                                        "system",
                                                        "content":
                                                        EXTRACT_TOC_PROMPT,
                                                    }, {
                                                        "role":
                                                        "user",
                                                        "content":
                                                        page_content
                                                    }])
        result = completion.choices[0].message.content
        try:
            parsed_toc = ast.literal_eval(result)
            # print(f'{pdf_path}: {page_num + 1}: parsed_toc: {parsed_toc}')
        except:
            print(f"Unable to parse toc for {pdf_path} on page {page_num + 1}")
            continue

        with open(csv_file_path, mode='a', newline='',
                  encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            for entry in parsed_toc:
                section_name, llm_page_number = entry
                section_name = clean(section_name)
                real_page_number = find_zero_indexed_page_start(
                    page, section_name)
                # The LLM hallucinated a section name that doesn't have a link in the TOC, so don't include it in the CSV.
                if not real_page_number:
                    print(f'threw away section name: {section_name}')
                    continue
                csv_writer.writerow([
                    os.path.basename(pdf_path), section_name, 'UNDEFINED',
                    real_page_number
                ])


def iterate_folder(folder_path):
    final_result = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            toc_pages = sorted(TOC_PAGES_PART_ONE_MAPPING[filename])
            extract_toc(pdf_path, toc_pages)
    print(final_result)


# iterate_folder("dataset")

# Unit Tests
file_name_global = 'Argo Group International Holdings, Ltd._20230320_DEFM14A_20737540_4621891.Pdf'
pdf_path_global = f'dataset/{file_name_global}'
extract_toc(pdf_path_global, TOC_PAGES_PART_ONE_MAPPING[file_name_global])

# def retry_on_failed_extractions():
#     failed_files = []
#     for filename in failed_files:
#         pdf_path = f'dataset/{filename}'
#         toc_pages = sorted(TOC_PAGES_PART_ONE_MAPPING[filename])
#         extract_toc(pdf_path, toc_pages)
