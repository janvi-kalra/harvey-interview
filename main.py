import fitz  # PyMuPDF
import os


def extract_toc(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Extract the table of contents
    toc = pdf_document.get_toc()
    print(f"got TOC for {pdf_path}: {toc}")

    # Print the table of contents
    for entry in toc:
        level, title, page = entry
        print(f"Level: {level}, Title: {title}, Page: {page}")

    # Close the PDF document
    pdf_document.close()


# TODO(janvi): Study OS.
def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            extract_toc(pdf_path)


# process_folder("dataset")  # Replace 'dataset' with your folder's name
extract_toc('dataset/Zendesk MA.Pdf')
