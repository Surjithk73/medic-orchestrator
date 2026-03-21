import os
import json
import random
from typing import Type
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv()

# Two API keys - alternate between them on every request
GEMINI_API_KEYS = [k.strip() for k in os.environ.get("GEMINI_API_KEYS", "").split(",") if k.strip()]
if not GEMINI_API_KEYS:
    single = os.environ.get("GOOGLE_API_KEY", "")
    GEMINI_API_KEYS = [single] if single else []

if not GEMINI_API_KEYS:
    print("WARNING: No Gemini API keys configured!")

_current_key_index = 0

def _get_next_key() -> str:
    global _current_key_index
    if not GEMINI_API_KEYS:
        return ""
    key = GEMINI_API_KEYS[_current_key_index % len(GEMINI_API_KEYS)]
    _current_key_index += 1
    return key

# Models for agent extraction tasks (lighter, faster)
AGENT_MODELS = [
    "gemini-2.5-flash-lite-preview-06-17",
    "gemini-3.1-flash-lite-preview",
]

# Models for final synthesis (more capable)
SYNTHESIS_MODELS = [
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite-preview-06-17",
]

# Ultimate fallback
FALLBACK_MODEL = "gemini-2.5-pro"

def _make_model(model_name: str) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.1,
        max_retries=1,
        google_api_key=_get_next_key()
    )

def _make_openrouter_fallback() -> ChatOpenAI:
    """Free Llama fallback via OpenRouter if all Gemini fails"""
    return ChatOpenAI(
        model="meta-llama/llama-3.3-70b-instruct:free",
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.0,
        max_retries=2,
        max_tokens=4096,
        model_kwargs={"response_format": {"type": "json_object"}},
        default_headers={
            "HTTP-Referer": "https://medorch.vercel.app",
            "X-Title": "Medic Orchestrator"
        }
    )


class LLMRouter:
    """
    Extraction (agents): randomly picks from AGENT_MODELS, alternates API keys.
    Synthesis (report):  randomly picks from SYNTHESIS_MODELS, alternates API keys.
    Fallback chain: Gemini models → OpenRouter Llama → Gemini 2.5 Pro
    """

    async def invoke_extraction(self, prompt: str, schema_cls: Type[BaseModel]) -> BaseModel:
        schema_json = schema_cls.model_json_schema()
        example_fields = {}
        for field_name, field_info in schema_cls.model_fields.items():
            ann = field_info.annotation
            if ann == str:
                example_fields[field_name] = "example text"
            elif ann == float:
                example_fields[field_name] = 0.85
            elif ann == int:
                example_fields[field_name] = 42
            elif hasattr(ann, '__origin__') and ann.__origin__ == list:
                example_fields[field_name] = ["item1", "item2"]
            else:
                example_fields[field_name] = None

        json_prompt = f"""You are a precise data extraction assistant. Respond with ONLY valid JSON.

{prompt}

Required JSON Schema:
{schema_json}

Example format:
{json.dumps(example_fields, indent=2)}

RULES: Output ONLY valid JSON. No markdown, no backticks, no extra text."""

        # Shuffle agent models so each call uses a random one
        models_to_try = random.sample(AGENT_MODELS, len(AGENT_MODELS))

        for model_name in models_to_try:
            try:
                llm = _make_model(model_name).with_structured_output(schema_cls)
                result = await llm.ainvoke(prompt)
                print(f"✓ Extraction successful [{model_name}]")
                return result
            except Exception as e:
                print(f"✗ {model_name} extraction failed: {e}")

        # OpenRouter free fallback
        try:
            llm = _make_openrouter_fallback().with_structured_output(schema_cls)
            result = await llm.ainvoke(json_prompt)
            print(f"✓ Extraction successful [openrouter-llama]")
            return result
        except Exception as e:
            print(f"✗ OpenRouter fallback failed: {e}")

        # Last resort: Gemini 2.5 Pro
        llm = _make_model(FALLBACK_MODEL).with_structured_output(schema_cls)
        result = await llm.ainvoke(prompt)
        print(f"✓ Extraction successful [{FALLBACK_MODEL}]")
        return result

    async def invoke_synthesis(self, prompt: str) -> str:
        # Shuffle synthesis models so each call uses a random one
        models_to_try = random.sample(SYNTHESIS_MODELS, len(SYNTHESIS_MODELS))

        for model_name in models_to_try:
            try:
                res = await _make_model(model_name).ainvoke(prompt)
                print(f"✓ Synthesis successful [{model_name}]")
                return res.content
            except Exception as e:
                print(f"✗ {model_name} synthesis failed: {e}")

        # OpenRouter free fallback
        try:
            res = await _make_openrouter_fallback().ainvoke(prompt)
            print(f"✓ Synthesis successful [openrouter-llama]")
            return res.content
        except Exception as e:
            print(f"✗ OpenRouter synthesis fallback failed: {e}")

        # Last resort: Gemini 2.5 Pro
        res = await _make_model(FALLBACK_MODEL).ainvoke(prompt)
        print(f"✓ Synthesis successful [{FALLBACK_MODEL}]")
        return res.content


_router = LLMRouter()

def get_router() -> LLMRouter:
    return _router
