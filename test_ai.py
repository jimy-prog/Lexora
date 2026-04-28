import sys
import os
import json

# Add teacher_admin to path so we can import services
sys.path.append(os.path.join(os.path.dirname(__file__), "../teacher_admin"))

from services.ai_extractor import extract_ielts_exam_from_pdf

if __name__ == "__main__":
    print("Testing AI Extraction on Listening Practice Test 18.pdf...")
    pdf_path = "Listening Practice Test 18.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"File {pdf_path} not found.")
        sys.exit(1)
        
    result = extract_ielts_exam_from_pdf(pdf_path, test_scope="Listening Section", progress_callback=lambda p, m: print(f"[{p}%] {m}"))
    print("\n--- EXTRACTION RESULT ---")
    print(json.dumps(result, indent=2))
