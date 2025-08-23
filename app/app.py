from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

@app.route("/health")
def health():
    return jsonify({"ok": True})

@app.route("/api/recommend", methods=["POST"])
def recommend():
    # Demo picks
    picks = [
        {
            "ticker": "EXAI",
            "name": "Example AI Chips Co.",
            "thesis": "Differentiated interconnect; capacity scaling; margin expansion.",
            "stats": {"P/E":"—","Rev 3yr CAGR":"78%","Gross Margin":"61%","Moat":"Scale + Ecosystem"}
        },
        {
            "ticker":"EVXP",
            "name":"EverExpand Motors",
            "thesis":"Software-led margins; charging optionality; near FCF+.",
            "stats":{"P/S":"9.2","Units YoY":"+46%","Cash":"$7.1B","Moat":"Vertical integration"}
        }
    ]
    return jsonify(picks)

# Serve static assets or SPA index.html
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    static_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(static_path):
        return send_from_directory(app.static_folder, path)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
