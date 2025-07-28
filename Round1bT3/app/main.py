'''import os
import json
import fitz
from datetime import datetime
import time

def load_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def extract_keywords(text):
    # Basic keyword tokenizer
    words = text.lower().split()
    return list(set([w.strip(",.()") for w in words if len(w) > 3]))



def extract_sections(doc, keywords, doc_name):
    extracted = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().lower()
        match_count = sum(1 for kw in keywords if kw in text)
        
        if match_count == 0:
            continue  # ❌ skip pages with no matches
        
        heading = get_main_heading(page)
        extracted.append({
            "document": doc_name,
            "page": page_num,
            "section_title": heading,
            "score": match_count
        })

    extracted.sort(key=lambda x: x["score"], reverse=True)
    for i, sec in enumerate(extracted):
        sec["importance_rank"] = i + 1
        sec.pop("score")
    return extracted


def get_main_heading(page):
    # Extract largest text on the page
    blocks = page.get_text("dict")["blocks"]
    max_size = 0
    heading = "Untitled"
    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                size = span["size"]
                text = span["text"].strip()
                if size > max_size and len(text) > 5:
                    max_size = size
                    heading = text
    return heading

def get_subsection_texts(sections, doc):
    subs = []
    for sec in sections[:3]:
        page = doc.load_page(sec["page"] - 1)
        full_text = page.get_text()
        subs.append({
            "document": sec["document"],
            "page": sec["page"],
            "refined_text": full_text.strip()
        })
    return subs

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)

    persona = load_text(os.path.join(input_dir, "persona.txt"))
    job = load_text(os.path.join(input_dir, "job.txt"))
    keywords = extract_keywords(job)
    keywords = set(job.lower().split())  # but less accurate


    extracted_sections = []
    all_subs = []
    documents = []

    for file in os.listdir(input_dir):
        if file.endswith(".pdf"):
            documents.append(file)
            doc = fitz.open(os.path.join(input_dir, file))
            sections = extract_sections(doc, keywords, file)
            subs = get_subsection_texts(sections, doc)
            extracted_sections.extend(sections)
            all_subs.extend(subs)

    result = {
        "metadata": {
            "documents": documents,
            "persona": persona,
            "job": job,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": all_subs
    }

    with open(os.path.join(output_dir, "challenge1b_output.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("✅ Output saved to output/challenge1b_output.json")

if __name__ == "__main__":
    start = time.time()
    main()
    print(f"⏱️ Total run time: {round(time.time() - start, 2)} seconds")'''



import os
import fitz  # PyMuPDF
import json
from datetime import datetime
import time

def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def extract_keywords(job_text):
    return {
        "reaction", "kinetics", "rate", "mechanism", "rate law",
        "activation energy", "arrhenius", "collision theory",
        "transition state", "order", "first-order", "second-order"
    }

def get_main_heading(page):
    blocks = page.get_text("dict")["blocks"]
    max_size = 0
    heading = "Untitled"
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                size = span["size"]
                text = span["text"].strip()
                if size > max_size and len(text) > 5:
                    max_size = size
                    heading = text
    return heading

def extract_relevant_sections(doc, doc_name, keywords):
    matches = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().lower()
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            heading = get_main_heading(page)
            matches.append({
                "document": doc_name,
                "page": page_num,
                "section_title": heading,
                "score": score
            })
    matches.sort(key=lambda x: x["score"], reverse=True)
    for i, match in enumerate(matches):
        match["importance_rank"] = i + 1
        match.pop("score")
    return matches

def extract_subsections(doc, matches):
    subs = []
    seen = set()
    for m in matches[:3]:
        if (m["document"], m["page"]) in seen:
            continue
        page = doc.load_page(m["page"] - 1)
        text = page.get_text().strip()
        subs.append({
            "document": m["document"],
            "page": m["page"],
            "refined_text": text
        })
        seen.add((m["document"], m["page"]))
    return subs

def main():
    start_time = time.time()

    input_dir = "/app/input"
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)

    persona = load_text(os.path.join(input_dir, "persona.txt"))
    job = load_text(os.path.join(input_dir, "job.txt"))
    keywords = extract_keywords(job)

    extracted_sections = []
    subsection_analysis = []
    documents = []

    for file in os.listdir(input_dir):
        if file.endswith(".pdf"):
            path = os.path.join(input_dir, file)
            doc = fitz.open(path)
            documents.append(file)
            sections = extract_relevant_sections(doc, file, keywords)
            subs = extract_subsections(doc, sections)
            extracted_sections.extend(sections)
            subsection_analysis.extend(subs)

    result = {
        "metadata": {
            "documents": documents,
            "persona": persona,
            "job": job,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(os.path.join(output_dir, "challenge1b_output.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"✅ Output written in {round(time.time() - start_time, 2)} seconds")

if __name__ == "__main__":
    main()

