Hey team, this is Wali. Here's what I've built for the backend and how you can connect your parts to it.

The backend is a Flask API that lives in the backend/ folder. The entry point is run.py, just run "python run.py" and the server starts on port 5000. Before running it you need to install the dependencies with "pip install -r requirements.txt" and create a .env file by copying .env.example and filling in both API keys.

---

SETUP

1. pip install -r requirements.txt
2. cp .env.example .env
3. Fill in GEMINI_API_KEY — get one free from aistudio.google.com
4. Fill in GROQ_API_KEY — get one free from console.groq.com
5. python run.py

The backend now runs on two AI providers. Gemini (gemini-2.0-flash) is primary. If Gemini fails for any reason, it automatically falls back to Groq (llama-3.3-70b-versatile) without any change to the response format. Flutter doesn't need to know or care which one ran.

---

ENDPOINTS

All responses follow the same envelope:
- success: true/false
- data: the result object (when success is true)
- error: the error message (when success is false)

---

POST /api/v1/brand/generate

The main endpoint. Send it a business description or website URL and get back a full brand kit.

Request body:
  input    (string,  required) — plain text description of the business OR a website URL.
                                  If it's a URL, the backend scrapes it automatically, Flutter doesn't need to do anything special.
  platform (string,  optional) — "general", "instagram", "twitter", or "linkedin". Tailors the tagline and description for that platform. Defaults to "general".
  logo     (boolean, optional) — set to true if you want the AI to generate a logo concept description (text). Defaults to false.
                                  If you want an actual logo image, call /generate-logo separately using the logo_concept from this response.

Response data fields:
  brand_names       — array of 3 name suggestions
  tagline           — one compelling tagline
  description       — 2-3 sentence brand description
  visual_identity   — object with primary_colors (array), font_style, overall_mood
  logo_concept      — string description of the ideal logo, or null if logo was false
  marketing_content — object with instagram_caption, elevator_pitch, slogan
  target_audience   — ideal customer profile
  brand_values      — array of 4 values
  confidence        — object with a score (0-100) and reason for every field above.
                      Example: confidence.tagline.score = 90, confidence.tagline.reason = "Directly addresses the target demographic with clear platform fit"
                      Flutter should display these scores next to each section so the user can see how confident the AI is.

---

POST /api/v1/brand/generate-logo

Generates an actual logo image from a logo concept description using Google Imagen 3.
Call this after /generate when logo was set to true, passing the logo_concept text you got back.

Note: Imagen 3 requires a paid Gemini API tier. If the account is on the free tier this endpoint returns a 502 with a clear error message. There is no Groq fallback for image generation.

Request body:
  logo_concept (string, required) — the logo concept description from /generate, or any custom description.
  brand_name   (string, optional) — the brand name to include in the image prompt for better results.

Response data fields:
  image_base64 — the generated logo as a base64-encoded PNG string
  mime_type    — always "image/png"

Flutter usage: decode image_base64 and display it directly as an image. No file download needed.

---

POST /api/v1/brand/refine

The human-in-the-loop endpoint. When a user rejects a field, call this instead of regenerating the whole brand kit. The AI acknowledges the feedback and regenerates only that one field.

Request body:
  input            (string, required) — same business description or URL as the original /generate call
  platform         (string, required) — same platform as the original /generate call
  field            (string, required) — which field to regenerate. Must be one of:
                                        brand_names, tagline, description, visual_identity,
                                        logo_concept, marketing_content, target_audience, brand_values
  rejected_value   (string, required) — the value the user didn't like, as a string
  rejection_reason (string, required) — what the user said was wrong with it

Response data fields:
  field           — the field that was regenerated
  acknowledgement — a short sentence from the AI explaining what it understood and what it's changing. Display this to the user so they feel heard.
  value           — the new regenerated value (same type as the original field)
  confidence      — updated score and reason for the new value

---

GET /api/v1/health

Simple health check. Returns { "success": true, "status": "ok" }. Useful to ping before making real requests.

---

STORAGE

The backend doesn't touch storage at all, it just generates and returns JSON. Whoever is handling Firebase/Supabase should take the response and save it on the client side. If you need a storage endpoint on the backend side just let me know.

---

TESTS

Run with: pytest tests/
Install test deps first with: pip install -r requirements-dev.txt
Tests don't hit any real AI API so they run instantly.
