import pygame
import math
import random
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename='solar_system.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Program info
PROGRAM_INFO = """
Solar System Simulator by Adrian Lesniak
Version: 1.0

Controls:
- Left Click: Create Black Hole
- Buttons at Bottom: Control Simulation Speed
- +/- Buttons: Adjust Black Hole Size
- Reset Button: Remove Black Hole

Features:
- Real-time gravitational physics
- Time dilation effects
- Planet collisions
- Black hole interactions
"""

# Initialize Pygame
pygame.init()
WIDTH = 1200
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Układ Słoneczny")

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GRAY = (169, 169, 169)
ORANGE = (255, 198, 73)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
BROWN = (150, 75, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
SUN_GLOW = (255, 69, 0)
SUN_CORE = (255, 255, 0)
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER = (150, 150, 150)
BUTTON_TEXT = (255, 255, 255)
BLACK_HOLE_COLOR = (20, 20, 20)
BLACK_HOLE_GLOW = (70, 0, 70)
COLLISION_FLASH = (255, 255, 200)
BLACK_HOLE_ABSORPTION = (128, 0, 128)

# Global variables
speed_multiplier = 1.0
black_hole = None
black_hole_size = 20

# Add physics constants
G = 0.1  # Gravitational constant (scaled for visualization)
LIGHT_SPEED = 30  # Scaled speed of light for visualization
EVENT_HORIZON_FACTOR = 2.0  # Schwarzschild radius factor

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def draw(self, screen):
        color = BUTTON_HOVER if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect)
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self.text, True, BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                self.action()

class Sun:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.base_radius = radius
        self.glow_radius = radius * 1.5
        self.time = 0
        self.mass = radius * 1000  # Sun has much larger mass
        self.active = True  # Add active state for sun
    
    def draw(self, screen):
        if not self.active:
            return
            
        # Pulsating effect
        self.time += 0.05
        pulse = math.sin(self.time) * 5
        
        # Draw multiple layers of glow
        for i in range(5):
            alpha = 255 - (i * 50)
            glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            radius = self.glow_radius - (i * 5) + pulse
            pygame.draw.circle(glow_surface, (*SUN_GLOW, alpha), (self.x, self.y), int(radius))
            screen.blit(glow_surface, (0, 0))
        
        # Draw sun core
        pygame.draw.circle(screen, SUN_CORE, (self.x, self.y), self.base_radius)

    def check_black_hole_interaction(self, black_hole):
        if not self.active or not black_hole:
            return False
            
        distance = math.sqrt((self.x - black_hole.x)**2 + (self.y - black_hole.y)**2)
        if distance < black_hole.event_horizon + self.base_radius:
            self.active = False
            # Massive growth of black hole when absorbing sun
            black_hole.mass += self.mass * 2
            black_hole.radius *= 1.5
            black_hole.event_horizon = black_hole.radius * EVENT_HORIZON_FACTOR
            return True
        return False

    def reset_position(self):
        self.x = WIDTH//2
        self.y = HEIGHT//2
        self.active = True

    def affect_planets(self, planets):
        if not self.active:
            return
        
        for planet in planets:
            if not planet.active:
                continue
                
            dx = planet.orbit_center_offset_x + WIDTH//2 - self.x
            dy = planet.orbit_center_offset_y + HEIGHT//2 - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            # Prevent division by zero and handle very close distances
            if distance < 1:
                distance = 1
            elif distance < planet.radius + self.base_radius:
                # Handle collision with sun
                planet.active = False
                continue
            
            force = G * self.mass * planet.mass / (distance**2)
            angle = math.atan2(dy, dx)
            
            # Scale force effect for better visualization
            force_scale = 0.00001
            planet.velocity_x += math.cos(angle) * force * force_scale
            planet.velocity_y += math.sin(angle) * force * force_scale

class BlackHole:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = radius * 100  # Mass proportional to radius
        self.time = 0
        self.effect_radius = radius * 12
        self.event_horizon = self.radius * EVENT_HORIZON_FACTOR
        self.absorbed_planets = []
        self.absorption_animations = []
        self.pull_strength = 0.5  # Add pull strength control
        
    def calculate_gravity(self, x, y, mass):
        dx = self.x - x
        dy = self.y - y
        r = math.sqrt(dx**2 + dy**2)
        if r < 1: r = 1  # Prevent division by zero
        
        # Calculate gravitational force
        force = G * self.mass * mass / (r * r)
        
        # Calculate time dilation effect
        time_dilation = 1 / math.sqrt(1 - min(0.99, (2 * G * self.mass) / (r * LIGHT_SPEED**2)))
        
        return force * dx/r, force * dy/r, time_dilation

    def affect_planet(self, planet, center_x, center_y):
        planet_x = center_x + math.cos(math.radians(planet.angle)) * planet.distance_from_sun
        planet_y = center_y + math.sin(math.radians(planet.angle)) * planet.distance_from_sun
        
        dx = self.x - planet_x
        dy = self.y - planet_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.radius:  # Only absorb if directly touching black hole
            self.start_absorption(planet)
            return True
        
        # Calculate gravitational force with smoother falloff
        force = (G * self.mass * planet.mass) / (distance**2)
        force = min(force, 2.0)  # Limit maximum force
        
        angle = math.atan2(dy, dx)
        pull_x = math.cos(angle) * force * self.pull_strength
        pull_y = math.sin(angle) * force * self.pull_strength
        
        # Update planet's orbit center instead of making it inactive
        planet.orbit_center_offset_x += pull_x * 0.01
        planet.orbit_center_offset_y += pull_y * 0.01
        
        # Calculate time dilation
        planet.time_dilation = 1 + (self.mass / (distance * LIGHT_SPEED))
        
        return False

    def start_absorption(self, planet):
        if planet not in self.absorbed_planets:
            self.absorbed_planets.append(planet)
            self.absorption_animations.append([0.0, planet])
            self.mass += planet.mass
            self.radius = math.sqrt(self.radius**2 + planet.radius)
            self.event_horizon = self.radius * EVENT_HORIZON_FACTOR
    
    def draw(self, screen):
        self.time += 0.05
        pulse = math.sin(self.time) * 3
        
        # Draw effect radius
        pygame.draw.circle(screen, (40, 0, 40), (int(self.x), int(self.y)), int(self.effect_radius), 1)
        
        # Draw black hole glow (fix syntax error)
        for i in range(3):
            alpha = 200 - (i * 60)
            glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            radius = self.radius + 10 - (i * 3) + pulse
            pygame.draw.circle(glow_surface, (*BLACK_HOLE_GLOW, alpha), (self.x, self.y), int(radius))
            screen.blit(glow_surface, (0, 0))
        
        # Draw black hole core
        pygame.draw.circle(screen, BLACK_HOLE_COLOR, (self.x, self.y), self.radius)

        # Draw absorption animations
        for anim in self.absorption_animations[:]:
            progress, planet = anim
            if progress < 1.0:
                # Create spiral effect
                spiral_x = self.x + math.cos(progress * 12) * (50 - progress * 50)
                spiral_y = self.y + math.sin(progress * 12) * (50 - progress * 50)
                size = max(2, planet.radius * (1 - progress))
                pygame.draw.circle(screen, planet.color, (int(spiral_x), int(spiral_y)), int(size))
                anim[0] += 0.05
            else:
                self.absorption_animations.remove(anim)

    def affect_sun(self, sun):
        if not sun.active:
            return
            
        dx = self.x - sun.x
        dy = self.y - sun.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 1:  # Prevent division by zero
            # Calculate gravitational force between black hole and sun
            force = G * self.mass * sun.mass / (distance * distance)
            # Move sun slightly towards black hole
            sun.x += (dx/distance) * force * 0.0001
            sun.y += (dy/distance) * force * 0.0001

# Planet class
class Planet:
    def __init__(self, distance_from_sun, radius, color, orbital_period, name, has_rings=False, ring_color=None):
        self.distance_from_sun = distance_from_sun
        self.radius = radius
        self.color = color
        self.orbital_period = orbital_period  # In Earth years
        self.angle = 0
        self.name = name
        self.has_rings = has_rings
        self.ring_color = ring_color
        self.orbit_center_offset_x = 0
        self.orbit_center_offset_y = 0
        self.original_distance = distance_from_sun
        self.velocity_x = 0
        self.velocity_y = 0
        self.collision_flash = 0
        self.active = True
        self.mass = radius * 10  # Mass proportional to radius
        self.time_dilation = 1.0
        self.orbital_velocity = math.sqrt(G * 1000 / distance_from_sun)  # Calculate orbital velocity
        self.initial_distance = distance_from_sun
        self.initial_angle = random.uniform(0, 360)
        self.angle = self.initial_angle

    def reset_position(self):
        self.distance_from_sun = self.initial_distance
        self.angle = self.initial_angle
        self.velocity_x = 0
        self.velocity_y = 0
        self.orbit_center_offset_x = 0
        self.orbit_center_offset_y = 0
        self.active = True
        self.collision_flash = 0
        self.time_dilation = 1.0

    def apply_gravity_to(self, other_planet):
        if not self.active or not other_planet.active:
            return

        x1 = WIDTH//2 + math.cos(math.radians(self.angle)) * self.distance_from_sun
        y1 = HEIGHT//2 + math.sin(math.radians(self.angle)) * self.distance_from_sun
        x2 = WIDTH//2 + math.cos(math.radians(other_planet.angle)) * other_planet.distance_from_sun
        y2 = HEIGHT//2 + math.sin(math.radians(other_planet.angle)) * other_planet.distance_from_sun

        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx**2 + dy**2)

        if distance < (self.radius + other_planet.radius):
            # Collision handling
            self.handle_collision(other_planet)
        else:
            # Gravitational force
            force = G * self.mass * other_planet.mass / (distance**2)
            angle = math.atan2(dy, dx)
            
            # Apply forces
            self.velocity_x += math.cos(angle) * force * 0.0001
            self.velocity_y += math.sin(angle) * force * 0.0001
            other_planet.velocity_x -= math.cos(angle) * force * 0.0001
            other_planet.velocity_y -= math.sin(angle) * force * 0.0001

    def handle_collision(self, other_planet):
        # Elastic collision
        self.collision_flash = 1.0
        other_planet.collision_flash = 1.0

        # Exchange momentum
        temp_vx = self.velocity_x
        temp_vy = self.velocity_y
        self.velocity_x = other_planet.velocity_x * 0.8
        self.velocity_y = other_planet.velocity_y * 0.8
        other_planet.velocity_x = temp_vx * 0.8
        other_planet.velocity_y = temp_vy * 0.8

    def check_collision(self, other_planet):
        if not self.active or not other_planet.active:
            return False
            
        x1 = WIDTH//2 + math.cos(math.radians(self.angle)) * self.distance_from_sun
        y1 = HEIGHT//2 + math.sin(math.radians(self.angle)) * self.distance_from_sun
        x2 = WIDTH//2 + math.cos(math.radians(other_planet.angle)) * other_planet.distance_from_sun
        y2 = HEIGHT//2 + math.sin(math.radians(other_planet.angle)) * other_planet.distance_from_sun
        
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        return distance < (self.radius + other_planet.radius)

    def update(self, speed_multiplier, black_hole=None):
        if not self.active:
            return

        effective_speed = speed_multiplier / self.time_dilation
        self.angle += (self.orbital_velocity * effective_speed)
        
        if black_hole:
            if not black_hole.affect_planet(self, WIDTH//2, HEIGHT//2):
                # Only apply these if not absorbed
                max_offset = 300  # Maximum orbit distortion
                self.orbit_center_offset_x = max(min(self.orbit_center_offset_x, max_offset), -max_offset)
                self.orbit_center_offset_y = max(min(self.orbit_center_offset_y, max_offset), -max_offset)
                
                # Gradually return to original orbit when far from black hole
                if math.sqrt(self.orbit_center_offset_x**2 + self.orbit_center_offset_y**2) < 1:
                    self.orbit_center_offset_x *= 0.99
                    self.orbit_center_offset_y *= 0.99
        else:
            # Return to normal orbit
            self.orbit_center_offset_x *= 0.95
            self.orbit_center_offset_y *= 0.95
            self.time_dilation = 1.0

        # Maintain minimum distance from sun
        min_distance = self.radius + 50
        if self.distance_from_sun < min_distance:
            self.distance_from_sun = min_distance

        if self.collision_flash > 0:
            self.collision_flash -= 0.1

    def draw(self, screen, center_x, center_y):
        if not self.active:
            return
            
        # Adjust center based on black hole influence
        adjusted_center_x = center_x + self.orbit_center_offset_x
        adjusted_center_y = center_y + self.orbit_center_offset_y
        
        x = adjusted_center_x + math.cos(math.radians(self.angle)) * self.distance_from_sun
        y = adjusted_center_y + math.sin(math.radians(self.angle)) * self.distance_from_sun
        
        # Draw orbital path
        pygame.draw.circle(screen, (50, 50, 50), (center_x, center_y), int(self.distance_from_sun), 1)
        
        # Draw planet
        pygame.draw.circle(screen, self.color, (int(x), int(y)), self.radius)
        
        # Draw planet name
        font = pygame.font.SysFont(None, 20)
        text = font.render(self.name, True, WHITE)
        screen.blit(text, (int(x - text.get_width()/2), int(y + self.radius + 5)))
        
        # Draw rings if planet has them
        if self.has_rings:
            ring_rect = pygame.Rect(x - self.radius*2, y - self.radius//2, 
                                  self.radius*4, self.radius)
            pygame.draw.ellipse(screen, self.ring_color, ring_rect, 2)

        # Draw collision flash
        if self.collision_flash > 0:
            flash_radius = self.radius + 5
            alpha = int(255 * self.collision_flash)
            flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(flash_surface, (*COLLISION_FLASH, alpha), 
                             (int(x), int(y)), int(flash_radius))
            screen.blit(flash_surface, (0, 0))
        
        # Add time dilation indicator
        if self.time_dilation > 1.1:
            time_text = f"T×{self.time_dilation:.1f}"
            font = pygame.font.SysFont(None, 16)
            text = font.render(time_text, True, (255, 0, 0))
            screen.blit(text, (int(x - text.get_width()/2), int(y - self.radius - 15)))

def change_speed(factor):
    global speed_multiplier
    speed_multiplier = factor

def create_black_hole(pos):
    global black_hole
    black_hole = BlackHole(pos[0], pos[1], black_hole_size)

def change_black_hole_size(delta):
    global black_hole_size
    black_hole_size = max(10, min(50, black_hole_size + delta))

def reset_black_hole():
    global black_hole
    black_hole = None

def reset_simulation():
    global black_hole
    black_hole = None
    sun.reset_position()
    for planet in planets:
        planet.reset_position()

class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.info_font = pygame.font.SysFont(None, 24)
        self.header_font = pygame.font.SysFont(None, 32)
        
    def draw_header(self):
        # Draw program author
        author = self.header_font.render("Solar System Simulator - By Adrian Lesniak", True, (200, 200, 200))
        self.screen.blit(author, (10, 10))
        
        # Draw controls info
        y_pos = 50
        for line in PROGRAM_INFO.split('\n'):
            if line.strip():
                text = self.info_font.render(line, True, (180, 180, 180))
                self.screen.blit(text, (10, y_pos))
                y_pos += 25

    def save_state(self, planets, black_hole, sun):
        try:
            state = {
                'timestamp': str(datetime.now()),
                'black_hole': {
                    'exists': black_hole is not None,
                    'x': black_hole.x if black_hole else 0,
                    'y': black_hole.y if black_hole else 0,
                    'radius': black_hole.radius if black_hole else 0
                },
                'planets': [(p.distance_from_sun, p.angle, p.active) for p in planets],
                'sun': {'active': sun.active, 'x': sun.x, 'y': sun.y}
            }
            with open('simulation_state.json', 'w') as f:
                json.dump(state, f)
            logging.info("Simulation state saved successfully")
        except Exception as e:
            logging.error(f"Error saving state: {str(e)}")

    def load_state(self, planets, black_hole, sun):
        try:
            with open('simulation_state.json', 'r') as f:
                state = json.load(f)
                
            if state['black_hole']['exists']:
                black_hole = BlackHole(
                    state['black_hole']['x'],
                    state['black_hole']['y'],
                    state['black_hole']['radius']
                )
                
            for planet, (dist, angle, active) in zip(planets, state['planets']):
                planet.distance_from_sun = dist
                planet.angle = angle
                planet.active = active
                
            sun.active = state['sun']['active']
            sun.x = state['sun']['x']
            sun.y = state['sun']['y']
            
            logging.info("Simulation state loaded successfully")
            return black_hole
        except Exception as e:
            logging.error(f"Error loading state: {str(e)}")
            return None

# Create buttons with corrected reset function
buttons = [
    Button(10, HEIGHT-40, 80, 30, "0.5x", lambda: change_speed(0.5)),
    Button(100, HEIGHT-40, 80, 30, "1x", lambda: change_speed(1.0)),
    Button(190, HEIGHT-40, 80, 30, "2x", lambda: change_speed(2.0)),
    Button(280, HEIGHT-40, 80, 30, "5x", lambda: change_speed(5.0)),
    Button(10, HEIGHT-80, 120, 30, "Reset Black Hole", reset_black_hole),
    Button(140, HEIGHT-80, 30, 30, "-", lambda: change_black_hole_size(-5)),
    Button(180, HEIGHT-80, 30, 30, "+", lambda: change_black_hole_size(5)),
    Button(10, HEIGHT-80, 120, 30, "Reset All", reset_simulation)
]

# Add new buttons for save/load
buttons.extend([
    Button(400, HEIGHT-80, 80, 30, "Save", lambda: ui_manager.save_state(planets, black_hole, sun)),
    Button(490, HEIGHT-80, 80, 30, "Load", lambda: setattr(globals(), 'black_hole', ui_manager.load_state(planets, black_hole, sun)))
])

# Create planets with adjusted distances and names
mercury = Planet(65, 5, GRAY, 0.24, "Merkury")
venus = Planet(95, 10, ORANGE, 0.62, "Wenus")
earth = Planet(130, 12, BLUE, 1.0, "Ziemia")
mars = Planet(165, 8, RED, 1.88, "Mars")
jupiter = Planet(220, 25, BROWN, 11.86, "Jowisz")
saturn = Planet(280, 20, ORANGE, 29.46, "Saturn", True, (139, 69, 19))
uranus = Planet(330, 15, LIGHT_BLUE, 84.01, "Uran")
neptune = Planet(380, 15, DARK_BLUE, 164.79, "Neptun")

planets = [mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]

# Create sun
sun = Sun(WIDTH//2, HEIGHT//2, 40)

# Create UI manager
ui_manager = UIManager(screen)

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[1] < HEIGHT-100:  # Avoid buttons area
                if event.button == 1:  # Left click
                    create_black_hole(mouse_pos)
        
        # Handle button events
        for button in buttons:
            button.handle_event(event)

    screen.fill((0, 0, 0))

    # Draw header
    ui_manager.draw_header()

    # Draw indicators
    font = pygame.font.SysFont(None, 36)
    speed_text = font.render(f"Speed: {speed_multiplier}x", True, WHITE)
    screen.blit(speed_text, (370, HEIGHT-35))

    bh_font = pygame.font.SysFont(None, 24)
    bh_text = bh_font.render(f"Black Hole Size: {black_hole_size}", True, WHITE)
    screen.blit(bh_text, (230, HEIGHT-75))

    # Check collisions between planets
    for i, planet1 in enumerate(planets):
        for planet2 in planets[i+1:]:
            if planet1.check_collision(planet2):
                planet1.collision_flash = 1.0
                planet2.collision_flash = 1.0
                # Transfer momentum
                planet1.velocity_x = (planet1.velocity_x or 0) * -0.5
                planet1.velocity_y = (planet1.velocity_y or 0) * -0.5
                planet2.velocity_x = (planet2.velocity_x or 0) * -0.5
                planet2.velocity_y = (planet2.velocity_y or 0) * -0.5

    # Update physics
    if sun.active:
        sun.affect_planets(planets)
    
    # Inter-planetary gravity
    for i, planet1 in enumerate(planets):
        for planet2 in planets[i+1:]:
            planet1.apply_gravity_to(planet2)

    # Draw all objects
    if black_hole:
        black_hole.affect_sun(sun)
        sun.check_black_hole_interaction(black_hole)
        black_hole.draw(screen)
    
    sun.draw(screen)
    
    for planet in planets:
        planet.update(speed_multiplier, black_hole)
        planet.draw(screen, WIDTH//2, HEIGHT//2)
    
    # Draw buttons last so they're always on top
    for button in buttons:
        button.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
