# services/damage_service.py
import json, os, math

class DamageService:
    _cache = None

    @classmethod
    def _load(cls):
        if cls._cache is None:
            path = os.path.join("config", "damage_config.json")
            with open(path, "r", encoding="utf-8") as f:
                cls._cache = json.load(f)
        return cls._cache

    @classmethod
    def get_damage(cls, projectile_type: str, distance: float = 0.0) -> int:
        cfg = cls._load()
        rule = cfg.get(projectile_type, cfg.get("_default", {"base": 10}))
        base = rule.get("base", 10)
        # optional distance falloff
        fall = rule.get("falloff_per_200", 0)  # damage subtract per 200px
        if fall:
            base = max(1, int(base - (distance / 200.0) * fall))
        return base
