# spawn_api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pygame
from services.spawn_validator import SpawnValidator
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

def _rects_from_json(raw_rects):
    rects = []
    for r in raw_rects:
        x, y, w, h = r
        rects.append(pygame.Rect(int(x), int(y), int(w), int(h)))
    return rects

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/spawns/generate")
def generate_spawns():
    data = request.get_json(force=True) or {}
    want = int(data.get("want", 5))
    map_width = int(data["map_width"])
    map_height = int(data["map_height"])
    collider_rects = _rects_from_json(data.get("collider_rects", []))
    avoid_point = tuple(data["avoid_point"]) if "avoid_point" in data else None
    min_distance = int(data.get("min_distance", 0))
    max_attempts = int(data.get("max_attempts", 300))

    spawns = SpawnValidator.generate_spawns(
        want, map_width, map_height, collider_rects, avoid_point, min_distance, max_attempts
    )
    return jsonify({"spawns": spawns})

@app.post("/spawns/validate")
def validate_spawn():
    data = request.get_json(force=True) or {}
    x = int(data["x"]); y = int(data["y"])
    collider_rects = _rects_from_json(data.get("collider_rects", []))
    avoid_point = tuple(data["avoid_point"]) if "avoid_point" in data else None
    min_distance = int(data.get("min_distance", 0))

    ok = SpawnValidator.is_valid_spawn(x, y, collider_rects, avoid_point, min_distance)
    return jsonify({"valid": ok})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7003, debug=True)
