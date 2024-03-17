def find_toc_link_page_number(pdf_path):
    # Open the PDF
    doc = fitz.open(pdf_path)

    for page_num in range(0, max(len(doc), 3)):
        page = doc.load_page(page_num)

        # Get all link annotations in the page
        links = page.get_links()

        for link in links:
            if link['kind'] == fitz.LINK_URI or link['kind'] == fitz.LINK_GOTO:
                # Get the link text
                link_text = page.get_text("text", clip=link['from'])

                if "table of contents" in link_text.lower(
                ) and link['kind'] == fitz.LINK_GOTO:
                    toc_page_num = link[
                        'page'] + 1  # Adding 1 as page numbers are 0-indexed
                    print(
                        f'"Found on page {page_num + 1}, linking to page {toc_page_num}'
                    )
                    return toc_page_num

    print(f'No "Table of Contents" link found for {pdf_path}.')
    return None


#  for page_num in range(0, 20):
#         page = doc.load_page(page_num)
#         text = page.get_text()
#         # tabs = page.find_tables()
#         # for i, tab in enumerate(tabs):  # iterate over all tables
#         #     df = tab.to_pandas()
#         #     print(df)

# # Attempt to extract the title from the top of the page
# # Adjust the rectangle coordinates as needed
# title_area = fitz.Rect(0, 50, page.rect.width, 150)
# title = page.get_text("text", clip=title_area).split('\n')[0].strip()
