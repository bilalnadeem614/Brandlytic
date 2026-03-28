from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    """Simple health check endpoint."""
    return jsonify({"success": True, "status": "ok"})
