import fitz
import os
from openai import OpenAI

# Part 3: Classify. Use an OpenAi function here.

IS_TOC_PAGE_PROMPT = "You are an expert at classifying whether the provided text relates to the Termination, Indemnification, or Confidentiality of an acquisition. Given a snippet of text, return Termination, Indemnification, Confidentiality, or None"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


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
        print(result)
        if result == "true" or result == "'true'":
            toc_pages.add(page_num)
            print(f"page number {page_num + 1}")

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
# print(extract_toc_pages('dataset/Zendesk MA.Pdf'))
