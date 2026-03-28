from flask import Blueprint, request, jsonify
from app.services.ai_service import generate_brand_kit, refine_field
from app.services.scraper_service import scrape_website
from app.utils.helpers import is_url, success_response, error_response

brand_bp = Blueprint("brand", __name__)

_VALID_PLATFORMS = {"general", "instagram", "twitter", "linkedin"}

_VALID_FIELDS = {
    "brand_names",
    "tagline",
    "description",
    "visual_identity",
    "logo_concept",
    "marketing_content",
    "target_audience",
    "brand_values",
}


@brand_bp.route("/generate", methods=["POST"])
def generate():
    """
    Generate a brand kit from a text prompt or website URL.

    Request JSON:
        input    (str,  required): Business description or website URL.
        platform (str,  optional): Target platform. Default: "general".
                                   Options: general, instagram, twitter, linkedin.
        logo     (bool, optional): Whether to include a logo concept. Default: false.

    Returns:
        JSON with the full brand kit including confidence scores per field.
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify(error_response("Request body must be JSON.")[0]), 400

    raw_input = body.get("input", "").strip()
    platform = body.get("platform", "general").strip().lower()
    include_logo = bool(body.get("logo", False))

    if not raw_input:
        return jsonify(error_response("'input' field is required.")[0]), 400
    if platform not in _VALID_PLATFORMS:
        return jsonify(error_response(
            f"Invalid platform. Must be one of: {', '.join(_VALID_PLATFORMS)}."
        )[0]), 400

    business_input = raw_input
    if is_url(raw_input):
        try:
            business_input = scrape_website(raw_input)
        except ValueError as e:
            return jsonify(error_response(str(e))[0]), 400

    try:
        brand_kit = generate_brand_kit(
            business_input=business_input,
            platform=platform,
            include_logo=include_logo,
        )
    except ValueError as e:
        return jsonify(error_response(str(e))[0]), 400
    except RuntimeError as e:
        return jsonify(error_response(str(e))[0]), 502

    return jsonify(success_response(brand_kit.to_dict())[0]), 200


@brand_bp.route("/refine", methods=["POST"])
def refine():
    """
    Regenerate a single brand kit field after user rejection.

    The AI acknowledges the user's feedback and produces a revised value
    along with an updated confidence score.

    Request JSON:
        input            (str, required): Original business description or URL.
        platform         (str, required): Same platform used in /generate.
        field            (str, required): The field being rejected.
                                          One of: brand_names, tagline, description,
                                          visual_identity, logo_concept,
                                          marketing_content, target_audience, brand_values.
        rejected_value   (str, required): The value the user is rejecting (as a string).
        rejection_reason (str, required): The user's reason for rejecting it.

    Returns:
        JSON with: field, acknowledgement, value, confidence.
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify(error_response("Request body must be JSON.")[0]), 400

    raw_input = body.get("input", "").strip()
    platform = body.get("platform", "general").strip().lower()
    field = body.get("field", "").strip().lower()
    rejected_value = body.get("rejected_value", "").strip()
    rejection_reason = body.get("rejection_reason", "").strip()

    if not raw_input:
        return jsonify(error_response("'input' field is required.")[0]), 400
    if platform not in _VALID_PLATFORMS:
        return jsonify(error_response(
            f"Invalid platform. Must be one of: {', '.join(_VALID_PLATFORMS)}."
        )[0]), 400
    if not field:
        return jsonify(error_response("'field' is required.")[0]), 400
    if field not in _VALID_FIELDS:
        return jsonify(error_response(
            f"Invalid field. Must be one of: {', '.join(_VALID_FIELDS)}."
        )[0]), 400
    if not rejected_value:
        return jsonify(error_response("'rejected_value' is required.")[0]), 400
    if not rejection_reason:
        return jsonify(error_response("'rejection_reason' is required.")[0]), 400

    # Resolve URL to text if needed
    business_input = raw_input
    if is_url(raw_input):
        try:
            business_input = scrape_website(raw_input)
        except ValueError as e:
            return jsonify(error_response(str(e))[0]), 400

    try:
        result = refine_field(
            business_input=business_input,
            platform=platform,
            field=field,
            rejected_value=rejected_value,
            rejection_reason=rejection_reason,
        )
    except ValueError as e:
        return jsonify(error_response(str(e))[0]), 400
    except RuntimeError as e:
        return jsonify(error_response(str(e))[0]), 502

    return jsonify(success_response(result)[0]), 200
