import os
import fitz  # PyMuPDF
from PIL import Image
import io
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

def convert_pdf_to_images(pdf_path: str, progress_callback=None) -> list[Image.Image]:
    doc = fitz.open(pdf_path)
    images = []
    total_pages = min(len(doc), 15) # Max pages to process for MVP
    
    for page_num in range(total_pages):
        if progress_callback:
            progress_callback(10 + int((page_num / total_pages) * 30), f"Slicing page {page_num + 1} of {total_pages}...")
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        img_data = pix.tobytes("png")
        images.append(Image.open(io.BytesIO(img_data)))
    return images

def extract_ielts_exam_from_pdf(pdf_path: str, test_scope: str = "Reading Section", progress_callback=None) -> dict:
    if progress_callback:
        progress_callback(5, "Opening PDF Document...")
        
    images = convert_pdf_to_images(pdf_path, progress_callback)
    
    if progress_callback:
        progress_callback(45, "Images processed. Booting Gemini 2.5 Flash...")
        
    prompt = f"""
    You are an expert IELTS Assessment Architect. I am providing you with images of the pages of an IELTS {test_scope} exam.
    Extract the text and strictly format it into the JSON structure below.
    """
    
    if "Listening" in test_scope:
        prompt += """
        CRITICAL LISTENING RULES:
        This is a Listening Test. DO NOT extract reading passages. Instead, organize the test strictly into 'Part 1', 'Part 2', 'Part 3', and 'Part 4' as the `section_type`.
        Look for questions numbered 1-40. Categorize them as "MCQ", "GAP_FILL", "TFNG" or "MATCHING".
        The `passage_text` field can be empty unless there is a specific overarching context block or audio transcript provided that relates to the questions.
        """
    else:
        prompt += """
        CRITICAL READING RULES:
        1. This is an IELTS Reading Test. There are EXACTLY THREE (3) Reading Passages. Do NOT generate 6 passages. Ensure you only output 'Reading Passage 1', 'Reading Passage 2', and 'Reading Passage 3'.
        2. Extract the reading passages faithfully and include paragraph breaks using simple HTML <p> tags.
        3. Analyze the questions carefully. There are typically 40 questions in total.
        4. CRITICAL: You MUST correctly identify 'TRUE / FALSE / NOT GIVEN' or 'YES / NO / NOT GIVEN' questions. Label their `q_type` strictly as "TFNG". Do not ignore them.
        5. Categorize other questions accurately as "MCQ", "GAP_FILL", or "MATCHING".
        """

    prompt += """
    You must output ONLY valid JSON matching this schema exactly. DO NOT wrap the output in markdown code blocks like ```json ... ```:
    {
      "sections": [
        {
          "section_type": "Section Title (e.g. Part 1 or Reading Passage 1)",
          "blocks": [
            {
              "instructions": "Instruction text for this specific question group (e.g. 'Questions 1-4 Complete the sentences below')",
              "passage_text": "The full text of the reading passage if it appears here (or empty for listening tests). Use simple HTML <p> tags for paragraphs.",
              "questions": [
                {
                  "q_type": "GAP_FILL",
                  "question_number": 1,
                  "prompt": "The question prompt text",
                  "correct_answer_text": "Extract correct answer here if an Answer Key exists in the document, otherwise leave empty.",
                  "options": [
                    {"text": "Option A text", "is_correct": false}
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
    """
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        contents = [prompt] + images
        if progress_callback:
            progress_callback(60, "Uploading data to Gemini and analyzing document structure...")
            
        response = model.generate_content(
            contents, 
            generation_config={"response_mime_type": "application/json"}
        )
        
        if progress_callback:
            progress_callback(90, "Received AI Schema. Parsing JSON map...")
            
        # Clean markdown code blocks if the model hallucinates them
        raw_text = response.text.strip()
        raw_text = re.sub(r'^```json\s*', '', raw_text)
        raw_text = re.sub(r'\s*```$', '', raw_text)
        
        return json.loads(raw_text)
    except Exception as e:
        print("Error parsing OCR LLM response:", str(e))
        return {"error": str(e), "sections": []}
