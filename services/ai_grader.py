import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# ─── Always reload .env so the key is picked up even if .env was created
# after the module was first imported (e.g. mid-session).
load_dotenv(override=True)


class APIKeyManager:
    _keys = []
    _current_idx = 0

    @classmethod
    def get_keys(cls):
        load_dotenv(override=True)
        raw = os.environ.get("GEMINI_API_KEY", "").strip()
        cls._keys = [k.strip() for k in raw.split(",") if k.strip()]
        return cls._keys

    @classmethod
    def get_current_key(cls):
        keys = cls.get_keys()
        if not keys:
            return None
        cls._current_idx = cls._current_idx % len(keys)
        return keys[cls._current_idx]

    @classmethod
    def rotate_to_next(cls):
        keys = cls.get_keys()
        if keys:
            cls._current_idx = (cls._current_idx + 1) % len(keys)
            print(f"[APIKeyManager] Rotated to key index {cls._current_idx}")


def _get_model():
    key = APIKeyManager.get_current_key()
    if not key:
        return None
    genai.configure(api_key=key)
    return genai.GenerativeModel("gemini-2.5-flash")


def _log_platform_error(attempt_id: int, error_type: str, message: str, details: str):
    from master_database import SessionMaster, PlatformErrorLog
    db = SessionMaster()
    try:
        log_entry = PlatformErrorLog(
            attempt_id=attempt_id,
            error_type=error_type,
            message=message,
            details=details
        )
        db.add(log_entry)
        db.commit()
        print(f"[AI Grader Error Logged] Attempt {attempt_id}: {message}")
    except Exception as e:
        print(f"[AI Grader Log Error] Failed to write to database: {e}")
    finally:
        db.close()


STUDENT_FRIENDLY_AI_FALLBACK = (
    "**Evaluation in Progress**\n\n"
    "AI evaluation is taking slightly longer than expected. "
    "Our team has been notified and is reviewing your test. "
    "Please check back shortly."
)


def _generate_content_with_retry(contents, generation_config=None, attempt_id=None):
    import time
    import re
    for attempt in range(6):
        model = _get_model()
        if not model:
            raise ValueError("No API keys configured.")
        try:
            if generation_config:
                return model.generate_content(contents, generation_config=generation_config)
            else:
                return model.generate_content(contents)
        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "quota" in err_str or "rate limit" in err_str:
                keys = APIKeyManager.get_keys()
                if len(keys) > 1:
                    APIKeyManager.rotate_to_next()
                    print(f"[AI Grader] Rotated API Key due to 429. Attempt {attempt+1}/6...")
                    time.sleep(2)
                    continue

                delay = 15
                if "retry in" in err_str:
                    try:
                        match = re.search(r"retry in ([\d\.]+)", err_str)
                        if match:
                            delay = int(float(match.group(1))) + 2
                    except Exception:
                        pass
                print(f"[AI Grader] Hit 429 Rate Limit. Waiting {delay} seconds (attempt {attempt+1}/6)...")
                time.sleep(delay)
            else:
                raise e

    model = _get_model()
    if generation_config:
        return model.generate_content(contents, generation_config=generation_config)
    else:
        return model.generate_content(contents)


# ─────────────────────────────────────────────────────────────────────────────
# WRITING GRADER
# ─────────────────────────────────────────────────────────────────────────────
def grade_writing_submission(question_prompt: str, student_essay: str, attempt_id: int = None) -> dict:
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
        response = _generate_content_with_retry(
            prompt,
            generation_config={"response_mime_type": "application/json"},
            attempt_id=attempt_id
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
        if attempt_id:
            _log_platform_error(
                attempt_id=attempt_id,
                error_type="writing_grading",
                message=f"Writing grading failed: {str(e)}",
                details=f"Prompt: {question_prompt[:200]}\nEssay: {student_essay[:200]}"
            )
        return {
            "overall_band": 0.0,
            "criteria_scores": {
                "task_achievement": 0.0,
                "coherence_cohesion": 0.0,
                "lexical_resource": 0.0,
                "grammar_accuracy": 0.0
            },
            "feedback_markdown": STUDENT_FRIENDLY_AI_FALLBACK
        }


# ─────────────────────────────────────────────────────────────────────────────
# SPEAKING GRADER
# ─────────────────────────────────────────────────────────────────────────────
def grade_speaking_submission(question_prompt: str, audio_file_path: str, attempt_id: int = None) -> dict:
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
        mime_type = "audio/webm" if audio_file_path.endswith(".webm") else None
        audio_file = genai.upload_file(path=audio_file_path, mime_type=mime_type)

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

        response = _generate_content_with_retry(
            [audio_file, prompt],
            generation_config={"response_mime_type": "application/json"},
            attempt_id=attempt_id
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
        if attempt_id:
            _log_platform_error(
                attempt_id=attempt_id,
                error_type="speaking_single_grading",
                message=f"Single speaking grading failed: {str(e)}",
                details=f"Prompt: {question_prompt[:200]}"
            )
        return {
            "overall_band": 0.0,
            "criteria_scores": {
                "fluency_coherence": 0.0,
                "lexical_resource": 0.0,
                "grammar_accuracy": 0.0,
                "pronunciation": 0.0
            },
            "feedback_markdown": STUDENT_FRIENDLY_AI_FALLBACK
        }


def grade_speaking_exam_consolidated(speaking_list: list, attempt_id: int = None) -> dict:
    """
    Consolidates and grades an entire IELTS speaking test in a single Gemini API call.
    Uploads all audio files, waits for them to become active concurrently,
    and asks Gemini to evaluate them all at once.
    """
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
            "feedback_markdown": "AI Grading service is not configured."
        }

    uploaded_files = []
    try:
        # 1. Upload all valid files
        for idx, (prompt_text, filepath) in enumerate(speaking_list):
            if not filepath or not os.path.exists(filepath):
                continue
            print(f"[AI Speaking Grader] Uploading audio {idx+1}/{len(speaking_list)}: {filepath}")
            mime_type = "audio/webm" if filepath.endswith(".webm") else None
            audio_file = genai.upload_file(path=filepath, mime_type=mime_type)
            uploaded_files.append((idx, prompt_text, audio_file))

        # 2. Wait for all files to become ACTIVE concurrently
        import time
        max_retries = 30
        for retry in range(max_retries):
            all_active = True
            for i, (idx, prompt_text, file_obj) in enumerate(uploaded_files):
                file_obj = genai.get_file(file_obj.name)
                uploaded_files[i] = (idx, prompt_text, file_obj)
                if file_obj.state.name == "PROCESSING":
                    all_active = False
                elif file_obj.state.name != "ACTIVE":
                    # Mismatch or failed
                    pass
            if all_active:
                break
            time.sleep(1)

        # 3. Build consolidated media mapping and prompt
        content_parts = []
        file_mapping_text = []
        for idx, prompt_text, file_obj in uploaded_files:
            if file_obj.state.name == "ACTIVE":
                content_parts.append(file_obj)
                file_mapping_text.append(
                    f"- Audio File {len(content_parts)} (index {len(content_parts)-1} in the uploaded files below): "
                    f"Prompt: '{prompt_text}'"
                )

        if not content_parts:
            return {
                "overall_band": 0.0,
                "criteria_scores": {
                    "fluency_coherence": 0.0,
                    "lexical_resource": 0.0,
                    "grammar_accuracy": 0.0,
                    "pronunciation": 0.0
                },
                "feedback_markdown": "No valid active speaking recordings could be processed."
            }

        mappings_str = "\n".join(file_mapping_text)

        prompt = f"""You are a strict, experienced IELTS Speaking Examiner.

Evaluate the student's entire speaking exam recordings mapped below:

{mappings_str}

CRITICAL RULES:
- If all audios are silent or unintelligible, award Band 1.0 or 0.0.
- Evaluate objectively against official IELTS Speaking descriptors for the 4 criteria:
  1. Fluency & Coherence
  2. Lexical Resource
  3. Grammatical Range & Accuracy
  4. Pronunciation
- Provide a summary and brief transcript/review of responses for Part 1, Part 2, and Part 3.

Provide constructive feedback in markdown with headings:
- **Transcribed Responses Summary**: Short review or transcription highlights.
- **Overall Assessment**: Synthesis of their performance.
- **Fluency & Coherence Feedback**: Analysis.
- **Lexical Resource & Grammar**: Improvements.
- **Pronunciation & Pacing Suggestions**: Advice.

You must output ONLY valid JSON matching this schema exactly. DO NOT wrap in markdown code blocks:
{{
  "overall_band": 6.5,
  "criteria_scores": {{
    "fluency_coherence": 6.0,
    "lexical_resource": 6.5,
    "grammar_accuracy": 6.5,
    "pronunciation": 7.0
  }},
  "feedback_markdown": "Feedback text here..."
}}"""

        content_parts.append(prompt)

        # 4. Generate evaluation in a single call
        response = _generate_content_with_retry(
            content_parts,
            generation_config={"response_mime_type": "application/json"},
            attempt_id=attempt_id
        )

        # 5. Clean up files on Gemini servers
        for _, _, file_obj in uploaded_files:
            try:
                file_obj.delete()
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
        print(f"[AI Speaking Grader Consolidated Error] {e}")
        # Clean up files in case of crash
        for _, _, file_obj in uploaded_files:
            try:
                file_obj.delete()
            except Exception:
                pass
        if attempt_id:
            _log_platform_error(
                attempt_id=attempt_id,
                error_type="speaking_consolidated_grading",
                message=f"Consolidated speaking grading failed: {str(e)}",
                details=f"File count: {len(speaking_list)}"
            )
        return {
            "overall_band": 0.0,
            "criteria_scores": {
                "fluency_coherence": 0.0,
                "lexical_resource": 0.0,
                "grammar_accuracy": 0.0,
                "pronunciation": 0.0
            },
            "feedback_markdown": STUDENT_FRIENDLY_AI_FALLBACK
        }
