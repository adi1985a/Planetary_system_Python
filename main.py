"""
Planetary System Simulator
Autor: Adrian Lesniak

Opis programu:
Symulator układu planetarnego z możliwością tworzenia czarnej dziury, kolizji planet, efektów dylatacji czasu i zapisu/odczytu stanu symulacji. Program posiada graficzny interfejs użytkownika z jasnymi kolorami, przyciskami, ikonami oraz menu z opisem opcji. Po każdej akcji następuje powrót do menu po naciśnięciu klawisza.

Funkcje programu:
- Symulacja grawitacji i ruchu planet
- Tworzenie czarnej dziury i jej wpływ na układ
- Kolizje planet i słońca
- Efekty dylatacji czasu
- Zapis i odczyt stanu symulacji do pliku
- Atrakcyjny, jasny interfejs graficzny
- Obsługa wyjątków i logowanie błędów
- Wieloplatformowość

Wybrane opcje menu:
- Tworzenie czarnej dziury (lewy klik)
- Zmiana prędkości symulacji (przyciski na dole)
- Zmiana rozmiaru czarnej dziury (+/-)
- Reset czarnej dziury i całej symulacji
- Zapis/odczyt stanu

"""
import pygame
import math
import random
import json
import logging
from datetime import datetime
import time

class SingletonLogger:
    """
    Singleton logger for the application.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = logging.getLogger("SolarSystemLogger")
            handler = logging.FileHandler('solar_system.log', encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
            handler.setFormatter(formatter)
            cls._instance.logger.addHandler(handler)
            cls._instance.logger.setLevel(logging.INFO)
        return cls._instance

    def get_logger(self):
        return self.logger

# Zamień globalny logger na singleton
logger = SingletonLogger().get_logger()

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
# Set new window size for more space
WIDTH = 1500
HEIGHT = 1050
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Simulator")

# Define layout constants
HEADER_HEIGHT = 120
FOOTER_HEIGHT = 100
PANEL_MARGIN = 30
PANEL_TOP = HEADER_HEIGHT + PANEL_MARGIN
PANEL_BOTTOM = HEIGHT - FOOTER_HEIGHT - PANEL_MARGIN
PANEL_LEFT = PANEL_MARGIN
PANEL_RIGHT = WIDTH - PANEL_MARGIN
PANEL_WIDTH = PANEL_RIGHT - PANEL_LEFT
PANEL_HEIGHT = PANEL_BOTTOM - PANEL_TOP
PANEL_CENTER_X = PANEL_LEFT + PANEL_WIDTH // 2
PANEL_CENTER_Y = PANEL_TOP + PANEL_HEIGHT // 2

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
BUTTON_COLOR = (220, 220, 255)
BUTTON_HOVER = (255, 255, 180)
BUTTON_TEXT = (60, 60, 60)
BLACK_HOLE_COLOR = (20, 20, 20)
BLACK_HOLE_GLOW = (70, 0, 70)
COLLISION_FLASH = (255, 255, 200)
BLACK_HOLE_ABSORPTION = (128, 0, 128)

# Zdefiniuj jasne kolory i ikony unicode
HEADER_BG = (255, 255, 240)
HEADER_TEXT = (80, 80, 200)
INFO_BG = (240, 240, 255)
INFO_TEXT = (100, 100, 100)
# Zamień surrogaty unicode na bezpośrednie znaki
ICON_SAVE = '💾'
ICON_LOAD = '↺'
ICON_RESET = '♻'
ICON_PLUS = '➕'
ICON_MINUS = '➖'
ICON_BH = '⬤'
ICON_SPEED = '⏩'

# Global variables
speed_multiplier = 1.0
black_hole = None
black_hole_size = 20

# Add physics constants
G = 0.1  # Gravitational constant (scaled for visualization)
LIGHT_SPEED = 30  # Scaled speed of light for visualization
EVENT_HORIZON_FACTOR = 2.0  # Schwarzschild radius factor

class Button:
    """
    A class to manage buttons in the UI.
    """
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def draw(self, screen):
        """
        Draws the button on the screen.
        """
        color = BUTTON_HOVER if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self.text, True, BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        """
        Handles mouse events for the button.
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                self.action()

class Sun:
    """
    Represents the Sun in the solar system.
    """
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.base_radius = radius
        self.glow_radius = radius * 1.5
        self.time = 0
        self.mass = radius * 1000  # Sun has much larger mass
        self.active = True  # Add active state for sun
    
    def draw(self, screen):
        """
        Draws the Sun on the screen.
        """
        if not self.active:
            return
            
        # Pulsating effect
        self.time += 0.05
        pulse = math.sin(self.time) * 8
        
        # Animated glow
        for i in range(8):
            alpha = 180 - (i * 20)
            glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            radius = self.glow_radius + pulse - (i * 4)
            pygame.draw.circle(glow_surface, (*SUN_GLOW, alpha), (self.x, self.y), int(radius))
            screen.blit(glow_surface, (0, 0))
        
        # Sun core
        pygame.draw.circle(screen, SUN_CORE, (self.x, self.y), self.base_radius)
        # Subtle shadow
        shadow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (0,0,0,40), (self.x, self.y+10), self.base_radius+8)
        screen.blit(shadow_surface, (0,0))

    def check_black_hole_interaction(self, black_hole):
        """
        Checks if the Sun is interacting with a Black Hole.
        """
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
        """
        Resets the Sun's position to the center of the screen.
        """
        self.x = WIDTH//2
        self.y = HEIGHT//2
        self.active = True

    def affect_planets(self, planets):
        """
        Applies gravitational force from the Sun to all planets.
        """
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
                # Animacja kolizji ze Słońcem
                planet.collision_anim_time = 25
                planet.collision_pos = (int(self.x), int(self.y))
                continue
            
            force = G * self.mass * planet.mass / (distance**2)
            angle = math.atan2(dy, dx)
            
            # Scale force effect for better visualization
            force_scale = 0.00001
            planet.velocity_x += math.cos(angle) * force * force_scale
            planet.velocity_y += math.sin(angle) * force * force_scale

class BlackHole:
    """
    Represents a Black Hole in the solar system.
    """
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
        """
        Calculates gravitational force and time dilation effect.
        """
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
        """
        Applies gravitational force and time dilation to a planet.
        """
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
            # Start spiral absorption animation: [progress, planet, spiral_angle, stretch_factor]
            self.absorption_animations.append([0.0, planet, random.uniform(0, 2*math.pi), 1.0])
            # Do not immediately deactivate planet
            # planet.active = False  # Usunięte!
            self.mass += planet.mass
            self.radius = math.sqrt(self.radius**2 + planet.radius)
            self.event_horizon = self.radius * EVENT_HORIZON_FACTOR

    def draw(self, screen):
        self.time += 0.07
        pulse = math.sin(self.time) * 5
        # Animated effect radius
        for i in range(4):
            alpha = 120 - (i * 30)
            glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            radius = self.radius + 18 - (i * 5) + pulse
            pygame.draw.circle(glow_surface, (*BLACK_HOLE_GLOW, alpha), (int(self.x), int(self.y)), int(radius))
            screen.blit(glow_surface, (0, 0))
        # Swirling accretion disk
        for i in range(12):
            angle = self.time + i * 0.5
            r = self.radius + 22 + 6 * math.sin(angle*2)
            x = int(self.x + r * math.cos(angle))
            y = int(self.y + r * math.sin(angle))
            pygame.draw.circle(screen, (200, 0, 200, 60), (x, y), 2)
        # Black hole core
        pygame.draw.circle(screen, BLACK_HOLE_COLOR, (int(self.x), int(self.y)), int(self.radius))
        # Draw absorption animations (spaghettification)
        for anim in self.absorption_animations[:]:
            progress, planet, spiral_angle, stretch = anim
            if progress < 1.0:
                # Spiral inwards, stretch planet
                spiral_r = (1-progress) * 80
                spiral_theta = spiral_angle + progress * 8 * math.pi
                px = self.x + math.cos(spiral_theta) * spiral_r
                py = self.y + math.sin(spiral_theta) * spiral_r
                # Stretch planet as it approaches
                stretch = 1 + progress * 4
                anim[3] = stretch
                # Draw stretched planet (ellipse)
                planet_color = tuple(min(255, int(c + 40*progress)) for c in planet.color)
                ellipse_surface = pygame.Surface((planet.radius*2*stretch, planet.radius*2), pygame.SRCALPHA)
                pygame.draw.ellipse(ellipse_surface, planet_color, (0, 0, planet.radius*2*stretch, planet.radius*2))
                screen.blit(ellipse_surface, (int(px-planet.radius*stretch), int(py-planet.radius)))
                anim[0] += 0.025 + 0.02*progress
            else:
                # Deactivate planet after animation
                planet.active = False
                self.absorption_animations.remove(anim)

    def affect_sun(self, sun):
        """
        Applies gravitational force from the Black Hole to the Sun.
        """
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
    """
    Represents a planet in the solar system.
    """
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
        self.collision_anim_time = 0  # czas trwania animacji kolizji
        self.collision_pos = None     # pozycja kolizji
        self.active = True
        self.mass = radius * 10  # Mass proportional to radius
        self.time_dilation = 1.0
        self.orbital_velocity = math.sqrt(G * 1000 / distance_from_sun)  # Calculate orbital velocity
        self.initial_distance = distance_from_sun
        self.initial_angle = random.uniform(0, 360)
        self.angle = self.initial_angle

    def reset_position(self):
        """
        Resets the planet's position and velocity to its initial state.
        """
        self.distance_from_sun = self.initial_distance
        self.angle = self.initial_angle
        self.velocity_x = 0
        self.velocity_y = 0
        self.orbit_center_offset_x = 0
        self.orbit_center_offset_y = 0
        self.active = True
        self.collision_flash = 0
        self.collision_anim_time = 0
        self.collision_pos = None
        self.time_dilation = 1.0

    def apply_gravity_to(self, other_planet):
        """
        Applies gravitational force between this planet and another planet.
        """
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
        """
        Handles the collision between two planets.
        """
        # Elastic collision
        self.collision_flash = 1.0
        other_planet.collision_flash = 1.0
        # Animacja kolizji
        self.collision_anim_time = 20
        other_planet.collision_anim_time = 20
        # Pozycja kolizji (środek między planetami)
        x1 = PANEL_CENTER_X + math.cos(math.radians(self.angle)) * self.distance_from_sun + self.orbit_center_offset_x
        y1 = PANEL_CENTER_Y + math.sin(math.radians(self.angle)) * self.distance_from_sun + self.orbit_center_offset_y
        x2 = PANEL_CENTER_X + math.cos(math.radians(other_planet.angle)) * other_planet.distance_from_sun + other_planet.orbit_center_offset_x
        y2 = PANEL_CENTER_Y + math.sin(math.radians(other_planet.angle)) * other_planet.distance_from_sun + other_planet.orbit_center_offset_y
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        self.collision_pos = (cx, cy)
        other_planet.collision_pos = (cx, cy)

    def check_collision(self, other_planet):
        """
        Checks if two planets are colliding.
        """
        if not self.active or not other_planet.active:
            return False
            
        x1 = WIDTH//2 + math.cos(math.radians(self.angle)) * self.distance_from_sun
        y1 = HEIGHT//2 + math.sin(math.radians(self.angle)) * self.distance_from_sun
        x2 = WIDTH//2 + math.cos(math.radians(other_planet.angle)) * other_planet.distance_from_sun
        y2 = HEIGHT//2 + math.sin(math.radians(other_planet.angle)) * other_planet.distance_from_sun
        
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        return distance < (self.radius + other_planet.radius)

    def update(self, speed_multiplier, black_hole=None):
        """
        Updates the planet's position and velocity based on its orbit and black hole influence.
        """
        if not self.active:
            return
        # If being absorbed, skip normal update
        for anim in getattr(black_hole, 'absorption_animations', []) if black_hole else []:
            if anim[1] is self and anim[0] < 1.0:
                return
        effective_speed = speed_multiplier / self.time_dilation
        self.angle += (self.orbital_velocity * effective_speed)
        # --- Black hole gravity and slingshot effect ---
        if black_hole:
            # Pozycja planety
            px = PANEL_CENTER_X + math.cos(math.radians(self.angle)) * self.distance_from_sun + self.orbit_center_offset_x
            py = PANEL_CENTER_Y + math.sin(math.radians(self.angle)) * self.distance_from_sun + self.orbit_center_offset_y
            dx = black_hole.x - px
            dy = black_hole.y - py
            distance = math.sqrt(dx**2 + dy**2)
            # Jeśli planeta bardzo blisko czarnej dziury, absorpcja
            if distance < black_hole.radius*1.2:
                black_hole.start_absorption(self)
                return
            # Jeśli planeta przeleci bardzo blisko czarnej dziury, efekt slingshot/wybicia
            elif distance < black_hole.effect_radius*0.7 and not hasattr(self, 'ejected'):
                # Oblicz prędkość ucieczki i kierunek
                v_escape = math.sqrt(2 * G * black_hole.mass / max(distance, 1))
                angle = math.atan2(dy, dx)
                # Nadaj planecie nową prędkość (asysta grawitacyjna)
                self.velocity_x += math.cos(angle) * v_escape * 0.7
                self.velocity_y += math.sin(angle) * v_escape * 0.7
                # Zmień orbitę na bardzo wydłużoną (lub trajektorię ucieczki)
                self.distance_from_sun += random.randint(100, 300)
                self.orbit_center_offset_x += int(dx * 0.5)
                self.orbit_center_offset_y += int(dy * 0.5)
                self.ejected = True  # Flaga, by nie powtarzać efektu
            # Jeśli planeta już wybita, kontynuuj ruch po trajektorii
            if hasattr(self, 'ejected') and self.ejected:
                # Ruch po prostej z zachowaniem pędu
                self.orbit_center_offset_x += self.velocity_x
                self.orbit_center_offset_y += self.velocity_y
                # Jeśli planeta opuści panel, dezaktywuj
                if (px < PANEL_LEFT-100 or px > PANEL_RIGHT+100 or py < PANEL_TOP-100 or py > PANEL_BOTTOM+100):
                    self.active = False
                return
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
        if self.collision_anim_time > 0:
            self.collision_anim_time -= 1

    def draw(self, screen, center_x, center_y):
        """
        Draws the planet on the screen.
        """
        if not self.active:
            return
        # If being absorbed, skip normal draw (handled by black hole)
        for anim in getattr(black_hole, 'absorption_animations', []) if 'black_hole' in globals() and black_hole else []:
            if anim[1] is self and anim[0] < 1.0:
                return
            
        # Adjust center based on black hole influence
        adjusted_center_x = center_x + self.orbit_center_offset_x
        adjusted_center_y = center_y + self.orbit_center_offset_y
        
        x = adjusted_center_x + math.cos(math.radians(self.angle)) * self.distance_from_sun
        y = adjusted_center_y + math.sin(math.radians(self.angle)) * self.distance_from_sun
        
        # Draw orbital path
        if black_hole:
            # Deform orbit: ellipse based on black hole position
            dx = black_hole.x - center_x
            dy = black_hole.y - center_y
            orbit_a = int(self.distance_from_sun + abs(dx)*0.2)
            orbit_b = int(self.distance_from_sun + abs(dy)*0.2)
            orbit_rect = pygame.Rect(center_x-orbit_a, center_y-orbit_b, 2*orbit_a, 2*orbit_b)
            pygame.draw.ellipse(screen, (50,50,50), orbit_rect, 1)
        else:
            pygame.draw.circle(screen, (50, 50, 50), (center_x, center_y), int(self.distance_from_sun), 1)
        
        # Subtle shadow
        shadow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (0,0,0,40), (int(x), int(y+8)), self.radius+3)
        screen.blit(shadow_surface, (0,0))
        # Gradient planet
        for i in range(self.radius, 0, -1):
            color = tuple(min(255, int(c + (self.radius-i)*8)) for c in self.color)
            pygame.draw.circle(screen, color, (int(x), int(y)), i)
        
        # Draw planet name
        font = pygame.font.SysFont(None, 20)
        text = font.render(self.name, True, WHITE)
        screen.blit(text, (int(x - text.get_width()/2), int(y + self.radius + 5)))
        
        # Animated rings for Saturn
        if self.has_rings:
            ring_surface = pygame.Surface((self.radius*5, self.radius*2), pygame.SRCALPHA)
            ring_angle = math.sin(pygame.time.get_ticks()/400) * 10
            ring_rect = pygame.Rect(self.radius*0.5, self.radius*0.5, self.radius*4, self.radius)
            pygame.draw.ellipse(ring_surface, self.ring_color, ring_rect, 2)
            ring_surface = pygame.transform.rotate(ring_surface, ring_angle)
            screen.blit(ring_surface, (int(x - ring_surface.get_width()/2), int(y - ring_surface.get_height()/2)))
        
        # Draw collision flash
        if self.collision_flash > 0:
            flash_radius = self.radius + 5
            alpha = int(255 * self.collision_flash)
            flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(flash_surface, (*COLLISION_FLASH, alpha), (int(x), int(y)), int(flash_radius))
            screen.blit(flash_surface, (0, 0))
        
        # Animacja kolizji (rozbłysk)
        if self.collision_anim_time > 0 and self.collision_pos:
            anim_progress = 1 - self.collision_anim_time / 20
            max_radius = self.radius * 4 + 20
            flash_radius = int(max_radius * anim_progress)
            alpha = int(255 * (1 - anim_progress))
            flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(flash_surface, (255, 220, 0, alpha), self.collision_pos, flash_radius)
            pygame.draw.circle(flash_surface, (255, 80, 0, int(alpha*0.7)), self.collision_pos, int(flash_radius*0.6))
            screen.blit(flash_surface, (0, 0))
        
        # Add time dilation indicator
        if self.time_dilation > 1.1:
            time_text = f"T×{self.time_dilation:.1f}"
            font = pygame.font.SysFont(None, 16)
            text = font.render(time_text, True, (255, 0, 0))
            screen.blit(text, (int(x - text.get_width()/2), int(y - self.radius - 15)))

def change_speed(factor):
    """
    Changes the simulation speed multiplier.
    """
    global speed_multiplier
    speed_multiplier = factor
    wait_for_key(f"Speed set to {factor}x. Press any key...")

def create_black_hole(pos):
    """
    Creates a new Black Hole at the specified position.
    """
    global black_hole
    black_hole = BlackHole(pos[0], pos[1], black_hole_size)
    wait_for_key("Black hole created! Press any key...")

def change_black_hole_size(delta):
    """
    Changes the size of the Black Hole.
    """
    global black_hole_size
    black_hole_size = max(10, min(50, black_hole_size + delta))
    wait_for_key(f"Black hole size: {black_hole_size}. Press any key...")

def reset_black_hole():
    """
    Resets the Black Hole to its initial state.
    """
    global black_hole
    black_hole = None
    wait_for_key("Black hole reset! Press any key...")

def reset_simulation():
    """
    Resets the simulation to its initial state (removes Black Hole, resets planets).
    """
    global black_hole
    black_hole = None
    sun.reset_position()
    for planet in planets:
        planet.reset_position()
    wait_for_key("Simulation reset! Press any key...")

class UIManager:
    """
    Manages the user interface, including drawing headers and saving/loading states.
    """
    def __init__(self, screen):
        self.screen = screen
        self.info_font = pygame.font.SysFont(None, 24)
        self.header_font = pygame.font.SysFont(None, 32)
        
    def draw_header(self):
        """
        Draws the header at the top of the screen.
        """
        # Pasek informacyjny z tłem
        pygame.draw.rect(self.screen, HEADER_BG, (0, 0, WIDTH, HEADER_HEIGHT))
        # Title
        author = self.header_font.render("Solar System Simulator - By Adrian Lesniak", True, HEADER_TEXT)
        self.screen.blit(author, (10, 10))
        # Description
        desc = self.info_font.render("A planetary system simulator with black hole, collisions, and time effects.", True, INFO_TEXT)
        self.screen.blit(desc, (10, 55))
        # Instruction (with extra margin)
        instruction = self.info_font.render("After each action, press any key to return to the menu.", True, INFO_TEXT)
        self.screen.blit(instruction, (10, 85))
        # Usunięto linię 'Menu options:' i listę opcji

    def save_state(self, planets, black_hole, sun):
        """
        Saves the current simulation state to a JSON file.
        """
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
            logger.info("Simulation state saved successfully")
            wait_for_key("State saved! Press any key...")
        except Exception as e:
            logger.error(f"Error saving state: {str(e)}")

    def load_state(self, planets, black_hole, sun):
        """
        Loads a simulation state from a JSON file.
        """
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
            
            logger.info("Simulation state loaded successfully")
            wait_for_key("State loaded! Press any key...")
            return black_hole
        except Exception as e:
            logger.error(f"Error loading state: {str(e)}")
            wait_for_key("Error loading state! Press any key...")
            return None

# Przesuń przyciski niżej (np. 30px od dołu okna)
BUTTON_Y_OFFSET = 30
BUTTON_HEIGHT = 30
BUTTON_MARGIN = 10

# Wylicz nową pozycję Y dla przycisków
def get_button_y(row=0):
    return HEIGHT - BUTTON_Y_OFFSET - (BUTTON_HEIGHT + BUTTON_MARGIN) * row

# Przypisz przyciski do dwóch rzędów
# Przyciski bez ikon
buttons = [
    Button(10, get_button_y(1), 120, BUTTON_HEIGHT, "Reset BH", reset_black_hole),
    Button(140, get_button_y(1), 30, BUTTON_HEIGHT, "-", lambda: change_black_hole_size(-5)),
    Button(180, get_button_y(1), 30, BUTTON_HEIGHT, "+", lambda: change_black_hole_size(5)),
    Button(220, get_button_y(1), 120, BUTTON_HEIGHT, "Reset All", reset_simulation),
    Button(400, get_button_y(1), 80, BUTTON_HEIGHT, "Save", lambda: ui_manager.save_state(planets, black_hole, sun)),
    Button(490, get_button_y(1), 80, BUTTON_HEIGHT, "Load", lambda: setattr(globals(), 'black_hole', ui_manager.load_state(planets, black_hole, sun))),
    Button(10, get_button_y(0), 80, BUTTON_HEIGHT, "0.5x", lambda: change_speed(0.5)),
    Button(100, get_button_y(0), 80, BUTTON_HEIGHT, "1x", lambda: change_speed(1.0)),
    Button(190, get_button_y(0), 80, BUTTON_HEIGHT, "2x", lambda: change_speed(2.0)),
    Button(280, get_button_y(0), 80, BUTTON_HEIGHT, "5x", lambda: change_speed(5.0))
]

# Add new buttons for save/load
# buttons.extend([
#     Button(400, HEIGHT-80, 80, 30, "Save", lambda: ui_manager.save_state(planets, black_hole, sun)),
#     Button(490, HEIGHT-80, 80, 30, "Load", lambda: setattr(globals(), 'black_hole', ui_manager.load_state(planets, black_hole, sun)))
# ])

# Create planets with adjusted distances and names
mercury = Planet(65, 5, GRAY, 0.24, "Mercury")
venus = Planet(95, 10, ORANGE, 0.62, "Venus")
earth = Planet(130, 12, BLUE, 1.0, "Earth")
mars = Planet(165, 8, RED, 1.88, "Mars")
jupiter = Planet(220, 25, BROWN, 11.86, "Jupiter")
saturn = Planet(280, 20, ORANGE, 29.46, "Saturn", True, (139, 69, 19))
uranus = Planet(330, 15, LIGHT_BLUE, 84.01, "Uranus")
neptune = Planet(380, 15, DARK_BLUE, 164.79, "Neptune")

planets = [mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]

# Create sun
sun = Sun(PANEL_CENTER_X, PANEL_CENTER_Y, 40)

# Create UI manager
ui_manager = UIManager(screen)

# Dodaj zmienną do przechowywania komunikatu o błędzie
error_message = None

# Add animated background with stars
def draw_starry_background(surface, star_list):
    surface.fill((0, 0, 20))
    for star in star_list:
        pygame.draw.circle(surface, (255, 255, 255), (int(star[0]), int(star[1])), star[2])
        star[0] += star[3]
        if star[0] > WIDTH:
            star[0] = 0
            star[1] = random.randint(0, HEIGHT)

# Initialize stars for background
star_list = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2), random.uniform(0.1, 0.5)] for _ in range(150)]

# Main game loop
running = True
clock = pygame.time.Clock()

def wait_for_key(message="Press any key to return to the menu..."):
    font = pygame.font.SysFont(None, 32)
    info = font.render(message, True, (80, 80, 200))
    screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        time.sleep(0.05)

while running:
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[1] < HEIGHT-100:  # Avoid buttons area
                    if event.button == 1:  # Left click
                        try:
                            create_black_hole(mouse_pos)
                        except Exception as e:
                            error_message = f"Error creating black hole: {str(e)}"
                            logger.error(error_message)
            # Handle button events
            for button in buttons:
                try:
                    button.handle_event(event)
                except Exception as e:
                    error_message = f"Error handling button event: {str(e)}"
                    logger.error(error_message)

        # Draw animated starry background first
        draw_starry_background(screen, star_list)

        # Draw a bright panel background and border for the simulation area
        panel_surface = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))
        panel_surface.fill((245, 245, 255))
        pygame.draw.rect(panel_surface, (200, 200, 220), (0, 0, PANEL_WIDTH, PANEL_HEIGHT), 4)
        screen.blit(panel_surface, (PANEL_LEFT, PANEL_TOP))

        try:
            screen.fill((0, 0, 0))
            # Draw header
            ui_manager.draw_header()
            # Draw indicators
            font = pygame.font.SysFont(None, 36)
            speed_text = font.render(f"Speed: {speed_multiplier}x", True, WHITE)
            bh_font = pygame.font.SysFont(None, 24)
            bh_text = bh_font.render(f"Black Hole Size: {black_hole_size}", True, WHITE)
            # Pozycje:
            speed_x = WIDTH - speed_text.get_width() - 20
            speed_y = HEIGHT - BUTTON_Y_OFFSET - BUTTON_HEIGHT*2 - 20
            bh_x = WIDTH - bh_text.get_width() - 20
            bh_y = speed_y - bh_text.get_height() - 10
            screen.blit(bh_text, (bh_x, bh_y))
            screen.blit(speed_text, (speed_x, speed_y))
        except Exception as e:
            error_message = f"Error drawing UI: {str(e)}"
            logger.error(error_message)

        # Check collisions between planets
        for i, planet1 in enumerate(planets):
            for planet2 in planets[i+1:]:
                try:
                    if planet1.check_collision(planet2):
                        planet1.collision_flash = 1.0
                        planet2.collision_flash = 1.0
                        # Transfer momentum
                        planet1.velocity_x = (planet1.velocity_x or 0) * -0.5
                        planet1.velocity_y = (planet1.velocity_y or 0) * -0.5
                        planet2.velocity_x = (planet2.velocity_x or 0) * -0.5
                        planet2.velocity_y = (planet2.velocity_y or 0) * -0.5
                except Exception as e:
                    error_message = f"Error handling planet collision: {str(e)}"
                    logger.error(error_message)

        # Update physics
        try:
            if sun.active:
                sun.affect_planets(planets)
        except Exception as e:
            error_message = f"Error affecting sun's gravity: {str(e)}"
            logger.error(error_message)
        # Inter-planetary gravity
        for i, planet1 in enumerate(planets):
            for planet2 in planets[i+1:]:
                try:
                    planet1.apply_gravity_to(planet2)
                except Exception as e:
                    error_message = f"Error handling inter-planetary gravity: {str(e)}"
                    logger.error(error_message)
        # Draw all objects
        try:
            if black_hole:
                black_hole.affect_sun(sun)
                sun.check_black_hole_interaction(black_hole)
                black_hole.draw(screen)
            sun.draw(screen)
            for planet in planets:
                planet.update(speed_multiplier, black_hole)
                planet.draw(screen, PANEL_CENTER_X, PANEL_CENTER_Y)
        except Exception as e:
            error_message = f"Error drawing objects: {str(e)}"
            logger.error(error_message)
        # Draw buttons last so they're always on top
        for button in buttons:
            try:
                button.draw(screen)
            except Exception as e:
                error_message = f"Error drawing button: {str(e)}"
                logger.error(error_message)
        # Wyświetl komunikat o błędzie na ekranie, jeśli wystąpił
        if error_message:
            err_font = pygame.font.SysFont(None, 28)
            err_text = err_font.render(error_message, True, (255, 80, 80))
            screen.blit(err_text, (10, HEIGHT-120))
        pygame.display.flip()
        clock.tick(60)
    except Exception as e:
        error_message = f"Critical error: {str(e)}"
        logger.critical(error_message)
        # Wyświetl błąd na ekranie
        screen.fill((255, 255, 255))
        err_font = pygame.font.SysFont(None, 36)
        err_text = err_font.render(error_message, True, (255, 0, 0))
        screen.blit(err_text, (10, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

pygame.quit()
