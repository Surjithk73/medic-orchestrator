import os
from typing import Type
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv()

def _make_nemotron() -> ChatOpenAI:
    """Use NVIDIA Nemotron as primary model - fast and free"""
    return ChatOpenAI(
        model="nvidia/llama-3.1-nemotron-70b-instruct",
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.0,  # Lower temperature for more consistent JSON
        max_retries=3,
        model_kwargs={"response_format": {"type": "json_object"}},
        default_headers={
            "HTTP-Referer": "https://medic-orchestrator.app",
            "X-Title": "Medic Orchestrator"
        }
    )

def _make_gemini_flash() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        max_retries=2
    )

def _make_gemini_pro() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.2,
        max_retries=2
    )


class LLMRouter:
    """
    Creates fresh LangChain model instances on each call so they always bind
    to the current running asyncio event loop.

    Fallback chain:
      1. Nemotron 70B with JSON mode (primary)
      2. Gemini 2.5 Flash (fallback)
      3. Gemini 2.5 Pro (last resort)
    """

    async def invoke_extraction(self, prompt: str, schema_cls: Type[BaseModel]) -> BaseModel:
        # Enhanced prompt for Nemotron with clear JSON instructions
        schema_json = schema_cls.model_json_schema()
        json_prompt = f"""You are a precise data extraction assistant. Extract information and respond with ONLY valid JSON.

{prompt}

Required JSON Schema:
{schema_json}

CRITICAL RULES:
- Output ONLY valid JSON matching the schema above
- Do NOT include any explanatory text before or after the JSON
- Do NOT wrap the JSON in markdown code blocks
- Ensure all required fields are present
- Use null for missing optional fields

JSON Response:"""
        
        try:
            llm = _make_nemotron().with_structured_output(schema_cls)
            result = await llm.ainvoke(json_prompt)
            print(f"✓ Nemotron extraction successful")
            return result
        except Exception as e:
            print(f"Nemotron extraction failed: {e}. Trying Gemini Flash...")

        try:
            llm = _make_gemini_flash().with_structured_output(schema_cls)
            result = await llm.ainvoke(prompt)
            print(f"✓ Gemini Flash extraction successful")
            return result
        except Exception as e:
            print(f"Gemini Flash extraction failed: {e}. Trying Gemini Pro...")

        llm = _make_gemini_pro().with_structured_output(schema_cls)
        result = await llm.ainvoke(prompt)
        print(f"✓ Gemini Pro extraction successful")
        return result

    async def invoke_synthesis(self, prompt: str) -> str:
        try:
            res = await _make_nemotron().ainvoke(prompt)
            print(f"✓ Nemotron synthesis successful")
            return res.content
        except Exception as e:
            print(f"Nemotron synthesis failed: {e}. Falling back to Gemini Pro...")

        try:
            res = await _make_gemini_pro().ainvoke(prompt)
            print(f"✓ Gemini Pro synthesis successful")
            return res.content
        except Exception as e:
            print(f"Gemini Pro synthesis failed: {e}. Falling back to Gemini Flash...")

        res = await _make_gemini_flash().ainvoke(prompt)
        print(f"✓ Gemini Flash synthesis successful")
        return res.content


# Single shared instance — but because every method call creates fresh LangChain
# model objects, switching event loops is no longer a problem.
_router = LLMRouter()

def get_router() -> LLMRouter:
    return _router
