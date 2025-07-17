# core/camera.py
import pygame
class Camera:
    def __init__(self, viewport_width, viewport_height, world_width=None, world_height=None):
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 1.5
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.world_width = world_width
        self.world_height = world_height

    def follow(self, target_rect):
        # Center camera on player considering zoom
        half_width = self.viewport_width / (2 * self.zoom)
        half_height = self.viewport_height / (2 * self.zoom)

        desired_x = target_rect.centerx - half_width
        desired_y = target_rect.centery - half_height

        if self.world_width is not None:
            max_x = max(0, self.world_width - self.viewport_width / self.zoom)
            self.offset_x = max(0, min(desired_x, max_x))
        else:
            self.offset_x = desired_x

        if self.world_height is not None:
            max_y = max(0, self.world_height - self.viewport_height / self.zoom)
            self.offset_y = max(0, min(desired_y, max_y))
        else:
            self.offset_y = desired_y

        print(f"[CAMERA] Offset: ({self.offset_x:.1f}, {self.offset_y:.1f}) | Zoom: {self.zoom:.2f}")

    def apply(self, rect):
        return pygame.Rect(
            int((rect.x - self.offset_x) * self.zoom),
            int((rect.y - self.offset_y) * self.zoom),
            int(rect.width * self.zoom),
            int(rect.height * self.zoom)
        )

    def apply_point(self, x, y):
        return int((x - self.offset_x) * self.zoom), int((y - self.offset_y) * self.zoom)

    def set_zoom(self, zoom_amount):
        self.zoom = max(self.min_zoom, min(self.max_zoom, zoom_amount))
