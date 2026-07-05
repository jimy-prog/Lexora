import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Configure Gemini if the key is present
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def grade_writing_submission(question_prompt: str, student_essay: str) -> dict:
    """
    Evaluates an IELTS writing essay response using Gemini 2.5 Flash.
    Falls back to sandbox evaluation if GEMINI_API_KEY is not set.
    """
    if not GEMINI_API_KEY:
        print("[AI Writing Grader] WARNING: GEMINI_API_KEY is not set. Running in Sandbox Mode.")
        return {
            "overall_band": 7.0,
            "criteria_scores": {
                "task_achievement": 7.0,
                "coherence_cohesion": 7.0,
                "lexical_resource": 6.5,
                "grammar_accuracy": 7.5
            },
            "feedback_markdown": "### [AI Evaluation Sandbox Mode]\n*Note: Set your `GEMINI_API_KEY` in the environment to enable live AI assessment.*\n\n**Overall Assessment**:\nYour response is well-structured and directly addresses the prompt. You have presented clear arguments supported by relevant examples.\n\n**Strengths**:\n- Good paragraph transitions and clear progression of ideas.\n- Accurate lexical selection fitting academic writing standards.\n\n**Weaknesses**:\n- Some minor grammatical range errors in complex sentence structures.\n- Word count is slightly close to the minimum limit."
        }

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a certified IELTS Writing Examiner.
    Evaluate the student's essay written in response to the question prompt below.
    
    Question Prompt:
    {question_prompt}
    
    Student's Essay:
    {student_essay}
    
    You must evaluate strictly according to official IELTS Writing Band Descriptors.
    Return the overall band score (0-9, can be half bands e.g. 6.5) and individual band scores for the 4 criteria:
    1. Task Achievement / Task Response (TA/TR)
    2. Coherence & Cohesion (CC)
    3. Lexical Resource (LR)
    4. Grammatical Range & Accuracy (GRA)
    
    Provide constructive feedback in markdown with headings:
    - **Overall Assessment**: Brief summary.
    - **Strengths**: What the student did well.
    - **Weaknesses / Errors**: Specific areas of concern, grammar mistakes, spelling issues, etc.
    - **Vocabulary & Grammar Improvements**: Specific word or structure upgrade suggestions.
    
    You must output ONLY valid JSON matching this schema exactly. DO NOT wrap the output in markdown code blocks like ```json ... ```:
    {{
      "overall_band": 6.5,
      "criteria_scores": {{
        "task_achievement": 6.0,
        "coherence_cohesion": 7.0,
        "lexical_resource": 6.5,
        "grammar_accuracy": 6.5
      }},
      "feedback_markdown": "Feedback text here..."
    }}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        data = json.loads(response.text.strip())
        return data
    except Exception as e:
        print(f"[AI Writing Grader Error] {e}")
        return {
            "overall_band": 0.0,
            "criteria_scores": {
                "task_achievement": 0.0,
                "coherence_cohesion": 0.0,
                "lexical_resource": 0.0,
                "grammar_accuracy": 0.0
            },
            "feedback_markdown": f"Error running AI essay grader: {str(e)}"
        }

def grade_speaking_submission(question_prompt: str, audio_file_path: str) -> dict:
    """
    Transcribes and evaluates an IELTS speaking audio submission using Gemini 2.5 Flash.
    Falls back to sandbox evaluation if GEMINI_API_KEY is not set.
    """
    if not os.path.exists(audio_file_path):
        return {
            "overall_band": 0.0,
            "criteria_scores": {
                "fluency_coherence": 0.0,
                "lexical_resource": 0.0,
                "grammar_accuracy": 0.0,
                "pronunciation": 0.0
            },
            "feedback_markdown": "Audio file not found."
        }
        
    if not GEMINI_API_KEY:
        print("[AI Speaking Grader] WARNING: GEMINI_API_KEY is not set. Running in Sandbox Mode.")
        return {
            "overall_band": 6.5,
            "criteria_scores": {
                "fluency_coherence": 6.0,
                "lexical_resource": 6.5,
                "grammar_accuracy": 6.5,
                "pronunciation": 7.0
            },
            "feedback_markdown": "### [AI Evaluation Sandbox Mode]\n*Note: Set your `GEMINI_API_KEY` in the environment to enable live AI assessment.*\n\n**Transcribed Text**:\n[Simulated Sandbox Transcription] \"In my opinion, team sports like football help develop collaboration skills, while individual activities encourage self-reliance...\"\n\n**Overall Assessment**:\nThe response shows good fluency and clear pronunciation. Intonation is natural and grammar errors are minor.\n\n**Suggestions**:\n- Work on reducing pause transitions between sentences.\n- Expand vocabulary choices when speaking about sports types."
        }

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        # Upload audio file to Gemini File API
        print(f"[AI Speaking Grader] Uploading audio: {audio_file_path}")
        audio_file = genai.upload_file(path=audio_file_path)
        
        prompt = f"""
        You are a certified IELTS Speaking Examiner.
        Listen to the student's recorded audio response to the speaking prompt below and transcribe/evaluate it.
        
        Speaking Prompt:
        {question_prompt}
        
        Evaluate strictly according to official IELTS Speaking Band Descriptors.
        Return the overall band score (0-9, half bands e.g. 6.0) and individual band scores for the 4 criteria:
        1. Fluency & Coherence
        2. Lexical Resource
        3. Grammatical Range & Accuracy
        4. Pronunciation
        
        Provide constructive feedback in markdown with headings:
        - **Transcribed Text**: Your transcription of their spoken response.
        - **Overall Assessment**: Brief summary.
        - **Pronunciation & Fluency feedback**: Suggestions on pacing, word stress, or intonation.
        - **Vocabulary & Grammar Suggestions**: Constructive corrections.
        
        You must output ONLY valid JSON matching this schema exactly. DO NOT wrap the output in markdown code blocks like ```json ... ```:
        {{
          "overall_band": 6.0,
          "criteria_scores": {{
            "fluency_coherence": 5.5,
            "lexical_resource": 6.0,
            "grammar_accuracy": 6.0,
            "pronunciation": 6.5
          }},
          "feedback_markdown": "Feedback text here..."
        }}
        """
        
        response = model.generate_content(
            [audio_file, prompt],
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Clean up the file in Gemini File API
        try:
            audio_file.delete()
        except Exception:
            pass
            
        data = json.loads(response.text.strip())
        return data
    except Exception as e:
        print(f"[AI Speaking Grader Error] {e}")
        return {
            "overall_band": 0.0,
            "criteria_scores": {
                "fluency_coherence": 0.0,
                "lexical_resource": 0.0,
                "grammar_accuracy": 0.0,
                "pronunciation": 0.0
            },
            "feedback_markdown": f"Error running AI speaking grader: {str(e)}"
        }
