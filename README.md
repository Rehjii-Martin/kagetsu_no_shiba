# Kagetsu no Shiba

_Kagetsu no Shiba_ is a 2D action game prototype inspired by classic **BYOND-era Dragon Ball Z fan games**, reimagined with original lore and mechanics. This early prototype introduces core gameplay systems such as directional ki blasts, stamina-based resource management, and melee combat — all forming the foundation for a story-driven journey through a new cosmic saga.

---

## ✨ Vision

This project isn't just a clone — it's a **spiritual successor** with a unique narrative, drawing inspiration from the energy, intensity, and tactical combat of DBZ BYOND titles, but building an **original world** with new characters, forms, and transformations. Kagetsu Shiba is the beginning of that saga.

---

## 🕹️ Current Features

### ⚡ Ki Charging and Energy Blasts
- **Hold `Spacebar`** to charge ki blasts.
- Scales in **size, power, and energy cost** based on charge duration.
- Visual **charging aura** intensifies as energy builds.
- **Tap** for a quick blast, **hold** for a powered shot.
- Projectiles use **custom sprite rotation**, **smooth spawning**, and **zoom-consistent rendering**.
- Projectiles **trigger explosions** on impact with walls or enemies.

### 🧭 Directional Combat
- Fire ki blasts in **8 directions**, guided by movement input or last known direction.
- Automatically defaults to current facing if no directional input is held.
- Aiming adapts to mouse clicks on UI skill panels or keyboard movement.

### 🥋 Melee Attacks
- Press `F` to **punch** and `G` to **kick**.
- Each strike spawns a **brief melee swipe animation** in front of the player.
- Melee includes **knockback effect logic** and **combo potential** (WIP).

### 🧠 Player Stats & Energy
- Dynamic stamina/energy system with recovery over time.
- **Different races** have different base stats for:
  - Max health
  - Max energy
  - Recovery rate
  - Movement speed

### 🎯 Collisions & World
- Supports **Tiled-based `.tmx` maps** via pytmx.
- Walls defined in "Collision Layer" block player and projectile movement.
- **Camera smoothly follows the player**, supports `Z`/`X` to zoom in/out.


### 📊 HUD Interface
- Health and energy bars shown on screen.
- Tab-based UI panel (toggle with `Tab`) for:
  - **Skills** (Ki Blast, Dash)
  - **Vitals** (WIP)
- Skill panel buttons are **clickable** to trigger player actions.

### 💬 Chat Interface
- Type messages into a chatbox by clicking or pressing Enter.
- Messages are logged and displayed, with scrolling support.
- Chat UI integrated into HUD.

---

## 🧪 Dev Tools & Debugging

- Terminal logs events like:
  - Projectile direction and impact location
  - Energy cost spent
  - Collision detection status
- Use `ESC` to open the **exit dialog**, complete with Yes/No buttons.
- Press `Z` and `X` to zoom in/out (with camera-adjusted scaling).
- Hitbox rectangles and explosion effects can be toggled for debugging.

---

## 🧱 Tech Stack

- **Python 3.13**
- **Pygame 2.6.1**
- **pytmx** for TMX tilemap support
- Modular structure for rapid development:

``` plaintext
kagetsu-no-shiba/
├── assets/
│   └── projectiles/, characters/, effects/
├── core/
│   ├── main.py
│   ├── game.py
│   ├── camera.py
│   ├── projectile.py
│   └── explosion.py
├── entities/
│   └── player.py
├── ui/
│   ├── hud_screen.py
│   └── panels/
│       ├── skills.py
│       └── vitals.py
├── config/, utils/, systems/

```

Getting Started
1. Clone and Navigate
```bash

git clone https://github.com/Rehjii-Martin/kagetsu_no_shiba.git

cd kagetsu_no_shiba
```

2. Install Dependencies (optional)
``` bash

pip install pygame pytmx
```

3. Run the Game

``` bash

python core/main.py
```

---

## Controls

|Key|Action|
|---|---|
|`W A S D`|Move|
|`Spacebar`|Charge / Fire Ki Blast|
|`F`|Punch|
|`G`|Kick|
|`Q`|Dash (uses energy)|
|`Tab`|Toggle UI panel|
|`Z / X`|Zoom out / Zoom in|
|`ESC`|Exit dialog (Yes / No)|
|`Enter`|Open / Submit chat|


## Roadmap

-  Directional projectiles with zoom support
    
-  Collision detection with map walls
    
-  Explosion sprite effects on hit
    
-  UI Skill panel with clickable abilities
    
-  Dash with cooldown and energy cost
    
-  Melee swipe sprite animations
    
-  Enemy AI and dummy enemies
    
-  Form transformation via Resonance
    
-  Story and lore cutscenes
    
-  Title screen + game states
    
-  Sound effects and basic music
    

---

## 🧑‍💻 Author

**Rehjii-Martin**  
_Built for fun, power, and pixel-perfect chaos._

> “Kagetsu no Shiba is not nostalgia — it’s the return of intensity.”