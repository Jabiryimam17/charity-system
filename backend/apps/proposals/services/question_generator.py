from openai import OpenAI
from django.conf import settings
import json

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)
STANDARD_QUESTIONS = [
    "Is the budget estimate realistic for the described scope?",
    "Who are the direct beneficiaries and how were they identified?",
    "What is the expected timeline for completion?",
    "What is the urgency of this proposal relative to other community needs?",
    "Does this proposal address a root cause or only a symptom?",
]

def generate_ai_questions(title: str, description:str, category:str) -> list[str]:
    prompt = f"""You are evaluating a charity proposal for a governance system.
    Based on the proposal below, generate 4 specific review questions that reviewers should answer.
    Focus on domain-specific concerns, unusual claims, missing details, or feasibility risks.
    Do NOT repeat generic questions about budget or timeline — those are already covered.
    Return ONLY a JSON array of strings. No explanation, no markdown, no preamble.
    
    Proposal Title: {title}
    Category: {category}
    Description: {description}
    """
    try:
        response = client.chat.completions.create(
            model=set.OPENROUTER_MODEL,
            messages=[{'role':'user', 'content':prompt}],
            max_tokens=500,
            temperature=0.4
        )
        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        questions = json.load(raw.strip())
        if not isinstance(questions, list):
            raise ValueError("Invalid response format")
        return [str(q) for q in questions]
    except Exception as e:
        print(f"[question_generator] Failed to generate questions: {str(e)}")
        return []

def build_questions(title: str, description: str, category: str)->list[str]:
    ai_questions = generate_ai_questions(title, description, category)
    return STANDARD_QUESTIONS+ai_questions