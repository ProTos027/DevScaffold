"""
Contract Builder Agent - Generates Component Plan from Intent Spec using Google GenAI SDK with structured output.
"""
from google import genai
import json
from typing import List, Dict, Optional

from ..schemas import IntentSpecSchema, ComponentPlanSchema


CONTRACT_BUILDER_SYSTEM_PROMPT = """You are a software architect for DevScaffold.
Your job is to convert a validated Intent Specification into a detailed Component Plan.

RULES:
1. Each component has: id, type, responsibilities, depends_on, public_interfaces, data_models
2. Component types: 'backend_module', 'frontend_component', 'data_model', 'middleware'
3. Dependencies must be explicit - a component can only depend on other components
4. Public interfaces are user-facing (e.g., API endpoints, UI pages)
5. Return ONLY valid JSON matching the exact schema below

IMPORTANT:
- For authentication, always create: user_model, auth_service
- For CRUD features, create appropriate service components
- For frontends, create frontend components that depend on backend services
- Ensure no circular dependencies
- Be specific with responsibilities
"""


def build_component_plan(spec: IntentSpecSchema, model_name: str, api_key: str) -> ComponentPlanSchema:
    """
    Use Google GenAI SDK to generate Component Plan from Intent Spec with structured output.
    
    Args:
        spec: Validated IntentSpecSchema
        model_name: Gemini model name
        api_key: Google API key
    
    Returns:
        ComponentPlanSchema object
    """
    # Initialize Google GenAI Client
    client = genai.Client(api_key=api_key)
    
    # Model name mapping
    if not model_name.startswith("gemini-"):
        model_name = f"gemini-2.5-flash"
        
    # Convert spec to JSON string for prompt
    spec_json = spec.model_dump_json(indent=2)
    
    try:
        # Generate content with structured output
        response = client.models.generate_content(
            model=model_name,
            contents=f"Intent Spec:\n{spec_json}\n\nGenerate the Component Plan:",
            config={
                "system_instruction": CONTRACT_BUILDER_SYSTEM_PROMPT,
                "response_mime_type": "application/json",
                "response_json_schema": ComponentPlanSchema.model_json_schema(),
            },
        )
        
        # Extract content
        content = response.candidates[0].content.parts[0].text
        plan_dict = json.loads(content)
        
        # Handle case where Gemini returns just a list of components
        if isinstance(plan_dict, list):
            plan_dict = {"components": plan_dict}
        
        # Validate with Pydantic
        plan = ComponentPlanSchema(**plan_dict)
        return plan
        
    except Exception as e:
        raise ValueError(f"Failed to generate Component Plan from spec: {e}")
