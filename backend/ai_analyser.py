import requests
import json
import os
import re

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Free models — change to any model you like from openrouter.ai/models
# Other free options:
#   "mistralai/mistral-7b-instruct:free"
#   "google/gemma-2-9b-it:free"
#   "meta-llama/llama-3.1-8b-instruct:free"
DEFAULT_MODEL = "meta-llama/llama-3.1-8b-instruct"


def get_headers():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set in .env file.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "AI Resume Analyser"
    }


def call_openrouter(prompt: str, max_tokens: int = 1500) -> str:
    payload = {
        "model": DEFAULT_MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(
        OPENROUTER_API_URL,
        headers=get_headers(),
        json=payload,
        timeout=60
    )
    if response.status_code != 200:
        raise ValueError(f"OpenRouter API error {response.status_code}: {response.text}")
    return response.json()["choices"][0]["message"]["content"]


def clean_json_response(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def extract_skills(resume_text: str) -> dict:
    prompt = f"""Analyze the following resume and extract structured information.

Return ONLY a valid JSON object with these exact keys:
{{
  "technical_skills": ["list of technical skills, languages, frameworks, tools"],
  "soft_skills": ["list of soft skills"],
  "experience_years": "estimated total years of experience as a number or string",
  "job_titles": ["list of job titles held"],
  "education": ["list of education qualifications"],
  "certifications": ["list of certifications if any"],
  "summary": "2-3 sentence professional summary of the candidate"
}}

Resume:
{resume_text}

Return ONLY the JSON. No explanation, no markdown fences."""

    raw = call_openrouter(prompt, max_tokens=1500)
    cleaned = clean_json_response(raw)
    return json.loads(cleaned)


def analyse_gap(resume_skills: list, job_title: str, job_description: str) -> dict:
    prompt = f"""You are an expert career coach and ATS specialist.

Candidate skills: {json.dumps(resume_skills)}

Job Title: {job_title}
Job Description:
{job_description}

Analyze the fit and return ONLY a valid JSON object with these exact keys:
{{
  "match_score": <float between 0.0 and 1.0>,
  "matching_skills": ["skills the candidate has that match the job"],
  "missing_skills": ["important skills from the job the candidate lacks"],
  "keywords_to_add": ["top 10 ATS keywords to add to resume to pass screening"],
  "recommendation": "2-3 sentences of specific advice for this candidate to improve their chances",
  "apply_chance": "High / Medium / Low"
}}

Return ONLY the JSON. No explanation, no markdown fences."""

    raw = call_openrouter(prompt, max_tokens=1200)
    cleaned = clean_json_response(raw)
    return json.loads(cleaned)


def improve_resume_bullet(bullet_point: str, job_description: str) -> str:
    prompt = f"""Rewrite this resume bullet point to better match the job description below.
Make it more impactful, quantified where possible, and include relevant ATS keywords.

Original bullet: {bullet_point}

Job description: {job_description}

Return ONLY the improved bullet point. No explanation."""

    return call_openrouter(prompt, max_tokens=300)
