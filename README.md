# Kagetsu no Shiba

_Kagetsu no Shiba:_ is a 2D action game prototype inspired by classic **BYOND-era Dragon Ball Z fan games**, reimagined with original lore and mechanics. This early prototype introduces core gameplay systems such as directional ki blasts, stamina-based resource management, and melee combat — all forming the foundation for a story-driven journey through a new cosmic saga.

---

## ✨ Vision

This project isn't just a clone — it's a **spiritual successor** with a unique narrative, drawing inspiration from the energy, intensity, and tactical combat of DBZ BYOND titles, but building an **original world** with new characters, forms, and transformations. Kagetsu Shiba is the beginning of that saga.

---

## Current Features

### Ki Charging and Energy Blasts

- **Hold `Spacebar`** to charge ki blasts.
    
- Scales in **size, power, and energy cost** based on charge duration.
    
- Visual **charging aura** intensifies as energy builds.
    
- **Tap** for a quick blast, **hold** for a powered shot.
    

### Directional Combat

- Fire ki blasts in **8 directions**, guided by movement input or last known direction.
    
- Automatically defaults to current facing if no input is held.
    

### Melee Attacks

- Press `F` to **punch** and `G` to **kick**.
    
- Each strike spawns a **brief energy swipe** animation in front of the player.
    
- Useful for close-quarters combat or conserving energy.
    

### HUD: Health + Resonance

- Health bar and energy meter visible in the top-left corner.
    
- Energy regenerates over time.
    
- Designed to support resonance-based transformations later.
    

---

## Debug & Dev Tools

- Terminal logs events like:
    
    - Charge start/release
        
    - Ki projectile energy cost
        
    - Punch/kick hit registration
        
- Easy to monitor real-time state changes during gameplay
    

---

## Tech Stack

- **Python 3.13**
    
- **Pygame 2.6.1**
    
- Modular file structure for extensibility:
    
    ``` css
    
    kagetsu-no-shiba/ 
    ├── core/ 
    │   ├── game.py 
    │   └── main.py 
    |   └── projectiles.py 
    ├── entities/ 
    │   └── player.py 
    ├── assets/ 
    │   └── characters/ 
    │       └── players/ 
    │           └── walksheet_1.png 
    ├── projectile.py

    ```
    

---

## Getting Started

### 1. Clone and Navigate

``` bash

CopyEdit

`git clone https://github.com/yourusername/kagetsu-shiba.git cd kagetsu-shiba`
```

### 2. Run the Game

``` bash

CopyEdit

`python core/main.py`

```

### 3. Controls

|Key|Action|
|---|---|
|`W A S D`|Move|
|`Space`|Charge / Fire Ki Blast|
|`F`|Punch|
|`G`|Kick|

---

## Roadmap

-  Melee swipe sprite animations
    
-  Collision & hit detection
    
-  Enemy AI
    
-  Form transformation (Resonance-based)
    
-  Story and lore introduction
    
-  Title screen and game states