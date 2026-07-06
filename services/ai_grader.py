import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# ─── Always reload .env so the key is picked up even if .env was created
# after the module was first imported (e.g. mid-session).
load_dotenv(override=True)


def _get_api_key() -> str:
    """Read the Gemini API key fresh from the environment each time it's needed."""
    load_dotenv(override=True)
    return os.environ.get("GEMINI_API_KEY", "").strip()


def _get_model():
    key = _get_api_key()
    if not key:
        return None
    genai.configure(api_key=key)
    return genai.GenerativeModel("gemini-2.5-flash")


# ─────────────────────────────────────────────────────────────────────────────
# WRITING GRADER
# ─────────────────────────────────────────────────────────────────────────────
def grade_writing_submission(question_prompt: str, student_essay: str) -> dict:
    """
    Evaluates an IELTS writing essay response using Gemini 2.5 Flash.
    Returns a score of 0 with critical feedback for very short / empty submissions.
    """
    model = _get_model()
    if not model:
        # No API key configured – return a neutral holding state (no fake scores)
        return {
            "overall_band": 0.0,
            "criteria_scores": {
                "task_achievement": 0.0,
                "coherence_cohesion": 0.0,
                "lexical_resource": 0.0,
                "grammar_accuracy": 0.0
            },
            "feedback_markdown": (
                "**AI Grading Unavailable**\n\n"
                "The AI grading service is not configured. "
                "Please contact your administrator."
            )
        }

    word_count = len(student_essay.split()) if student_essay.strip() else 0

    prompt = f"""You are a strict, experienced IELTS Writing Examiner with 15+ years of marking official Cambridge tests.

Your evaluation must be EVIDENCE-BASED and HONEST. You must cite specific examples from the actual essay text to support every claim.

CRITICAL RULES YOU MUST FOLLOW:
- If the essay contains fewer than 50 words, award Band 1.0 or lower across all criteria. State clearly that the response is far too short.
- If the essay is gibberish, random words, or numbers only, award Band 0.0 and explain why.
- NEVER say "well-structured" or "good transitions" unless you can quote at least one clear example of this from the actual essay.
- NEVER invent content or assume quality that isn't demonstrably present in the submitted text.
- Do NOT be encouraging or generous. IELTS marking is objective and strict.
- Band 7+ is reserved for genuinely high-quality academic writing. Most responses score between 4–6.

Word count of submitted essay: {word_count} words

Question Prompt:
{question_prompt}

Student's Submitted Essay (evaluate ONLY what is written below — nothing else):
\"\"\"
{student_essay if student_essay.strip() else "[EMPTY — No essay submitted]"}
\"\"\"

Evaluate strictly according to official IELTS Writing Band Descriptors for all 4 criteria:
1. Task Achievement / Task Response (TA/TR) — did they answer the question fully with relevant ideas?
2. Coherence & Cohesion (CC) — is there logical organisation and effective use of cohesive devices?
3. Lexical Resource (LR) — is the vocabulary range, accuracy and appropriateness sufficient?
4. Grammatical Range & Accuracy (GRA) — is there variety and accuracy in grammar structures?

Provide feedback in markdown under these exact headings:
- **Overall Assessment**: What was the quality of this submission? Be direct and honest.
- **Task Achievement**: Quote evidence from the essay. What was missing or underdeveloped?
- **Strengths** (if any): Only list genuine, quote-backed strengths. If there are none, write "None identified."
- **Weaknesses & Errors**: List specific problems with direct quotes from the essay.
- **Improvement Suggestions**: Concrete, actionable advice.

You must output ONLY valid JSON matching this schema. DO NOT wrap in markdown code blocks:
{{
  "overall_band": 5.5,
  "criteria_scores": {{
    "task_achievement": 5.0,
    "coherence_cohesion": 6.0,
    "lexical_resource": 5.5,
    "grammar_accuracy": 5.5
  }},
  "feedback_markdown": "Feedback text here..."
}}"""

    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        raw = response.text.strip()
        # Strip any accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
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
            "feedback_markdown": (
                f"**AI Grading Error**\n\nThe AI grader encountered an error while processing this submission.\n\n"
                f"Technical details: {str(e)}"
            )
        }


# ─────────────────────────────────────────────────────────────────────────────
# SPEAKING GRADER
# ─────────────────────────────────────────────────────────────────────────────
def grade_speaking_submission(question_prompt: str, audio_file_path: str) -> dict:
    """
    Transcribes and evaluates an IELTS speaking audio submission using Gemini 2.5 Flash.
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
            "feedback_markdown": "**Submission Error**: Audio file not found or was not uploaded correctly."
        }

    model = _get_model()
    if not model:
        return {
            "overall_band": 0.0,
            "criteria_scores": {
                "fluency_coherence": 0.0,
                "lexical_resource": 0.0,
                "grammar_accuracy": 0.0,
                "pronunciation": 0.0
            },
            "feedback_markdown": (
                "**AI Grading Unavailable**\n\n"
                "The AI grading service is not configured. "
                "Please contact your administrator."
            )
        }

    try:
        print(f"[AI Speaking Grader] Uploading audio: {audio_file_path}")
        audio_file = genai.upload_file(path=audio_file_path)

        # Wait for file to become active on Gemini servers
        import time
        for _ in range(30):
            if audio_file.state.name == "PROCESSING":
                time.sleep(1)
                audio_file = genai.get_file(audio_file.name)
            elif audio_file.state.name == "ACTIVE":
                break
            else:
                raise ValueError(f"Gemini file processing failed: {audio_file.state.name}")

        prompt = f"""You are a strict, experienced IELTS Speaking Examiner.

Listen carefully to the audio recording and evaluate it honestly against IELTS Speaking Band Descriptors.

CRITICAL RULES:
- If the audio is silent, unintelligible, or contains only a few words, award Band 1.0 or 0.0 and explain why.
- NEVER fabricate fluency or vocabulary quality that isn't demonstrated in the recording.
- Cite specific moments or utterances from the transcription to support every claim.
- Be direct and honest. Avoid empty encouragement.

Speaking Prompt given to the student:
{question_prompt}

Evaluate for all 4 IELTS Speaking criteria:
1. Fluency & Coherence
2. Lexical Resource
3. Grammatical Range & Accuracy
4. Pronunciation

Provide feedback in markdown under these headings:
- **Transcribed Text**: Your verbatim transcription of the recording.
- **Overall Assessment**: Honest summary of performance.
- **Strengths** (if any): Only quote-backed genuine strengths. If none, state "None identified."
- **Weaknesses**: Specific issues with examples from the transcription.
- **Improvement Suggestions**: Actionable advice.

You must output ONLY valid JSON. DO NOT wrap in markdown code blocks:
{{
  "overall_band": 5.5,
  "criteria_scores": {{
    "fluency_coherence": 5.0,
    "lexical_resource": 5.5,
    "grammar_accuracy": 5.5,
    "pronunciation": 6.0
  }},
  "feedback_markdown": "Feedback text here..."
}}"""

        response = model.generate_content(
            [audio_file, prompt],
            generation_config={"response_mime_type": "application/json"}
        )

        try:
            audio_file.delete()
        except Exception:
            pass

        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
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
            "feedback_markdown": (
                f"**AI Grading Error**\n\nThe AI grader encountered an error.\n\n"
                f"Technical details: {str(e)}"
            )
        }
