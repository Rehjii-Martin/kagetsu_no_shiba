import pygame
from pytmx import TiledTileLayer
class TilemapRenderer:
    def __init__(self, tmx_data, camera):
        self.tmx_data = tmx_data
        self.camera = camera
    def draw(self, surface):
        tw, th = self.tmx_data.tilewidth, self.tmx_data.tileheight
        sx = int(self.camera.offset_x // tw)
        sy = int(self.camera.offset_y // th)
        ex = int((self.camera.offset_x + self.camera.viewport_width/self.camera.zoom) // tw) + 1
        ey = int((self.camera.offset_y + self.camera.viewport_height/self.camera.zoom) // th) + 1
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer):
                for x in range(max(0, sx), min(layer.width, ex)):
                    for y in range(max(0, sy), min(layer.height, ey)):
                        gid = layer.data[y][x]
                        img = self.tmx_data.get_tile_image_by_gid(gid & 0x1FFFFFFF)
                        if img:
                            dx = int((x*tw - self.camera.offset_x)*self.camera.zoom)
                            dy = int((y*th - self.camera.offset_y)*self.camera.zoom)
                            img_s = pygame.transform.scale(img, (int(tw*self.camera.zoom), int(th*self.camera.zoom)))
                            surface.blit(img_s, (dx, dy))
