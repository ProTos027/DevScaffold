"""
Spec Builder Agent - Converts user prompt to Intent Spec using Google GenAI SDK with structured output.
"""
from google import genai
import json
from typing import Optional

from ..schemas import IntentSpecSchema, DataEntity


SPEC_BUILDER_SYSTEM_PROMPT = """You are a resilient Intent Specification Parser for DevScaffold.

Your primary goal: Convert natural language prompts into a structured IntentSpecSchema.

RESILIENCE & BEST-GUESS DIRECTIVES:
1. HANDLE VAGUENESS: If the user input is vague, short, or seems like "garbage" (e.g., "abc", "test", "web app"), do NOT fail. Instead, make your best guess for a "standard" project of that likely type.
2. FLAG VAGUENESS: If you had to make significant assumptions, set `vague_intent: true` and provide a short `explanation` of what you assumed (e.g., "Prompt was too brief; assumed a standard Todo list with FastAPI and SQLite").
3. ALWAYS PROVIDE A BACKEND: If no backend is mentioned, default to "fastapi" (it's our baseline).
4. LITERALISM vs. INTELLIGENCE: While you should be literal for specific requests (e.g., "Postgres only"), you must be intelligent for vague ones. 
5. NO HALLUCINATION: Only add data entities if they are logically required (e.g., 'User' for auth).
6. ALWAYS SPECIFY API TYPE: In `architecture`, always include `api_type`. Default to "rest" if not specified.
7. AUTH CONSISTENCY: If you include "authentication" in `features`, you MUST add a "User" entity to `data_entities`.
8. JWT REQUIREMENT: If you set `auth_method` to "jwt" in `constraints`, you MUST include "authentication" in `features`.
9. COMPATIBILITY: If a frontend is requested, you MUST provide a backend. 
10. FRAMEWORK MAPPING:
   - "Spring Boot", "Java Spring", "Java" -> backend: "springboot"
   - "FastAPI", "fast api" -> backend: "fastapi"
   - "Express", "Node" -> backend: "express"
   - "Django" -> backend: "django"
"""


def build_spec_from_prompt(prompt: str, model_name: str, api_key: str) -> IntentSpecSchema:
    """
    Use Google GenAI SDK to generate Intent Spec from user prompt with structured output.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt is empty or only whitespace. Cannot build intent specification.")

    client = genai.Client(api_key=api_key)
    
    if not model_name.startswith("gemini-"):
        model_name = f"gemini-2.5-flash"

    try:
        print(f"DEBUG: spec_builder.py - User Prompt: {prompt[:200]}...")
        
        response = client.models.generate_content(
            model=model_name,
            contents=f"USER INPUT: {prompt}",
            config={
                "system_instruction": SPEC_BUILDER_SYSTEM_PROMPT,
                "response_mime_type": "application/json",
                "response_json_schema": IntentSpecSchema.model_json_schema(),
            },
        )
        
        content = response.candidates[0].content.parts[0].text
        print(f"DEBUG: spec_builder.py - Raw Response: {content}")
        
        spec_dict = json.loads(content)
        spec = IntentSpecSchema(**spec_dict)
        
        # DO NOT apply silent fallbacks here. 
        # Let the validator find missing fields based on the raw LLM output.
        
        return spec
        
    except Exception as e:
        from ..utils import format_gemini_error
        clean_msg = format_gemini_error(e)
        print(f"❌ SPEC BUILDER ERROR: {clean_msg}")
        raise ValueError(clean_msg)
