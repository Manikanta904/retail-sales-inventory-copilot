"""
Gemini LLM reasoning integration service for Retail Copilot.
Consumes structured Python evidence packages and retrieved local business rules,
and returns schema-validated JSON reasoning.
"""
import os
import json
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

from backend.core.config import GEMINI_LLM_MODEL
from backend.core.prompts import RETAIL_COPILOT_SYSTEM_PROMPT


class GeminiService:
    """
    Service responsible for interfacing with Gemini API via the official google-genai SDK.
    """

    def __init__(self, model_name: str = GEMINI_LLM_MODEL) -> None:
        self.model_name = model_name


    def is_available(self) -> bool:
        """Checks if GEMINI_API_KEY environment variable is configured."""
        key = os.environ.get("GEMINI_API_KEY", "").strip()
        return len(key) > 0

    def generate_reasoning_response(
        self,
        question: str,
        evidence_package: Dict[str, Any],
        retrieved_rules: List[Dict[str, Any]],
        system_prompt: str = RETAIL_COPILOT_SYSTEM_PROMPT,
    ) -> Optional[Dict[str, Any]]:
        """
        Sends authoritative evidence and retrieved rules to Gemini LLM for reasoning synthesis.
        Returns parsed JSON dict or None if API key is missing or error occurs.
        Never prints or logs the API key.
        """
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            return None

        try:
            client = genai.Client(api_key=api_key)

            # Format retrieved rules text
            rules_text = "\n\n".join(
                [f"Rule [{r['source']} - {r['title']}]:\n{r['text']}" for r in retrieved_rules]
            )

            prompt_content = f"""USER QUESTION:
"{question}"

AUTHORITATIVE PYTHON EVIDENCE PACKAGE:
{json.dumps(evidence_package, indent=2)}

RETRIEVED LOCAL RETAIL BUSINESS RULES:
{rules_text if rules_text else "No specific rules retrieved."}

Produce a grounded, evidence-backed JSON response for the store manager following the exact required schema.
"""

            # Call Gemini API with model fallback
            try:
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt_content,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        temperature=0.2,
                    ),
                )
            except Exception:
                # Fallback to gemini-1.5-flash if target model name is unsupported
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt_content,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        temperature=0.2,
                    ),
                )

            if not response or not response.text:
                return None

            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                lines = raw_text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_text = "\n".join(lines).strip()

            parsed_data = json.loads(raw_text)
            if isinstance(parsed_data, dict):
                return parsed_data
            return None

        except Exception as e:
            print(f"[GeminiService Error] {type(e).__name__}: {e}")
            return None

