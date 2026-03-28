import os
import json
from google import genai
from google.genai import types
from groq import Groq
from app.models.brand_kit import BrandKit

_gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
_groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

_GEMINI_MODEL = "gemini-2.0-flash"
_GROQ_MODEL = "llama-3.3-70b-versatile"

_SYSTEM_PROMPT = """You are a world-class brand strategist and creative director.
You generate complete, professional brand identities.
Always respond with valid JSON only. No markdown fences, no extra text."""


def _build_prompt(business_input: str, platform: str, include_logo: bool) -> str:
    logo_instruction = (
        "Provide a detailed logo_concept string describing the ideal logo."
        if include_logo else
        "Set logo_concept to null."
    )

    return f"""Generate a complete brand identity for the following business.

Business: {business_input}
Target Platform: {platform}
{logo_instruction}

For each field, also provide a confidence score (0-100) indicating how well it fits
the brand voice, and a short reason explaining the score.

Respond ONLY with this JSON structure, no extra text:

{{
  "brand_names": ["Name1", "Name2", "Name3"],
  "tagline": "A single compelling tagline tailored for {platform}",
  "description": "2-3 sentence brand description tailored for {platform}",
  "visual_identity": {{
    "primary_colors": ["Color name #hexcode", "Color name #hexcode", "Color name #hexcode"],
    "font_style": "Typography description",
    "overall_mood": "Visual mood and aesthetic"
  }},
  "logo_concept": null,
  "marketing_content": {{
    "instagram_caption": "Caption with hashtags",
    "elevator_pitch": "30-second pitch",
    "slogan": "One-liner slogan"
  }},
  "target_audience": "Ideal customer profile description",
  "brand_values": ["Value 1", "Value 2", "Value 3", "Value 4"],
  "confidence": {{
    "brand_names":      {{"score": 85, "reason": "Short reason why this score"}},
    "tagline":          {{"score": 90, "reason": "Short reason why this score"}},
    "description":      {{"score": 88, "reason": "Short reason why this score"}},
    "visual_identity":  {{"score": 82, "reason": "Short reason why this score"}},
    "logo_concept":     {{"score": 78, "reason": "Short reason why this score"}},
    "marketing_content":{{"score": 91, "reason": "Short reason why this score"}},
    "target_audience":  {{"score": 87, "reason": "Short reason why this score"}},
    "brand_values":     {{"score": 84, "reason": "Short reason why this score"}}
  }}
}}"""


def _build_refine_prompt(
    business_input: str,
    platform: str,
    field: str,
    rejected_value: str,
    rejection_reason: str,
) -> str:
    return f"""The user has reviewed the brand kit you generated and rejected the "{field}" field.

Original business: {business_input}
Target platform: {platform}

What you generated for "{field}":
{rejected_value}

User's rejection reason:
{rejection_reason}

Acknowledge the user's feedback in one short sentence, then regenerate only the "{field}" field
with a revised approach that directly addresses their concern. Also provide an updated confidence
score and reason.

Respond ONLY with this JSON structure, no extra text:

{{
  "field": "{field}",
  "acknowledgement": "One sentence acknowledging what the user didn't like and what you are changing.",
  "value": <the regenerated value for {field} — same type as before>,
  "confidence": {{
    "score": <0-100>,
    "reason": "Why this revised version better matches the brand voice"
  }}
}}"""


def _parse_raw(raw: str) -> dict:
    """Strip markdown fences and parse JSON."""
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON: {e}") from e


def _call_gemini(messages: list[dict], temperature: float = 0.7) -> str:
    """Make a Gemini API call and return the raw text response."""
    system_prompt = next(
        (m["content"] for m in messages if m["role"] == "system"), None
    )
    user_messages = [m for m in messages if m["role"] != "system"]
    prompt = user_messages[-1]["content"] if user_messages else ""
    response = _gemini_client.models.generate_content(
        model=_GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=1800,
        ),
    )
    return response.text.strip()


def _call_groq(messages: list[dict], temperature: float = 0.7) -> str:
    """Make a Groq API call and return the raw text response."""
    response = _groq_client.chat.completions.create(
        model=_GROQ_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=1800,
    )
    return response.choices[0].message.content.strip()


def _call_ai(messages: list[dict], temperature: float = 0.7) -> str:
    """Call Gemini with Groq as fallback."""
    try:
        return _call_gemini(messages, temperature)
    except Exception as gemini_err:
        print(f"[ai_service] Gemini failed ({gemini_err}), falling back to Groq.")
        try:
            return _call_groq(messages, temperature)
        except Exception as groq_err:
            raise RuntimeError(
                f"Both AI providers failed. Gemini: {gemini_err} | Groq: {groq_err}"
            ) from groq_err


def generate_brand_kit(
    business_input: str,
    platform: str = "general",
    include_logo: bool = False,
) -> BrandKit:
    """
    Generate a brand kit from a business description or URL content.

    Args:
        business_input: Raw business description or scraped website text.
        platform:       Target platform (instagram, twitter, linkedin, general).
        include_logo:   Whether to generate a logo concept.

    Returns:
        A populated BrandKit instance with confidence scores.

    Raises:
        ValueError: If the AI response cannot be parsed.
        RuntimeError: If the Groq API call fails.
    """
    raw = _call_ai([
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": _build_prompt(business_input, platform, include_logo)},
    ])

    data = _parse_raw(raw)

    return BrandKit(
        brand_names=data.get("brand_names", []),
        tagline=data.get("tagline", ""),
        description=data.get("description", ""),
        visual_identity=data.get("visual_identity", {}),
        logo_concept=data.get("logo_concept"),
        marketing_content=data.get("marketing_content", {}),
        target_audience=data.get("target_audience", ""),
        brand_values=data.get("brand_values", []),
        confidence=data.get("confidence", {}),
    )


def refine_field(
    business_input: str,
    platform: str,
    field: str,
    rejected_value: str,
    rejection_reason: str,
) -> dict:
    """
    Regenerate a single brand kit field based on user rejection feedback.

    Args:
        business_input:   Original business description.
        platform:         Target platform.
        field:            The field name the user rejected.
        rejected_value:   The value the user rejected (as a string).
        rejection_reason: The user's reason for rejecting it.

    Returns:
        Dict with keys: field, acknowledgement, value, confidence.

    Raises:
        ValueError: If the AI response cannot be parsed.
        RuntimeError: If the Groq API call fails.
    """
    raw = _call_ai(
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _build_refine_prompt(
                business_input, platform, field, rejected_value, rejection_reason
            )},
        ],
        temperature=0.85,  # slightly higher temp for more creative regeneration
    )

    return _parse_raw(raw)
