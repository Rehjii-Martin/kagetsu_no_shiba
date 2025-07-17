import pygame

pygame.init()

# Create large surface
large_map = pygame.Surface((3000, 3000))
large_map.fill((30, 30, 30))  # dark base

# Add thick orange border
orange = (255, 120, 0)
border_width = 12
pygame.draw.rect(large_map, orange, (0, 0, 3000, 3000), border_width)

# Save it
pygame.image.save(large_map, "assets/maps/planet_map_placeholder.png")
print("✅ Large map with border saved!")
