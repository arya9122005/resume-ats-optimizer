"""Flask entry point. Run with:  python app.py"""
from flask import Flask, render_template, request, jsonify

import config
from services.validators import validate_inputs
from services.mock_data import mock_analysis
from services.analyzer import run_ai_analysis
from services.llm_client import LLMError

app = Flask(__name__)

if not config.USE_MOCK and not config.GEMINI_API_KEY:
    print("WARNING: USE_MOCK=false but GEMINI_API_KEY is empty. Add your key to .env.")


@app.route("/")
def index():
    return render_template("index.html", use_mock=config.USE_MOCK)


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    resume_text = str(data.get("resume_text", ""))
    jd_text = str(data.get("jd_text", ""))

    errors = validate_inputs(resume_text, jd_text)
    if errors:
        return jsonify({"error": " ".join(errors)}), 400

    if config.USE_MOCK:
        return jsonify(mock_analysis(resume_text, jd_text))

    try:
        return jsonify(run_ai_analysis(resume_text, jd_text))
    except LLMError as err:
        return jsonify({"error": err.message}), err.status_code
    except Exception:
        app.logger.exception("Unexpected error during analysis")  # details go to the terminal only
        return jsonify({"error": "Something unexpected went wrong. Please try again."}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)