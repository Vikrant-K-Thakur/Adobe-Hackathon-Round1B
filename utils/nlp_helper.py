from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Dict, Any
import torch

# Load the model (will be cached after first run)
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_enhanced_query(query: str, section_title: str, persona: str = "") -> str:
    """Create an enhanced query combining context."""
    if "travel planner" in persona.lower():
        if "itinerary" in query.lower() or "plan" in query.lower():
            return f"travel planning guide for {section_title} with group activities"
        elif "restaurant" in query.lower() or "dining" in query.lower():
            return f"best group dining options in {section_title}"
    return f"{query} related to {section_title}"

def calculate_similarity(query_emb: Any, text_emb: Any) -> float:
    """Calculate cosine similarity between embeddings."""
    try:
        similarity = util.pytorch_cos_sim(query_emb, text_emb)
        return similarity.item()  # Convert single-element tensor to Python float
    except Exception as e:
        print(f"Similarity calculation error: {str(e)}")
        return 0.0

def analyze_content_relevance(text: str, persona_type: str) -> float:
    """Analyze content relevance based on persona."""
    text = text.lower()
    relevance_score = 1.0
    
    if "travel planner" in persona_type.lower():
        keywords = ["group", "itinerary", "schedule", "activities", "accommodation", 
                   "transportation", "budget", "booking", "reservation"]
        matches = sum(1 for keyword in keywords if keyword in text)
        relevance_score += (matches / len(keywords)) * 0.5
    
    return relevance_score

def rank_relevant_sections(query: str, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rank sections based on relevance with travel-specific enhancements."""
    if not sections:
        return []

    # Extract persona type
    persona_type = ""
    if "needs to" in query.lower():
        persona_type = query.lower().split("needs to")[0].strip()

    # Create query embedding
    try:
        query_embedding = model.encode(query, convert_to_tensor=True)
    except Exception as e:
        print(f"Query encoding error: {str(e)}")
        return []

    results = []

    for section in sections:
        try:
            title = section.get("section_title", "").strip()
            content = section.get("refined_text", "").strip()
            
            if not content:
                continue

            # Enhanced query with travel context
            enhanced_query = get_enhanced_query(query, title, persona_type)
            try:
                enhanced_embedding = model.encode(enhanced_query, convert_to_tensor=True)
            except Exception as e:
                print(f"Enhanced query encoding error: {str(e)}")
                enhanced_embedding = query_embedding  # Fallback to original query
            
            # Get embeddings
            title_embedding = None
            if title:
                try:
                    title_embedding = model.encode(title, convert_to_tensor=True)
                except Exception as e:
                    print(f"Title encoding error: {str(e)}")
            
            try:
                content_embedding = model.encode(content, convert_to_tensor=True)
            except Exception as e:
                print(f"Content encoding error: {str(e)}")
                continue
            
            # Calculate similarities
            content_score = calculate_similarity(query_embedding, content_embedding)
            enhanced_score = calculate_similarity(enhanced_embedding, content_embedding)
            title_score = calculate_similarity(query_embedding, title_embedding) if title_embedding is not None else 0
            
            # Persona relevance
            persona_relevance = analyze_content_relevance(content, persona_type)
            
            # Travel-specific scoring
            if "travel planner" in persona_type.lower():
                has_group = any(word in content.lower() for word in ["group", "friends", "together"])
                has_days = any(word in content.lower() for word in ["day", "itinerary", "schedule"])
                
                final_score = (
                    content_score * 0.3 +
                    enhanced_score * 0.3 +
                    title_score * 0.2 +
                    persona_relevance * 0.2
                ) * (1.3 if has_group else 1.0) * (1.2 if has_days else 1.0)
            else:
                final_score = content_score

            results.append({
                "document": section["document"],
                "page": section["page"],
                "section_title": title,
                "refined_text": content,
                "similarity_score": final_score
            })
            
        except Exception as e:
            print(f"Error processing section: {str(e)}")
            continue

    # Sort and ensure diversity
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    final_results = []
    seen_docs = set()
    for result in results:
        if result['document'] not in seen_docs:
            final_results.append(result)
            seen_docs.add(result['document'])
        if len(final_results) >= 5:
            break
            
    return final_results