import os
import fitz  # PyMuPDF
from PIL import Image
import io
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Configure Gemini if the key is present
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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

def crop_pdf_media(pdf_path: str, page_num: int, box_2d: list[int]) -> str:
    """
    Crops a specific bounding box [ymin, xmin, ymax, xmax] from a PDF page (0-indexed).
    Saves the cropped image to uploads/images/ and returns the relative URL.
    """
    try:
        import time
        doc = fitz.open(pdf_path)
        if page_num < 0 or page_num >= len(doc):
            return ""
            
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # High-quality render
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        width, height = img.size
        ymin, xmin, ymax, xmax = box_2d
        
        left = int((xmin / 1000) * width)
        top = int((ymin / 1000) * height)
        right = int((xmax / 1000) * width)
        bottom = int((ymax / 1000) * height)
        
        # Safeguards
        left = max(0, min(left, width - 1))
        top = max(0, min(top, height - 1))
        right = max(left + 1, min(right, width))
        bottom = max(top + 1, min(bottom, height))
        
        cropped_img = img.crop((left, top, right, bottom))
        
        os.makedirs("uploads/images", exist_ok=True)
        filename = f"extracted_media_{int(time.time())}_{page_num}.png"
        dest_path = f"uploads/images/{filename}"
        cropped_img.save(dest_path, "PNG")
        
        return f"/uploads/images/{filename}"
    except Exception as e:
        print(f"Error cropping media from PDF page {page_num}: {e}")
        return ""

def extract_ielts_exam_from_pdf(pdf_path: str, test_scope: str = "Reading Section", progress_callback=None) -> dict:
    """
    Extracts an IELTS exam structure from a PDF document.
    Falls back to sandbox mock extraction if GEMINI_API_KEY is not set.
    """
    if not GEMINI_API_KEY:
        print("[AI Extractor] WARNING: GEMINI_API_KEY is not set. Running in Sandbox Mode.")
        if progress_callback:
            progress_callback(30, "Sandbox Ingestion: Reading PDF pages...")
            progress_callback(60, "Sandbox Ingestion: Parsing mock exam template...")
            progress_callback(100, "Sandbox Ingestion: Done!")
            
        return {
            "sections": [
                {
                    "section_type": f"{test_scope} (AI Sandbox Mode)",
                    "blocks": [
                        {
                            "instructions": "Questions 1-3: Complete the sentences below. Choose NO MORE THAN TWO WORDS from the passage.",
                            "passage_text": "<p>The Great Library of Alexandria was one of the largest and most significant libraries of the ancient world. It was dedicated to the Muses, the nine goddesses of the arts.</p><p>It flourished under the patronage of the Ptolemaic dynasty and functioned as a major center of scholarship from its creation in the third century BC until the Roman conquest of Egypt in 30 BC.</p>",
                            "layout_style": "default",
                            "media_box": None,
                            "questions": [
                                {
                                    "q_type": "GAP_FILL",
                                    "question_number": 1,
                                    "prompt": "The Library of Alexandria was dedicated to the ______.",
                                    "correct_answer_text": "Muses",
                                    "low_confidence": False,
                                    "options": []
                                },
                                {
                                    "q_type": "GAP_FILL",
                                    "question_number": 2,
                                    "prompt": "The library flourished under the ______ dynasty.",
                                    "correct_answer_text": "Ptolemaic",
                                    "low_confidence": False,
                                    "options": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }

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
    CRITICAL MEDIA & LAYOUT DETECTION INSTRUCTIONS:
    1. For every question block, detect if it contains a diagram, map, flowchart, office plan, or illustration. If it does, specify the `"media_box"` containing the page index (0-indexed) and normalized bounding box coordinates `[ymin, xmin, ymax, xmax]` on a 0-1000 scale.
    2. Classify `"layout_style"` as `"default"`, `"two_column"` (for reading passages), or `"map_split"` (for map/diagram labeling tasks).
    3. If any text element, number, or word is blurry or ambiguous, flag the question with `"low_confidence": true`.
    
    You must output ONLY valid JSON matching this schema exactly. DO NOT wrap the output in markdown code blocks like ```json ... ```:
    {
      "sections": [
        {
          "section_type": "Section Title (e.g. Part 1 or Reading Passage 1)",
          "blocks": [
            {
              "instructions": "Instruction text for this specific question group (e.g. 'Questions 1-4 Complete the sentences below')",
              "passage_text": "The full text of the reading passage if it appears here (or empty for listening tests). Use simple HTML <p> tags for paragraphs.",
              "layout_style": "default",
              "media_box": {
                 "page_number": 0,
                 "box_2d": [ymin, xmin, ymax, xmax]
              },
              "questions": [
                {
                  "q_type": "GAP_FILL",
                  "question_number": 1,
                  "prompt": "The question prompt text",
                  "correct_answer_text": "Extract correct answer here if an Answer Key exists in the document, otherwise leave empty.",
                  "low_confidence": false,
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
