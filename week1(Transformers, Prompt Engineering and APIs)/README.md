# Agentic AI: Week 1 Assignment
**Student:** Rutuparn Mandar Ranade  
**Roll No:** 24B3982  

## Overview
This repository contains the completed assignment for Week 1 of the Agentic AI course. The submission explores fundamental concepts in Large Language Model (LLM) behavior, prompt engineering, API integration, and context management[cite: 1].

---

## Assignment Contents

### 1. Understanding Context Limitations
* **Problem:** Analyzed the "Lost in the middle" phenomenon, where LLMs prioritize information at the start and end of large prompts over the middle, mirroring human behavior.
* **Scenario:** Addressed the challenges of managing a 50-page medical history document within a limited 4,000-token context window.
* **Solutions:** Proposed using MCP (Model Context Protocol) servers to enhance middle-information retrieval and topic-based document summarization to reduce input size.

### 2. API Integration: 'Study Buddy' Bot
* **Task:** Built a Python-based 'Study Buddy' bot using the OpenAI API to provide simplified explanations of user-provided topics.
* **Functionality:** Implemented input validation to handle empty prompts and utilized a structured chat completions endpoint to generate concise summaries.

### 3. Sentiment Analysis & Prompting Techniques
* **Task:** Classified a complex product review (mixed signals: positive delivery, negative product experience) using different prompting strategies.
* **Comparison:** 
    * **Zero-shot:** Performed without examples.
    * **Few-shot:** Provided explicit examples to calibrate model logic.
* **Conclusion:** Identified that few-shot prompting performs better by standardizing the output structure and handling conflicting context.

### 4. Advanced Prompt Engineering for Student Planning
* **Objective:** Designed a tool to generate weekly study schedules for IIT Bombay students.
* **Refinement:** 
    * **Weaknesses identified:** Lack of persona and poor output structure in the initial prompt.
    * **Improved Prompt:** Incorporated an "Expert IITB Alumni Mentor" persona, strict Markdown table output formatting, and specific constraints (e.g., max 3 hours per subject) to ensure actionable and scannable results.

### 5. Mechanism Analysis: Self-Attention
* **Explanation:** Demonstrated how the Transformer’s self-attention mechanism disambiguates words like "bank" in the sentence "The bank by the river was steep" by calculating high attention scores between "bank" and contextually relevant words like "river" and "steep".

---

## Technical Skills Demonstrated
* **LLM Architecture:** Understanding of context windows and self-attention mechanisms.
* **Prompt Engineering:** Applying zero-shot, few-shot, and persona-based prompting to improve model output.
* **API Development:** Integrating LLMs into Python scripts with proper validation and configuration.
