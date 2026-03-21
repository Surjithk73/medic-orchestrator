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
        temperature=0.1,
        max_retries=2,
        model_kwargs={"response_format": {"type": "json_object"}},
        default_headers={
            "HTTP-Referer": "https://medic-orchestrator.app",
            "X-Title": "Medic Orchestrator"
        }
    )

def _make_deepseek_chat() -> ChatOpenAI:
    """DeepSeek Chat (not R1) for structured output - cheaper and works better"""
    return ChatOpenAI(
        model="deepseek/deepseek-chat",
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.1,
        max_retries=2,
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

def _make_deepseek() -> ChatOpenAI:
    """DeepSeek R1 for complex reasoning"""
    return ChatOpenAI(
        model="deepseek/deepseek-r1",
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.1,
        max_retries=2,
        default_headers={
            "HTTP-Referer": "https://medic-orchestrator.app",
            "X-Title": "Medic Orchestrator"
        }
    )


class LLMRouter:
    """
    Creates fresh LangChain model instances on each call so they always bind
    to the current running asyncio event loop — avoiding the 'attached to a
    different loop' error that plagues globally-cached LLM clients.

    Fallback chain:
      1. Nemotron 70B with JSON mode (fast, free, good structured extraction)
      2. DeepSeek Chat with JSON mode (cheaper than R1, better for structured output)
      3. Gemini 2.5 Flash (backup if OpenRouter fails)
    """

    async def invoke_extraction(self, prompt: str, schema_cls: Type[BaseModel]) -> BaseModel:
        # Add JSON instruction to prompt
        json_prompt = f"{prompt}\n\nYou MUST respond with valid JSON only, matching this schema: {schema_cls.model_json_schema()}"
        
        try:
            llm = _make_nemotron().with_structured_output(schema_cls)
            return await llm.ainvoke(json_prompt)
        except Exception as e:
            print(f"Nemotron extraction failed: {e}. Trying DeepSeek Chat...")

        try:
            llm = _make_deepseek_chat().with_structured_output(schema_cls)
            return await llm.ainvoke(json_prompt)
        except Exception as e:
            print(f"DeepSeek Chat extraction failed: {e}. Falling back to Gemini Flash...")

        llm = _make_gemini_flash().with_structured_output(schema_cls)
        return await llm.ainvoke(prompt)  # Gemini doesn't need the JSON instruction

    async def invoke_synthesis(self, prompt: str) -> str:
        try:
            res = await _make_deepseek_chat().ainvoke(prompt)
            return res.content
        except Exception as e:
            print(f"DeepSeek Chat synthesis failed: {e}. Falling back to Nemotron...")

        try:
            res = await _make_nemotron().ainvoke(prompt)
            return res.content
        except Exception as e:
            print(f"Nemotron synthesis failed: {e}. Falling back to Gemini Pro...")

        res = await _make_gemini_pro().ainvoke(prompt)
        return res.content


# Single shared instance — but because every method call creates fresh LangChain
# model objects, switching event loops is no longer a problem.
_router = LLMRouter()

def get_router() -> LLMRouter:
    return _router
