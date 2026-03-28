from flask import Blueprint, request, jsonify
from app.services.ai_service import generate_brand_kit
from app.services.scraper_service import scrape_website
from app.utils.helpers import is_url, success_response, error_response

brand_bp = Blueprint("brand", __name__)


@brand_bp.route("/generate", methods=["POST"])
def generate():
    """
    Generate a brand kit from a text prompt or website URL.

    Request JSON:
        input    (str, required): Business description or website URL.
        platform (str, optional): Target platform. Default: "general".
                                  Options: general, instagram, twitter, linkedin.
        logo     (bool, optional): Whether to include a logo concept. Default: false.

    Returns:
        JSON with the generated brand kit.
    """
    body = request.get_json(silent=True)

    if not body:
        return jsonify(*error_response("Request body must be JSON."))

    raw_input = body.get("input", "").strip()
    platform = body.get("platform", "general").strip().lower()
    include_logo = bool(body.get("logo", False))

    if not raw_input:
        return jsonify(*error_response("'input' field is required."))

    valid_platforms = {"general", "instagram", "twitter", "linkedin"}
    if platform not in valid_platforms:
        return jsonify(*error_response(
            f"Invalid platform. Must be one of: {', '.join(valid_platforms)}."
        ))

    # If input is a URL, scrape it first
    business_input = raw_input
    if is_url(raw_input):
        try:
            business_input = scrape_website(raw_input)
        except ValueError as e:
            return jsonify(*error_response(str(e)))

    # Generate brand kit
    try:
        brand_kit = generate_brand_kit(
            business_input=business_input,
            platform=platform,
            include_logo=include_logo,
        )
    except ValueError as e:
        return jsonify(*error_response(str(e)))
    except RuntimeError as e:
        return jsonify(*error_response(str(e), status=502))

    return jsonify(*success_response(brand_kit.to_dict(), status=200))
