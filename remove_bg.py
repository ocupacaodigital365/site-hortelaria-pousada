"""
Remove background from logo using flood-fill from edges.
This approach only removes the outer background, keeping
white areas inside the logo design intact.
"""
from PIL import Image
from collections import deque
import os

INPUT  = os.path.join("assets", "img", "logo_backup.png")  # use original
OUTPUT = os.path.join("assets", "img", "logo.png")

# Tolerance: how different a pixel can be from the background color
# and still be considered background
TOLERANCE = 40

img = Image.open(INPUT).convert("RGBA")
pixels = img.load()
w, h = img.size

# Sample background color from corner pixels
bg_r, bg_g, bg_b, _ = pixels[0, 0]
print(f"Background color sampled: RGB({bg_r}, {bg_g}, {bg_b})")

def is_background(r, g, b):
    """Check if a pixel is close enough to the background color."""
    return (abs(r - bg_r) <= TOLERANCE and 
            abs(g - bg_g) <= TOLERANCE and 
            abs(b - bg_b) <= TOLERANCE)

# Flood fill from all edges
visited = set()
queue = deque()

# Add all edge pixels to the queue
for x in range(w):
    queue.append((x, 0))
    queue.append((x, h - 1))
for y in range(h):
    queue.append((0, y))
    queue.append((w - 1, y))

count = 0
while queue:
    x, y = queue.popleft()
    if (x, y) in visited:
        continue
    if x < 0 or x >= w or y < 0 or y >= h:
        continue
    visited.add((x, y))
    
    r, g, b, a = pixels[x, y]
    if is_background(r, g, b):
        pixels[x, y] = (r, g, b, 0)  # Make transparent
        count += 1
        # Add neighbors (4-connected)
        queue.append((x + 1, y))
        queue.append((x - 1, y))
        queue.append((x, y + 1))
        queue.append((x, y - 1))
        # Also 8-connected for smoother edges
        queue.append((x + 1, y + 1))
        queue.append((x - 1, y - 1))
        queue.append((x + 1, y - 1))
        queue.append((x - 1, y + 1))

# Now do a second pass for anti-aliasing on edge pixels
# Find pixels that border transparent pixels and are semi-background
for y in range(h):
    for x in range(w):
        r, g, b, a = pixels[x, y]
        if a == 0:
            continue  # already transparent
        
        # Check if any neighbor is transparent
        has_transparent_neighbor = False
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                _, _, _, na = pixels[nx, ny]
                if na == 0:
                    has_transparent_neighbor = True
                    break
        
        if has_transparent_neighbor and is_background(r, g, b):
            # Semi-transparent for smoother edges
            pixels[x, y] = (r, g, b, 80)

print(f"Made {count} pixels transparent")

# Crop to content (remove empty transparent edges)
bbox = img.getbbox()
if bbox:
    img = img.crop(bbox)
    print(f"Cropped to: {img.size[0]}x{img.size[1]}")

img.save(OUTPUT, "PNG")
print(f"Saved to {OUTPUT}")
