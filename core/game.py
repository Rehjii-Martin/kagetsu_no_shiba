import pygame
import math
from entities.player import Player
from core.projectile import Projectile

class Game:
    def __init__(self, screen):
        self.screen   = screen
        self.player   = Player(100, 100)
        self.bg_color = (10, 10, 10)

        # ─── Projectiles ──────────────────────────────────────────────
        self.projectiles    = []
        self.last_shot_time = 0
        self.shot_cooldown  = 0.25

        # ─── Melee Attacks ───────────────────────────────────────────
        self.melee_attacks = []
        self.melee_duration = 0.25

        # ─── Player Stats ─────────────────────────────────────────────
        self.max_health = 100
        self.health     = 100
        self.max_energy = 100
        self.energy     = 100
        self.energy_recovery_rate = 10  # per second
        self.energy_blast_cost = 15

        # ─── Charging ─────────────────────────────────────────────────
        self.is_charging = False
        self.charge_time = 0.0
        self.max_charge_duration = 2.0  # seconds
        self.space_was_pressed = False

    def update(self, dt):
        keys = pygame.key.get_pressed()
        now  = pygame.time.get_ticks() / 1000.0

        self.player.update(keys, dt)

        # ─── Charging Blast ───────────────────────────────────────────
        if keys[pygame.K_SPACE]:
            if not self.space_was_pressed:
                print("Started charging")
                self.space_was_pressed = True
                self.is_charging = True
                self.charge_time = 0.0
            else:
                self.charge_time += dt
                print(f"Charging... time = {self.charge_time:.2f}s")
        elif self.space_was_pressed:
            charge_ratio = min(self.charge_time / self.max_charge_duration, 1.0)
            if charge_ratio == 0.0:
                charge_ratio = 0.1

            if self.energy >= self.energy_blast_cost:
                print(f"Releasing blast! Charge ratio: {charge_ratio:.2f}")
                px, py = self.player.rect.center
                dx, dy = 0, 0
                if keys[pygame.K_w]: dy -= 1
                if keys[pygame.K_s]: dy += 1
                if keys[pygame.K_a]: dx -= 1
                if keys[pygame.K_d]: dx += 1
                if dx == 0 and dy == 0:
                    dir_map = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
                    dx, dy = dir_map.get(self.player.direction, (1, 0))

                length = math.hypot(dx, dy)
                dx /= length
                dy /= length

                hand_offset = 12
                blast_x = px + dx * hand_offset
                blast_y = py + dy * hand_offset

                size_scale = 1.0 + charge_ratio
                cost = int(self.energy_blast_cost + 30 * charge_ratio)

                if self.energy >= cost:
                    print(f"Firing projectile with cost: {cost}, scale: {size_scale:.2f}")
                    proj = Projectile(
                        start_pos=(blast_x, blast_y),
                        direction=(dx, dy),
                        speed=70,
                        max_range=1000,
                        image_path=None
                    )
                    proj.image = pygame.transform.smoothscale(
                        proj.image,
                        (int(proj.image.get_width() * size_scale), int(proj.image.get_height() * size_scale))
                    )
                    proj.rect = proj.image.get_rect(center=(blast_x, blast_y))
                    self.projectiles.append(proj)
                    self.energy -= cost

            self.is_charging = False
            self.charge_time = 0.0
            self.space_was_pressed = False

        # ─── Melee Attacks ───────────────────────────────────────────
        if keys[pygame.K_j]:  # punch
            print("Punch pressed")
            self.spawn_melee("punch")
        if keys[pygame.K_k]:  # kick
            print("Kick pressed")
            self.spawn_melee("kick")

        for atk in self.melee_attacks[:]:
            atk['timer'] -= dt
            if atk['timer'] <= 0:
                self.melee_attacks.remove(atk)

        # ─── Update Projectiles ─────────────────────────────
        for proj in self.projectiles:
            proj.update(dt)

        # ─── Recover Energy ────────────────────────────────
        self.energy += self.energy_recovery_rate * dt
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def spawn_melee(self, attack_type):
        px, py = self.player.rect.center
        dir_map = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        dx, dy = dir_map.get(self.player.direction, (1, 0))
        offset = 28
        fx = px + dx * offset
        fy = py + dy * offset
        color = (255, 255, 0) if attack_type == "punch" else (255, 140, 0)
        print(f"Spawning {attack_type} at ({fx}, {fy})")
        self.melee_attacks.append({"pos": (fx, fy), "type": attack_type, "timer": self.melee_duration, "color": color})

    def draw(self):
        self.screen.fill(self.bg_color)
        self.player.draw(self.screen)

        # ─── Charging Aura ─────────────────────────────────
        if self.is_charging:
            charge_ratio = min(self.charge_time / self.max_charge_duration, 1.0)
            pulse = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * 0.01)
            aura_radius = int(20 + 40 * charge_ratio * pulse)
            alpha = 120 + int(100 * math.sin(pygame.time.get_ticks() * 0.01))
            aura_color = (0, 255, 255, max(100, min(alpha, 255)))
            aura_surface = pygame.Surface((aura_radius*2, aura_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surface, aura_color, (aura_radius, aura_radius), aura_radius, width=3)
            self.screen.blit(aura_surface, (self.player.rect.centerx - aura_radius, self.player.rect.centery - aura_radius))

        for proj in self.projectiles:
            proj.draw(self.screen)

        # ─── Melee Attack Visuals ──────────────────────────
        for atk in self.melee_attacks:
            pos = atk['pos']
            pygame.draw.circle(self.screen, atk['color'], (int(pos[0]), int(pos[1])), 12)  # filled circle


        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        # ─── UI Bar Dimensions ─────────────────────────────
        bar_x = 20
        bar_y = 20
        bar_width = 200
        bar_height = 20
        spacing = 5

        # ─── Health Bar ────────────────────────────────────
        pygame.draw.rect(self.screen, (0, 0, 0), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        health_ratio = self.health / self.max_health
        pygame.draw.rect(self.screen, (200, 0, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))

        # ─── Energy/Resonance Bar ─────────────────────────
        bar_y += bar_height + spacing
        pygame.draw.rect(self.screen, (0, 0, 0), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        energy_ratio = self.energy / self.max_energy
        pygame.draw.rect(self.screen, (0, 180, 180), (bar_x, bar_y, bar_width * energy_ratio, bar_height))
