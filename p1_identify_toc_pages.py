import fitz
import os
from openai import OpenAI

# Part 1: Identify the page numbers in the PDF that have the table of contents of them
# Return {pdfName: [pageNumber1, pageNumber2, ...]}. These page numbers do not have to be contiguous.
# Further, we can assume that the table of contents is always within the first 20 pages of a document so we
# only need to search the first 20 pages for efficiency.

EXAMPLE_1_TRUE_INPUT = 'TABLE OF CONTENTS \n SUMMARY TERM SHEET \n 1 \n The Special General Meeting \n 1 \n Record Date and Quorum \n 1 \n Required Votes \n 2 \n The Parties to the Merger \n 2 \n The Merger Proposal \n 3 \n When the Merger Becomes Effective \n 4'
EXAMPLE_2_FALSE_INPUT = 'The Merger Agreement (Page 57) \n Treatment of Common Shares (Page 57) \n At the effective time, each common share issued and outstanding immediately prior to the effective time (other than any common share that is owned by Argo Group as treasury shares, by Argo Group, Brookfield Reinsurance. \n'
IS_TOC_PAGE_PROMPT = f"You are an expert at assessing whether the provided text excerpt belongs to a Table of Contents. A Table of Contents is a collection of titles and their corresponding number. When presented with text, carefully evaluate its characteristics and if it aligns with the criteria of being part of a Table of Contents, respond with 'true'. If it does not meet these criteria, respond with 'false'. Your analysis should focus on distinguishing between Table of Contents entries and regular pages of text. \n Example 1: \n Input: {EXAMPLE_1_TRUE_INPUT} \n Output: 'true'.."

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def has_links(page):
    # In order to be a TOC page, the page is likely to have >= 1 link on the page
    links = page.get_links()
    num_links = 0
    for link in links:
        if link['kind'] == fitz.LINK_GOTO:
            link_text = page.get_text("text", clip=link['from'])
            if link_text.lower().strip('\n') != "table of contents":
                num_links += 1
    return num_links


def identify_toc_pages(pdf_path):
    doc = fitz.open(pdf_path)
    toc_pages = set()
    print(f'{pdf_path}')

    for page_num in range(0, 20):
        page = doc.load_page(page_num)
        page_content = page.get_text()

        completion = client.chat.completions.create(model="gpt-4",
                                                    messages=[{
                                                        "role":
                                                        "system",
                                                        "content":
                                                        IS_TOC_PAGE_PROMPT,
                                                    }, {
                                                        "role":
                                                        "user",
                                                        "content":
                                                        page_content
                                                    }])
        result = completion.choices[0].message.content
        if result == "true" or result == "'true'":
            print(f"page number {page_num + 1}")
            if has_links(page) >= 1:
                toc_pages.add(page_num)
            else:
                print('discarded bc not enough links on the page')

    return toc_pages


def iterate_folder(folder_path):
    final_result = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            toc_pages = identify_toc_pages(pdf_path)
            final_result[filename] = toc_pages
    print(final_result)


iterate_folder("dataset")

# # Unit tests
# print(identify_toc_pages('dataset/Zendesk MA.Pdf'))
# print(
#     identify_toc_pages(
#         'dataset/Coupa Software Inc_20230123_DEFM14A_20571922_4573621.pdf'))
# print(
#     identify_toc_pages(
#         'dataset/Archaea Energy Inc._20221114_DEFM14A_20445339_4545162.Pdf'))
# print(
#     identify_toc_pages(
#         'dataset/Ranger Oil Corp_20230518_DEFM14A_20894462_4669228.Pdf'))
