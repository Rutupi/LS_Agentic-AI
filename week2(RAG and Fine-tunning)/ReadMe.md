# Agentic AI: Week 2 Assignment
**Student:** Rutuparn Mandar Ranade  
**Roll No:** 24B3982  

## Overview
This assignment demonstrates the implementation of a functional RAG pipeline from scratch, evaluates various chunking strategies, and establishes a decision framework for choosing between RAG, Fine-Tuning, or Prompt Engineering[cite: 2].

---

## Assignment Contents

### 1. Minimal RAG Pipeline
* **Pipeline Implementation:** Built a custom RAG pipeline without high-level frameworks, covering chunking, embedding, vector search, and generation[cite: 2].
* **Technical Stack:** Used `sentence-transformers` (all-MiniLM-L6-v2) for embeddings and `google/flan-t5-base` for generation[cite: 2].
* **Key Results:** Successfully implemented manual cosine similarity for retrieval and tested the pipeline's "hallucination guard" by querying information absent from the source document[cite: 2].

### 2. Chunking Strategy Showdown
* **Strategies Implemented:** Compared three distinct methods:
    * **Fixed-size chunking:** Splits text by word count[cite: 2].
    * **Sentence-based chunking:** Groups content by sentence boundaries[cite: 2].
    * **Sliding window chunking:** Uses heavy overlap to maintain context[cite: 2].
* **Retrieval Comparison:** Evaluated performance using a 5-question benchmark[cite: 2]. All three strategies achieved a 5/5 hit rate on this specific dataset[cite: 2].

### 3. RAG vs. Fine-Tuning: Decision Framework
* **Decision Tree:** Developed a logical function to recommend the optimal architecture (RAG, Fine-Tuning, or Prompt Engineering) based on data frequency, output format requirements, latency, and knowledge type[cite: 2].
* **Hallucination Stress Test:** Conducted a rigorous test comparing in-scope vs. out-of-scope queries[cite: 2].
* **Analysis Insights:**
    * **Chunk Dilution:** Identified that relevant information can be "drowned out" in large chunks, though the LLM's attention mechanism may sometimes recover it[cite: 2].
    * **False Positives:** Observed that vector similarity can trigger false positives when queries contain concrete keyword entities absent from the source text, leading to hallucinations[cite: 2].
    * **Thresholding:** Demonstrated the importance of similarity thresholds to trigger hallucination guards effectively[cite: 2].

---

## Technical Skills Demonstrated
* **RAG Engineering:** End-to-end implementation of vector storage, manual similarity calculation, and retrieval-augmented generation[cite: 2].
* **Empirical Analysis:** Measuring the impact of different chunking strategies on retrieval hit rates[cite: 2].
* **System Design:** Designing decision logic for choosing LLM deployment strategies based on enterprise constraints[cite: 2].
