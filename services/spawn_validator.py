
import random, math, pygame

class SpawnValidator:
    @staticmethod
    def is_valid_spawn(x, y, collider_rects, avoid_point=None, min_distance=0):
        test_rect = pygame.Rect(x - 16, y - 32, 32, 64)
        if any(test_rect.colliderect(r) for r in collider_rects):
            return False
        if avoid_point:
            ax, ay = avoid_point
            if math.hypot(x - ax, y - ay) < min_distance:
                return False
        return True

    @classmethod
    def generate_spawns(cls, want, map_width, map_height, collider_rects, avoid_point=None, min_distance=0, max_attempts=300):
        result = []
        attempts = 0
        while len(result) < want and attempts < max_attempts:
            attempts += 1
            x = random.randint(32, map_width  - 32)
            y = random.randint(32, map_height - 32)
            if cls.is_valid_spawn(x, y, collider_rects, avoid_point, min_distance):
                result.append((x, y))
        return result
