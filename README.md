# harvey-interview

## Extracting the Table of Contents

### 1

- Tried to use get_toc() from PyNum so need to come up with an approach for this

### 2

- Notice that in the example dataset there is always a link to the Table of Contents in the first couple pages of the document.
- Follow that link to see what page number the TOC starts at
- We don't know how many pages the TOC is
- We use an OpenAI function to determine if the page is a TOC or not (will return T/F). We know the pages that the TOC are on
- Use RAG to take the page and get the LLM to return a comma separated value of (Section Header, Section Body, Page Number).
- Works for every doc but breaks for "PREFERRED APARTMENT COMMUNITIES INC_20220414_DEFM14A_20015574_4442255" because there are no links to TOC there

### 3

Notice that all the TOC pages are i/ii/iii and before the first page

### 3

## Classifying Sections into Termination, Indemnification, Confidentiality, or None of the Above

## Summarizing the similarities/differences in doc's Termination, Confidentiality, or Indemnification provisions

# part 1 - go through an find the pages that are TOC and print out the results

# part 2 - go through and try to find the TOC for those pages and put it in

# part 3 - find the text body of those TOC results by crawling through the individual documents and update the csvs

# part 4 - classification


reason we split it up is because it's not reliable. make more specific prompts. for latency. 


