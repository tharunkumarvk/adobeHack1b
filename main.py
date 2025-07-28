import fitz  # PyMuPDF
import json
import time
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
import numpy as np
import re
from datetime import datetime
import os

# Initialize DistilBERT model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased")
model.eval()

def extract_text_from_pdf(pdf_path):
    """Extract text, page numbers, and sections from a PDF."""
    doc = fitz.open(pdf_path)
    sections = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        current_section = {"title": None, "text": "", "page": page_num + 1}
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    text = "".join(span["text"] for span in line["spans"])
                    # Heuristic: assume bold or large font indicates a section title
                    if any(span["flags"] & 16 for span in line["spans"]) or len(text.strip()) < 50:
                        if current_section["text"]:
                            sections.append(current_section)
                            current_section = {"title": None, "text": "", "page": page_num + 1}
                        current_section["title"] = text.strip()
                    else:
                        current_section["text"] += text + "\n"
        if current_section["text"]:
            sections.append(current_section)
    doc.close()
    return sections

def clean_text(text):
    """Clean extracted text by removing noise."""
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"[^a-zA-Z0-9\s.,;:!?-]", "", text)
    return text

def score_relevance(text, persona, job):
    """Score text relevance using DistilBERT."""
    prompt = f"Persona: {persona}\nJob: {job}\nText: {text[:512]}"  # Truncate for model
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    score = torch.sigmoid(outputs.logits).numpy()[0][1]  # Positive class probability
    return score

def process_documents(input_dir, persona, job):
    """Process all PDF documents in the input directory and generate output JSON."""
    # Get all PDF files from the input directory
    doc_paths = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".pdf")]
    if not doc_paths:
        raise ValueError("No PDF files found in the input directory.")

    all_sections = []
    for doc_path in doc_paths:
        sections = extract_text_from_pdf(doc_path)
        for section in sections:
            section["doc"] = os.path.basename(doc_path)
            section["text"] = clean_text(section["text"])
            section["relevance"] = score_relevance(section["text"], persona, job)
            all_sections.append(section)

    # Rank sections by relevance
    all_sections.sort(key=lambda x: x["relevance"], reverse=True)
    for i, section in enumerate(all_sections):
        section["importance_rank"] = i + 1

    # Extract subsections (split section text into paragraphs)
    subsections = []
    for section in all_sections:
        paragraphs = section["text"].split("\n\n")
        for para in paragraphs:
            if para.strip():
                subsections.append({
                    "doc": section["doc"],
                    "refined_text": clean_text(para)[:200],  # Limit length
                    "page": section["page"],
                    "relevance": score_relevance(para, persona, job)
                })

    # Rank subsections
    subsections.sort(key=lambda x: x["relevance"], reverse=True)

    # Generate output JSON
    output = {
        "metadata": {
            "input_documents": [os.path.basename(path) for path in doc_paths],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.utcnow().isoformat()
        },
        "extracted_sections": [
            {
                "document": s["doc"],
                "page_number": s["page"],
                "section_title": s["title"] or "Untitled",
                "importance_rank": s["importance_rank"]
            } for s in all_sections[:5]  # Top 5 sections
        ],
        "sub_section_analysis": [
            {
                "document": s["doc"],
                "refined_text": s["refined_text"],
                "page_number": s["page"]
            } for s in subsections[:5]  # Top 5 subsections
        ]
    }
    return output

def main():
    # Define input directory and example persona/job (modify persona/job as needed)
    input_dir = "input"
    persona = "PhD Researcher in Computational Biology"
    job = "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"

    # Create input directory if it doesn't exist
    os.makedirs(input_dir, exist_ok=True)

    start_time = time.time()
    output = process_documents(input_dir, persona, job)
    print(json.dumps(output, indent=2))
    print(f"Processing time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()