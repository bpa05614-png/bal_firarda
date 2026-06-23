import os
import json
import math
import random
import time

import pygame

import sys


# ============================================================
# Music (random from ./songs, auto-advance on end)
# ============================================================



def resource_path(relative):
    # Works for dev and for PyInstaller one-file/one-folder
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)

MUSIC_DIR = resource_path("songs")
MUSIC_EXTS = {".mp3", ".ogg", ".wav", ".flac"}
MUSIC_END_EVENT = pygame.USEREVENT + 77  # if you already use this, change 77 to another number





def _list_music_files(folder):
    if not os.path.isdir(folder):
        return []
    out = []
    for name in os.listdir(folder):
        p = os.path.join(folder, name)
        if os.path.isfile(p) and os.path.splitext(name)[1].lower() in MUSIC_EXTS:
            out.append(p)
    return sorted(out)


class RandomMusicPlayer:
    def __init__(self, folder, end_event=MUSIC_END_EVENT, volume=0.6):
        self.folder = folder
        self.tracks = _list_music_files(folder)
        self.last_track = None
        self.end_event = end_event

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception as e:
            print("[Music] Mixer init failed:", e)

        pygame.mixer.music.set_endevent(self.end_event)
        pygame.mixer.music.set_volume(volume)

        if not self.tracks:
            print(f"[Music] No tracks found in: {folder}")
        else:
            print(f"[Music] Found {len(self.tracks)} track(s) in: {folder}")

    def _pick_next(self):
        if not self.tracks:
            return None
        if len(self.tracks) == 1:
            return self.tracks[0]
        choices = [t for t in self.tracks if t != self.last_track]
        return random.choice(choices) if choices else random.choice(self.tracks)

    def play_next(self):
        nxt = self._pick_next()
        if not nxt:
            return
        try:
            pygame.mixer.music.load(nxt)
            pygame.mixer.music.play()
            self.last_track = nxt
        except Exception as e:
            print(f"[Music] Failed to play {nxt}: {e}")
            if nxt in self.tracks:
                self.tracks.remove(nxt)
            if self.tracks:
                self.play_next()

    def start(self):
        if self.tracks and not pygame.mixer.music.get_busy():
            self.play_next()

    def handle_event(self, event):
        if event.type == self.end_event:
            self.play_next()



GAME_TITLE = "Bal Firarda"
CAT_NAME = "Bal"

ELIF_SKY_MESSAGES = [
    "Elif, you are so important",
    "Elif, I’m so glad you exist",
    "Elif, you are truly beautiful",
    "Elif, your heart is full of kindness",
    "Elif, your smile lights up the world",
    "Elif, you are wonderfully sensitive",
    "Elif, you being yourself is amazing",
    "Elif, your courage is inspiring",
    "Elif, you are incredibly precious",
    "Elif, you have such a kind heart",
    "Elif, you're shining again today",
    "Elif, may all your dreams come true",
    "Elif, you're one of a kind",
    "Elif, Bal loves you so much",
    "Elif, Bal is lucky to have you as a mom",
    "Elif, ¿cómo te llamas?",
    "I’m so grateful to have you in my life",
    "Elif, be proud of yourself today",
    "Elif, protect your heart; it’s truly precious",
    "Elif, your presence is like light itself",
    "Elif, your grace is truly beautiful",
    "Elif, your gentle soul means so much",
    "Elif, you are the best thing that has happened to Bal",
    "Elif, your smile warms the heart",
    "Elif, your presence brings peace",
    "Elif, everything is better with you",
"Elif, the world is brighter because of you",
    "Elif, your kindness makes everything softer",
    "Elif, your voice brings calm like the wind",
    "Elif, you carry so much warmth inside you",
    "Elif, you matter more than words can say",
    "Elif, you turn ordinary days into magic",
    "Elif, your presence feels like home",
    "Elif, you make hearts feel safe",
    "Elif, your thoughts are gentle and deep",
    "Elif, your strength comes with grace",
    "Elif, thank you for being so genuine",
    "Elif, you are poetry in motion",
    "Elif, the stars would be proud of you",
    "Elif, you bring light just by being you",
    "Elif, your compassion is a gift to the world",
    "Elif, your dreams deserve to soar",
    "Elif, you're a quiet kind of magic",
    "Elif, even silence is beautiful with you",
    "Elif, your love leaves traces of joy",
    "Elif, your calm is contagious",
    "Elif, being near you feels like spring",
    "Elif, every little thing about you matters",
    "Elif, the world needs hearts like yours",
    "Elif, your wonder never goes unnoticed",
    "Elif, you are a gentle miracle",
    "Elif, even the moon would write songs for you if it could",
    "Elif, your soul leaves traces of light wherever you go",
    "Elif, your soul feels like a place one would never want to leave",

]

SKY_MSG_MAX_ACTIVE = 3
SKY_MSG_INTERVAL = (2.8, 4.8)          # keep your frequency

SKY_MSG_MIN_SCREEN_GAP = 520           # was 280
SKY_MSG_MIN_Y_GAP = 70                 # was 42

SKY_MSG_PAR_RANGE = (0.22, 0.27)       # was effectively ~0.18..0.30

SKY_MSG_SPAWN_OFF = (140, 360)         # was ~140..360



def lerp_color(a, b, t):
    return (int(lerp(a[0], b[0], t)), int(lerp(a[1], b[1], t)), int(lerp(a[2], b[2], t)))


def clamp(v, a, b): return max(a, min(b, v))


def lerp(a, b, t): return a + (b - a) * t


def ease_out_quad(t): return 1 - (1 - t) * (1 - t)


def seeded_rand(a, b, seed):
    r = random.Random(seed)
    return r.uniform(a, b)


def seeded_int(a, b, seed):
    r = random.Random(seed)
    return r.randint(a, b)


def approach(v, target, rate):
    if v < target: return min(target, v + rate)
    if v > target: return max(target, v - rate)
    return v


def draw_vertical_gradient(surf, top_color, bottom_color):
    w, h = surf.get_size()
    if h <= 1:
        surf.fill(top_color)
        return
    for y in range(h):
        t = y / (h - 1)
        r = int(lerp(top_color[0], bottom_color[0], t))
        g = int(lerp(top_color[1], bottom_color[1], t))
        b = int(lerp(top_color[2], bottom_color[2], t))
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))


def draw_vignette(surf, strength=0.42):
    w, h = surf.get_size()
    radius = int(math.hypot(w, h) * 0.6)
    center = (w // 2, h // 2)
    layers = 16
    for i in range(layers):
        t = i / (layers - 1)
        alpha = int(255 * strength * (t ** 2))
        color = (0, 0, 0, alpha)
        r = int(lerp(radius * 0.35, radius, t))
        ring = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(ring, color, (r, r), r)
        ring.set_alpha(alpha)
        surf.blit(ring, (center[0] - r, center[1] - r))


def drop_shadow_circle(dest, center, radius, color, shadow_alpha=70, offset=(0, 2)):
    sh = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, shadow_alpha), (radius + 4, radius + 4), radius)
    dest.blit(sh, (center[0] - radius + offset[0] - 4, center[1] - radius + offset[1] - 4))
    pygame.draw.circle(dest, color, center, radius)


def draw_speech_bubble(surf, x, y, text, font, alpha=255):
    """Draw a rounded speech bubble above (x,y) with a little tail."""
    txt = font.render(text, True, (40, 35, 50))
    pad = 10
    w, h = txt.get_width() + pad * 2, txt.get_height() + pad * 2
    bubble = pygame.Surface((w, h + 12), pygame.SRCALPHA)
    pygame.draw.rect(bubble, (255, 245, 235, alpha), (0, 0, w, h), border_radius=10)
    pygame.draw.rect(bubble, (200, 180, 170, alpha), (0, 0, w, h), 2, border_radius=10)
    # tail
    pygame.draw.polygon(bubble, (255, 245, 235, alpha), [(w // 2 - 8, h), (w // 2 + 8, h), (w // 2, h + 10)])
    pygame.draw.polygon(bubble, (200, 180, 170, alpha), [(w // 2 - 8, h), (w // 2 + 8, h), (w // 2, h + 10)], 2)
    bubble.blit(txt, (pad, pad))
    surf.blit(bubble, (int(x - w // 2), int(y - h - 16)))



class SkyMessage:
    """
    A floating sky text that fades in/out and drifts across the screen with parallax.
    We keep messages spaced apart using screen-space checks at spawn time.
    """
    def __init__(self, world_x, y, par, msg, font, ttl=12):
        self.x = float(world_x)
        self.y = float(y)
        self.par = float(par)
        self.msg = msg
        self.ttl = float(ttl)
        self.t = 0.0
        self.phase = random.random() * 10.0
        self.drift = random.uniform(-6.0, 6.0)  # gentle sideways drift

        # pre-render once; we only change alpha per frame
        self._txt = font.render(self.msg, True, (40, 40, 60))
        self._shd = font.render(self.msg, True, (255, 255, 255))
        self.w = self._txt.get_width()
        self.h = self._txt.get_height()


    def update(self, dt):
        self.t += dt
        self.x += self.drift * dt
        self.y += math.sin(self.t * 0.6 + self.phase) * 5.0 * dt
        return self.t >= self.ttl

    def _fade(self):
        if self.t < 0.8:
            return clamp(self.t / 0.8, 0, 1)
        if self.t > self.ttl - 1.2:
            return clamp((self.ttl - self.t) / 1.2, 0, 1)
        return 1.0

    def screen_x(self, cam_x, w):
        return self.x - cam_x * self.par + w * 0.5

    def draw(self, surf, cam_x, w):
        a = self._fade()
        if a <= 0:
            return

        sx = int(self.x - cam_x * self.par + w * 0.5)
        sy = int(self.y)

        if sx < -800 or sx > w + 800:
            return

        txt_alpha = int(220 * a)
        shd_alpha = int(240 * a)
        self._txt.set_alpha(txt_alpha)
        self._shd.set_alpha(shd_alpha)

        px = sx - self._txt.get_width() // 2
        py = sy - self._txt.get_height() // 2

        surf.blit(self._shd, (px, py + 1))
        surf.blit(self._txt, (px, py))

class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "color", "glow")

    def __init__(self, x, y, vx, vy, life, size, color, glow=False):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.glow = glow

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        return self.life <= 0

    def draw(self, surf):
        if self.life <= 0: return
        t = clamp(self.life / self.max_life, 0, 1)
        alpha = int(255 * t)
        c = (*self.color[:3], alpha)
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), max(1, int(self.size * (0.6 + 0.4 * t))))


# ============================================================
# Cute world props (themed)
# ============================================================
class Mushroom:
    # Bouncy pad
    def __init__(self, x, ground_y):
        self.x = x
        self.y = ground_y
        self.r = 18
        self.wobble = 0.0

    def draw(self, surf, screen_x, y_base, theme):
        if theme == "scifi":
            pad = pygame.Surface((64, 28), pygame.SRCALPHA)
            pygame.draw.ellipse(pad, (0, 255, 240, 60), (0, 0, 64, 16))
            pygame.draw.ellipse(pad, (0, 230, 255), (0, 0, 64, 16), 2)
            core = pygame.Surface((40, 16), pygame.SRCALPHA)
            pygame.draw.ellipse(core, (30, 50, 90), (0, 0, 40, 16))
            surf.blit(pad, (int(screen_x - 32), int(y_base - 16)))
            surf.blit(core, (int(screen_x - 20), int(y_base - 20)))
        elif theme == "medieval":
            # hay bale trampoline
            w, h = 70, 26
            bale = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(bale, (220, 190, 80), (0, 0, w, h), border_radius=6)
            pygame.draw.rect(bale, (160, 130, 60), (0, 0, w, h), 2, border_radius=6)
            for i in range(6, w, 10):
                pygame.draw.line(bale, (200, 170, 70), (i, 4), (i + 6, h - 4), 1)
            oy = int(self.wobble)
            surf.blit(bale, (int(screen_x - w // 2), int(y_base - h + oy)))
        else:
            pygame.draw.rect(surf, (210, 180, 150), (screen_x - 6, y_base - 26, 12, 26), border_radius=4)
            cap = pygame.Surface((self.r * 2 + 6, self.r + 12), pygame.SRCALPHA)
            pygame.draw.ellipse(cap, (255, 90, 120), (0, 0, self.r * 2 + 6, self.r + 10))
            pygame.draw.ellipse(cap, (180, 40, 70), (0, 0, self.r * 2 + 6, self.r + 10), 2)
            for dx in (-10, 0, 10):
                pygame.draw.circle(cap, (255, 230, 230), (self.r + 3 + dx, 12), 4)
            oy = int(self.wobble)
            surf.blit(cap, (screen_x - (self.r + 3), y_base - 36 + oy))

    def update(self, dt):
        self.wobble = approach(self.wobble, 0, 60 * dt)


class Trampoline:
    # Springier than mushroom
    def __init__(self, x, ground_y):
        self.x = x
        self.y = ground_y
        self.bounce = 0.0

    def draw(self, surf, screen_x, y_base, theme=None):
        w, h = 90, 18
        base = pygame.Surface((w, h + 12), pygame.SRCALPHA)
        pygame.draw.ellipse(base, (80, 80, 90), (0, h, w, 12))
        pygame.draw.rect(base, (220, 80, 120), (0, 0, w, h), border_radius=12)
        for i in range(8, w, 16):
            pygame.draw.line(base, (255, 190, 210), (i, 4), (i + 6, h - 4), 2)
        oy = int(-4 * math.sin(self.bounce * 6))
        surf.blit(base, (int(screen_x - w // 2), int(y_base - h + oy)))

    def pump(self):
        self.bounce = 1.0


class Puddle:
    # Slows and clears buffs
    def __init__(self, x, ground_y):
        self.x = x
        self.y = ground_y
        self.w = 80
        self.h = 12
        self.phase = random.random() * 10
        self.cooldown = 0.0

    def draw(self, surf, screen_x, y_base, t, theme=None):
        ripple = int(2 * math.sin(t * 3 + self.phase))
        col = (120, 160, 220);
        edge = (80, 120, 180)
        pygame.draw.ellipse(surf, col, (screen_x - self.w // 2, y_base - self.h + ripple, self.w, self.h))
        pygame.draw.ellipse(surf, edge, (screen_x - self.w // 2, y_base - self.h + ripple, self.w, self.h), 2)


class TeleportGate:
    def __init__(self, x, ground_y):
        self.x = x
        self.y = ground_y
        self.cooldown = 0.0
        self.phase = random.random() * 10

    def update(self, dt):
        self.cooldown = max(0.0, self.cooldown - dt)

    def draw(self, surf, screen_x, y_base, t, theme=None):
        r = 28
        ring = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        glow_base = (0, 240, 255)
        glow = int(120 + 80 * math.sin(t * 4 + self.phase))
        pygame.draw.circle(ring, (*glow_base, 60), (r + 4, r + 4), r + 4)
        pygame.draw.circle(ring, (*glow_base, glow), (r + 4, r + 4), r, 4)
        pygame.draw.circle(ring, (255, 255, 255, 120), (r + 4, r + 4), 6)
        surf.blit(ring, (int(screen_x - r - 4), int(y_base - 50 - r)))


# ============================================================
# Parallax flyers for background (butterflies & birds)
# ============================================================
class BgButterfly:
    def __init__(self, x, y, par, hue=(255, 150, 200), roam=28):
        # home (world) position – they’ll orbit this
        self.base_x, self.base_y = x, y
        self.x, self.y = x, y
        self.par = par
        self.t = random.random() * 20
        self.hue = hue
        self.roam = roam  # how far from home to wander

    def update(self, dt):
        self.t += dt * 2
        # bounded wander around home (no endless drift)
        self.x = self.base_x + math.cos(self.t * 0.7) * self.roam * 0.6 + math.sin(self.t * 1.1) * self.roam * 0.3
        self.y = self.base_y + math.sin(self.t * 2.0) * self.roam * 0.35

    def draw(self, surf, cam_x, w):
        sx = int(self.x - cam_x * self.par + w // 2)
        sy = int(self.y)
        flap = 6 + 4 * math.sin(self.t * 5)
        pygame.draw.line(surf, (80, 60, 90), (sx, sy), (sx, sy - 6), 2)
        pygame.draw.ellipse(surf, self.hue, (sx - 8, sy - 8 - flap * 0.1, 10, 7))
        pygame.draw.ellipse(surf, (180, 120, 200), (sx - 1, sy - 8 + flap * 0.1, 10, 7))


class BgBird:
    def __init__(self, x, y, par, speed, scale=1.0, color=(60, 60, 80)):
        self.x, self.y = x, y
        self.par = par
        self.speed = speed
        self.scale = scale
        self.t = random.random() * 10
        self.color = color

    def update(self, dt):
        self.t += dt
        self.x += self.speed * dt
        self.y += math.sin(self.t * 2) * 0.3

    def draw(self, surf, cam_x, w):
        sx = int(self.x - cam_x * self.par + w // 2)
        sy = int(self.y)
        s = self.scale
        pygame.draw.circle(surf, self.color, (sx, sy), int(3 * s))
        pygame.draw.polygon(surf, self.color, [(sx - 2, sy), (sx - 10, sy - 4), (sx - 6, sy + 2)])
        pygame.draw.polygon(surf, self.color, [(sx + 2, sy), (sx + 10, sy - 4), (sx + 6, sy + 2)])


# ============================================================
# Parallax Clouds
# ============================================================
class Cloud:
    def __init__(self, x, y, scale, speed):
        self.x, self.y = x, y
        self.scale = scale
        self.speed = speed
        self._sprite = None
        self._last_scale = None
        self._ensure_sprite()

    def _ensure_sprite(self):
        if self._last_scale != self.scale or self._sprite is None:
            s = int(80 * self.scale)
            surf = pygame.Surface((s * 3, s * 2), pygame.SRCALPHA)
            base = (255, 255, 255, 205)
            pygame.draw.circle(surf, base, (int(s * 0.6), int(s * 1.0)), int(s * 0.75))
            pygame.draw.circle(surf, base, (int(s * 1.2), int(s * 0.9)), int(s * 0.9))
            pygame.draw.circle(surf, base, (int(s * 1.8), int(s * 1.05)), int(s * 0.7))
            pygame.draw.circle(surf, base, (int(s * 1.3), int(s * 1.2)), int(s * 0.8))
            self._sprite = surf
            self._last_scale = self.scale

    def update(self, dt, camera_dx):
        self.x -= (self.speed + camera_dx * 0.08) * dt

    def draw(self, dest, cam_x, w):
        self._ensure_sprite()
        cx = int(self.x - cam_x + w // 2)
        dest.blit(self._sprite, (cx, int(self.y)))


# ============================================================
# Player Cat
# ============================================================
class PlayerCat:
    def __init__(self, x, ground_y):
        self.x = x
        self.y = ground_y
        self.vx = 0
        self.vy = 0
        self.ground_y = ground_y
        self.on_ground = True
        self.coyote = 0.0
        self.jump_buffer = 0.0
        self.jumps_left = 1
        self.facing = 1
        self.dash_time = 0.0
        self.invuln = 0.0
        self.anim_t = 0.0
        self.tail_wag_t = random.random() * 100
        self.blink_t = 0
        self.blink_interval = random.uniform(2.0, 4.0)
        self.blink_dur = 0.12
        self.just_jumped = False
        self.width = 56
        self.height = 48
        self.after = []  # afterimages
        self.sleeping = False

        # powers (shield removed)
        self.magnet = 0.0
        self.speed_boost = 0.0
        self.wings = 0.0  # double-jump + glide

    def give_power(self, tname, dur):
        if tname == "bell":
            self.magnet = max(self.magnet, dur)
        elif tname == "fish":
            self.speed_boost = max(self.speed_boost, dur)
        elif tname == "wings":
            self.wings = max(self.wings, dur)

    def update(self, dt, left, right, jump_held, dash_pressed, walk_mode=False):
        """
        Update player physics & state.
        - Normal mode: original movement (accel/decel, jump buffer + coyote, dash, powers).
        - Walk mode: only walking & sleeping are allowed. No jumping, dashing, or acceleration.
                     The cat walks at a constant gentle speed while holding left/right.
        """
        self.just_jumped = False

        # If sleeping, slowly settle and ignore inputs
        if self.sleeping:
            left = right = False
            jump_held = False
            dash_pressed = False
            if abs(self.vx) > 0:
                self.vx *= (1 - 6 * dt)

        # Timers (animations & blinking)
        self.anim_t += dt
        self.tail_wag_t += dt * 2.2
        self.blink_t += dt

        # Blinks (stay closed while sleeping)
        self.blinking = False
        if self.sleeping:
            self.blinking = True
        else:
            if self.blink_t >= self.blink_interval:
                self.blinking = True
                if self.blink_t >= self.blink_interval + self.blink_dur:
                    self.blink_t = 0
                    self.blink_interval = random.uniform(2.0, 4.0)

        # -------------------------------------------------------------------------
        # WALK MODE: override controls to allow only walking & sleeping
        # -------------------------------------------------------------------------
        if walk_mode:
            # Hard-disable jump/dash and speed/air-control powers
            jump_held = False
            dash_pressed = False
            self.dash_time = 0.0
            self.speed_boost = 0.0
            self.wings = 0.0
            # Clear jump-related helpers so there's no residual jump on toggle
            self.jump_buffer = 0.0
            self.coyote = 0.0
            self.jumps_left = 0

            # Constant-speed walk when holding a direction; quick stop when released
            WALK_SPEED = 160.0
            STOP_DECEL = 2400.0

            ix = (1 if right else 0) - (1 if left else 0)
            if ix != 0:
                self.facing = 1 if ix > 0 else -1
                self.vx = self.facing * WALK_SPEED
            else:
                if self.vx > 0:
                    self.vx = max(0.0, self.vx - STOP_DECEL * dt)
                elif self.vx < 0:
                    self.vx = min(0.0, self.vx + STOP_DECEL * dt)

            # Plain gravity; no glide, no extra jumps
            gravity = 1500
            self.vy += gravity * dt

            # Integrate
            self.x += self.vx * dt
            self.y += self.vy * dt

            # Ground clamp
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.vy = 0.0
                self.on_ground = True
            else:
                self.on_ground = False

            # Power timeouts (keep other timers draining)
            self.invuln = max(0.0, self.invuln - dt)
            self.magnet = max(0.0, self.magnet - dt)
            self.speed_boost = 0.0
            self.wings = 0.0

            # Afterimages disabled (none appended); keep existing ones fading
            self.after = [(x, y, a - dt) for (x, y, a) in self.after if a - dt > 0]
            return  # IMPORTANT: skip normal movement logic when in walk mode

        # -------------------------------------------------------------------------
        # NORMAL MODE (original behavior)
        # -------------------------------------------------------------------------
        # Movement feel
        base_max_vx = 260 + (100 if self.speed_boost > 0 else 0)
        acc = 1400
        decel = 1400
        gravity = 1500 if self.wings <= 0 else 1000
        jump_v = -520

        # Horizontal input
        ix = (1 if right else 0) - (1 if left else 0)

        if self.dash_time > 0:
            dash_dir = self.facing if ix == 0 else (1 if ix > 0 else -1)
            self.vx = dash_dir * (base_max_vx * 2.0)
            self.dash_time -= dt
        else:
            if ix != 0:
                self.facing = 1 if ix > 0 else -1
                self.vx = clamp(self.vx + ix * acc * dt, -base_max_vx, base_max_vx)
            else:
                if self.vx > 0:
                    self.vx = max(0, self.vx - decel * dt)
                elif self.vx < 0:
                    self.vx = min(0, self.vx + decel * dt)

        # Gravity + glide (hold jump with wings to float)
        self.vy += gravity * dt
        if self.wings > 0 and not self.on_ground and jump_held and self.vy > 0:
            self.vy -= 900 * dt  # glide updraft

        # Jump buffer & coyote
        if jump_held and not self.sleeping:
            self.jump_buffer = 0.12
        else:
            self.jump_buffer = max(0.0, self.jump_buffer - dt)

        max_jumps = 2 if self.wings > 0 else 1
        if self.on_ground:
            self.coyote = 0.12
            self.jumps_left = max_jumps
        else:
            self.coyote = max(0.0, self.coyote - dt)

        if (not self.sleeping) and self.jump_buffer > 0 and (self.coyote > 0 or self.jumps_left > 0):
            self.vy = jump_v
            if not self.on_ground:
                self.jumps_left -= 1
            self.on_ground = False
            self.just_jumped = True
            self.jump_buffer = 0

        # Dash
        if (not self.sleeping) and dash_pressed and self.dash_time <= 0:
            self.dash_time = 0.18
            self.invuln = 0.18

        # Power timeouts
        self.invuln = max(0.0, self.invuln - dt)
        self.magnet = max(0.0, self.magnet - dt)
        self.speed_boost = max(0.0, self.speed_boost - dt)
        self.wings = max(0.0, self.wings - dt)

        # Integrate
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Ground
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Afterimage during dash/speed
        if self.dash_time > 0 or self.speed_boost > 0:
            self.after.append((self.x, self.y, 0.25))
        self.after = [(x, y, a - dt) for (x, y, a) in self.after if a - dt > 0]

    def draw(self, surf, theme, offset=(0, 0)):
        x = int(self.x + offset[0]); y = int(self.y + offset[1])

        # Single cozy palette (theme is ignored)
        fur = (250, 197, 160)
        outline = (160, 120, 95)
        ear_in = (255, 179, 200)
        eye = (40, 50, 60)
        accent = (255, 170, 170, 120)
        scarf = (255, 120, 120)

        # Shadow
        shadow = pygame.Surface((80, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80), (0, 0, 80, 24))
        surf.blit(shadow, (x - 40, y - 6))

        # Afterimages (soft)
        for ax, ay, a in self.after:
            a = clamp(a * 3, 0, 1)
            ghost = pygame.Surface((72, 72), pygame.SRCALPHA)
            pygame.draw.circle(ghost, (255, 255, 255, int(40 * a)), (36, 36), 28)
            surf.blit(ghost, (int(ax - 36 + offset[0]), int(ay - 56 + offset[1])), special_flags=pygame.BLEND_ADD)
        # Tail sway (draw pointing to the right, then flip if needed)
        # Tail sway (draw pointing to the right, then flip if needed)
        sway = math.sin(self.tail_wag_t * 2.2) * 10
        tail_len = 28

        # Smaller surface, no offset drawing
        tail = pygame.Surface((tail_len, 18), pygame.SRCALPHA)

        pts = [(0, 9),
               (tail_len * 0.3, 9 + sway * 0.1),
               (tail_len * 0.6, 9 + sway * 0.2),
               (tail_len, 9 + sway * 0.35)]
        pygame.draw.lines(tail, outline, False, pts, 6)
        pygame.draw.lines(tail, fur, False, pts, 4)

        # Flip tail for correct side
        if self.facing == 1:  # right
            tail = pygame.transform.flip(tail, True, False)
            tail_x = x - self.width // 2 - tail_len + 2  # tightly sticks to left
        else:  # left
            tail_x = x + self.width // 2 - 2  # tightly sticks to right

        surf.blit(tail, (int(tail_x), int(y - 26)))

        # Body
        body_w, body_h = 52, 30
        body = pygame.Surface((body_w, body_h), pygame.SRCALPHA)
        pygame.draw.ellipse(body, fur, (0, 0, body_w, body_h))
        pygame.draw.ellipse(body, outline, (0, 0, body_w, body_h), 2)
        pygame.draw.rect(body, scarf, (8, 8, 36, 8), border_radius=6)

        if theme == "scifi":
            pygame.draw.line(body, (0, 255, 240), (10, 10), (42, 12), 3)
            pygame.draw.line(body, (0, 200, 255), (12, 18), (30, 20), 2)
        elif theme == "medieval":
            pygame.draw.line(body, (110, 90, 70), (8, 16), (44, 16), 3)
            pygame.draw.circle(body, (100, 80, 60), (8, 10), 3)

        surf.blit(body, (x - body_w // 2, y - body_h - 4))

        # Head
        head_r = 20
        head = pygame.Surface((head_r * 2 + 2, head_r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(head, fur, (head_r + 1, head_r + 1), head_r)
        pygame.draw.circle(head, outline, (head_r + 1, head_r + 1), head_r, 2)

        # Ears
        ear_left = [(head_r - 8, head_r - 6), (head_r - 16, head_r - 18), (head_r - 2, head_r - 14)]
        ear_right = [(head_r + 8, head_r - 6), (head_r + 2, head_r - 14), (head_r + 16, head_r - 18)]
        pygame.draw.polygon(head, fur, ear_left);
        pygame.draw.polygon(head, outline, ear_left, 2)
        pygame.draw.polygon(head, fur, ear_right);
        pygame.draw.polygon(head, outline, ear_right, 2)
        pygame.draw.polygon(head, ear_in, [(p[0] * 0.98 + 1, p[1] * 0.98 + 1) for p in ear_left])
        pygame.draw.polygon(head, ear_in, [(p[0] * 0.98 + 1, p[1] * 0.98 + 1) for p in ear_right])

        # Face
        eye_y = head_r
        eye_dx = 8
        if getattr(self, 'blinking', False):
            # closed eyes
            pygame.draw.line(head, eye, (head_r - eye_dx - 1, eye_y), (head_r - eye_dx + 5, eye_y), 2)
            pygame.draw.line(head, eye, (head_r + eye_dx - 5, eye_y), (head_r + eye_dx + 1, eye_y), 2)
        else:
            if theme == "scifi":
                pygame.draw.rect(head, (0, 210, 255), (head_r - 12, eye_y - 5, 24, 10), border_radius=5)
                pygame.draw.rect(head, (0, 255, 240), (head_r - 12, eye_y - 5, 24, 10), 2, border_radius=5)
                pygame.draw.circle(head, (255, 255, 255), (head_r - 4, eye_y - 1), 1)
                pygame.draw.circle(head, (255, 255, 255), (head_r + 4, eye_y - 1), 1)
            else:
                pygame.draw.circle(head, eye, (head_r - eye_dx, eye_y), 3)
                pygame.draw.circle(head, eye, (head_r + eye_dx, eye_y), 3)
                pygame.draw.circle(head, (255, 255, 255), (head_r - eye_dx + 1, eye_y - 1), 1)
                pygame.draw.circle(head, (255, 255, 255), (head_r + eye_dx + 1, eye_y - 1), 1)

        # Nose & mouth
        pygame.draw.circle(head, (255, 140, 140), (head_r, head_r + 4), 2)
        pygame.draw.line(head, eye, (head_r, head_r + 4), (head_r, head_r + 8), 1)
        pygame.draw.line(head, eye, (head_r, head_r + 8), (head_r - 4, head_r + 10), 1)
        pygame.draw.line(head, eye, (head_r, head_r + 8), (head_r + 4, head_r + 10), 1)

        # Helmet band / blush
        if theme == "medieval":
            pygame.draw.rect(head, (120, 100, 80), (head_r - 18, head_r - 14, 36, 8), border_radius=4)
        blush_s = pygame.Surface((24, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(blush_s, accent, (0, 0, 24, 14))
        head.blit(blush_s, (head_r - 20, head_r + 4))
        head.blit(blush_s, (head_r, head_r + 4))

        # Wings visual when active
        if self.wings > 0:
            wing = pygame.Surface((36, 20), pygame.SRCALPHA)
            pygame.draw.polygon(wing, (255, 255, 255, 160), [(2, 18), (34, 10), (20, 2), (8, 8)])
            surf.blit(wing, (x - 16, y - 54))

        # Place head
        head_x = x + (10 if self.facing == 1 else -10) - (head_r + 1)
        head_y = y - 30 - head_r - 8
        surf.blit(head, (head_x, head_y))

        # Feet dots
        foot_y = y - 8
        pygame.draw.circle(surf, outline, (x - 12, foot_y), 2)
        pygame.draw.circle(surf, outline, (x + 12, foot_y), 2)


# ============================================================
# Collectibles & PowerUps
# ============================================================
class Coin:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0
        self.t = random.random() * 6

    def update(self, dt, cat):
        self.t += dt * 4
        self.y += math.sin(self.t) * 0.2
        if cat.magnet > 0:
            dx = cat.x - self.x
            dy = (cat.y - 30) - self.y
            dist = math.hypot(dx, dy)
            if dist < 260:
                pull = (260 - dist) * 3.2
                self.vx += (dx / dist if dist > 1 else 0) * pull * dt
                self.vy += (dy / dist if dist > 1 else 0) * pull * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= (1 - 4 * dt)
        self.vy *= (1 - 4 * dt)

    def draw(self, surf, screen_x, _y):
        # gold coin
        base = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(base, (255, 215, 80), (12, 12), 11)
        pygame.draw.circle(base, (200, 160, 60), (12, 12), 11, 2)
        pygame.draw.circle(base, (255, 255, 200, 180), (8, 8), 4)
        surf.blit(base, (int(screen_x - 12), int(self.y - 28)))


class PowerUp:
    def __init__(self, x, y, kind):
        self.x, self.y = x, y
        self.kind = kind  # 'bell', 'fish', 'wings'
        self.t = random.random() * 6

    def draw(self, surf, screen_x, y):
        base = pygame.Surface((28, 28), pygame.SRCALPHA)
        col = {"bell": (255, 210, 0), "fish": (110, 200, 255), "wings": (255, 255, 255)}[self.kind]
        pygame.draw.circle(base, (*col, 200), (14, 14), 14)
        pygame.draw.circle(base, (255, 255, 255, 60), (10, 10), 6)
        if self.kind == "bell":
            pygame.draw.arc(base, (120, 90, 0), (6, 8, 16, 12), 3.4, 6.0, 3)
            pygame.draw.circle(base, (120, 90, 0), (14, 20), 2)
        elif self.kind == "fish":
            pygame.draw.polygon(base, (20, 100, 160), [(6, 18), (22, 14), (6, 10)])
            pygame.draw.circle(base, (255, 255, 255), (9, 14), 2)
        else:
            pygame.draw.polygon(base, (200, 200, 255), [(6, 18), (14, 8), (22, 18)])
            pygame.draw.line(base, (160, 160, 200), (10, 14), (18, 14), 2)
        oy = int(3 * math.sin(self.t))
        surf.blit(base, (int(screen_x - 14), int(self.y - 30 + oy)))


# ============================================================
# Backgrounds (3 themes) + Day/Night
# ============================================================
def day_night_colors(t):
    def mix(a, b, u):
        return tuple(int(lerp(a[i], b[i], u)) for i in range(3))

    if t < 0.25:  # dawn→day
        u = (t - 0.00) / 0.25;
        top = mix((255, 200, 170), (180, 215, 255), u);
        bot = mix((255, 170, 200), (255, 230, 245), u)
    elif t < 0.5:  # day→golden
        u = (t - 0.25) / 0.25;
        top = mix((180, 215, 255), (255, 190, 160), u);
        bot = mix((255, 230, 245), (255, 150, 160), u)
    elif t < 0.75:  # golden→dusk
        u = (t - 0.5) / 0.25;
        top = mix((255, 190, 160), (80, 70, 100), u);
        bot = mix((255, 150, 160), (25, 20, 30), u)
    else:  # dusk→dawn
        u = (t - 0.75) / 0.25;
        top = mix((80, 70, 100), (255, 200, 170), u);
        bot = mix((25, 20, 30), (255, 170, 200), u)
    return top, bot


# ============================================================
# Sky decorations
# ============================================================
class BirdFlock:
    """Simple cohesive flock with a species look."""
    SPECIES = {
        "swallow": ((60, 60, 80), 0.9),
        "goose": ((90, 90, 110), 1.2),
        "seagull": ((200, 200, 220), 1.0),
        "sparrow": ((80, 70, 70), 0.7),
    }

    def __init__(self, x, y, par=0.24, speed=26, n=8, species="swallow"):
        self.x, self.y = x, y
        self.par = par
        self.base_speed = speed
        self.t = random.random() * 10
        self.members = [(random.uniform(-36, 36), random.uniform(-16, 16)) for _ in range(n)]
        self.species = species if species in self.SPECIES else "swallow"
        self.color, self.scale = self.SPECIES[self.species]

    def update(self, dt):
        self.t += dt
        drift = math.sin(self.t * 0.7) * 4
        self.x += (self.base_speed + 6 * math.sin(self.t * 0.4)) * dt
        self.y += math.sin(self.t * 0.9) * dt * 10
        # light cohesion flutter
        self.members = [
            (ox + math.sin(self.t * 2 + i) * 4 * dt, oy + math.cos(self.t * 1.6 + i) * 3 * dt)
            for i, (ox, oy) in enumerate(self.members)
        ]

    def _draw_member(self, surf, sx, sy, a):
        s = self.scale
        if self.species == "goose":
            # body + long neck + wings
            pygame.draw.ellipse(surf, self.color, (sx - 6 * s, sy - 3 * s, 12 * s, 6 * s))
            pygame.draw.line(surf, self.color, (sx + 5 * s, sy - 2 * s), (sx + 10 * s, sy - 5 * s), int(2 * s))
            flap = math.sin(a) * 4 * s
            pygame.draw.polygon(surf, self.color,
                                [(sx - 1 * s, sy - 1 * s), (sx - 10 * s, sy - 6 * s - flap), (sx - 6 * s, sy + 1 * s)])
            pygame.draw.polygon(surf, self.color,
                                [(sx + 1 * s, sy - 1 * s), (sx + 10 * s, sy - 6 * s + flap), (sx + 6 * s, sy + 1 * s)])
        elif self.species == "seagull":
            wing = 8 * s + 3 * math.sin(a)
            pygame.draw.lines(surf, self.color, False, [(sx - wing, sy), (sx, sy - 3 * s), (sx + wing, sy)], int(2 * s))
        else:
            # swallow/sparrow "V"
            wing = 9 * s + 3 * math.sin(a)
            pygame.draw.line(surf, self.color, (sx, sy), (sx - wing, sy - 3 * s), int(2 * s))
            pygame.draw.line(surf, self.color, (sx, sy), (sx + wing, sy - 3 * s), int(2 * s))

    def draw(self, surf, cam_x, w):
        a = self.t * 4
        sx0 = int(self.x - cam_x * self.par + w // 2)
        sy0 = int(self.y)
        for i, (ox, oy) in enumerate(self.members):
            self._draw_member(surf, sx0 + int(ox), sy0 + int(oy), a + i * 0.3)


class CottageHouse:
    """Tiny cozy cottages with per-house variation so same-style homes look different."""

    def __init__(self, rng, style="tudor"):
        self.style = style
        self.rng = rng
        self.sprite = self._build(style)

    def _darker(self, c, amt=40):
        return (max(0, c[0] - amt), max(0, c[1] - amt), max(0, c[2] - amt))

    def _build(self, style):
        R = self.rng
        px = 2
        cols, rows = 64, 56
        surf = pygame.Surface((cols * px, rows * px), pygame.SRCALPHA)

        def put(x, y, c, w=1, h=1):
            pygame.draw.rect(surf, c, (x * px, y * px, px * w, px * h))

        # --- palettes ---------------------------------------------------------
        roof_main = R.choice([(180, 70, 60), (160, 90, 60), (180, 120, 70), (140, 70, 120), (110, 80, 140)])
        roof_shadow = self._darker(roof_main, 40)
        wall_main = R.choice([(240, 228, 210), (226, 214, 196), (232, 222, 206), (214, 202, 186)])
        wall_line = (130, 110, 95)
        timber = (100, 70, 55)
        stone = (160, 150, 140)
        plank_dark = (130, 110, 95)
        shadow = (90, 80, 70)

        # --- geometry (per-house) -------------------------------------------
        x0, y0 = 8, 20
        w = R.randint(36, 44)  # varied width
        h = R.randint(20, 26)  # varied height
        door_w = R.randint(5, 7)
        door_h = R.randint(8, 10)
        door_dx = R.randint(-5, 5)  # door offset from center

        # roof variants
        roof_type = R.choice(["gable", "hip"])  # lightweight variants
        roof_h = R.randint(10, 14)  # roof height variance

        # --- walls ------------------------------------------------------------
        pygame.draw.rect(surf, wall_main, (x0 * px, y0 * px, w * px, h * px))
        pygame.draw.rect(surf, (120, 100, 90), (x0 * px, y0 * px, w * px, h * px), 2)

        # material/style details on walls
        if style in ("tudor", "fairytale"):
            # pick a tudor beam pattern variant
            pattern = R.choice(["cross", "diag", "grid"])
            # horizontal mid beam
            pygame.draw.line(surf, timber, (x0 * px, (y0 + 8) * px), ((x0 + w) * px, (y0 + 8) * px), 3)
            # vertical center or offset
            cx = x0 + w // 2 + R.randint(-1, 1)
            pygame.draw.line(surf, timber, (cx * px, y0 * px), (cx * px, (y0 + h) * px), 3)
            if pattern in ("cross", "diag"):
                pygame.draw.line(surf, timber, (x0 * px, y0 * px), ((x0 + 8) * px, (y0 + 10) * px), 3)
                pygame.draw.line(surf, timber, (((x0 + w) - 1) * px, y0 * px), (((x0 + w) - 10) * px, (y0 + 10) * px),
                                 3)
            if pattern == "grid":
                step = 10
                for gx in range(x0 + step, x0 + w, step):
                    pygame.draw.line(surf, timber, (gx * px, (y0 + 2) * px), (gx * px, (y0 + h - 2) * px), 2)
        elif style == "stone":
            # random stones density variant
            for _ in range(R.randint(60, 120)):
                sx = R.randint(x0 + 1, x0 + w - 2);
                sy = R.randint(y0 + 1, y0 + h - 2)
                tint = self._darker(stone, R.randint(-10, 20))
                put(sx, sy, tint)
        elif style == "wood":
            # vertical planks
            for ix in range(x0 + 2, x0 + w - 1, R.choice([2, 3])):
                pygame.draw.line(surf, plank_dark, (ix * px, (y0 + 1) * px), (ix * px, (y0 + h - 2) * px), 1)

        # --- door -------------------------------------------------------------
        dx = x0 + w // 2 + door_dx - door_w // 2
        dy = y0 + h - door_h
        door_col = R.choice([(125, 75, 58), (110, 70, 55), (140, 90, 70)])
        pygame.draw.rect(surf, door_col, (dx * px, dy * px, door_w * px, door_h * px))
        pygame.draw.rect(surf, self._darker(door_col, 50), (dx * px, dy * px, door_w * px, door_h * px), 2)
        # knob
        put(dx + door_w - 2, dy + door_h // 2, (240, 210, 120), 1, 1)
        # optional tiny step/stone
        if R.random() < 0.6:
            pygame.draw.rect(surf, (140, 130, 120), ((dx - 1) * px, (dy + door_h) * px, (door_w + 2) * px, 2))

        # --- windows (varied shape/pos; right window shifted left) -----------
        def draw_window(wx, wy, ww, wh, arched=False, shutters=False):
            glass = (200, 225, 255)
            frame = (90, 80, 75)
            rect = pygame.Rect(wx * px, wy * px, ww * px, wh * px)
            if arched:
                pygame.draw.rect(surf, glass, rect, border_radius=ww // 2)
                pygame.draw.rect(surf, frame, rect, 2, border_radius=ww // 2)
            else:
                pygame.draw.rect(surf, glass, rect, border_radius=3)
                pygame.draw.rect(surf, frame, rect, 2, border_radius=3)
            # tiny highlight
            put(wx + ww // 2, wy, (230, 250, 255), 1, 1)
            # shutters (optional)
            if shutters:
                sh_w = max(2, ww // 3)
                sh_col = self._darker(wall_main, 40)
                pygame.draw.rect(surf, sh_col, ((wx - sh_w) * px, wy * px, sh_w * px, wh * px))
                pygame.draw.rect(surf, sh_col, (((wx + ww)) * px, wy * px, sh_w * px, wh * px))

        ww = R.choice([9, 10, 11])
        wh = R.choice([7, 8])
        wy = y0 + R.randint(5, 8)
        # left window with slight jitter
        wx_left = x0 + R.randint(4, 8)
        draw_window(wx_left, wy, ww, wh,
                    arched=(style in ("fairytale", "tudor") and R.random() < 0.5),
                    shutters=(R.random() < 0.35))

        # RIGHT WINDOW: shift a bit to the LEFT vs old code (w-12) + jitter
        right_shift = R.randint(14, 17)  # was fixed 12 -> now 14..17 (further left)
        wx_right = x0 + w - right_shift
        # keep some jitter so houses differ
        wx_right += R.randint(-1, 1)
        draw_window(wx_right, wy, ww, wh,
                    arched=(style in ("fairytale", "tudor") and R.random() < 0.5),
                    shutters=(R.random() < 0.35))

        # optional third tiny attic window (dormer on gable only)
        if roof_type == "gable" and R.random() < 0.35:
            ax = x0 + w // 2 + R.randint(-3, 3)
            ay = y0 - roof_h + R.randint(3, 5)
            draw_window(ax, ay, 6, 6, arched=True, shutters=False)

        # --- roof -------------------------------------------------------------
        rx0 = x0 - 2
        if roof_type == "gable":
            pts = [((rx0) * px, (y0) * px),
                   (((x0 + w + 2)) * px, (y0) * px),
                   (((x0 + w // 2)) * px, (y0 - roof_h) * px)]
            pygame.draw.polygon(surf, roof_main, pts)
            pygame.draw.polygon(surf, (80, 60, 55), pts, 2)
        else:  # hip (simple trapezoid look)
            top_l = x0 + R.randint(6, 10)
            top_r = x0 + w - R.randint(6, 10)
            pts = [((rx0) * px, (y0) * px),
                   (((x0 + w + 2)) * px, (y0) * px),
                   (top_r * px, (y0 - roof_h) * px),
                   (top_l * px, (y0 - roof_h) * px)]
            pygame.draw.polygon(surf, roof_main, pts)
            pygame.draw.polygon(surf, (80, 60, 55), pts, 2)

        # roof shading strips
        for i in range(6):
            t = i / 6
            cx = int(lerp(rx0, x0 + w + 2, t))
            pygame.draw.line(surf, roof_shadow,
                             (cx * px, (y0 - 1) * px),
                             ((x0 + w // 2) * px, (y0 - roof_h + 1) * px), 1)

        # --- chimney (pos/height vary) ---------------------------------------
        if R.random() < 0.9:
            on_left = R.random() < 0.45
            cx = (x0 + (6 if on_left else w - 6))
            ch = R.randint(6, 10)
            pygame.draw.rect(surf, (120, 90, 80), (cx * px, (y0 - roof_h + 4) * px, 4 * px, ch * px))
            pygame.draw.rect(surf, (70, 50, 45), (cx * px, (y0 - roof_h + 4) * px, 4 * px, ch * px), 2)
            for k in range(R.randint(2, 4)):
                r = 3 - k
                pygame.draw.circle(
                    surf, (255, 255, 255, R.randint(150, 200)),
                    (int((cx + 2) * px), int((y0 - roof_h - 2 - k * 3) * px)), max(1, r)
                )

        # --- flowers / shrubs -------------------------------------------------
        base_y = y0 + h
        for b in range(R.randint(2, 4)):
            bx = x0 + R.randint(3, w - 6)
            col = R.choice([(255, 160, 190), (255, 200, 120), (160, 210, 120), (170, 170, 255)])
            pygame.draw.ellipse(surf, (90, 130, 90), ((bx - 4) * px, (base_y - 4) * px, 10 * px, 6 * px))
            pygame.draw.circle(surf, col, ((bx) * px, (base_y - 1) * px), 3)

        # light ground shadow
        sh = pygame.Surface((cols * px, rows * px), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 60), ((x0 + 8) * px, (base_y + 4) * px, int((w * 0.65)) * px, 6 * px))
        surf.blit(sh, (0, 0))

        # small dormer accent for "fairytale" (sometimes a little ridge cap)
        if style == "fairytale" and roof_type == "gable" and R.random() < 0.4:
            ridge_x = x0 + w // 2
            pygame.draw.rect(surf, self._darker(roof_main, 25), ((ridge_x - 1) * px, (y0 - roof_h - 1) * px, 2 * px, 4))

        # final scale jitter for non-identical silhouette
        scale_j = 1.0 + R.uniform(-0.03, 0.12)
        sp = pygame.transform.scale(
            surf,
            (max(1, int(surf.get_width() * scale_j)),
             max(1, int(surf.get_height() * scale_j)))
        )
        return sp


class HumanNPC:
    """
    Tiny pixel humans with genders & simple sprite-based animations.
    States: idle, wave, dance, walk, run, jump (hands up), fall, kiss
    """

    def __init__(self, game, world_x, ground_y, style="adult", facing=1, par=0.40, roam=36):
        self.g = game
        self.world_x = world_x
        self.home_x = world_x
        self.ground_y = ground_y
        self.par = par
        self.facing = 1 if facing >= 0 else -1

        # ---- new: genders (back-compat for style="adult"/"child") ----
        if style in ("man", "woman", "child"):
            self.kind = style
        elif style == "child":
            self.kind = "child"
        elif style == "adult":
            self.kind = random.choice(["man", "woman"])
        else:
            self.kind = "man"

        # motion/animation
        self.vx = 0.0
        self.vy = 0.0
        self.oy = 0.0  # vertical offset for jumping/falling
        self.on_ground = True
        self.gravity = 520.0
        self.roam = max(0, roam)  # how far left/right from home they may wander

        self.state = "idle"
        self.next_change = 0.0
        self.frame_i = 0
        self.frame_t = 0.0
        self.t = random.random() * 10

        # speech / greetings
        self.cooldown = 0.0
        self.say_ttl = 0.0
        self.say_text = ""

        # couple/kissing hook (set by spawner)
        self.partner = None  # -> other HumanNPC
        self._kiss_t = 0.0

        # palette & frames
        self._seed_colors()
        self.frames = self._make_frames()  # dict[str] -> [Surface,...]
        # default sprite size
        sp = self.frames["idle"][0]
        self.w, self.h = sp.get_width(), sp.get_height()

    # ---------- palettes ----------
    def _seed_colors(self):
        rng = random.Random((id(self) ^ int(self.world_x * 7)) & 0x7fffffff)
        # skin & hair ranges
        self.skin = rng.choice([(243, 213, 183), (222, 184, 146), (185, 140, 111), (146, 110, 86)])
        self.hair = rng.choice(
            [(40, 35, 30), (30, 30, 35), (100, 60, 30), (130, 80, 50), (20, 20, 20), (155, 120, 70), (80, 50, 20)])
        # outfit
        if self.kind == "woman" and rng.random() < 0.55:
            self.outfit = "dress"
            self.top = rng.choice([(255, 160, 190), (180, 170, 240), (120, 180, 255), (160, 210, 170), (255, 210, 120)])
            self.bottom = None
        else:
            self.outfit = "separates"
            self.top = rng.choice([(120, 180, 255), (255, 160, 145), (255, 210, 120), (160, 210, 170), (180, 170, 240)])
            self.bottom = rng.choice([(70, 80, 120), (120, 90, 70), (80, 120, 90), (140, 140, 160)])
        self.shoe = (50, 45, 55)
        self.outline = (40, 35, 45)

    # ---------- sprite builder ----------
    def _build_sprite(self, pose="idle", flip=False):
        """
        Builds a small pixel sprite for current palette and a pose key.
        Pose keys: idle, wave0, wave1, danceL, danceR, walk0, walk1, run0, run1, jump, fall, kiss
        """
        # sizes tuned vs the cat
        if self.kind == "child":
            cols, rows, px = 12, 22, 2
            head_h = 6
        else:
            cols, rows, px = 14, 28, 2
            head_h = 7

        surf = pygame.Surface((cols * px, rows * px), pygame.SRCALPHA)

        def p(x, y, c, w=1, h=1):
            pygame.draw.rect(surf, c, (x * px, y * px, px * w, px * h))

        cx = cols // 2

        # --- head + hair ---
        for y in range(2, 2 + head_h):
            for x in range(cx - 3, cx + 3):
                p(x, y, self.skin)
        # hair cap / long hair (women get a bit longer)
        for x in range(cx - 3, cx + 3): p(x, 2, self.hair)
        if self.kind == "woman":
            for y in range(3, 3 + (2 if self.kind == "child" else 3)):
                p(cx - 4, y, self.hair);
                p(cx + 3, y, self.hair)
        # eyes (closed if kiss)
        if pose == "kiss":
            p(cx - 2, 4, (20, 25, 35));
            p(cx + 1, 4, (20, 25, 35))
            # tiny lids (lines) for cutesy look
            pygame.draw.line(surf, (20, 25, 35), ((cx - 2) * px, (4) * px), ((cx + 2) * px, (4) * px), 1)
        else:
            p(cx - 2, 4, (20, 25, 35));
            p(cx + 1, 4, (20, 25, 35))

        # --- body (top) ---
        top_y = 2 + head_h
        if self.outfit == "dress":
            # bodice
            for y in range(top_y, top_y + 7):
                for x in range(cx - 3, cx + 3): p(x, y, self.top)
            # skirt flare
            for y in range(top_y + 7, rows - 3):
                for x in range(cx - 4, cx + 4): p(x, y, self.top)
                if y % 2 == 0: p(cx - 5, y, self.top); p(cx + 4, y, self.top)
        else:
            for y in range(top_y, top_y + 7):
                for x in range(cx - 3, cx + 3): p(x, y, self.top)

        # --- legs / pants (or lower dress shading) ---
        leg_top = top_y + 7

        def legs(style):
            if self.outfit == "dress":
                # peek shoes only
                p(cx - 3, rows - 2, self.shoe, 2, 1)
                p(cx + 1, rows - 2, self.shoe, 2, 1)
                return
            # pants legs
            if style == "together":
                for y in range(leg_top, rows - 2):
                    p(cx - 1, y, self.bottom);
                    p(cx, y, self.bottom)
            elif style == "apartL":
                for y in range(leg_top, rows - 2):
                    p(cx - 2, y, self.bottom);
                    p(cx + 1, y, self.bottom)
            elif style == "apartR":
                for y in range(leg_top, rows - 2):
                    p(cx - 3, y, self.bottom);
                    p(cx + 2, y, self.bottom)
            elif style == "runL":
                for y in range(leg_top, rows - 2):
                    p(cx - 3, y, self.bottom);
                    p(cx, y, self.bottom)
            elif style == "runR":
                for y in range(leg_top, rows - 2):
                    p(cx - 1, y, self.bottom);
                    p(cx + 2, y, self.bottom)
            elif style == "jump":
                for y in range(leg_top, rows - 3):
                    p(cx - 1, y, self.bottom);
                    p(cx, y, self.bottom)
            elif style == "fall":
                for y in range(leg_top, rows - 2):
                    p(cx - 2, y, self.bottom);
                    p(cx + 1, y, self.bottom)
            # shoes
            p(cx - 3, rows - 2, self.shoe, 2, 1)
            p(cx + 1, rows - 2, self.shoe, 2, 1)

        # --- arms (pose-specific) ---
        def arms(mode):
            skin = self.skin
            shirt = self.top
            if mode == "down":
                p(cx - 4, top_y + 1, shirt);
                p(cx + 3, top_y + 1, shirt)
                p(cx - 5, top_y + 2, skin);
                p(cx + 4, top_y + 2, skin)
            elif mode == "wave0":
                # right arm up
                p(cx + 3, top_y, shirt);
                p(cx + 4, top_y - 1, skin);
                p(cx + 5, top_y - 2, skin)
                p(cx - 4, top_y + 1, shirt);
                p(cx - 5, top_y + 2, skin)
            elif mode == "wave1":
                p(cx + 2, top_y - 1, shirt);
                p(cx + 3, top_y - 2, skin);
                p(cx + 4, top_y - 3, skin)
                p(cx - 4, top_y + 1, shirt);
                p(cx - 5, top_y + 2, skin)
            elif mode == "danceL":
                p(cx - 4, top_y - 1, shirt);
                p(cx - 5, top_y - 2, skin)
                p(cx + 3, top_y + 1, shirt);
                p(cx + 4, top_y + 2, skin)
            elif mode == "danceR":
                p(cx + 3, top_y - 1, shirt);
                p(cx + 4, top_y - 2, skin)
                p(cx - 4, top_y + 1, shirt);
                p(cx - 5, top_y + 2, skin)
            elif mode == "up":
                p(cx - 3, top_y - 1, shirt);
                p(cx - 4, top_y - 2, skin)
                p(cx + 2, top_y - 1, shirt);
                p(cx + 3, top_y - 2, skin)
            elif mode == "fall":
                p(cx - 5, top_y, skin);
                p(cx + 4, top_y, skin)
                p(cx - 4, top_y - 1, shirt);
                p(cx + 3, top_y - 1, shirt)

        # choose limbs by pose
        if pose in ("idle", "kiss"):
            legs("together");
            arms("down")
        elif pose == "wave0":
            legs("together");
            arms("wave0")
        elif pose == "wave1":
            legs("together");
            arms("wave1")
        elif pose == "danceL":
            legs("apartL");
            arms("danceL")
        elif pose == "danceR":
            legs("apartR");
            arms("danceR")
        elif pose == "walk0":
            legs("apartL");
            arms("danceR")
        elif pose == "walk1":
            legs("apartR");
            arms("danceL")
        elif pose == "run0":
            legs("runL");
            arms("danceR")
        elif pose == "run1":
            legs("runR");
            arms("danceL")
        elif pose == "jump":
            legs("jump");
            arms("up")
        elif pose == "fall":
            legs("fall");
            arms("fall")

        # outline pass (4-neighborhood)
        out = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        for y in range(rows * px):
            for x in range(cols * px):
                if surf.get_at((x, y)).a:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < surf.get_width() and 0 <= ny < surf.get_height() and surf.get_at((nx, ny)).a == 0:
                            out.set_at((nx, ny), (*self.outline, 255))
        final = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        final.blit(out, (0, 0));
        final.blit(surf, (0, 0))
        if flip: final = pygame.transform.flip(final, True, False)
        return final

    def _make_frames(self):
        # prebuild a tiny set of frames per animation
        flip = (self.facing == -1)
        f = {}
        f["idle"] = [self._build_sprite("idle", flip)]
        f["wave"] = [self._build_sprite("wave0", flip), self._build_sprite("wave1", flip)]
        f["dance"] = [self._build_sprite("danceL", flip), self._build_sprite("danceR", flip)]
        f["walk"] = [self._build_sprite("walk0", flip), self._build_sprite("walk1", flip)]
        f["run"] = [self._build_sprite("run0", flip), self._build_sprite("run1", flip)]
        f["jump"] = [self._build_sprite("jump", flip)]
        f["fall"] = [self._build_sprite("fall", flip)]
        f["kiss"] = [self._build_sprite("kiss", flip)]
        return f

    # ---------- behavior ----------
    def _choose_next(self):
        r = random.random()
        # if near cat — wave
        if abs(self.world_x - self.g.cat.x) < 90 and self.cooldown <= 0:
            self.state, self.next_change = "wave", 1.2
            self.cooldown = 5.0
            self.vx = 0
            return
        # couples sometimes kiss
        if self.partner and self.kind != "child" and self.partner.kind != "child":
            if r < 0.12 and abs(self.world_x - self.partner.world_x) < 36:
                self.state, self.next_change = "kiss", 1.4
                self.vx = 0;
                self.partner.state = "kiss";
                self.partner.next_change = 1.4
                # face each other
                if self.world_x <= self.partner.world_x:
                    self.facing, self.partner.facing = 1, -1
                else:
                    self.facing, self.partner.facing = -1, 1
                return
        # random ambient actions
        if r < 0.40:
            self.state, self.next_change = "idle", random.uniform(1.2, 3.0);
            self.vx = 0
        elif r < 0.58:
            self.state, self.next_change = "wave", 1.0;
            self.vx = 0
        elif r < 0.72:
            self.state, self.next_change = "dance", random.uniform(1.5, 2.2);
            self.vx = 0
        elif r < 0.88:
            self.state, self.next_change = "walk", random.uniform(1.6, 2.6);
            self.vx = 28 * self.facing
        elif r < 0.96:
            self.state, self.next_change = "run", random.uniform(0.9, 1.4);
            self.vx = 58 * self.facing
        else:
            # jump -> fall handled in update by vy sign
            self.state, self.next_change = "jump", 0.8
            self.vy = -210.0;
            self.on_ground = False

    def update(self, dt):
        self.t += dt
        self.frame_t += dt
        self.cooldown = max(0.0, self.cooldown - dt)
        self.say_ttl = max(0.0, self.say_ttl - dt)

        # timers/state changes
        self.next_change -= dt
        if self.next_change <= 0:
            self._choose_next()

        # gait frame speed
        if self.state in ("walk", "dance", "wave", "run"):
            speed = 6.0 if self.state == "walk" else (9.0 if self.state == "run" else 4.0)
            if self.state == "dance": speed = 5.0
            if self.state == "wave":  speed = 6.0
            if self.frame_t >= 1.0 / speed:
                self.frame_t = 0.0
                self.frame_i = (self.frame_i + 1) % len(self.frames[self.state])

        # move within roam band
        if self.state in ("walk", "run"):
            self.world_x += self.vx * dt
            left = self.home_x - self.roam
            right = self.home_x + self.roam
            if self.world_x < left:
                self.world_x = left;
                self.facing = 1;
                self.vx = abs(self.vx)
                self._choose_next()
            elif self.world_x > right:
                self.world_x = right;
                self.facing = -1;
                self.vx = -abs(self.vx)
                self._choose_next()

        # simple jump/fall
        if self.state == "jump" or not self.on_ground:
            self.vy += self.gravity * dt
            self.oy += self.vy * dt
            if self.vy > 0:
                # display 'fall' frame while descending
                pass
            if self.oy >= 0:
                self.oy = 0
                self.vy = 0
                self.on_ground = True
                # land -> idle quickly
                self.state = "idle"
                self.next_change = random.uniform(0.7, 1.6)

        # greet the cat if close
        if self.cooldown <= 0 and abs(self.world_x - self.g.cat.x) < 90 and self.state not in ("kiss", "run"):
            if random.random() < 0.20:
                self.say_text = random.choice(["Hi!", "Nice day!", "Meow friend!", "Hello!"])
                self.say_ttl = 1.8
                self.cooldown = 6.0

    def draw(self, surf, cam_x, w):
        sx = int(self.world_x - cam_x * self.par + w // 2)
        sy = int(self.ground_y + self.oy)
        # pick visual state (jump uses fall frame when descending)
        vis_state = self.state
        if self.state == "jump" and self.vy > 0:
            vis_state = "fall"
        frame_list = self.frames.get(vis_state, self.frames["idle"])
        sp = frame_list[self.frame_i % len(frame_list)]
        surf.blit(sp, (sx - self.w // 2, sy - self.h))

        # hearts during kiss
        if self.state == "kiss":
            self._kiss_t += 6 / 60
            for i in range(2):
                hx = sx + (-8 + i * 16)
                hy = sy - self.h - 8 - int(abs(math.sin(self._kiss_t + i)) * 4)
                pygame.draw.circle(surf, (255, 120, 150), (hx - 2, hy), 3)
                pygame.draw.circle(surf, (255, 120, 150), (hx + 2, hy), 3)
                pygame.draw.polygon(surf, (255, 120, 150), [(hx - 5, hy), (hx + 5, hy), (hx, hy + 6)])

        # speech bubble
        if self.say_ttl > 0:
            a = int(255 * clamp(self.say_ttl / 1.8, 0, 1))
            draw_speech_bubble(surf, sx, sy - self.h - 8, self.say_text, self.g.font, alpha=a)


class HotAirBalloon:
    def __init__(self, x, y, par=0.26, speed=10):
        self.x, self.y = x, y
        self.par = par
        self.speed = speed
        self.t = random.random() * 20
        # randomized palette by default
        self.palette = self._rand_palette()
        self.sprite = self._build(self.palette)

    def _darker(self, c, amt=60):
        return (max(0, c[0] - amt), max(0, c[1] - amt), max(0, c[2] - amt))

    def _rand_palette(self):
        # bright, friendly colors
        colors = [(255, 120, 110), (255, 190, 80), (120, 200, 255),
                  (155, 130, 230), (120, 220, 170), (255, 160, 210)]
        main = random.choice(colors)
        others = [c for c in colors if c != main]
        stripes = random.sample(others, k=min(3, len(others))) or [main]
        return {
            "main": main,
            "outline": self._darker(main, 80),
            "stripes": stripes,
            "basket": (170, 120, 80),
            "rope": (120, 100, 80),
        }

    def _build(self, palette=None):
        pal = palette or {
            "main": (255, 120, 110),
            "outline": (200, 60, 60),
            "stripes": [(255, 220, 120), (120, 200, 255), (180, 255, 190)],
            "basket": (170, 120, 80),
            "rope": (120, 100, 80),
        }
        surf = pygame.Surface((80, 110), pygame.SRCALPHA)
        # balloon
        pygame.draw.ellipse(surf, pal["main"], (10, 0, 60, 70))
        pygame.draw.ellipse(surf, pal["outline"], (10, 0, 60, 70), 3)
        # stripes
        for k, c in enumerate(pal["stripes"]):
            pygame.draw.arc(surf, c, (10, 0, 60, 70), 0.6 + k * 0.8, 2.6 + k * 0.8, 3)
        # ropes
        pygame.draw.line(surf, pal["rope"], (30, 62), (22, 80), 2)
        pygame.draw.line(surf, pal["rope"], (50, 62), (58, 80), 2)
        # basket
        pygame.draw.rect(surf, pal["basket"], (20, 80, 40, 16), border_radius=4)
        pygame.draw.rect(surf, (120, 90, 60), (20, 80, 40, 16), 2, border_radius=4)
        return surf


class RainbowArc:
    def __init__(self, x, y, radius=420, par=0.20):
        self.x, self.y, self.r, self.par = x, y, radius, par
        self.colors = [
            (255, 60, 60),
            (255, 140, 40),
            (255, 210, 60),
            (110, 210, 90),
            (80, 170, 255),
            (140, 120, 225),
        ]

    def draw(self, surf, cam_x, w, t_cycle, font):
        day = 1.0 - abs(0.5 - t_cycle) * 2.0
        alpha = int(180 * (0.25 + 0.75 * day))

        sx = int(self.x - cam_x * self.par + w // 2)
        sy = int(self.y)
        rect = pygame.Rect(sx - self.r, sy - self.r, self.r * 2, self.r * 2)

        # wider than a perfect semicircle so the feet "reach" the horizon
        start_angle = math.pi * (-0.02)
        end_angle = math.pi * (1.02)

        for i, c in enumerate(self.colors):
            pygame.draw.arc(
                surf,
                (*c[:3], alpha),
                rect.inflate(i * 14, i * 14),
                start_angle,
                end_angle,
                6
            )
        # message stays the same...
        msg = "You are important!"
        txt = font.render(msg, True, (40, 40, 60))
        shadow = font.render(msg, True, (255, 255, 255))
        px = sx - txt.get_width() // 2
        py = int(sy - self.r + 36)
        surf.blit(shadow, (px, py + 1))
        surf.blit(txt, (px, py))


class JetBanner:
    """A tiny jet towing a waving banner with a message."""

    def __init__(self, x, y, msg="You are important!", par=0.24, speed=90):
        self.x, self.y, self.msg = x, y, msg
        self.par = par
        self.speed = speed
        self.t = random.random() * 10

    def update(self, dt):
        self.t += dt
        self.x += self.speed * dt
        self.y += math.sin(self.t * 0.8) * 6 * dt

    def draw(self, surf, cam_x, w, font):
        sx = int(self.x - cam_x * self.par + w // 2)
        sy = int(self.y)
        # jet
        pygame.draw.polygon(surf, (80, 90, 110), [(sx, sy), (sx - 26, sy - 6), (sx - 20, sy + 6)])
        pygame.draw.polygon(surf, (160, 180, 210), [(sx - 12, sy - 2), (sx - 18, sy - 5), (sx - 18, sy + 1)])
        # contrail
        pygame.draw.line(surf, (220, 230, 255), (sx - 26, sy), (sx - 46, sy), 2)
        # banner
        length, height = 320, 36
        wave = int(6 * math.sin(self.t * 2.6))
        banner = pygame.Surface((length, height), pygame.SRCALPHA)
        pygame.draw.rect(banner, (255, 255, 255, 230), (0, 0, length, height), border_radius=8)
        pygame.draw.rect(banner, (90, 90, 110), (0, 0, length, height), 2, border_radius=8)
        text = font.render(self.msg, True, (40, 40, 60))
        banner.blit(text, (12, (height - text.get_height()) // 2))
        # ropes
        pygame.draw.line(surf, (90, 90, 110), (sx - 46, sy), (sx - 60, sy + wave), 2)
        # place with a little wave
        surf.blit(banner, (sx - 60 - length, sy - height // 2 + wave))


# ============================================================
# Pixel-art Sky Whale (drop-in replacement)
# ============================================================
class SkyWhale:
    """
    Cute pixel-art whale with white belly, dark outline, blush,
    and an animated spout — scaled up with nearest-neighbor so it
    looks like your references.
    """

    def __init__(self, x, y, par=0.18, speed=12, scale=1.6, tint="blue"):
        self.x, self.y = x, y
        self.par = par
        self.speed = speed
        self.t = random.random() * 20
        self.scale = scale
        self.tint = tint
        self.sprite = self._build_sprite()

    # --- helpers ------------------------------------------------
    def _colors(self):
        # slight tint options; feel free to tweak
        if self.tint == "ice":
            body = (150, 210, 255)
        elif self.tint == "mint":
            body = (120, 220, 220)
        else:  # "blue"
            body = (90, 170, 230)
        return {
            "body": body,
            "body_dark": (60, 135, 200),
            "belly": (235, 246, 255),
            "outline": (20, 45, 85),
            "eye": (10, 25, 40),
            "cheek": (255, 180, 200),
            "water": (90, 220, 255),
        }

    def _outline_surface(self, src, color):
        w, h = src.get_width(), src.get_height()
        out = pygame.Surface((w, h), pygame.SRCALPHA)
        get = src.get_at
        for y in range(h):
            for x in range(w):
                if get((x, y)).a > 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h and get((nx, ny)).a == 0:
                            out.set_at((nx, ny), (*color, 255))
        return out

    def _build_sprite(self):
        c = self._colors()
        w, h = 28, 18
        s = pygame.Surface((w, h), pygame.SRCALPHA)

        # base "pixel canvas"
        base = pygame.Surface((w, h), pygame.SRCALPHA)

        # --- body (ellipse + rounded head + tail) ---
        pygame.draw.ellipse(base, c["body"], (1, 5, 20, 12))
        pygame.draw.ellipse(base, c["body"], (4, 4, 12, 10))  # head bulge
        pygame.draw.polygon(base, c["body"], [(18, 9), (27, 5), (27, 13)])  # tail
        # dorsal “bump”
        pygame.draw.rect(base, c["body"], (6, 4, 4, 2))

        # --- belly ---
        pygame.draw.ellipse(base, c["belly"], (5, 10, 15, 8))

        # --- fin ---
        pygame.draw.polygon(base, c["body_dark"], [(10, 13), (13, 11), (12, 15)])

        # --- eye + blush ---
        base.set_at((8, 9), c["eye"])
        base.set_at((8, 10), c["eye"])
        pygame.draw.rect(base, c["cheek"], (11, 12, 2, 2))

        # --- tiny highlight on top-left ---
        pygame.draw.rect(base, (255, 255, 255), (6, 7, 1, 1))

        # outline behind body so it hugs the shape
        outline = self._outline_surface(base, c["outline"])
        final = pygame.Surface((w, h), pygame.SRCALPHA)
        final.blit(outline, (0, 0))
        final.blit(base, (0, 0))
        return final

    def update(self, dt):
        self.t += dt
        self.x += self.speed * dt
        self.y += math.sin(self.t * 0.5) * 5 * dt

    def draw(self, surf, cam_x, w_screen):
        # where to draw
        sx = int(self.x - cam_x * self.par + w_screen // 2)
        sy = int(self.y)

        # pixel scaling (keep it integer for crisp pixels)
        px = max(2, int(4 * self.scale))  # tune 4->5 for bigger pixels
        sp = pygame.transform.scale(
            self.sprite, (self.sprite.get_width() * px, self.sprite.get_height() * px)
        )

        # soft drop shadow
        shadow_w = int(sp.get_width() * 0.7)
        shadow_h = max(6, int(sp.get_height() * 0.18))
        sh = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 70), sh.get_rect())
        surf.blit(sh, (sx - shadow_w // 2, sy + sp.get_height() // 2 - shadow_h // 3))

        # whale
        surf.blit(sp, (sx - sp.get_width() // 2, sy - sp.get_height() // 2))

        # animated pixel spout (3 droplets that wiggle)
        c = self._colors()
        top_x = sx - sp.get_width() // 2 + 7 * px
        top_y = sy - sp.get_height() // 2 - 2 * px
        for i in range(3):
            ox = int((i - 1) * 3 * px + math.sin(self.t * 3 + i) * px * 0.5)
            oy = int(- (4 + i) * px - abs(math.sin(self.t * 2 + i)) * px)
            pygame.draw.rect(surf, c["water"], (top_x + ox, top_y + oy, px, px))


class BgBalloon:
    def __init__(self, x, y, par=0.26, roam=40):
        self.base_x, self.base_y = x, y
        self.x, self.y = x, y
        self.par = par
        self.roam = roam
        self.t = random.random() * 20

        def darker(c, amt=80):
            return (max(0, c[0] - amt), max(0, c[1] - amt), max(0, c[2] - amt))

        colors = [(255, 120, 110), (255, 190, 80), (120, 200, 255),
                  (155, 130, 230), (120, 220, 170), (255, 160, 210)]
        main = random.choice(colors)
        others = [c for c in colors if c != main]
        stripes = random.sample(others, k=min(3, len(others))) or [main]
        pal = {
            "main": main,
            "outline": darker(main, 80),
            "stripes": stripes,
            "basket": (170, 120, 80),
            "rope": (120, 100, 80),
        }
        # reuse the balloon art with our palette
        self.sprite = HotAirBalloon(0, 0, par, speed=0)._build(palette=pal)

    def update(self, dt):
        # gentle bounded wander around a "home" point (no drift across the world)
        self.t += dt
        self.x = self.base_x + math.sin(self.t * 0.35) * self.roam
        self.y = self.base_y + math.sin(self.t * 0.8) * (self.roam * 0.4)

    def draw(self, surf, cam_x, w):
        sx = int(self.x - cam_x * self.par + w // 2)
        sy = int(self.y)
        surf.blit(
            self.sprite,
            (sx - self.sprite.get_width() // 2, sy - self.sprite.get_height() // 2),
        )


class FloatingIsland:
    def __init__(self, x, y, par=0.20, drift=6, scale=1.0):
        self.x, self.y, self.par = x, y, par
        self.drift = drift
        self.t = random.random() * 10
        self.scale = scale

    def update(self, dt):
        self.t += dt
        self.x += self.drift * dt
        self.y += math.sin(self.t * 0.6) * 4 * dt

    def draw(self, surf, cam_x, w):
        sx = int(self.x - cam_x * self.par + w // 2)
        sy = int(self.y)
        s = self.scale
        island = pygame.Surface((int(280 * s), int(160 * s)), pygame.SRCALPHA)
        # rock
        pygame.draw.polygon(island, (110, 100, 120, 220),
                            [(30 * s, 50 * s), (250 * s, 50 * s), (220 * s, 130 * s), (140 * s, 150 * s),
                             (80 * s, 130 * s)], )
        pygame.draw.polygon(island, (70, 60, 80, 230),
                            [(30 * s, 50 * s), (250 * s, 50 * s), (220 * s, 130 * s), (140 * s, 150 * s),
                             (80 * s, 130 * s)], 3)
        # grass top
        pygame.draw.ellipse(island, (120, 180, 110, 230), (20 * s, 20 * s, 240 * s, 60 * s))
        pygame.draw.ellipse(island, (80, 130, 80, 230), (20 * s, 20 * s, 240 * s, 60 * s), 3)
        # tiny waterfall
        if random.random() < 0.7:
            pygame.draw.rect(island, (130, 180, 255, 160), (150 * s, 60 * s, 10 * s, 50 * s), border_radius=4)
        # a tiny house silhouette
        pygame.draw.rect(island, (95, 85, 105, 240), (70 * s, 42 * s, 28 * s, 18 * s))
        pygame.draw.polygon(island, (75, 65, 90, 240), [(66 * s, 42 * s), (84 * s, 30 * s), (102 * s, 42 * s)])
        surf.blit(island, (sx - int(140 * s), sy - int(80 * s)))


class NormalBackground:
    """
    Pixel-art meadow with procedural trees (sakura / maple / jacaranda / oak / pine / willow)
    styled like 16-bit RPGs: chunky pixels, dark outlines, and gentle dithers.

    The trees are generated once per seed and cached, then blitted with nearest-neighbor scaling.
    """

    def __init__(self, game):
        self.g = game
        # --- NEW: floating sky messages (Elif) ---
        self.sky_msgs = []
        self.sky_msg_timer = random.uniform(1.0, 2.0)

        # clouds / flyers unchanged (kept from your original)
        self.clouds = []
        W = self.g.w
        for _ in range(10):
            self.clouds.append(Cloud(
                random.uniform(-W, W * 2),
                random.uniform(20, 220),
                random.uniform(0.7, 1.4),
                random.uniform(10, 30)
            ))
        self.ground_col = (240, 230, 220)
        self.tile_size = 20
        # Ground-hugging butterflies, more of them, parallax matches foreground trees a bit

        self.birds = [BgBird(random.uniform(-800, 1200), random.uniform(120, 220), 0.28 + random.random() * 0.25,
                             speed=20 + random.random() * 25, scale=random.uniform(0.8, 1.2))
                      for _ in range(6)]
        # --- Sky decorations ---
        RX = lambda: random.uniform(-1400, 1800)

        # Flocks (mixed species)
        species_choices = ["swallow", "goose", "seagull", "sparrow"]
        self.flocks = []

        # Hot air balloons
        self.balloon_block_cache = {}
        self.balloon_block_w = 700

        # A friendly sky whale (or two)  ➜ removed
        self.whales = []

        # Giant floating islands        ➜ removed
        self.islands = []

        # A rainbow near the horizon (centered ahead of start)
        # Fixed rainbow: sits behind the hills (parallax matches far hills)
        # --- sparse world objects (like trees) ---
        self.bfly_block_cache = {}  # i -> [BgButterfly, ...]
        self.rainbow_block_cache = {}  # I -> [RainbowArc, ...]

        self.bfly_block_w = 420  # butterflies: wider blocks than trees
        self.rainbow_block_w = 4200  # rainbows: very rare / far apart

        # --- people (ground NPCs) ---
        self.people_block_cache = {}  # i -> [HumanNPC,...]
        self.people_block_w = 360

        # ----- NEW: tree field config -----
        self.block_w = 160  # one "cell" that may contain 1–2 trees
        self.parallax = 0.42  # parallax depth for trees (behind the cat)
        self.min_tree_gap = 90  # new: baseline spacing (pixels) between tree centers

        self.tree_cache = {}  # (seed, species, scale_k) -> Surface
        self.tree_block_cache = {}  # i -> list of trees (stable world_x etc.)
        self.max_tree_blocks = 512  # cap to avoid unbounded growth
        self.house_block_cache = {}  # i -> [ {world_x, par, sprite, w, h} ... ]
        self.house_block_w = 520  # spacing between candidate blocks
        self.house_gap_margin = 18  # how much space to keep from tree edges
        self.house_min_gap_extra = 24  # extra breathing room beyond house width
        self.house_parallax_bias = -0.015  # houses slightly behind tree layer

    # ------------------------------------------------------------
    # tiny helpers
    # ------------------------------------------------------------
    def _ensure_people_block(self, i):
        """Create humans (men, women, kids) in block i, placed in open gaps, some roaming and some paired."""
        if i in self.people_block_cache:
            return
        rng = self._rng(99111 * i)
        group = []
        if rng.random() < 0.80:  # more lively blocks
            n = rng.randint(1, 3)
            block_x0 = i * self.people_block_w
            block_x1 = block_x0 + self.people_block_w
            gaps = self._collect_tree_gaps(block_x0, block_x1, needed_width=30)

            def spawn_one(kind, x):
                par = self.parallax + 0.005 + rng.uniform(-0.01, 0.01)
                facing = 1 if rng.random() < 0.5 else -1
                roam = rng.uniform(18, 52)
                h = HumanNPC(self.g, x, self.g.ground_y, style=kind, facing=facing, par=par, roam=roam)
                return h

            for _ in range(n):
                # choose a clear gap, else fallback to anywhere in block
                if gaps:
                    gL, gR = rng.choice(gaps)
                    x = rng.uniform(gL + 16, gR - 16)
                    gap_w = (gR - gL) - 32
                else:
                    x = block_x0 + rng.uniform(60, self.people_block_w - 60)
                    gap_w = 120

                # chance: adult couple (man & woman) who may kiss
                if rng.random() < 0.35:
                    man = spawn_one("man", x - 10)
                    woman = spawn_one("woman", x + 10)
                    man.partner = woman;
                    woman.partner = man
                    # keep their roam inside the same space
                    r = clamp(gap_w * 0.4, 18, 60)
                    man.roam = woman.roam = r
                    group += [man, woman]
                # chance: adult + child
                elif rng.random() < 0.40:
                    adult_kind = rng.choice(["man", "woman"])
                    adult = spawn_one(adult_kind, x + rng.uniform(-8, 8))
                    kid = spawn_one("child", x + rng.uniform(-20, -12) * (1 if adult.facing > 0 else -1))
                    # keep kid near adult
                    kid.roam = min(kid.roam, 24)
                    group += [adult, kid]
                else:
                    # single (random gender)
                    kind = rng.choice(["man", "woman", "child", "woman", "man"])
                    h = spawn_one(kind, x)
                    group.append(h)

        self.people_block_cache[i] = group

    def _collect_tree_gaps(self, x0, x1, needed_width):
        """
        Return a list of (gap_left, gap_right) in world space within [x0,x1],
        where no tree occupies that horizontal space (with a margin), and the
        gap is wide enough for a house of `needed_width`.
        """
        # ensure all tree blocks covering [x0,x1] exist
        j0 = int(math.floor(x0 / self.block_w)) - 1
        j1 = int(math.floor(x1 / self.block_w)) + 1

        L = x0 + self.house_gap_margin
        R = x1 - self.house_gap_margin
        if L >= R:
            return []

        # collect blocking intervals from trees (with a small margin)
        blocks = []
        for j in range(j0, j1 + 1):
            for t in self._get_block_trees(j):
                left = t["world_x"] - t["w"] * 0.5 - self.house_gap_margin
                right = t["world_x"] + t["w"] * 0.5 + self.house_gap_margin
                # clip to [L,R]
                if right <= L or left >= R:
                    continue
                blocks.append((max(left, L), min(right, R)))

        # add bounds so we can compute complements
        blocks.append((L - 1_000_000, L))
        blocks.append((R, R + 1_000_000))
        blocks.sort(key=lambda ab: ab[0])

        # merge
        merged = []
        for a, b in blocks:
            if not merged or a > merged[-1][1]:
                merged.append([a, b])
            else:
                merged[-1][1] = max(merged[-1][1], b)

        # gaps = complements inside [L,R]
        gaps = []
        prev = L
        for a, b in merged:
            gap_l = max(prev, L)
            gap_r = min(a, R)
            if gap_r - gap_l >= needed_width + self.house_min_gap_extra:
                gaps.append((gap_l, gap_r))
            prev = max(prev, b)
            if prev >= R:
                break
        return gaps

    def _ensure_house_block(self, i):
        """Deterministically create 0–2 cottages in block i, snapped into tree gaps."""
        if i in self.house_block_cache:
            return

        rng = self._rng(66473 * i)
        group = []

        if rng.random() < 0.55:
            n = rng.randint(1, 2)
            block_x0 = i * self.house_block_w
            block_x1 = block_x0 + self.house_block_w

            for _ in range(n):
                style = rng.choice(["tudor", "stone", "wood", "fairytale"])
                cottage = CottageHouse(rng, style=style)
                sp = cottage.sprite
                w, h = sp.get_width(), sp.get_height()

                # 1) pick a rough preferred spot (stable)
                preferred = block_x0 + rng.uniform(80, self.house_block_w - 80)

                # 2) query gaps in this block wide enough for the house
                gaps = self._collect_tree_gaps(block_x0, block_x1, w)

                if gaps:
                    # choose the gap whose center is closest to our preferred spot
                    best = min(gaps, key=lambda g: abs((g[0] + g[1]) * 0.5 - preferred))
                    center = (best[0] + best[1]) * 0.5
                    # tiny deterministic jitter so houses don’t line up perfectly
                    world_x = center + rng.uniform(-8, 8)
                else:
                    # fallback: no perfect gap — clamp to block & hope for partial opening
                    world_x = max(block_x0 + 60, min(block_x1 - 60, preferred))

                # keep houses just a hair behind the tree layer so they read as "between"
                par = self.parallax + self.house_parallax_bias + rng.uniform(-0.005, 0.005)

                group.append({"world_x": world_x, "par": par, "sprite": sp, "w": w, "h": h})

        self.house_block_cache[i] = group

    def _spawn_sky_message(self, camera_dx):
        g = self.g
        if not ELIF_SKY_MESSAGES:
            return False
        if len(self.sky_msgs) >= SKY_MSG_MAX_ACTIVE:
            return False

        direction = 1 if camera_dx >= 0 else -1  # spawn ahead of movement

        for _ in range(28):
            par = random.uniform(*SKY_MSG_PAR_RANGE)
            y = random.uniform(60, 190)

            msg = random.choice(ELIF_SKY_MESSAGES)
            new_w, new_h = g.font.size(msg)  # fast, no surface needed yet

            off = random.uniform(*SKY_MSG_SPAWN_OFF)
            sx_spawn = (g.w + off) if direction >= 0 else (-off)

            world_x = g.camera_x * par - g.w * 0.5 + sx_spawn

            ok = True
            for m in self.sky_msgs:
                mx = m.screen_x(g.camera_x, g.w)

                # width-aware horizontal spacing (center-to-center)
                needed_x = SKY_MSG_MIN_SCREEN_GAP + 0.5 * (m.w + new_w)

                if abs(mx - sx_spawn) < needed_x:
                    ok = False
                    break

                # if somewhat close in x, force bigger y separation too (also height-aware)
                needed_y = max(SKY_MSG_MIN_Y_GAP, 0.5 * (m.h + new_h) + 10)
                if abs(mx - sx_spawn) < needed_x * 1.15 and abs(m.y - y) < needed_y:
                    ok = False
                    break

            if ok:
                self.sky_msgs.append(
                    SkyMessage(world_x, y, par, msg, font=g.font, ttl=random.uniform(12.0, 18.0))
                )
                return True

        # no safe spot found → do NOT force a spawn (prevents overlaps)
        return False

    def _ensure_balloon_block(self, i):
        """Create a few hot-air balloons anchored to world block i."""
        if i in self.balloon_block_cache:
            return
        rng = self._rng(77777 * i)
        group = []
        # ~60% of blocks get 1–3 balloons
        if rng.random() < 0.60:
            n = rng.randint(1, 3)
            for _ in range(n):
                base_x = i * self.balloon_block_w + rng.uniform(90, self.balloon_block_w - 90)
                base_y = rng.uniform(70, 180)
                par = 0.22 + rng.uniform(0.00, 0.08)  # around the far-mid sky
                roam = rng.uniform(24, 48)
                group.append(BgBalloon(base_x, base_y, par=par, roam=roam))
        self.balloon_block_cache[i] = group

    def _ensure_rainbow_block(self, I):
        if I in self.rainbow_block_cache:
            return
        rng = self._rng(88499 * I)
        arcs = []
        # fewer rainbows overall
        if I == 0 or rng.random() < 0.22:
            par = 0.18
            block_x0 = I * self.rainbow_block_w
            world_x = block_x0 + rng.uniform(self.rainbow_block_w * 0.25,
                                             self.rainbow_block_w * 0.75)
            # lower on the screen so the feet are near the hills
            y = int(self.g.h * 0.78 + rng.uniform(-6, 12))
            radius = rng.randint(420, 560)
            arcs.append(RainbowArc(world_x, y, radius=radius, par=par))
        self.rainbow_block_cache[I] = arcs

    def _get_block_trees(self, i):
        """Return a stable list of trees for block i."""
        if i in self.tree_block_cache:
            return self.tree_block_cache[i]

        rng = self._rng(i * 71143)
        n = rng.choices([1, 2], weights=[0.35, 0.65])[0]

        trees = []
        for j in range(n):
            s2 = i * 71143 + 97 * j
            rr = self._rng(s2)

            species = rr.choices(
                ["sakura", "jacaranda", "maple", "oak", "pine", "willow",
                 "red", "yellow", "blue", "lightblue", "turquoise",
                 "orange", "green", "darkgreen", "lightgreen",
                 "hexmono", "hexmulti"],
                weights=[1] * 17, k=1
            )[0]

            # base placement strictly inside this block
            local_x = rr.uniform(30, self.block_w - 30)

            # choose size & sprite (deterministic)
            scale_k = rr.choices([2, 3, 4], weights=[1, 8, 2])[0]
            tree_surf = self._get_tree(s2, species, scale_k)
            tree_w = tree_surf.get_width()

            # keep spacing only within this block (stable)
            if trees:
                last = trees[-1]
                size_gap = (last["w"] + tree_w) // 2
                required = max(self.min_tree_gap, size_gap)
                prev_local_x = last["world_x"] - i * self.block_w
                if local_x - prev_local_x < required:
                    local_x = prev_local_x + required

            # clamp to block edges after spacing
            local_x = max(30, min(self.block_w - 30, local_x))

            world_x = i * self.block_w + local_x
            par_i = self.parallax + rr.uniform(-0.02, 0.02)

            trees.append({"world_x": world_x, "surf": tree_surf, "w": tree_w, "par": par_i})

        self.tree_block_cache[i] = trees
        return trees

    def _ensure_bfly_block(self, i):
        """Create (rare) ground butterfly clusters for block i."""
        if i in self.bfly_block_cache:
            return
        rng = self._rng(99001 * i)
        group = []
        # ~40% of butterfly blocks get a small cluster (2–4)
        if rng.random() < 0.40:
            n = rng.randint(2, 4)
            # place the cluster somewhere inside this block in world-space
            base_x = i * self.bfly_block_w + rng.uniform(70, self.bfly_block_w - 70)
            base_y = self.g.ground_y - rng.uniform(28, 64)
            for k in range(n):
                par = self.parallax + rng.uniform(-0.02, 0.02)  # near trees
                hue = rng.choice([(255, 150, 200), (255, 180, 210), (200, 160, 240), (255, 200, 120)])
                b = BgButterfly(
                    base_x + rng.uniform(-18, 18),
                    base_y + rng.uniform(-10, 10),
                    par,
                    hue=hue,
                    roam=rng.uniform(18, 32)
                )
                group.append(b)
        self.bfly_block_cache[i] = group



    def _rand_hex_tuple(self, rng):
        hexdig = "0123456789ABCDEF"
        h = "#" + "".join(rng.choice(hexdig) for _ in range(6))
        return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))

    # ---- palettes for far/mid/near hills (inspired by your refs) ----
    def _hill_colors(self, t_cycle):
        # atmospheric fade with time-of-day (slightly cooler at night)
        cool = (165, 190, 220);
        warm = (255, 210, 190)
        mood = lerp_color(warm, cool, 0.6 if (t_cycle > 0.70 or t_cycle < 0.08) else 0.15)

        # base palettes: (far, mid, near)
        palettes = [
            # 0 Alpine (blue mountains)
            [(170, 205, 230), (130, 170, 205), (100, 140, 185)],
            # 1 Spring (minty greens)
            [(206, 234, 212), (176, 216, 192), (144, 194, 168)],
            # 2 Desert (red/orange dusk)
            [(240, 190, 170), (220, 150, 120), (190, 110, 100)],
            # 3 Lavender dusk (purples)
            [(212, 188, 240), (182, 156, 218), (148, 128, 195)],
            # 4 Teal (blue-green)
            [(170, 220, 215), (140, 198, 190), (110, 175, 168)],
        ]
        pal = palettes[self.g.hill_palette % len(palettes)]
        # very light blend with mood for day/night feel
        return [lerp_color(p, mood, 0.08) for p in pal]

    # ---- SHAPES ----
    def _rolling_height(self, wx, amp1, amp2, amp3, phase):
        # smooth layered sines for soft hills (stable in world space)
        return (math.sin(wx * 0.0023 + phase) * amp1 +
                math.sin(wx * 0.0049 + phase * 1.7) * amp2 +
                math.cos(wx * 0.0012 - phase * 0.6) * amp3)

    def _mountain_height(self, wx, amp, rough, phase):
        # jagged "triangle-ish" ridges using sharpened sines
        s1 = abs(math.sin(wx * 0.0027 + phase)) ** 1.7
        s2 = abs(math.sin(wx * 0.0063 - phase * 0.7)) ** 3.0
        s3 = abs(math.sin(wx * 0.0109 + phase * 0.3)) ** 2.2
        return -(s1 * amp + s2 * rough + s3 * (rough * 0.5))  # negative -> peaks point up

    def _draw_hill_layer(self, surf, base_y, color, parallax, style, amp_tuple, seed, snow=False):
        g = self.g
        pts = []
        phase = seed * 0.0003

        # denser sampling = smoother ridge
        step = 4 if style == "mountain" else 6
        for sx in range(-60, g.w + 60, step):
            wx = (sx + g.camera_x * parallax)
            if style == "rolling":
                amp1, amp2, amp3 = amp_tuple
                y = base_y + self._rolling_height(wx, amp1, amp2, amp3, phase)
            else:
                amp, rough = amp_tuple[0], amp_tuple[1]
                y = base_y + self._mountain_height(wx, amp, rough, phase)
            pts.append((sx, int(y)))

        poly = [(-60, g.h), (-60, base_y + 240)] + pts + [(g.w + 60, base_y + 240), (g.w + 60, g.h)]

        # draw the hill onto its own transparent layer
        layer = pygame.Surface((g.w, g.h), pygame.SRCALPHA)
        pygame.draw.polygon(layer, color, poly)

        # soft vertical gradient (cache per (top_y, bot_y, style) to avoid rebuilding every frame)
        top_y = int(base_y - 140)
        bot_y = int(base_y + 200)
        key = (top_y, bot_y, style, g.w, g.h)
        if not hasattr(self, "_shade_cache"):
            self._shade_cache = {}
        shade = self._shade_cache.get(key)
        if shade is None:
            shade = pygame.Surface((g.w, g.h), pygame.SRCALPHA)
            v_top = 255
            v_bot = 215 if style == "mountain" else 225
            for y in range(g.h):
                t = clamp((y - top_y) / max(1, (bot_y - top_y)), 0, 1)
                v = int(lerp(v_top, v_bot, t))
                pygame.draw.line(shade, (v, v, v), (0, y), (g.w, y))
            self._shade_cache[key] = shade

        layer.blit(shade, (0, 0), special_flags=pygame.BLEND_MULT)

        # remove dotted "snow rim" (it caused the blocky dashes along the ridge)
        # If you still want a hint of snow, uncomment this single anti-aliased line:
        # if snow and style == "mountain":
        #     pygame.draw.aalines(layer, (min(255, color[0]+45), min(255, color[1]+45), min(255, color[2]+60)),
        #                         False, pts, 1)

        surf.blit(layer, (0, 0))

    def draw_hills(self, surf, t_cycle):
        g = self.g
        far_col, mid_col, near_col = self._hill_colors(t_cycle)

        # choose style behavior
        mode = {0: "mixed", 1: "rolling", 2: "mountain"}[g.hill_style]
        far_style = "mountain" if mode in ("mixed", "mountain") else "rolling"
        mid_style = "rolling"
        near_style = "rolling" if mode != "mountain" else "mountain"

        # base lines
        far_y = int(g.h * 0.62)
        mid_y = int(g.h * 0.68)
        near_y = int(g.h * 0.74)

        # draw back→front with parallax
        self._draw_hill_layer(surf, far_y, far_col, parallax=0.18, style=far_style,
                              amp_tuple=(40, 22) if far_style == "mountain" else (20, 12, 8),
                              seed=713, snow=True)
        self._draw_hill_layer(surf, mid_y, mid_col, parallax=0.24, style=mid_style,
                              amp_tuple=(26, 14, 10) if mid_style == "rolling" else (34, 16),
                              seed=917)
        self._draw_hill_layer(surf, near_y, near_col, parallax=0.32, style=near_style,
                              amp_tuple=(32, 18, 12) if near_style == "rolling" else (30, 14),
                              seed=1231)

    def _rng(self, seed):
        return random.Random(seed)

    def _hsv_to_rgb(self, h, s, v):
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(max(0, min(1, h)), max(0, min(1, s)), max(0, min(1, v)))
        return (int(r * 255), int(g * 255), int(b * 255))

    def _random_hex_color(self, rng, min_v=0.55):
        # bright-ish random color (random hex)
        h = rng.random()
        s = 0.55 + rng.random() * 0.4
        v = min_v + rng.random() * (1.0 - min_v)
        return self._hsv_to_rgb(h, s, v)

    def _shape_of(self, species):
        if species == "pine": return "triangle"
        if species == "willow": return "willow"
        return "round"  # default

    def _darker(self, c, amt=30):
        """Shift color by -amt (negative amt will lighten). Always clamp to 0..255."""

        def clamp255(v): return max(0, min(255, int(v)))

        return (clamp255(c[0] - amt), clamp255(c[1] - amt), clamp255(c[2] - amt))

    def _palette(self, species, rng):
        """
        Returns (palette_list, mode)
        mode in {"normal","mono","multi"}:
          - "normal" -> pick from palette_list (dithered)
          - "mono"   -> single random hex color across all leaves (with slight dither)
          - "multi"  -> per-leaf random hex colors (confetti)
        """
        # classic species palettes
        if species == "sakura":
            return ([(255, 180, 208), (255, 162, 195), (246, 140, 183), (235, 118, 170)], "normal")
        if species == "jacaranda":
            return ([(206, 168, 255), (186, 148, 240), (174, 132, 232), (225, 205, 255)], "normal")
        if species == "maple":
            return ([(255, 140, 84), (255, 108, 76), (232, 84, 64), (255, 176, 110)], "normal")
        if species == "oak":
            return ([(124, 190, 108), (104, 170, 94), (144, 206, 124), (86, 148, 86)], "normal")
        if species == "pine":
            return ([(86, 138, 96), (70, 120, 82), (104, 156, 112), (60, 98, 70)], "normal")
        if species == "willow":
            return ([(140, 192, 126), (118, 176, 112), (156, 206, 142), (100, 158, 100)], "normal")

        # explicit color families (HSV with little jitter)
        def family(h_range, s=(0.55, 0.9), v=(0.75, 1.0)):
            h = rng.uniform(*h_range)
            cols = []
            for j in range(4):
                hj = (h + rng.uniform(-0.02, 0.02)) % 1.0
                sj = rng.uniform(*s)
                vj = rng.uniform(*v)
                cols.append(self._hsv_to_rgb(hj, sj, vj))
            return cols

        if species == "red":        return (family((0.97, 1.00)), "normal")
        if species == "orange":     return (family((0.06, 0.11)), "normal")
        if species == "yellow":     return (family((0.13, 0.18), v=(0.90, 1.0)), "normal")
        if species == "green":      return (family((0.32, 0.38)), "normal")
        if species == "darkgreen":  return (family((0.28, 0.32), v=(0.55, 0.80)), "normal")
        if species == "lightgreen": return (family((0.38, 0.44), v=(0.85, 1.0)), "normal")
        if species == "turquoise":  return (family((0.48, 0.52)), "normal")
        if species == "lightblue":  return (family((0.53, 0.58), v=(0.85, 1.0)), "normal")
        if species == "blue":       return (family((0.60, 0.66)), "normal")

        # random hex variants
        if species == "hexmono":
            base = self._random_hex_color(rng)
            return ([base], "mono")
        if species == "hexmulti":
            return ([], "multi")  # palette not used

        # fallback
        return ([(120, 180, 120)], "normal")

    # ------------------------------------------------------------
    # pixel canvas builder (no smoothing)
    # ------------------------------------------------------------
    def _make_canvas(self, cols, rows, px=2):
        surf = pygame.Surface((cols * px, rows * px), pygame.SRCALPHA)

        def pset(x, y, col):
            if 0 <= x < cols and 0 <= y < rows:
                pygame.draw.rect(surf, col, (x * px, y * px, px, px))

        return surf, pset

    # ------------------------------------------------------------
    # canopy mask helpers (operate in grid coords)
    # ------------------------------------------------------------
    def _round_canopy(self, cols, rows, cx, cy, r, rng, squish_y=1.0):
        mask = set()
        for y in range(max(0, cy - int(r * squish_y) - 2), min(rows, cy + int(r * squish_y) + 3)):
            for x in range(max(0, cx - r - 2), min(cols, cx + r + 3)):
                dx = (x - cx)
                dy = (y - cy) / max(0.0001, squish_y)
                d2 = dx * dx + dy * dy
                thr = r * r + rng.randint(-2, 2)  # jittery edge
                if d2 <= thr:
                    mask.add((x, y))
        return mask

    def _triangle_canopy(self, cols, rows, cx, top_y, height, rng):
        mask = set()
        for i in range(height):
            y = top_y + i
            half = int((i / height) * (height * 0.7)) + rng.randint(-1, 1)
            for x in range(cx - half, cx + half + 1):
                if 0 <= x < cols and 0 <= y < rows:
                    mask.add((x, y))
        return mask

    # ------------------------------------------------------------
    # tree sprite generator (pixel art)
    # ------------------------------------------------------------
    def _build_tree_sprite(self, seed, species, scale_k):
        rng = self._rng(seed)
        cols, rows = 48, 56
        px_base = 2
        surf, pset = self._make_canvas(cols, rows, px=px_base)

        leaf_cols, mode = self._palette(species, rng)
        base_for_outline = leaf_cols[0] if leaf_cols else (160, 160, 160)
        leaf_outline = self._darker(base_for_outline, 55)
        bark = (116, 82, 62)
        bark_dark = (80, 56, 44)

        # trunk
        trunk_h = rng.randint(16, 22) if species != "pine" else rng.randint(22, 28)
        trunk_w = rng.choice([3, 3, 4, 5])
        tx = cols // 2 + rng.randint(-2, 2)
        base_y = rows - 6
        for i in range(trunk_h):
            y = base_y - i
            wob = rng.choice([-1, 0, 0, 1])
            for w in range(-trunk_w // 2, trunk_w // 2 + 1):
                pset(tx + w + wob, y, bark)
            if rng.random() < 0.35:
                pset(tx + wob + rng.choice([-2, 2]), y - 1, bark)

        # canopy mask
        canopy = set()
        cx, cy = tx, base_y - trunk_h - rng.randint(1, 3)
        shape = self._shape_of(species)

        if shape == "round":
            r0 = rng.randint(10, 14)
            canopy |= self._round_canopy(cols, rows, cx, cy, r0, rng, squish_y=1.0)
            for _ in range(3):
                offx = rng.randint(-8, 8);
                offy = rng.randint(-6, 6)
                canopy |= self._round_canopy(cols, rows, cx + offx, cy + offy, r0 - rng.randint(2, 4), rng,
                                             squish_y=rng.uniform(0.8, 1.1))
        elif shape == "willow":
            canopy |= self._round_canopy(cols, rows, cx, cy, rng.randint(10, 12), rng, squish_y=0.8)
            for x in range(cx - 12, cx + 13, 2):
                length = rng.randint(6, 14)
                for j in range(length):
                    canopy.add((x + rng.choice([-1, 0, 1]), cy + j + rng.randint(0, 1)))
        else:  # triangle (pine)
            height = rng.randint(20, 26)
            canopy |= self._triangle_canopy(cols, rows, cx, cy - height // 2, height, rng)

        # fill canopy with leaves
        for (x, y) in canopy:
            if mode == "multi":
                col = self._rand_hex_tuple(rng)
            elif mode == "mono":
                base = leaf_cols[0]
                # slight per-pixel variation so it still looks textured
                delta = rng.choice([-18, -10, 0, 0, 8, 14])
                col = self._darker(base, -delta)  # negative -> lighten
            else:
                col = leaf_cols[rng.randrange(len(leaf_cols))]
                if (x + y) % 2 == 0 and shape != "triangle":
                    col = self._darker(col, 12)
            pset(x, y, col)

        # canopy outline
        for (x, y) in list(canopy):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nb = (x + dx, y + dy)
                if nb not in canopy:
                    pset(nb[0], nb[1], leaf_outline)

        # branches peek-through
        for _ in range(6):
            bx = cx + rng.randint(-8, 8)
            by = cy + rng.randint(-6, 6)
            pset(bx, by, bark_dark)
            if rng.random() < 0.7:
                pset(bx + rng.choice([-1, 1]), by, bark_dark)

        # petals sprinkle for “flower” families
        if species in ("sakura", "jacaranda"):
            petal = leaf_cols[0]
            for _ in range(30):
                x = tx + rng.randint(-14, 14)
                y = base_y + rng.randint(0, 3)
                pset(x, y, self._darker(petal, rng.randint(-10, 30)))

        # tiny shadow
        for dx in range(-10, 11):
            pset(tx + dx, base_y + 1, (0, 0, 0, 70))

        scale_k = max(2, int(scale_k))
        final = pygame.transform.scale(surf,
                                       (surf.get_width() * scale_k // px_base, surf.get_height() * scale_k // px_base))
        return final

    def _get_tree(self, seed, species, scale_k):
        key = (seed, species, int(scale_k))
        if key not in self.tree_cache:
            self.tree_cache[key] = self._build_tree_sprite(seed, species, scale_k)
            # cap cache size
            if len(self.tree_cache) > 256:
                # drop random item to keep memory small
                self.tree_cache.pop(next(iter(self.tree_cache)))
        return self.tree_cache[key]

    # ------------------------------------------------------------
    # grass detail (unchanged)
    # ------------------------------------------------------------
    def draw_grass(self, surf, screen_x, y, world_x):
        state = random.getstate()
        random.seed(int(world_x / 20))
        try:
            for j in range(3):
                bx = screen_x + random.uniform(-6, 6)
                ln = random.uniform(16, 26)
                ang = random.uniform(-0.18, 0.18)
                endx = bx + math.sin(ang) * ln
                endy = y - math.cos(ang) * ln
                green = (80 + random.randint(-20, 20), 160 + random.randint(-20, 20), 90)
                pygame.draw.line(surf, green, (bx, y), (endx, endy), 2)
            if random.random() < 0.15:
                fx = screen_x + random.uniform(-5, 5)
                fy = y - random.uniform(15, 25)
                fcol = random.choice([(255, 100, 150), (255, 200, 100), (100, 150, 255)])
                pygame.draw.circle(surf, fcol, (int(fx), int(fy)), 4)
                pygame.draw.circle(surf, (255, 255, 100), (int(fx), int(fy)), 2)
        finally:
            random.setstate(state)

    # ------------------------------------------------------------
    # update (clouds/flyers parallax) — same as before
    # ------------------------------------------------------------
    def update(self, dt, camera_dx):
        for c in self.clouds:
            c.update(dt, camera_dx)
        for b in self.birds: b.update(dt)
        # update cached ground butterflies (bounded wander)
        for group in self.bfly_block_cache.values():
            for b in group:
                b.update(dt)

        cam = self.g.camera_x
        W = self.g.w
        direction = 1 if camera_dx > 0 else (-1 if camera_dx < 0 else 0)
        margin = W * 0.8
        for c in self.clouds:
            if direction >= 0 and c.x < cam - margin - W:
                c.x = cam + margin + random.randint(50, 200)
                c.y = random.randint(30, 220)
                c.scale = random.uniform(0.6, 1.4)
                c.speed = random.uniform(10, 30)
                c._sprite = None  # force refresh next draw

            elif direction <= 0 and c.x > cam + margin + W:
                c.x = cam - margin - random.randint(50, 200)
                c.y = random.randint(30, 220)
                c.scale = random.uniform(0.6, 1.4)
                c.speed = random.uniform(10, 30)
                c._sprite = None  # <— add this line
        # --- sky decor updates + recycling ---
        W = self.g.w;
        cam = self.g.camera_x

        def recycle(obj, par, margin=220):
            sx = int(obj.x - cam * par + W // 2)
            if sx < -margin:
                obj.x = cam + W + margin + random.randint(80, 260)
            elif sx > W + margin:
                obj.x = cam - margin - random.randint(80, 260)

        for fl in self.flocks:
            fl.update(dt);
            recycle(fl, fl.par, 260)

        for w in self.whales:
            w.update(dt);
            recycle(w, w.par, 360)
        for isl in self.islands:
            isl.update(dt);
            recycle(isl, isl.par, 360)

        for group in self.balloon_block_cache.values():
            for b in group:
                b.update(dt)
        # people idle/wave
        for group in self.people_block_cache.values():
            for person in group:
                person.update(dt)
        # --- NEW: sky messages update + spawn ---
        self.sky_msgs = [m for m in self.sky_msgs if not m.update(dt)]

        self.sky_msg_timer -= dt
        if self.sky_msg_timer <= 0.0:
            if self._spawn_sky_message(camera_dx):
                self.sky_msg_timer = random.uniform(*SKY_MSG_INTERVAL)
            else:
                # try again soon (but still not spamming)
                self.sky_msg_timer = random.uniform(0.6, 1.0)

    # ------------------------------------------------------------
    # draw pass
    # ------------------------------------------------------------
    def draw(self, surf, t_cycle):
        g = self.g

        # --- sky ---
        top, bot = day_night_colors(t_cycle)
        draw_vertical_gradient(surf, top, bot)

        # --- rainbows (world-anchored) drawn AFTER hills so they're visible ---
        par_r = 0.18
        rbw_block_w = getattr(self, "rainbow_block_w", 2400)
        left_world_r = g.camera_x * par_r - g.w // 2
        first_r = int(math.floor(left_world_r / rbw_block_w)) - 1
        count_r = g.w // rbw_block_w + 4
        for I in range(first_r, first_r + count_r):
            self._ensure_rainbow_block(I)
            for arc in self.rainbow_block_cache.get(I, []):
                arc.draw(surf, g.camera_x, g.w, t_cycle, self.g.font)

        # --- layered parallax hills (styles + palettes) ---
        self.draw_hills(surf, t_cycle)
        # prune far rainbow blocks
        if len(self.rainbow_block_cache) > 128:
            keep = set(range(first_r - 4, first_r + count_r + 4))
            for key in list(self.rainbow_block_cache.keys()):
                if key not in keep:
                    self.rainbow_block_cache.pop(key, None)

        # --- whimsical sky decorations (before clouds) ---
        for isl in self.islands:
            isl.draw(surf, g.camera_x, g.w)

        for fl in self.flocks:
            fl.draw(surf, g.camera_x, g.w)
        # Balloons (world-anchored, roam like butterflies)
        # Balloons (world-anchored, roam like butterflies)
        ball_block_w = self.balloon_block_w

        # Balloons parallax lives roughly ~0.22..0.28 — use a conservative window
        pmin, pmax = 0.20, 0.30
        lw_min = g.camera_x * pmin - g.w // 2
        lw_max = g.camera_x * pmax - g.w // 2
        rw_min = g.camera_x * pmin + g.w // 2
        rw_max = g.camera_x * pmax + g.w // 2
        first_ba = int(math.floor(min(lw_min, lw_max) / ball_block_w)) - 3
        last_ba = int(math.floor(max(rw_min, rw_max) / ball_block_w)) + 3

        for i in range(first_ba, last_ba + 1):
            self._ensure_balloon_block(i)
            for b in self.balloon_block_cache.get(i, []):
                b.draw(surf, g.camera_x, g.w)

        for wh in self.whales:
            wh.draw(surf, g.camera_x, g.w)

        # --- flyers before clouds (subtle) ---
        for b in self.birds:
            b.draw(surf, g.camera_x, g.w)

        # --- clouds ---
        for c in self.clouds:
            c.draw(surf, g.camera_x, g.w)

        # --- NEW: floating sky messages (draw on top of sky/clouds) ---
        for m in self.sky_msgs:
            m.draw(surf, g.camera_x, g.w)


        # --- ground ---
        ground_y = g.ground_y
        pygame.draw.rect(surf, self.ground_col, (0, ground_y, g.w, g.h - ground_y))

        # --- cottages on the ground (behind trees) ---
        par_h = self.parallax - 0.02
        pmin_h, pmax_h = par_h - 0.02, par_h + 0.02
        hbw = self.house_block_w
        lw_min = g.camera_x * pmin_h - g.w // 2
        lw_max = g.camera_x * pmax_h - g.w // 2
        rw_min = g.camera_x * pmin_h + g.w // 2
        rw_max = g.camera_x * pmax_h + g.w // 2
        first_h = int(math.floor(min(lw_min, lw_max) / hbw)) - 3
        last_h = int(math.floor(max(rw_min, rw_max) / hbw)) + 3

        for i in range(first_h, last_h + 1):
            self._ensure_house_block(i)
            for hobj in self.house_block_cache.get(i, []):
                sx = int(hobj["world_x"] - g.camera_x * hobj["par"] + g.w // 2)
                if -300 <= sx <= g.w + 300:
                    sp = hobj["sprite"]
                    surf.blit(sp, (sx - hobj["w"] // 2, g.ground_y - sp.get_height()))
        # prune far cottage blocks
        if len(self.house_block_cache) > 256:
            keep = set(range(first_h - 20, last_h + 20))
            for key in list(self.house_block_cache.keys()):
                if key not in keep:
                    self.house_block_cache.pop(key, None)

        # ---------- PIXEL TREES (stable per-block cache) ----------
        # (keep existing cache; just compute a conservative visible range)
        block_w = self.block_w
        par_base = self.parallax
        min_tree_gap = getattr(self, "min_tree_gap", 90)

        # cover the whole parallax jitter range so trees never pop
        pmin = par_base - 0.025
        pmax = par_base + 0.025
        lw_min = g.camera_x * pmin - g.w // 2
        lw_max = g.camera_x * pmax - g.w // 2
        rw_min = g.camera_x * pmin + g.w // 2
        rw_max = g.camera_x * pmax + g.w // 2
        start_i = int(math.floor(min(lw_min, lw_max) / block_w)) - 3
        end_i = int(math.floor(max(rw_min, rw_max) / block_w)) + 3

        for i in range(start_i, end_i + 1):
            if i not in self.tree_block_cache:
                rng = self._rng(i * 71143)
                n = rng.choices([1, 2], weights=[0.35, 0.65])[0]
                trees = []
                for j in range(n):
                    s2 = i * 71143 + 97 * j
                    rr = self._rng(s2)

                    species = rr.choices(
                        ["sakura", "jacaranda", "maple", "oak", "pine", "willow",
                         "red", "yellow", "blue", "lightblue", "turquoise",
                         "orange", "green", "darkgreen", "lightgreen",
                         "hexmono", "hexmulti"],
                        weights=[1] * 17, k=1
                    )[0]

                    local_x = rr.uniform(30, block_w - 30)

                    scale_k = rr.choices([2, 3, 4], weights=[1, 8, 2])[0]
                    tree_surf = self._get_tree(s2, species, scale_k)
                    tree_w = tree_surf.get_width()

                    if trees:
                        last = trees[-1]
                        size_gap = (last["w"] + tree_w) // 2
                        required = max(min_tree_gap, size_gap)
                        prev_local_x = last["world_x"] - i * block_w
                        if local_x - prev_local_x < required:
                            local_x = prev_local_x + required

                    local_x = max(30, min(block_w - 30, local_x))

                    world_x = i * block_w + local_x
                    par_i = par_base + rr.uniform(-0.02, 0.02)

                    trees.append({"world_x": world_x, "surf": tree_surf, "w": tree_w, "par": par_i})

                self.tree_block_cache[i] = trees

            # Draw trees for this block
            for t in self.tree_block_cache[i]:
                sx = int(t["world_x"] - g.camera_x * t["par"] + g.w // 2)
                if -200 <= sx <= g.w + 200:
                    s = t["surf"]
                    surf.blit(s, (sx - t["w"] // 2, ground_y - s.get_height()))

        # --- people (ground NPCs) ---
        par_p = self.parallax + 0.005
        pmin_p, pmax_p = par_p - 0.02, par_p + 0.02
        pbw = self.people_block_w
        lw_min = g.camera_x * pmin_p - g.w // 2
        lw_max = g.camera_x * pmax_p - g.w // 2
        rw_min = g.camera_x * pmin_p + g.w // 2
        rw_max = g.camera_x * pmax_p + g.w // 2
        first_p = int(math.floor(min(lw_min, lw_max) / pbw)) - 3
        last_p = int(math.floor(max(rw_min, rw_max) / pbw)) + 3

        for i in range(first_p, last_p + 1):
            self._ensure_people_block(i)
            for h in self.people_block_cache.get(i, []):
                sx = int(h.world_x - g.camera_x * h.par + g.w // 2)
                if -200 <= sx <= g.w + 200:
                    h.draw(surf, g.camera_x, g.w)

        # prune far people blocks
        if len(self.people_block_cache) > 512:
            keep = set(range(first_p - 20, last_p + 20))
            for key in list(self.people_block_cache.keys()):
                if key not in keep:
                    self.people_block_cache.pop(key, None)

        # Prune far-away cached blocks to keep memory bounded
        if len(self.tree_block_cache) > self.max_tree_blocks:
            keep = set(range(start_i - 20, end_i + 20))
            for k in list(self.tree_block_cache.keys()):
                if k not in keep:
                    self.tree_block_cache.pop(k, None)

        # --- foreground grass + flowers ---
        for pos in range(-self.tile_size, g.w + self.tile_size, self.tile_size):
            world_x = pos + (g.camera_x % (1 << 30))
            self.draw_grass(surf, pos, ground_y, world_x)

        # --- ground butterflies (world-anchored clusters) ---
        bfly_block_w = getattr(self, "bfly_block_w", 420)
        # same conservative pmin/pmax window as trees
        lw_min = g.camera_x * pmin - g.w // 2
        lw_max = g.camera_x * pmax - g.w // 2
        rw_min = g.camera_x * pmin + g.w // 2
        rw_max = g.camera_x * pmax + g.w // 2
        first_b = int(math.floor(min(lw_min, lw_max) / bfly_block_w)) - 3
        last_b = int(math.floor(max(rw_min, rw_max) / bfly_block_w)) + 3

        for i in range(first_b, last_b + 1):
            self._ensure_bfly_block(i)
            for b in self.bfly_block_cache.get(i, []):
                b.draw(surf, g.camera_x, g.w)

        # prune far butterfly blocks
        if len(self.bfly_block_cache) > 512:
            keep = set(range(first_b - 20, last_b + 20))
            for key in list(self.bfly_block_cache.keys()):
                if key not in keep:
                    self.bfly_block_cache.pop(key, None)





# ============================================================
# Game
# ============================================================
class Game:
    def __init__(self, width=1024, height=640):
        pygame.init()
        self.music = RandomMusicPlayer(MUSIC_DIR, volume=0.6)
        self.music.start()

        pygame.display.set_caption(GAME_TITLE)
        self.flags = 0
        self.screen = pygame.display.set_mode((width, height), self.flags)
        self.w, self.h = width, height
        self.clock = pygame.time.Clock()
        self.running = True
        self.photo_mode = False
        self.cozy_filter = True
        self.muted = False

        self.walk_mode = False   # WALK MODE: global toggle
        self.walk_buffer = {
            "coins": [],
            "mushrooms": [],
            "trampolines": [],
            "gates": [],
            "powerups": [],
        }

        self.theatre_mode = False
        self._dash_held_prev = False  # used only for manual dash edge-detect
        # tiny brain state for Theatre mode
        self._ai = {
            "intent": "right",
            "timer": 0.0,
            "jump_hold": 0.0,
            "dash_cd": 0.0,
            "sleep_cd": 0.0,
            "sleep_t": 0.0,
        }

        self.font = pygame.font.SysFont("fredoka one,fredoka,baloo,arialrounded,arial", 28)
        self.bigfont = pygame.font.SysFont("fredoka one,fredoka,baloo,arialrounded,arial", 64)
        self.smallfont = pygame.font.SysFont("arial,verdana", 18)

        self.scene = pygame.Surface((self.w, self.h)).convert()
        self.glow = pygame.Surface((self.w, self.h), pygame.SRCALPHA).convert_alpha()

        self._glow_small = pygame.Surface((self.w // 3, self.h // 3), pygame.SRCALPHA)
        self._glow_big = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        self.save_path = os.path.join(os.path.dirname(__file__), "cat_wanderer_save.json")
        self.theme = "normal"
        self.bg = NormalBackground(self)

        self.best_distance = 0
        self.load_save()

        self.reset(first=True)

    # -----------------------------
    def _theatre_brain(self, dt):
        """Return (left, right, jump_held, dash_pressed) when Theatre mode is ON."""
        s = self._ai
        # decay timers
        s["timer"] = max(0.0, s["timer"] - dt)
        s["jump_hold"] = max(0.0, s["jump_hold"] - dt)
        s["dash_cd"] = max(0.0, s["dash_cd"] - dt)
        s["sleep_cd"] = max(0.0, s["sleep_cd"] - dt)

        # handle sleep timing
        if self.cat.sleeping:
            s["sleep_t"] -= dt
            if s["sleep_t"] <= 0 and random.random() < 0.25:
                self.cat.sleeping = False  # wake up sometimes after timer
        else:
            # rare decision to sleep (only if on ground and cooldown passed)
            if self.cat.on_ground and s["sleep_cd"] <= 0 and random.random() < 0.015:
                self.cat.sleeping = True
                s["sleep_t"] = random.uniform(1.8, 4.0)
                s["sleep_cd"] = random.uniform(8.0, 14.0)

        # pick a new short-lived intent when timer elapses
        if s["timer"] <= 0:
            r = random.random()
            if r < 0.68:
                s["intent"], s["timer"] = "right", random.uniform(0.6, 1.6)
            elif r < 0.82:
                s["intent"], s["timer"] = "left", random.uniform(0.4, 1.0)
            elif r < 0.90:
                s["intent"], s["timer"] = "idle", random.uniform(0.4, 1.0)
            elif r < 0.97:
                s["intent"], s["timer"] = "hop", random.uniform(0.2, 0.5)
                if self.cat.on_ground and not self.cat.sleeping:
                    s["jump_hold"] = random.uniform(0.10, 0.25)
            else:
                s["intent"], s["timer"] = "sleep", random.uniform(2.0, 4.0)
                if self.cat.on_ground:
                    self.cat.sleeping = True
                    s["sleep_t"] = s["timer"]

        # translate intent -> controls
        left = right = jump_held = dash_pressed = False
        if s["intent"] == "right":
            right = True
            # occasional small hop while moving
            if self.cat.on_ground and not self.cat.sleeping and random.random() < 0.03:
                s["jump_hold"] = random.uniform(0.05, 0.18)
        elif s["intent"] == "left":
            left = True
        elif s["intent"] == "hop":
            right = True  # still trending right
        elif s["intent"] == "idle":
            pass
        elif s["intent"] == "sleep":
            # already handled by sleep_t
            pass

        if s["jump_hold"] > 0 and not self.cat.sleeping:
            jump_held = True

        # rare dash burst while moving
        if s["dash_cd"] <= 0 and (left or right) and not self.cat.sleeping and random.random() < 0.08:
            dash_pressed = True
            s["dash_cd"] = random.uniform(1.2, 2.2)

        return left, right, jump_held, dash_pressed

    def flush_walk_buffer(self):
        self.collectibles.extend(self.walk_buffer["coins"])
        self.mushrooms.extend(self.walk_buffer["mushrooms"])
        self.trampolines.extend(self.walk_buffer["trampolines"])
        self.gates.extend(self.walk_buffer["gates"])
        self.powerups.extend(self.walk_buffer["powerups"])
        for k in self.walk_buffer:
            self.walk_buffer[k].clear()

    def load_save(self):
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.theme = data.get('theme', 'normal')
                    self.best_distance = float(data.get('best_distance', 0.0))
                    self.hill_style = int(data.get('hill_style', 0))
                    self.hill_palette = int(data.get('hill_palette', 0))
            except Exception:
                pass

    def save_save(self):
        try:
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'theme': self.theme,
                    'best_distance': self.best_distance,
                    'hill_style': getattr(self, 'hill_style', 0),
                    'hill_palette': getattr(self, 'hill_palette', 0)
                }, f)
        except Exception:
            pass

    # -----------------------------
    # make this the ONLY theme setter
    def set_theme(self, _name="normal"):
        self.theme = "normal"
        self.bg = NormalBackground(self)  # no references to SciFi/Medieval

    # -----------------------------
    def reset(self, first=False):
        self.state = "menu" if first else "play"
        self.t = 0
        self.shake = 0.0
        self.ground_y = int(self.h * 0.82)
        self.camera_x = 0.0
        self.prev_camera_x = 0.0

        self.cat = PlayerCat(0.0, self.ground_y)

        self.particles = []
        self.collectibles = []
        self.powerups = []  # bell/fish/wings
        self.mushrooms = []
        self.trampolines = []
        self.puddles = []
        self.gates = []
        self.spawn_x = -400
        self.day_cycle = 0.15
        DAY_NIGHT_LENGTH_SEC = 600  # 10 minutes

        # in reset()
        self.cycle_speed = 1.0 / DAY_NIGHT_LENGTH_SEC
        # gameplay trackers
        self.distance = 0.0
        self.start_x = self.cat.x
        self.coins = 0

        # dialogue queue
        self.speeches = []  # [text, ttl]

        self.screenshot_id = 1

        self.set_theme(self.theme)
        if not hasattr(self, 'hill_style'):   self.hill_style = 0  # 0=mixed, 1=rolling, 2=mountains
        if not hasattr(self, 'hill_palette'): self.hill_palette = 0  # see palettes below
        self.hill_palette_names = ["Alpine", "Spring", "Desert", "Lavender", "Teal"]

    # -----------------------------
    def say(self, text, ttl=2.4):
        self.speeches.append([text, ttl])

    def spawn_chunk(self, start_x, end_x):
        """
        Spawn gameplay objects between [start_x, end_x).
        In walk mode we *still* run the normal spawn rolls and x-advances so
        the RNG stream and spacing are identical to normal. We simply do not
        append non-puddle objects while walk_mode is True.
        """
        x = start_x
        while x < end_x:
            # --- normal spawn roll (always run, even in walk mode) ---
            roll = random.random()

            if roll < 0.45:
                # 1–3 coins in a cute arc
                n = random.randint(1, 3)
                base_y = self.ground_y - random.randint(50, 110)
                # Only spawn if not walking
                if not self.walk_mode:
                    for i in range(n):
                        self.collectibles.append(Coin(x + i * 28, base_y - i * 6))
                # keep exact same x-advance and randomness as normal
                x += 120 + random.randint(-30, 40)

            elif roll < 0.70:
                # platforms & puddles
                r2 = random.random()
                if r2 < 0.4:
                    if not self.walk_mode:
                        self.mushrooms.append(Mushroom(x, self.ground_y))
                    x += 140
                elif r2 < 0.7:
                    if not self.walk_mode:
                        self.trampolines.append(Trampoline(x, self.ground_y))
                    x += 180
                else:
                    # puddles are allowed in walk mode (rate unchanged)
                    self.puddles.append(Puddle(x, self.ground_y))
                    x += 160

            elif roll < 0.85:
                # teleport gate
                if not self.walk_mode:
                    self.gates.append(TeleportGate(x, self.ground_y))
                x += 240

            else:
                # powerups
                kind = random.choice(["bell", "fish", "wings"])  # consume RNG either way
                if not self.walk_mode:
                    self.powerups.append(PowerUp(x, self.ground_y - 30, kind))
                x += 200

            # same jitter as normal path
            x += random.randint(30, 70)

        self.spawn_x = end_x

    # -----------------------------
    def spawn_ambient(self, dt):
        t = self.day_cycle
        is_night = (t > 0.70 or t < 0.08)

        if self.theme == "normal":
            if not is_night:
                if random.random() < 2.0 * dt:
                    x = self.w // 2 + random.uniform(-220, 220)
                    y = random.uniform(-10, 60)
                    vx = random.uniform(-20, -6)
                    vy = random.uniform(20, 40)
                    self.particles.append(
                        Particle(x, y, vx, vy, 2.5, random.randint(2, 4), (255, 190, 220), glow=False))
            else:
                if random.random() < 2.0 * dt:
                    x = self.w // 2 + random.uniform(-260, 260)
                    y = random.uniform(40, self.h * 0.7)
                    vx = random.uniform(-10, 10)
                    vy = random.uniform(-6, 6)
                    self.particles.append(Particle(x, y, vx, vy, 2.0, 2, (255, 240, 120), glow=True))

        elif self.theme == "scifi":
            if random.random() < 2.6 * dt:
                x = self.w // 2 + random.uniform(-260, 260)
                y = random.uniform(0, self.h * 0.7)
                vx = random.uniform(-20, 20)
                vy = random.uniform(-10, 10)
                self.particles.append(Particle(x, y, vx, vy, 1.6, random.randint(2, 3), (0, 255, 240), glow=True))
        else:
            if random.random() < 2.2 * dt:
                x = self.w // 2 + random.uniform(-260, 260)
                y = self.ground_y + random.uniform(-6, 6)
                vx = random.uniform(-10, 10)
                vy = random.uniform(-30, -10)
                self.particles.append(Particle(x, y, vx, vy, 1.8, 2, (255, 170, 70), glow=False))

        # Dash spark trail
        if self.cat.dash_time > 0 and random.random() < 16 * dt:
            c = (250, 197, 160) if self.theme != "scifi" else (0, 255, 240)
            self.particles.append(Particle(self.w // 2, self.cat.y - 30 + random.uniform(-8, 8),
                                           random.uniform(-60, 60), random.uniform(-40, 40),
                                           random.uniform(0.2, 0.4), random.randint(3, 5), c, glow=True))

    # -----------------------------
    def check_collisions(self, dt):
        cat = self.cat
        # Coins
        for y in self.collectibles:
            y.update(dt, cat)
        for y in list(self.collectibles):
            if math.hypot(y.x - cat.x, (y.y) - (cat.y - 20)) <= 22:
                self.collectibles.remove(y)
                self.coins += 1
                # small coin sparkle
                for _ in range(6):
                    ang = random.uniform(0, math.tau)
                    sp = random.uniform(40, 110)
                    self.particles.append(
                        Particle(self.w // 2, cat.y - 36, math.cos(ang) * sp, math.sin(ang) * sp, 0.4, 3,
                                 (255, 220, 100), glow=True))

        # Powerups
        for p in list(self.powerups):
            if abs(p.x - cat.x) < 26 and abs((p.y) - (cat.y - 30)) < 26:
                self.powerups.remove(p)
                if p.kind == "bell":
                    cat.give_power("bell", 10.0);
                    self.say("Ting! Coin magnet!")
                elif p.kind == "fish":
                    cat.give_power("fish", 5.0);
                    self.say("Zoom! Speed burst!")
                else:
                    cat.give_power("wings", 8.0);
                    self.say("Whee! I have wings!")

        # Mushrooms (bounce)
        for m in self.mushrooms:
            if abs(m.x - cat.x) < 30 and cat.on_ground:
                cat.vy = -680
                cat.on_ground = False
                cat.just_jumped = True
                m.wobble = 6
                self.shake = 0.2

        # Trampolines (bigger bounce)
        for tr in self.trampolines:
            if abs(tr.x - cat.x) < 50 and cat.on_ground:
                cat.vy = -900
                cat.on_ground = False
                cat.just_jumped = True
                tr.pump()
                self.shake = 0.25

        # Teleport gates
        for g in self.gates:
            g.update(dt)
            if g.cooldown <= 0 and abs(g.x - cat.x) < 26 and abs((g.y - 40) - (cat.y - 40)) < 36:
                shift = random.randint(380, 620)
                cat.x += shift
                g.cooldown = 1.5
                self.say("Whoosh! Teleport!")

        # Puddles — slow AND reset buffs (with small cooldown)
        for p in self.puddles:
            p.cooldown = max(0.0, p.cooldown - dt)
            if abs(p.x - cat.x) < 50 and cat.on_ground:
                cat.vx *= 0.6
                if p.cooldown <= 0.0:
                    splash_col = (110, 170, 230) if self.theme == "normal" else (
                        (0, 255, 240) if self.theme == "scifi" else (140, 110, 80))
                    for _ in range(14):
                        ang = random.uniform(-0.3, math.pi - 0.3)
                        sp = random.uniform(80, 180)
                        self.particles.append(Particle(self.w // 2, self.ground_y - 10,
                                                       math.cos(ang) * sp, -abs(math.sin(ang)) * sp,
                                                       0.35, random.randint(2, 3), splash_col, glow=False))
                    if (self.cat.magnet > 0) or (self.cat.speed_boost > 0) or (self.cat.wings > 0):
                        self.say("Splash! Buffs washed off…")
                    self.cat.magnet = 0.0
                    self.cat.speed_boost = 0.0
                    self.cat.wings = 0.0
                    p.cooldown = 0.6

    # -----------------------------
    def update(self, dt):
        self.t += dt
        self.day_cycle = (self.day_cycle + self.cycle_speed * dt) % 1.0

        if self.theatre_mode:
            left, right, jump_held, dash_pressed = self._theatre_brain(dt)
        else:
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            jump_held = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]

            # HOLD-TO-DASH: retrigger automatically when a held dash ends
            dash_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            dash_pressed = dash_held and (not self._dash_held_prev or self.cat.dash_time <= 0)
            self._dash_held_prev = dash_held

        # Player update (walk_mode handled inside PlayerCat)
        self.cat.update(dt, left, right, jump_held, dash_pressed, walk_mode=self.walk_mode)

        # Camera follow
        self.prev_camera_x = self.camera_x
        target = self.cat.x
        self.camera_x = lerp(self.camera_x, target, clamp(8.0 * dt, 0, 1))
        camera_dx = (self.camera_x - self.prev_camera_x) / max(dt, 1e-6)

        # Backgrounds
        self.bg.update(dt, camera_dx)

        # Spawner chunks ahead
        if self.cat.x + 800 > self.spawn_x:
            self.spawn_chunk(self.spawn_x, self.cat.x + 1000)

        # Collisions & interactions
        self.check_collisions(dt)

        # Particles
        self.spawn_ambient(dt)
        self.particles[:] = [p for p in self.particles if not p.update(dt)]

        # Update props
        for m in self.mushrooms:
            m.update(dt)
        for tr in self.trampolines:
            tr.bounce = max(0.0, tr.bounce - dt * 1.6)

        # Distance
        self.distance = self.cat.x - self.start_x
        self.best_distance = max(self.best_distance, abs(self.distance))

        # Age speech bubbles
        for s in list(self.speeches):
            s[1] -= dt
            if s[1] <= 0:
                self.speeches.remove(s)

    # -----------------------------
    def draw_props(self, surf):
        cam = self.camera_x
        # Mushrooms & trampolines & puddles
        for m in self.mushrooms:
            sx = int(m.x - cam + self.w // 2)
            if -50 <= sx <= self.w + 50:
                m.draw(surf, sx, self.ground_y, self.theme)
        for tr in self.trampolines:
            sx = int(tr.x - cam + self.w // 2)
            if -100 <= sx <= self.w + 100:
                tr.draw(surf, sx, self.ground_y, self.theme)
        for p in self.puddles:
            sx = int(p.x - cam + self.w // 2)
            if -80 <= sx <= self.w + 80:
                p.draw(surf, sx, self.ground_y, self.t, self.theme)

        # Teleport gates
        for gte in self.gates:
            sx = int(gte.x - cam + self.w // 2)
            if -120 <= sx <= self.w + 120:
                gte.draw(surf, sx, self.ground_y, self.t, self.theme)

        # Coins
        for y in self.collectibles:
            sx = int(y.x - cam + self.w // 2)
            if -40 <= sx <= self.w + 40:
                y.draw(surf, sx, self.ground_y)

        # Powerups
        for pu in self.powerups:
            sx = int(pu.x - cam + self.w // 2)
            if -40 <= sx <= self.w + 40:
                pu.draw(surf, sx, self.ground_y)

    # -----------------------------
    def render(self):
        scene = self.scene
        scene.fill((0, 0, 0))

        # Background per theme
        self.bg.draw(scene, self.day_cycle)

        # Ground finish layers
        if self.theme == "scifi":
            haze = pygame.Surface((self.w, 120), pygame.SRCALPHA)
            pygame.draw.rect(haze, (0, 255, 240, 35), (0, 0, self.w, 120))
            scene.blit(haze, (0, int(self.h * 0.76)))
        else:
            pygame.draw.rect(scene, (235, 229, 220), (0, self.ground_y, self.w, self.h - self.ground_y))

        # Props / pickups
        self.draw_props(scene)

        # Player
        self.cat.draw(scene, self.theme, offset=(self.w // 2 - self.cat.x, 0))

        # Speech bubbles near the cat (stack upwards)
        if self.speeches:
            base_x = self.w // 2
            base_y = int(self.cat.y - 70)
            for i, (msg, ttl) in enumerate(self.speeches):
                a = int(255 * clamp(ttl / 2.4, 0, 1))
                draw_speech_bubble(scene, base_x, base_y - i * 48, msg, self.font, alpha=a)

        # Particles — glow pass + normal
        self.glow.fill((0, 0, 0, 0))
        for p in self.particles:
            if p.glow:
                p.draw(self.glow)
            else:
                p.draw(scene)
        pygame.transform.smoothscale(self.glow, self._glow_small.get_size(), self._glow_small)
        pygame.transform.smoothscale(self._glow_small, self._glow_big.get_size(), self._glow_big)
        scene.blit(self._glow_big, (0, 0), special_flags=pygame.BLEND_ADD)

        # Cozy filter
        if self.cozy_filter:
            warm = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            warm.fill((255, 200, 150, 10))
            scene.blit(warm, (0, 0), special_flags=pygame.BLEND_MULT)

        # Vignette
        draw_vignette(scene, 0.42)

        # UI
        if not self.photo_mode:
            self.draw_ui(scene)

        # Screen shake
        ox = oy = 0
        if self.shake > 0:
            mag = 4 * self.shake
            ox = random.uniform(-mag, mag);
            oy = random.uniform(-mag, mag)
            self.shake = max(0.0, self.shake - 0.05)

        self.screen.blit(scene, (ox, oy))
        pygame.display.flip()

    # -----------------------------
    def draw_ui(self, surf):
        # --- Title / theme ---
        theme_title = {
            "normal": "Normal Meadow",
            "scifi": "Sci-Fi Neon City",
            "medieval": "Medieval Kingdom"
        }.get(self.theme, "Normal Meadow")
        label = self.font.render(theme_title, True, (60, 60, 70))
        surf.blit(label, (20, 18))

        # --- Control hints (top-left) ---
        # Main movement row — reflect walk mode by hiding Space/Shift when ON
        if self.walk_mode:
            # Walk-mode: show only walking + sleep, no jump/dash
            hint_text = "←/→ or A/D walk • S sleep • P photo • C cozy"
        else:
            hint_text = "←/→ or A/D walk • Space jump (hold to glide w/ wings) • Shift dash • S sleep • P photo • C cozy"
        hint = self.smallfont.render(hint_text, True, (60, 60, 70))
        surf.blit(hint, (20, 54))

        # Hills/palette row
        hint2 = self.smallfont.render(
            f"H: hills • J: palette  [{['Mixed', 'Rolling', 'Mountains'][self.hill_style]} / {self.hill_palette_names[self.hill_palette]}]",
            True, (60, 60, 70))
        surf.blit(hint2, (20, 74))

        # Walk Mode toggle row (E) — always visible
        if self.walk_mode:
            e_text = "E: Exit Walk Mode"
        else:
            e_text = "E: Enter Walk Mode"
        e_hint = self.smallfont.render(e_text, True, (60, 60, 70))
        surf.blit(e_hint, (20, 94))

        # Theatre Mode toggle row (T) — always visible
        theatre_on = getattr(self, "theatre_mode", False)
        t_text = "T: Exit Theatre Mode" if theatre_on else "T: Enter Theatre Mode"
        t_hint = self.smallfont.render(t_text, True, (60, 60, 70))
        surf.blit(t_hint, (20, 114))

        # --- HUD right (distance & coins) ---
        dist_str = f"Dist {int(self.distance):+d}"
        coin_str = f"Coins {self.coins}"
        hud = self.font.render(f"{dist_str}  |  {coin_str}", True, (60, 60, 70))
        surf.blit(hud, (self.w - hud.get_width() - 20, 18))

        # --- Power indicators (shifted down to avoid overlap with new rows) ---
        px = 22
        py = 138
        if self.cat.magnet > 0:
            pygame.draw.circle(surf, (255, 210, 0), (px, py), 10)
            px += 26
        if self.cat.speed_boost > 0:
            pygame.draw.circle(surf, (110, 200, 255), (px, py), 10)
            px += 26
        if self.cat.wings > 0:
            pygame.draw.circle(surf, (255, 255, 255), (px, py), 10)
            px += 26

        # --- Menus / overlays ---
        if self.state == "menu":
            title = self.bigfont.render("Bal Firarda", True, (60, 50, 70))
            surf.blit(title, (self.w // 2 - title.get_width() // 2, 120))

            tip = self.font.render("Press Space to start wandering", True, (80, 70, 95))
            t = (math.sin(self.t * 3) + 1) / 2
            tip.set_alpha(int(255 * ease_out_quad(t)))
            surf.blit(tip, (self.w // 2 - tip.get_width() // 2, 210))

            t3 = self.smallfont.render("S: sleep toggle • Coins & Distance are your progress.", True, (95, 90, 110))
            surf.blit(t3, (self.w // 2 - t3.get_width() // 2, 260))

            # Teach toggles on the menu as well
            t4 = self.smallfont.render("E: Walk Mode", True,
                                       (92, 88, 108))
            surf.blit(t4, (self.w // 2 - t4.get_width() // 2, 286))

            t5 = self.smallfont.render("T: Theatre Mode", True,
                                       (92, 88, 108))
            surf.blit(t5, (self.w // 2 - t5.get_width() // 2, 308))

        elif self.state == "pause":
            p = self.bigfont.render("Paused", True, (50, 50, 70))
            surf.blit(p, (self.w // 2 - p.get_width() // 2, 160))
            t1 = self.font.render("Esc: resume — R: restart — Q: quit — E: toggle Walk Mode — T: toggle Theatre Mode",
                                  True, (80, 80, 95))
            surf.blit(t1, (self.w // 2 - t1.get_width() // 2, 230))

    # -----------------------------
    def _apply_walk_mode_toggle(self):
        """Apply walk-mode on/off: clean spawns, normalize cat state."""
        if self.walk_mode:
            # purge everything *except* puddles
            self.collectibles.clear()
            self.powerups.clear()
            self.mushrooms.clear()
            self.trampolines.clear()
            self.gates.clear()

            # normalize the cat (kill powers, dash; if mid-air, place on ground)
            self.cat.dash_time = 0.0
            self.cat.speed_boost = 0.0
            self.cat.wings = 0.0
            if not self.cat.on_ground:
                self.cat.y = self.ground_y
                self.cat.vy = 0.0
                self.cat.on_ground = True
                self.cat.coyote = 0.0
                self.cat.jumps_left = 0

            self.say("Walk Mode: on")
        else:
            self.say("Walk Mode: off")

    def save_screenshot(self):
        path = os.path.join(os.path.dirname(__file__), f"neko_wanderer_{self.screenshot_id:03d}.png")
        pygame.image.save(self.scene, path)
        self.screenshot_id += 1
        self.say("I took a photo!")

    # -----------------------------
    def handle_events(self):
        for e in pygame.event.get():
            if hasattr(self, "music") and self.music:
                self.music.handle_event(e)
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: self.set_theme("normal")
                if e.key == pygame.K_t:
                    self.theatre_mode = not self.theatre_mode
                    if self.theatre_mode:
                        self.cat.sleeping = False
                        self.say("Theatre: ON")
                    else:
                        self.say("Theatre: OFF")
                if e.key == pygame.K_e:
                    self.walk_mode = not self.walk_mode
                    self._apply_walk_mode_toggle()

                if e.key == pygame.K_p: self.photo_mode = not self.photo_mode
                if e.key == pygame.K_c: self.cozy_filter = not self.cozy_filter

                if e.key == pygame.K_s:
                    self.cat.sleeping = not self.cat.sleeping
                    self.say("Zzz…") if self.cat.sleeping else self.say("I’m up!")

                if self.state == "menu":
                    if e.key == pygame.K_SPACE:
                        self.state = "play"
                elif self.state == "play":
                    if e.key == pygame.K_ESCAPE:
                        self.state = "pause"
                elif self.state == "pause":
                    if e.key == pygame.K_ESCAPE:
                        self.state = "play"
                    elif e.key == pygame.K_r:
                        self.reset();
                        self.state = "play"
                    elif e.key == pygame.K_q:
                        self.running = False
                if e.key == pygame.K_h:
                    self.hill_style = (self.hill_style + 1) % 3
                    self.say(["Hills: Mixed", "Hills: Rolling", "Hills: Mountains"][self.hill_style])
                if e.key == pygame.K_j:
                    self.hill_palette = (self.hill_palette + 1) % 5
                    self.say(f"Palette: {self.hill_palette_names[self.hill_palette]}")

    # -----------------------------
    def _read_controls(self):
        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        jump_held = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]

        # HOLD-TO-DASH (auto-retrigger when previous dash ends)
        dash_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        dash_pressed = dash_held and (not self._dash_held_prev or self.cat.dash_time <= 0)
        self._dash_held_prev = dash_held

        return left, right, jump_held, dash_pressed

    def run(self):
        dt = 0
        while self.running:
            self.handle_events()
            if self.state == "play":
                self.update(dt)
            self.render()
            dt = self.clock.tick(60) / 1000.0
        self.save_save()
        pygame.quit()


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    Game().run()
