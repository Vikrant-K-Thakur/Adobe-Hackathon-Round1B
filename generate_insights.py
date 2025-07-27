from utils.pdf_helper import extract_blocks_from_pdfs
from utils.nlp_helper import rank_relevant_sections
from datetime import datetime
from typing import List, Dict, Any
import re

def clean_section_title(title: str) -> str:
    """Clean and normalize section title."""
    if not title:
        return ""
    
    title = re.sub(r'\s+', ' ', title)
    title = re.sub(r'^[•\-\d.]+\s*', '', title)
    
    if ':' in title:
        main_part = title.split(':')[0].strip()
        if len(main_part) >= 8:
            title = main_part
    
    return title.strip()

def is_valid_title(title: str) -> bool:
    """Validate section titles."""
    title = title.strip()
    if not title or len(title) < 8:
        return False
        
    if re.match(r'^[\d\W]+$', title):
        return False
        
    unwanted = ['page', 'section', 'chapter', 'untitled', 'contents']
    if any(pat in title.lower() for pat in unwanted):
        return False
        
    return True

def process_section_text(text: str) -> str:
    """Process and clean section text."""
    if not text:
        return ""
        
    sentences = re.split(r'(?<=[.!?])\s+', text)
    valid_sentences = []
    
    for sent in sentences:
        sent = sent.strip()
        if (len(sent) >= 30 and 
            sent.count(' ') >= 3 and
            not any(skip in sent.lower() for skip in ['copyright', 'all rights reserved'])):
            valid_sentences.append(sent)
    
    return ' '.join(valid_sentences[:4]) if valid_sentences else ""

def generate_insights_for_persona(pdf_files: List[Any], persona: str, job: str) -> Dict[str, Any]:
    """Generate insights with travel-specific enhancements."""
    sections, doc_names = extract_blocks_from_pdfs(pdf_files)
    
    # Build travel-specific queries
    base_query = f"{persona.strip()} needs to {job.strip()}"
    queries = [
        base_query,
        f"{base_query} with group activities",
        f"Travel guide for {job.strip()}",
        f"Group itinerary for {job.strip().replace('plan a trip', '')}"
    ]

    # Rank sections for each query
    all_ranked = []
    for i, query in enumerate(queries):
        ranked = rank_relevant_sections(query, sections)
        for item in ranked:
            item["similarity_score"] *= (1.0 + (i * 0.1))
        all_ranked.extend(ranked)

    # Filter and deduplicate
    seen_titles = set()
    seen_docs = set()
    filtered_sections = []
    
    # Get best section from each document first
    doc_sections = {}
    for section in all_ranked:
        doc = section["document"]
        title = clean_section_title(section["section_title"])
        
        if not is_valid_title(title):
            continue
            
        if doc not in doc_sections or section["similarity_score"] > doc_sections[doc]["score"]:
            refined_text = process_section_text(section["refined_text"])
            if len(refined_text) >= 100:
                doc_sections[doc] = {
                    "section": {
                        "document": doc,
                        "section_title": title,
                        "page": section["page"]
                    },
                    "score": section["similarity_score"],
                    "refined_text": refined_text
                }

    # Select top 5 sections ensuring diversity
    docs_list = sorted(doc_sections.items(), key=lambda x: x[1]["score"], reverse=True)
    filtered_sections = [{
        "document": data["section"]["document"],
        "section_title": data["section"]["section_title"],
        "importance_rank": i + 1,
        "page_number": data["section"]["page"]
    } for i, (doc, data) in enumerate(docs_list[:5])]

    # Prepare subsection analysis
    subsection_analysis = [{
        "document": data["section"]["document"],
        "page_number": data["section"]["page"],
        "refined_text": data["refined_text"]
    } for doc, data in docs_list[:5]]

    return {
        "metadata": {
            "input_documents": doc_names,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": filtered_sections,
        "subsection_analysis": subsection_analysis
    }