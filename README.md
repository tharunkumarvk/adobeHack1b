# 🧠 Persona-Driven Document Intelligence – Round 1B (Adobe Hackathon 2025)

This repository contains the solution for **Round 1B** of the Adobe Hackathon 2025 challenge:
📄 *"Persona-Driven Document Intelligence"*.

The system processes PDFs to extract, rank, and output the most relevant sections and subsections based on a **given persona** and their **job-to-be-done**. It is optimized for **CPU-only execution**, is **Dockerized**, and requires **no internet access** during runtime.

-----

## 🚀 Features

  - ✅ Parses multiple PDF files and extracts section-wise text
  - ✅ Scores relevance using `DistilBERT` (fine-tuned prompt-based)
  - ✅ Ranks and outputs top 5 sections and top 5 paragraph-level subsections
  - ✅ Output formatted as structured JSON
  - ✅ Fast & lightweight (model \<1GB, total runtime \<60s for 3–5 PDFs)
  - ✅ Designed for offline Docker usage

-----

## 🗂 Directory Structure

```
.
├── Dockerfile             # Docker environment setup
├── main.py                # Main execution pipeline
├── input/                 # Put your input PDFs here
│   └── doc1.pdf
├── output.json            # Output gets written here (if redirected)
└── README.md              # You're reading it 😎
```

-----

## 🐳 Run Instructions (Docker)

### 1️⃣ Build the Docker image:

```bash
docker build -t round1b-solution .
```

### 2️⃣ Place your PDF(s) in the `/input` folder:

```bash
mkdir input
cp path/to/your/file.pdf input/
```

### 3️⃣ Run the container:

```bash
# On Windows (CMD/PowerShell)
docker run --rm -v %cd%/input:/app/input round1b-solution

# On Linux/macOS
docker run --rm -v $(pwd)/input:/app/input round1b-solution
```

### 4️⃣ Save the output to a file (optional):

```bash
docker run --rm -v %cd%/input:/app/input round1b-solution > output.json
```

-----

### 🧠 Output Format (Example)

```json
{
  "metadata": {
    "input_documents": ["doc1.pdf"],
    "persona": "PhD Researcher in Computational Biology",
    "job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks",
    "processing_timestamp": "2025-07-28T16:52:09.288178"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page_number": 11,
      "section_title": "DIAGNOSIS: 12mm calculi (calcium oxalate) noted in left",
      "importance_rank": 1
    }
    ...
  ],
  "sub_section_analysis": [
    {
      "document": "doc1.pdf",
      "refined_text": "kidney, which was causing a mild blockage...",
      "page_number": 11
    }
    ...
  ]
}
```

### ✍️ Customize Persona / Job-To-Be-Done

Open `main.py` and edit the following variables:

```python
persona = "PhD Researcher in Computational Biology"
job = "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
```

You can also refactor the script to take CLI arguments. Let us know if you'd like that set up\!

-----

### 🧠 Tech Stack

  - Python 3.9-slim (Docker)
  - PyMuPDF (`fitz`) for PDF parsing
  - HuggingFace `transformers` (`DistilBERT`) for semantic scoring
  - `Torch` (CPU-only)
  - Regex + heuristics for section detection

### 📋 Constraints Compliance

| Constraint            | Status |
| :-------------------- | :----: |
| Model Size \< 1GB      |   ✅    |
| Processing Time \< 60s |   ✅    |
| CPU-only              |   ✅    |
| Offline Execution     |   ✅    |

-----

### 🏁 Sample Test Case (included)

  - **Test PDF**: `doc1.pdf`
  - **Expected output**: `output.json`

Use the `output.json` included in the repository to validate the structure and ranking logic.

### 🏆 Hackathon Goals Met

  - Intelligent section identification
  - Relevance-based ranking using NLP
  - Structured & interpretable output
  - Fully containerized & offline-ready

-----

