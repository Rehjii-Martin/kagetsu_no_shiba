# damage_api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from services.damage_service import DamageService
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


app = Flask(__name__)
CORS(app)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/damage")
def get_damage():
    projectile_type = request.args.get("projectile_type", "_default")
    try:
        distance = float(request.args.get("distance", "0"))
    except ValueError:
        distance = 0.0
    dmg = DamageService.get_damage(projectile_type, distance)
    return jsonify({"projectile_type": projectile_type, "distance": distance, "damage": int(dmg)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7002, debug=True)
