# race_api.py
from flask import Flask, jsonify
from flask_cors import CORS
from services.race_service import RaceService
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/races/<race>/metadata")
def race_metadata(race):
    return jsonify(RaceService.get_metadata(race))

@app.get("/races/<race>/stats")
def race_stats(race):
    return jsonify(RaceService.get_stats(race))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7001, debug=True)
