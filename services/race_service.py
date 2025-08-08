
import json, os

class RaceService:
    _cache = None

    @classmethod
    def _load(cls):
        if cls._cache is None:
            path = os.path.join("config", "race_metadata.json")
            with open(path, "r", encoding="utf-8") as f:
                cls._cache = json.load(f)
        return cls._cache

    @classmethod
    def get_stats(cls, race: str) -> dict:
        data = cls._load().get(race, {})
        # defaults + override
        base = {"max_health":100,"max_energy":100,"energy_recovery_rate":10,"speed":100}
        base.update(data.get("stats", {}))
        return base

    @classmethod
    def get_metadata(cls, race: str) -> dict:
        data = cls._load().get(race, {})
        return {
            "description": data.get("description",""),
            "bonuses": data.get("bonuses",""),
            "stats": data.get("stats", {})
        }
