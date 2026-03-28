import os
import json
from groq import Groq
from app.models.brand_kit import BrandKit

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

_MODEL = "llama-3.3-70b-versatile"

_SYSTEM_PROMPT = """You are a world-class brand strategist and creative director.
You generate complete, professional brand identities.
Always respond with valid JSON only. No markdown fences, no extra text."""


def _build_prompt(business_input: str, platform: str, include_logo: bool) -> str:
    logo_instruction = (
        'Provide a detailed logo_concept string describing the ideal logo.'
        if include_logo else
        'Set logo_concept to null.'
    )

    return f"""Generate a complete brand identity for the following business.

Business: {business_input}
Target Platform: {platform}
{logo_instruction}

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
  "brand_values": ["Value 1", "Value 2", "Value 3", "Value 4"]
}}"""


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
        A populated BrandKit instance.

    Raises:
        ValueError: If the AI response cannot be parsed.
        RuntimeError: If the Groq API call fails.
    """
    try:
        response = _client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": _build_prompt(business_input, platform, include_logo)},
            ],
            temperature=0.7,
            max_tokens=1500,
        )
    except Exception as e:
        raise RuntimeError(f"Groq API error: {e}") from e

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if model adds them anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON: {e}") from e

    return BrandKit(
        brand_names=data.get("brand_names", []),
        tagline=data.get("tagline", ""),
        description=data.get("description", ""),
        visual_identity=data.get("visual_identity", {}),
        logo_concept=data.get("logo_concept"),
        marketing_content=data.get("marketing_content", {}),
        target_audience=data.get("target_audience", ""),
        brand_values=data.get("brand_values", []),
    )
