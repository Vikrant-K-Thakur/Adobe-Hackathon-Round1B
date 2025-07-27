import fitz
import re
from typing import List, Dict, Tuple

def clean_title(text: str) -> str:
    """Clean and format section title."""
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^[•\-\d.]+\s*', '', text)
    if ':' in text:
        text = text.split(':')[0].strip()
    return re.sub(r'[,;:\-]*$', '', text)

def get_best_title(lines: List[str]) -> str:
    """Select the best title candidate from lines."""
    candidates = []
    for line in lines:
        line = line.strip()
        if line and 8 <= len(line) <= 80:
            score = 0
            if line[0].isupper():
                score += 1
            if any(word[0].isupper() for word in line.split()):
                score += 1
            if not line.endswith('.'):
                score += 1
            candidates.append((score, line))
    
    return clean_title(sorted(candidates, key=lambda x: (-x[0], len(x[1])))[0][1] if candidates else "")

def extract_blocks_from_pdfs(pdf_files):
    sections = []
    doc_names = []

    for file in pdf_files:
        filename = file.filename
        doc_names.append(filename)
        file_bytes = file.read()

        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            toc = doc.get_toc()
            toc_entries = {page: title for _, title, page in toc}
        except Exception:
            continue

        current_heading = None
        current_text = ""
        
        for page_num, page in enumerate(doc, start=1):
            # Use TOC title if available
            if page_num in toc_entries:
                if current_text:
                    sections.append({
                        "document": filename,
                        "page": page_num,
                        "section_title": current_heading or f"Page {page_num}",
                        "refined_text": current_text
                    })
                current_heading = clean_title(toc_entries[page_num])
                current_text = ""

            blocks = page.get_text("blocks")
            for block in blocks:
                text = block[4].strip()
                if len(text) >= 50:
                    lines = [l for l in text.split("\n") if l.strip()]
                    if not lines:
                        continue

                    # Check for heading patterns
                    if (len(lines) <= 3 and all(len(l) <= 100 for l in lines) and
                        any(word in text.lower() for word in ['guide', 'overview', 'introduction'])):
                        new_heading = get_best_title(lines)
                        if new_heading:
                            if current_text:
                                sections.append({
                                    "document": filename,
                                    "page": page_num,
                                    "section_title": current_heading or f"Page {page_num}",
                                    "refined_text": current_text
                                })
                            current_heading = new_heading
                            current_text = ""
                            continue

                    # Add to current section
                    if not any(skip in text.lower() for skip in ["copyright", "all rights reserved"]):
                        current_text = (current_text + " " + text).strip()

        # Add the last section
        if current_text:
            sections.append({
                "document": filename,
                "page": page_num,
                "section_title": current_heading or f"Page {page_num}",
                "refined_text": current_text
            })

    return sections, doc_names