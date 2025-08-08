
import pygame, json, urllib.request, urllib.error, urllib.parse
import collections
from entities.player import Player
# from services.race_service import RaceService

RACE_CACHE = {}

def race_get_metadata(race: str, base_url: str = "http://localhost:7001") -> dict:
    try:
        url = f"{base_url}/races/{urllib.parse.quote(race)}/metadata"
        with urllib.request.urlopen(url, timeout=0.5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {"description": "", "bonuses": {}, "stats": {}}

def race_get_metadata_cached(race: str, base_url: str = "http://localhost:7001") -> dict:
    if race in RACE_CACHE:
        return RACE_CACHE[race]
    data = race_get_metadata(race, base_url=base_url)
    RACE_CACHE[race] = data
    return data
    
class CharacterCreateScreen:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 24)
        self.races = ["Saiyan", "Namekian", "Android", "Shiba"]
        self.selected = 0
        self.char_name = ""
        self.preview = Player(400, 420, race=self.races[self.selected])

        # Prefetch race metadata asynchronously so selection/enter never blocks
        import threading
        def _prefetch_all():
            for r in list(self.races):
                try:
                    if r not in RACE_CACHE:
                        RACE_CACHE[r] = race_get_metadata(r)
                except Exception:
                    pass
        threading.Thread(target=_prefetch_all, daemon=True).start()

        # Preview animation state
        self.preview_direction_index = 0
        self.preview_frame_index = 0
        self.preview_anim_timer = 0
        self.preview_anim_delay = 0.12
        self.preview_directions = ["right", "up", "left", "down"]

    def update(self, dt, events):
        # Animate preview character
        self.preview_anim_timer += dt
        if self.preview_anim_timer >= self.preview_anim_delay:
            self.preview_anim_timer = 0
            self.preview_frame_index = (self.preview_frame_index + 1) % 6
            if self.preview_frame_index == 0:
                self.preview_direction_index = (self.preview_direction_index + 1) % 4

            dir_name = self.preview_directions[self.preview_direction_index]
            self.preview.direction = dir_name
            self.preview.image = self.preview.animations[dir_name][self.preview_frame_index]

        # No movement
        fake_keys = collections.defaultdict(lambda: False)
        self.preview.update(fake_keys, dt, pygame.Rect(0, 0, 800, 600), [], override_animation=True)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.races)
                    self.preview = Player(400, 420, race=self.races[self.selected])
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.races)
                    self.preview = Player(400, 420, race=self.races[self.selected])
                elif event.key == pygame.K_BACKSPACE:
                    self.char_name = self.char_name[:-1]
                
                elif event.key == pygame.K_RETURN:
                    # Apply race bonuses before switching to HUD
                    race = self.races[self.selected]
                    meta = race_get_metadata_cached(race)

                    # Store chosen name/race on player
                    self.preview.name = self.char_name.strip() or "Player"
                    self.preview.race = race

                    # Apply bonuses from RaceService
                    bonuses = {}
                    if isinstance(meta, dict):
                        bonuses = meta.get("bonuses", {}) if isinstance(meta.get("bonuses", {}), dict) else {}
                    self.preview.max_health += bonuses.get("health", 0)
                    self.preview.health = self.preview.max_health
                    self.preview.damage_bonus = bonuses.get("damage", 0)  # new attr for projectile damage
                    self.preview.speed += bonuses.get("speed", 0)

                    # Pass this player instance into HUD screen
                    self.game.set_screen("hud", player=self.preview)

    def draw(self, surface):
        surface.fill((20, 20, 20))
        surface.blit(self.font.render("Select Your Race", True, (255,255,255)), (50, 30))

        # Show all races as a vertical list
        for i, race_name in enumerate(self.races):
            color = (255, 255, 0) if i == self.selected else (200, 200, 200)  # yellow if selected
            surface.blit(self.font.render(race_name, True, color), (60, 70 + i * 30))

        # Show detailed info for selected race
        race = self.races[self.selected]
        meta = race_get_metadata_cached(race)

        bonuses_val = meta.get("bonuses", "N/A")
        if isinstance(bonuses_val, dict):
            bonuses_val = ", ".join(f"{k}+{v}" for k, v in bonuses_val.items()) or "N/A"

        info = [
            f"Race: {race}",
            f"Bonuses: {bonuses_val}",
        ]

        for i, line in enumerate(info):
            surface.blit(self.font.render(line, True, (180,180,180)), (300, 60 + i * 25))

        # Name entry field
        surface.blit(self.font.render("Name:", True, (255,255,255)), (60, 220))
        surface.blit(self.font.render(self.char_name, True, (255,255,255)), (120, 220))

        # Draw preview character
        self.preview.draw(surface, None)
