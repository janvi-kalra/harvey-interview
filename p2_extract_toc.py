import fitz
import os
from openai import OpenAI
import ast
import csv
from part1_results import TOC_PAGES_PART_ONE_MAPPING

EXTRACT_TOC_PROMPT = "Given a string of a document's Table of Contents, you are an expert at converting it into a structured list (Section Header, Page Number) tuples that represent the table of contents."

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def clean(s):
    # Lowercase the string and remove specific whitespace characters
    return s.lower().replace('\n',
                             '').replace('\r',
                                         '').replace(' ',
                                                     '').replace('\t', '')


def find_zero_indexed_page_start(toc_page, section_name, seen_section_names):
    # Add current section name to dictionary
    if section_name not in seen_section_names:
        seen_section_names[section_name] = 1
    else:
        seen_section_names[section_name] += 1

    # Find link to real-indexed page name
    links = toc_page.get_links()
    num_of_skips = seen_section_names[section_name]
    for link in links:
        if link['kind'] == fitz.LINK_GOTO:
            link_text = toc_page.get_text("text", clip=link['from'])
            # Check if it's a substring
            if clean(section_name) in clean(link_text):
                if num_of_skips == 1:
                    toc_page_num = link['page']
                    return toc_page_num
                # Deal with duplicate section names
                num_of_skips -= 1
    return None


def extract_toc_for_pdf(pdf_path, toc_pages):
    doc = fitz.open(pdf_path)
    csv_file_path = os.path.join(
        'chunks',
        os.path.basename(pdf_path).replace('.Pdf', '.csv'))
    with open(csv_file_path, mode='w', newline='',
              encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            'Document',
            'Section Header',
            'Referenced Page Number',
            'Zero Indexed Page Number',
            'Classification',
            'Section Text',
        ])

    for page_num in toc_pages:
        page = doc.load_page(page_num)
        page_content = page.get_text()
        seen_section_names = {}

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
        except Exception:
            print(f"Unable to parse toc for {pdf_path} on page {page_num + 1}")
            continue

        with open(csv_file_path, mode='a', newline='',
                  encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            for entry in parsed_toc:
                section_name, referenced_page_number = entry
                zero_indexed_page_number = find_zero_indexed_page_start(
                    page, section_name, seen_section_names)
                # The LLM hallucinated a section name because it doesn't have a link in the TOC,
                # so don't include it in the CSV.
                if not zero_indexed_page_number:
                    # print(
                    #     f"Discarding hallucinated section name: {section_name}"
                    # )
                    continue
                csv_writer.writerow([
                    os.path.basename(pdf_path), section_name,
                    referenced_page_number, zero_indexed_page_number,
                    'UNDEFINED', 'UNDEFINED'
                ])


def iterate_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            toc_pages = sorted(TOC_PAGES_PART_ONE_MAPPING[filename])
            extract_toc_for_pdf(pdf_path, toc_pages)


# Main
iterate_folder("dataset")

# # Retry on failed PDFs: Update 'files' with the failed PDF paths.
# files = [
#     'Zendesk MA.Pdf',
#     'Coupa Software Inc_20230123_DEFM14A_20571922_4573621.Pdf',
#     'Archaea Energy Inc._20221114_DEFM14A_20445339_4545162.Pdf',
#     'Ranger Oil Corp_20230518_DEFM14A_20894462_4669228.Pdf',
# ]
# for file in files:
#     pdf_path_global = f'dataset/{file}'
#     extract_toc_for_pdf(pdf_path_global,
#                         sorted(TOC_PAGES_PART_ONE_MAPPING[file]))
