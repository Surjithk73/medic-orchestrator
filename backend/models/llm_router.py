import os
import json
from typing import Type
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv()

# Multiple Gemini API keys for rate limit management
GEMINI_API_KEYS = [
    "AIzaSyCtKlZzTq0j98COFuMRogtaRKu0FM5Wj_M",
    "AIzaSyBtrxZ2WwvIQDuyW0wV5YbfrVKw8PFfFnY",
    "AIzaSyBWgSGwBZ97hmNGaO-7S9FzqttNOyTMvpA",
    "AIzaSyDaSzU3vn3wzmKjvJBzKvijjDDOn11uc2o"
]

# Track which key to use next (round-robin)
_current_key_index = 0

def _get_next_gemini_key() -> str:
    """Get next API key in round-robin fashion"""
    global _current_key_index
    key = GEMINI_API_KEYS[_current_key_index]
    _current_key_index = (_current_key_index + 1) % len(GEMINI_API_KEYS)
    return key

def _make_gemini_flash() -> ChatGoogleGenerativeAI:
    """Primary model - Gemini 2.5 Flash with rotating API keys"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        max_retries=2,
        google_api_key=_get_next_gemini_key()
    )

def _make_nemotron() -> ChatOpenAI:
    """Fallback model - NVIDIA Nemotron"""
    return ChatOpenAI(
        model="nvidia/llama-3.1-nemotron-70b-instruct",
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.0,
        max_retries=3,
        model_kwargs={"response_format": {"type": "json_object"}},
        default_headers={
            "HTTP-Referer": "https://medic-orchestrator.app",
            "X-Title": "Medic Orchestrator"
        }
    )

def _make_gemini_pro() -> ChatGoogleGenerativeAI:
    """Last resort - Gemini 2.5 Pro with rotating API keys"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.2,
        max_retries=2,
        google_api_key=_get_next_gemini_key()
    )


class LLMRouter:
    """
    Creates fresh LangChain model instances on each call so they always bind
    to the current running asyncio event loop.

    Fallback chain:
      1. Gemini 2.5 Flash (primary) - with rotating API keys
      2. Nemotron 70B (fallback) - via OpenRouter
      3. Gemini 2.5 Pro (last resort) - with rotating API keys
    """

    async def invoke_extraction(self, prompt: str, schema_cls: Type[BaseModel]) -> BaseModel:
        # Enhanced prompt with clear JSON instructions
        schema_json = schema_cls.model_json_schema()
        
        # Create example based on schema to guide the model
        example_fields = {}
        for field_name, field_info in schema_cls.model_fields.items():
            if field_info.annotation == str:
                example_fields[field_name] = "example text"
            elif field_info.annotation == float:
                example_fields[field_name] = 0.85
            elif field_info.annotation == int:
                example_fields[field_name] = 42
            elif hasattr(field_info.annotation, '__origin__') and field_info.annotation.__origin__ == list:
                example_fields[field_name] = ["item1", "item2"]
            else:
                example_fields[field_name] = None
        
        example_json = json.dumps(example_fields, indent=2)
        
        json_prompt = f"""You are a precise data extraction assistant. Extract information and respond with ONLY valid JSON.

{prompt}

Required JSON Schema:
{schema_json}

Example JSON format:
{example_json}

CRITICAL RULES:
1. Output ONLY valid JSON matching the schema above
2. Do NOT include any explanatory text before or after the JSON
3. Do NOT wrap the JSON in markdown code blocks or backticks
4. Ensure all required fields are present
5. Use null for missing optional fields
6. Use proper JSON syntax: double quotes for strings, no trailing commas

Your JSON response:"""
        
        # Try Gemini Flash first (primary)
        try:
            llm = _make_gemini_flash().with_structured_output(schema_cls)
            result = await llm.ainvoke(prompt)
            print(f"✓ Gemini Flash extraction successful")
            return result
        except Exception as e:
            print(f"Gemini Flash extraction failed: {e}. Trying Nemotron...")

        # Fallback to Nemotron with enhanced prompt
        try:
            llm = _make_nemotron().with_structured_output(schema_cls)
            result = await llm.ainvoke(json_prompt)
            print(f"✓ Nemotron extraction successful")
            return result
        except Exception as e:
            print(f"Nemotron extraction failed: {e}. Trying Gemini Pro...")

        # Last resort: Gemini Pro
        llm = _make_gemini_pro().with_structured_output(schema_cls)
        result = await llm.ainvoke(prompt)
        print(f"✓ Gemini Pro extraction successful")
        return result

    async def invoke_synthesis(self, prompt: str) -> str:
        # Try Gemini Flash first (primary)
        try:
            res = await _make_gemini_flash().ainvoke(prompt)
            print(f"✓ Gemini Flash synthesis successful")
            return res.content
        except Exception as e:
            print(f"Gemini Flash synthesis failed: {e}. Falling back to Nemotron...")

        # Fallback to Nemotron
        try:
            res = await _make_nemotron().ainvoke(prompt)
            print(f"✓ Nemotron synthesis successful")
            return res.content
        except Exception as e:
            print(f"Nemotron synthesis failed: {e}. Falling back to Gemini Pro...")

        # Last resort: Gemini Pro
        res = await _make_gemini_pro().ainvoke(prompt)
        print(f"✓ Gemini Pro synthesis successful")
        return res.content


# Single shared instance — but because every method call creates fresh LangChain
# model objects, switching event loops is no longer a problem.
_router = LLMRouter()

def get_router() -> LLMRouter:
    return _router
