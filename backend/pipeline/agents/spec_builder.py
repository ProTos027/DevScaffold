"""
Spec Builder Agent - Converts user prompt to Intent Spec using Google GenAI SDK with structured output.
"""
from google import genai
import json
from typing import Optional

from ..schemas import IntentSpecSchema, DataEntity


SPEC_BUILDER_SYSTEM_PROMPT = """You are a literal Intent Specification Parser for DevScaffold.

Your ONLY job: Convert natural language prompts into a structured IntentSpecSchema.

CRITICAL DIRECTIVES:
1. BE LITERAL: Only add features, entities, and frameworks EXPLICITLY mentioned or unavoidable (e.g., if they ask for a 'blog', they need 'Posts').
2. NO HALLUCINATION: If the user says "API only", do NOT add a frontend. If they say "No auth", do NOT add authentication.
3. FRAMEWORK ACCURACY:
   - "Spring Boot", "Java Spring", "Java" → backend: "springboot"
   - "FastAPI", "fast api" → backend: "fastapi"
   - "Express", "Node" → backend: "express"
   - "Django" → backend: "django"
4. ENTITIES: ONLY create data entities that are essential for the project type or explicitly requested. Do NOT add extra fields or entities "just in case".
"""


def build_spec_from_prompt(prompt: str, model_name: str, api_key: str) -> IntentSpecSchema:
    """
    Use Google GenAI SDK to generate Intent Spec from user prompt with structured output.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt is empty or only whitespace. Cannot build intent specification.")

    client = genai.Client(api_key=api_key)
    
    if not model_name.startswith("gemini-"):
        model_name = f"gemini-1.5-flash"

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
        print(f"❌ SPEC BUILDER ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise ValueError(f"Failed to generate Intent Spec from prompt: {e}")
