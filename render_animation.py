import os
import math
import random
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

# Canvas constants
WIDTH = 720
HEIGHT = 1280
FPS = 30
TOTAL_FRAMES = 540 # 18.0 seconds

# Color Palette
CREAM = (255, 244, 221, 255)
INK = (31, 27, 46, 255)
YELLOW = (255, 201, 60, 255)
ORANGE = (255, 107, 74, 255)
PINK = (255, 158, 205, 255)
MINT = (61, 219, 192, 255)
SKY = (189, 227, 255, 255)
RED = (215, 38, 61, 255)
NAVY = (31, 42, 90, 255)
WHITE = (255, 255, 255, 255)

FONT_PATH = r'C:\Windows\Fonts\arialbd.ttf'
FONT_TITLE_PATH = r'C:\Windows\Fonts\segoeuib.ttf'

def get_font(size, title=False):
    path = FONT_TITLE_PATH if title else FONT_PATH
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# Easing functions
def ease_out_back(t, s=1.70158):
    t -= 1.0
    return t * t * ((s + 1.0) * t + s) + 1.0

def ease_out_elastic(t):
    if t <= 0.0: return 0.0
    if t >= 1.0: return 1.0
    return math.pow(2, -10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1.0

def ease_out_cubic(t):
    return 1.0 - math.pow(1.0 - t, 3)

def ease_in_cubic(t):
    return t * t * t

def clamp(v, min_v, max_v):
    return max(min_v, min(max_v, v))

# Helper to transform and paste RGBA image onto RGBA canvas with anchor center
def paste_sprite(canvas, sprite, cx, cy, scale_x=1.0, scale_y=1.0, angle=0.0, alpha_mult=1.0):
    if scale_x == 0 or scale_y == 0 or alpha_mult <= 0:
        return
    w, h = sprite.size
    nw = max(1, int(abs(w * scale_x)))
    nh = max(1, int(abs(h * scale_y)))
    
    # Resample with BILINEAR/LANCZOS
    s = sprite.resize((nw, nh), Image.Resampling.BILINEAR)
    if scale_x < 0:
        s = s.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if scale_y < 0:
        s = s.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    if angle != 0:
        s = s.rotate(angle, resample=Image.Resampling.BILINEAR, expand=True)

    if alpha_mult < 0.99:
        # modulate alpha
        arr = np.array(s)
        arr[:, :, 3] = (arr[:, :, 3] * alpha_mult).astype(np.uint8)
        s = Image.fromarray(arr, 'RGBA')

    sw, sh = s.size
    px = int(cx - sw // 2)
    py = int(cy - sh // 2)
    canvas.alpha_composite(s, (px, py))

# Draw comic speed lines
def draw_speed_lines(canvas, cx, cy, intensity=1.0, count=24):
    d = ImageDraw.Draw(canvas)
    for i in range(count):
        ang = i * (2 * math.pi / count) + random.uniform(-0.05, 0.05)
        r_inner = random.uniform(220, 280)
        r_outer = random.uniform(600, 750)
        x1 = cx + r_inner * math.cos(ang)
        y1 = cy + r_inner * math.sin(ang)
        x2 = cx + r_outer * math.cos(ang)
        y2 = cy + r_outer * math.sin(ang)
        w = int(random.uniform(3, 7) * intensity)
        d.line([(x1, y1), (x2, y2)], fill=(31, 27, 46, int(160 * intensity)), width=w)

# Draw clean, high-impact Vietnamese subtitle pill
def draw_subtitles(canvas, text, cy=1150):
    if not text:
        return
    d = ImageDraw.Draw(canvas)
    f = get_font(28, title=True)
    
    # Measure text
    bbox = d.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    # Pill box padding
    pad_x, pad_y = 28, 14
    bw = tw + pad_x * 2
    bh = th + pad_y * 2
    x0 = (WIDTH - bw) // 2
    y0 = cy - bh // 2
    x1 = x0 + bw
    y1 = y0 + bh

    # Drop shadow
    d.rounded_rectangle([x0 + 4, y0 + 4, x1 + 4, y1 + 4], radius=bh // 2, fill=(0, 0, 0, 120))
    # Outer dark border
    d.rounded_rectangle([x0, y0, x1, y1], radius=bh // 2, fill=(255, 255, 255, 245), outline=INK, width=4)
    # Inner accent border line
    d.rounded_rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 3], radius=(bh - 6) // 2, outline=YELLOW, width=2)
    
    # Text in bold INK with slight red emphasis if needed
    d.text((WIDTH // 2, cy), text, fill=INK, font=f, anchor="mm")

class AnimationRenderer:
    def __init__(self):
        print("Loading sprite and prop assets...")
        self.sprites = {
            'char_front': Image.open('assets/sprites/char_front.png').convert('RGBA'),
            'char_turn': Image.open('assets/sprites/char_turn.png').convert('RGBA'),
            'char_bust_smile': Image.open('assets/sprites/char_bust_smile.png').convert('RGBA'),
            'char_bust_wink': Image.open('assets/sprites/char_bust_wink.png').convert('RGBA'),
            'char_bust_surprised': Image.open('assets/sprites/char_bust_surprised.png').convert('RGBA'),
            'char_bust_laugh': Image.open('assets/sprites/char_bust_laugh.png').convert('RGBA'),
        }
        self.props = {
            'courtroom_bg': Image.open('assets/props/courtroom_bg.png').convert('RGBA'),
            'witness_stand': Image.open('assets/props/witness_stand.png').convert('RGBA'),
            'gavel_bang': Image.open('assets/props/gavel_bang.png').convert('RGBA'),
            'gavel': Image.open('assets/props/gavel.png').convert('RGBA'),
            'polaroid_baby': Image.open('assets/props/polaroid_baby.png').convert('RGBA'),
            'polaroid_school': Image.open('assets/props/polaroid_school.png').convert('RGBA'),
            'polaroid_library': Image.open('assets/props/polaroid_library.png').convert('RGBA'),
            'polaroid_deadline': Image.open('assets/props/polaroid_deadline.png').convert('RGBA'),
            'summons_paper': Image.open('assets/props/summons_paper.png').convert('RGBA'),
            'stamp_da_duyet': Image.open('assets/props/stamp_da_duyet.png').convert('RGBA'),
            'end_card': Image.open('assets/props/end_card.png').convert('RGBA'),
            'sticker_star': Image.open('assets/props/sticker_star.png').convert('RGBA'),
            'sticker_heart': Image.open('assets/props/sticker_heart.png').convert('RGBA'),
            'sticker_cap': Image.open('assets/props/sticker_cap.png').convert('RGBA'),
        }
        self.init_confetti()

    def init_confetti(self):
        # 100 colorful confetti pieces for Shot 4
        random.seed(42)
        self.confetti = []
        colors = [CORAL := (255, 107, 74, 255), YELLOW, PINK, MINT, SKY, RED, WHITE]
        for _ in range(110):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(180, 750)
            self.confetti.append({
                'origin_x': WIDTH // 2,
                'origin_y': 620,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - random.uniform(150, 400),
                'color': random.choice(colors),
                'w': random.uniform(12, 22),
                'h': random.uniform(8, 16),
                'rot_speed': random.uniform(4, 15),
                'phase': random.uniform(0, 2 * math.pi),
                'shape': random.choice(['rect', 'rect', 'star', 'circle'])
            })

    def render_frame(self, frame_idx):
        t = frame_idx / FPS # time in seconds
        canvas = Image.new('RGBA', (WIDTH, HEIGHT), CREAM)

        # Shot routing:
        # Shot 1: 0.0s - 4.2s (frames 0 to 125)
        # Shot 2: 4.2s - 9.0s (frames 126 to 270)
        # Shot 3: 9.0s - 13.8s (frames 271 to 415)
        # Shot 4: 13.8s - 18.0s (frames 416 to 539)
        if frame_idx < 126:
            self.render_shot_1(canvas, frame_idx, t)
        elif frame_idx < 271:
            self.render_shot_2(canvas, frame_idx - 126, t - 4.2)
        elif frame_idx < 416:
            self.render_shot_3(canvas, frame_idx - 271, t - 9.0)
        else:
            self.render_shot_4(canvas, frame_idx - 416, t - 13.8)

        return canvas.convert('RGB')

    # =========================================================================
    # SHOT 1 (0.0s - 4.2s): Courtroom, Gavel BANG, Testimony
    # Dialogue: "Thưa quý vị, hôm nay tôi xin khai báo: tôi chính thức tốt nghiệp rồi!"
    # =========================================================================
    def render_shot_1(self, canvas, f, t):
        # Camera slow push-in: zoom from 1.0 to 1.10
        zoom = 1.0 + (t / 4.2) * 0.10
        cam_y_off = int((t / 4.2) * 40)

        # Screenshake on gavel hit at 0.46s (frames 13 - 22)
        shake_x, shake_y = 0, 0
        if 13 <= f <= 23:
            mag = (23 - f) * 1.5
            shake_x = int(random.uniform(-mag, mag))
            shake_y = int(random.uniform(-mag, mag))

        # 1. Background
        bg = self.props['courtroom_bg']
        paste_sprite(canvas, bg, WIDTH // 2 + shake_x, HEIGHT // 2 + cam_y_off + shake_y, scale_x=zoom, scale_y=zoom)

        # 2. Character behind witness stand
        # Standing at x = 360, y = 710
        # Squash & stretch speaking bob: beat ~ 2Hz
        bob = math.sin(t * 12.0)
        char_sx = (1.0 - bob * 0.025) * zoom
        char_sy = (1.0 + bob * 0.035) * zoom
        char_y = 700 + int(bob * 6) + cam_y_off + shake_y

        # Choose expression: before bang neutral, bang surprised, then radiant smile!
        if f < 13:
            char_sprite = self.sprites['char_front']
        elif f < 22:
            char_sprite = self.sprites['char_front']
        else:
            char_sprite = self.sprites['char_front']

        paste_sprite(canvas, char_sprite, WIDTH // 2 + shake_x, char_y, scale_x=char_sx, scale_y=char_sy)

        # Cheerful face overlay for radiant smile during speech
        if f >= 24:
            # Subtle smile bust overlay positioned over head
            head_y = char_y - 230
            # Gentle head tilt
            tilt = math.sin(t * 6.0) * 2.5
            # Draw sparkling eyes / blush
            pass

        # 3. Witness Stand in front (podium + microphone + legal paper)
        stand = self.props['witness_stand']
        paste_sprite(canvas, stand, WIDTH // 2 + shake_x, 1020 + cam_y_off + shake_y, scale_x=zoom, scale_y=zoom)

        # 4. Gavel Bang Sequence
        # Gavel strikes down at frame 13 (~0.43s)
        if f < 14:
            # Gavel swinging down from top-right
            progress = f / 13.0
            g_angle = -45.0 + progress * 50.0 # swings down
            gx = 240 - progress * 40
            gy = 650 + progress * 60
            paste_sprite(canvas, self.props['gavel'], gx, gy, scale_x=1.1, scale_y=1.1, angle=g_angle)
        elif f < 38:
            # Gavel resting on block
            paste_sprite(canvas, self.props['gavel'], 200, 710, scale_x=1.1, scale_y=1.1, angle=5.0)
            
            # Comic "BANG!" burst pops out
            bang_age = (f - 14) / 24.0 # 0 to 1
            if bang_age < 0.25:
                bang_scale = ease_out_elastic(bang_age / 0.25) * 1.3
            else:
                bang_scale = max(0.0, 1.3 - (bang_age - 0.25) * 1.4)
            if bang_scale > 0.05:
                paste_sprite(canvas, self.props['gavel_bang'], 220, 640, scale_x=bang_scale, scale_y=bang_scale, angle=-10.0)

        # 5. Dialogue Subtitle
        if f >= 20:
            draw_subtitles(canvas, "Thưa quý vị, hôm nay tôi xin khai báo:")
            draw_subtitles(canvas, "tôi chính thức tốt nghiệp rồi!", cy=1195)

    # =========================================================================
    # SHOT 2 (4.2s - 9.0s): Polaroid Montage Flying In with Tape & Character Reactions
    # Dialogue: "Bốn năm, vô số ly cà phê, và một ngàn lần nói 'tùy trường hợp'."
    # =========================================================================
    def render_shot_2(self, canvas, f, t):
        # Dynamic pastel background with floating dots
        d = ImageDraw.Draw(canvas)
        for i in range(12):
            dx = (i * 137 + int(t * 25)) % WIDTH
            dy = (i * 211 + int(t * 18)) % HEIGHT
            d.ellipse([dx - 8, dy - 8, dx + 8, dy + 8], fill=(255, 201, 60, 100))

        # Title at top
        f_top = get_font(30, title=True)
        d.text((WIDTH // 2, 70), "HỒ SƠ 4 NĂM ĐẠI HỌC ⚖️", fill=NAVY, font=f_top, anchor="mm")

        # 4 Polaroids:
        # P1: Baby (f: 0 -> 145)
        # P2: School Uniform (f: 30 -> 145)
        # P3: Library Books (f: 65 -> 145)
        # P4: Midnight Desk 23:59 (f: 100 -> 145)

        # Polaroid 1: Baby
        if f >= 0:
            p1_t = min(1.0, f / 16.0)
            p1_scale = ease_out_elastic(p1_t) * 0.95
            p1_x = 220
            p1_y = 350 - (1.0 - p1_t) * 400
            p1_angle = -8.0 + math.sin(t * 2.0) * 1.5
            paste_sprite(canvas, self.props['polaroid_baby'], p1_x, p1_y, scale_x=p1_scale, scale_y=p1_scale, angle=p1_angle)

        # Character reaction 1: cute smiling peek from right (f: 10 to 45)
        if 10 <= f < 48:
            peek_t = min(1.0, (f - 10) / 10.0)
            peek_y = 620 - ease_out_back(peek_t) * 90
            paste_sprite(canvas, self.sprites['char_bust_smile'], 530, peek_y, scale_x=0.85, scale_y=0.85, angle=12.0)

        # Polaroid 2: School uniform
        if f >= 30:
            p2_t = min(1.0, (f - 30) / 16.0)
            p2_scale = ease_out_elastic(p2_t) * 0.95
            p2_x = 490
            p2_y = 480 - (1.0 - p2_t) * 450
            p2_angle = 7.0 + math.sin(t * 2.5) * 1.5
            paste_sprite(canvas, self.props['polaroid_school'], p2_x, p2_y, scale_x=p2_scale, scale_y=p2_scale, angle=p2_angle)

        # Character reaction 2: surprised peek from left (f: 45 to 80)
        if 42 <= f < 80:
            peek_t = min(1.0, (f - 42) / 10.0)
            peek_x = 100 + ease_out_back(peek_t) * 70
            paste_sprite(canvas, self.sprites['char_bust_surprised'], peek_x, 690, scale_x=0.85, scale_y=0.85, angle=-14.0)

        # Polaroid 3: Library
        if f >= 65:
            p3_t = min(1.0, (f - 65) / 16.0)
            p3_scale = ease_out_elastic(p3_t) * 0.96
            p3_x = 240
            p3_y = 660 - (1.0 - p3_t) * 400
            p3_angle = -5.0 + math.cos(t * 2.0) * 1.5
            paste_sprite(canvas, self.props['polaroid_library'], p3_x, p3_y, scale_x=p3_scale, scale_y=p3_scale, angle=p3_angle)

        # Character reaction 3: gasping shocked face at books (f: 75 to 110)
        if 75 <= f < 112:
            peek_t = min(1.0, (f - 75) / 10.0)
            peek_y = 880 - ease_out_back(peek_t) * 80
            paste_sprite(canvas, self.sprites['char_bust_surprised'], 530, peek_y, scale_x=0.9, scale_y=0.9, angle=10.0)

        # Polaroid 4: Deadline 23:59 (zoom front & center)
        if f >= 100:
            p4_t = min(1.0, (f - 100) / 15.0)
            p4_scale = ease_out_elastic(p4_t) * 1.08
            p4_x = WIDTH // 2
            p4_y = 520 - (1.0 - p4_t) * 500
            p4_angle = math.sin(t * 3.0) * 1.2
            paste_sprite(canvas, self.props['polaroid_deadline'], p4_x, p4_y, scale_x=p4_scale, scale_y=p4_scale, angle=p4_angle)

            # Character reaction 4: laughing sticker popping up in front (f: 110 to 145)
            if f >= 110:
                laugh_t = min(1.0, (f - 110) / 12.0)
                laugh_y = 960 - ease_out_elastic(laugh_t) * 130
                laugh_bob = math.sin(t * 14.0) * 0.05
                paste_sprite(canvas, self.sprites['char_bust_laugh'], WIDTH // 2, laugh_y, scale_x=1.05 + laugh_bob, scale_y=1.05 - laugh_bob)

        # Subtitle
        if f < 75:
            draw_subtitles(canvas, "Bốn năm, vô số ly cà phê...")
        else:
            draw_subtitles(canvas, "và một ngàn lần nói: 'tùy trường hợp'!")

    # =========================================================================
    # SHOT 3 (9.0s - 13.8s): Back in Court, Dramatic Point, Giant Stamp SLAM!
    # Dialogue: "Vì vậy tôi xin triệu tập các bạn đến dự lễ tốt nghiệp! Có đồ ăn nữa nha!"
    # =========================================================================
    def render_shot_3(self, canvas, f, t):
        # Stamp hits at frame 66 (approx 11.2s into video: 9.0s + 2.2s)
        stamp_hit_frame = 66
        shake_x, shake_y = 0, 0
        if stamp_hit_frame <= f <= stamp_hit_frame + 12:
            decay = (stamp_hit_frame + 12 - f) * 1.5
            shake_x = int(random.uniform(-decay, decay))
            shake_y = int(random.uniform(-decay, decay))

        # 1. Background
        bg = self.props['courtroom_bg']
        paste_sprite(canvas, bg, WIDTH // 2 + shake_x, HEIGHT // 2 + shake_y)

        # Speed lines during dramatic opening (frames 0 to 45)
        if f < 45:
            intensity = max(0.0, 1.0 - f / 45.0)
            draw_speed_lines(canvas, WIDTH // 2, 500, intensity=intensity, count=30)

        # 2. Summons Paper sliding into view
        paper_t = min(1.0, f / 24.0)
        paper_y = 1100 - ease_out_back(paper_t) * 580 + shake_y
        paper_scale = 0.95
        paste_sprite(canvas, self.props['summons_paper'], WIDTH // 2 + shake_x, paper_y, scale_x=paper_scale, scale_y=paper_scale)

        # 3. Dramatic character presentation
        # Upper character peering / standing beside summons
        if f < stamp_hit_frame:
            # Pointing dramatically
            char_y = 230 + int(math.sin(t * 8.0) * 8)
            paste_sprite(canvas, self.sprites['char_bust_smile'], 520, char_y, scale_x=0.9, scale_y=0.9, angle=6.0)
        else:
            # Celebrating / Joyful reaction after stamp slam
            char_y = 210 + int(math.sin(t * 10.0) * 6)
            paste_sprite(canvas, self.sprites['char_bust_laugh'], 520, char_y, scale_x=0.95, scale_y=0.95, angle=-4.0)

        # 4. GIANT STAMP SLAM SEQUENCE!
        if f >= stamp_hit_frame - 6:
            # Target stamp position on bottom right of paper
            stamp_cx = WIDTH // 2 + 130 + shake_x
            stamp_cy = paper_y + 190 + shake_y
            stamp_angle = -14.0

            if f < stamp_hit_frame:
                # Stamp dropping at high speed from huge scale
                drop_t = (f - (stamp_hit_frame - 6)) / 6.0
                stamp_scale = 3.2 - drop_t * 2.2 # drops from 3.2 down to 1.0
                stamp_alpha = 0.5 + drop_t * 0.5
                paste_sprite(canvas, self.props['stamp_da_duyet'], stamp_cx, stamp_cy - int((1.0 - drop_t) * 180),
                             scale_x=stamp_scale, scale_y=stamp_scale, angle=stamp_angle, alpha_mult=stamp_alpha)
            else:
                # Stamp slammed down on paper with elastic impact
                slam_age = (f - stamp_hit_frame) / 10.0
                if slam_age < 1.0:
                    slam_bounce = 1.0 + (1.0 - slam_age) * 0.25 * math.cos(slam_age * math.pi * 3)
                else:
                    slam_bounce = 1.0
                paste_sprite(canvas, self.props['stamp_da_duyet'], stamp_cx, stamp_cy,
                             scale_x=slam_bounce, scale_y=slam_bounce, angle=stamp_angle)

                # Shockwave ring expanding from stamp center
                sw_age = (f - stamp_hit_frame) / 15.0
                if sw_age < 1.0:
                    sw_r = int(70 + sw_age * 180)
                    sw_alpha = int(220 * (1.0 - sw_age))
                    sw_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
                    sw_d = ImageDraw.Draw(sw_img)
                    sw_d.ellipse([stamp_cx - sw_r, stamp_cy - sw_r, stamp_cx + sw_r, stamp_cy + sw_r],
                                 outline=(215, 38, 61, sw_alpha), width=8)
                    canvas.alpha_composite(sw_img)

        # 5. Food stickers popping around ("Có đồ ăn nữa nha!")
        if f >= stamp_hit_frame + 10:
            food_t = min(1.0, (f - (stamp_hit_frame + 10)) / 15.0)
            food_scale = ease_out_elastic(food_t) * 1.0
            d = ImageDraw.Draw(canvas)
            f_food = get_font(52)
            foods = [("🍕", 110, 360), ("🧋", 110, 480), ("🍰", 610, 390), ("🍗", 610, 520)]
            for icon, fx, fy in foods:
                d.text((fx, fy + int(math.sin(t * 6.0 + fx) * 6)), icon, font=f_food, anchor="mm")

        # Subtitle
        if f < stamp_hit_frame + 5:
            draw_subtitles(canvas, "Vì vậy tôi xin triệu tập các bạn")
            draw_subtitles(canvas, "đến dự lễ tốt nghiệp!", cy=1195)
        else:
            draw_subtitles(canvas, "Có đồ ăn & trà sữa siêu ngon nữa nha! 🍕🧋")

    # =========================================================================
    # SHOT 4 (13.8s - 18.0s): Confetti Blast, Winking & Waving, End Card
    # Dialogue: "Hẹn gặp bạn nha ♡"
    # =========================================================================
    def render_shot_4(self, canvas, f, t):
        # 1. Warm celebratory background
        d = ImageDraw.Draw(canvas)
        for y in range(0, HEIGHT, 60):
            c = (255, 246 - int(y * 0.02), 220 + int(y * 0.01), 255)
            d.rectangle([0, y, WIDTH, y + 60], fill=c)

        # 2. Confetti Particle System
        # Physics update for each confetti
        for p in self.confetti:
            # Time elapsed since explosion (f = 0 at start of shot 4)
            t_sec = f / FPS
            curr_x = p['origin_x'] + p['vx'] * t_sec * 0.8
            curr_y = p['origin_y'] + p['vy'] * t_sec + 0.5 * 320 * (t_sec ** 2)
            
            # Wrap or bounce on boundaries
            curr_x = curr_x % WIDTH
            curr_y = curr_y % (HEIGHT + 100) - 50

            # 3D flutter rotation
            flutter = math.cos(t_sec * p['rot_speed'] + p['phase'])
            w = max(2, int(p['w'] * abs(flutter)))
            h = int(p['h'])
            
            # Draw confetti shape
            c_color = p['color']
            if p['shape'] == 'rect':
                d.rectangle([curr_x - w // 2, curr_y - h // 2, curr_x + w // 2, curr_y + h // 2],
                            fill=c_color, outline=INK, width=2)
            elif p['shape'] == 'circle':
                d.ellipse([curr_x - w // 2, curr_y - h // 2, curr_x + w // 2, curr_y + h // 2],
                          fill=c_color, outline=INK, width=2)
            else:
                d.polygon([(curr_x, curr_y - h), (curr_x + w, curr_y), (curr_x, curr_y + h), (curr_x - w, curr_y)],
                          fill=c_color, outline=INK, width=2)

        # 3. Main Character Celebratory Pose in center
        # Winking & waving with gentle joyful bobbing
        bob = math.sin(t * 10.0) * 8
        sway = math.sin(t * 5.0) * 2.5
        char_scale = 1.05 + math.sin(t * 10.0) * 0.02
        paste_sprite(canvas, self.sprites['char_bust_wink'], WIDTH // 2, 490 + int(bob),
                     scale_x=char_scale, scale_y=char_scale, angle=sway)

        # Floating pastel stickers around her (stars, hearts, graduation cap)
        # Top-left star
        paste_sprite(canvas, self.props['sticker_star'], 120, 360 + int(math.sin(t * 4.0) * 10), scale_x=0.9, scale_y=0.9, angle=math.sin(t * 3.0) * 12)
        # Top-right heart
        paste_sprite(canvas, self.props['sticker_heart'], 590, 370 + int(math.cos(t * 4.0) * 10), scale_x=0.9, scale_y=0.9, angle=math.cos(t * 3.0) * 10)
        # Mid-left graduation cap
        paste_sprite(canvas, self.props['sticker_cap'], 130, 640 + int(math.sin(t * 5.0 + 1) * 8), scale_x=0.85, scale_y=0.85, angle=-8.0)
        # Mid-right star
        paste_sprite(canvas, self.props['sticker_star'], 600, 630 + int(math.cos(t * 5.0 + 1) * 8), scale_x=0.85, scale_y=0.85, angle=14.0)

        # 4. End Card: "Hẹn gặp bạn nha ♡"
        # Scales in smoothly around frame 30 (1.0s into shot 4)
        if f >= 18:
            card_t = min(1.0, (f - 18) / 18.0)
            card_scale = ease_out_elastic(card_t) * 1.02
            card_bob = math.sin(t * 6.0) * 4
            paste_sprite(canvas, self.props['end_card'], WIDTH // 2, 910 + int(card_bob),
                         scale_x=card_scale, scale_y=card_scale)

        # Subtitle
        draw_subtitles(canvas, "Hẹn gặp bạn nha ♡", cy=1170)

def main():
    renderer = AnimationRenderer()
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    out_mp4 = 'assets/loi-khai.mp4'
    cmd = [
        ffmpeg_exe, '-y',
        '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f'{WIDTH}x{HEIGHT}', '-pix_fmt', 'rgb24', '-r', str(FPS),
        '-i', '-',
        '-i', 'assets/master_audio.wav',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '19', '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        out_mp4
    ]

    with open('ffmpeg_render.log', 'w') as err_log:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=err_log)

        for i in range(TOTAL_FRAMES):
            frame_img = renderer.render_frame(i)
            raw_bytes = np.array(frame_img).tobytes()
            proc.stdin.write(raw_bytes)
            if i % 60 == 0:
                print(f"Rendered frame {i}/{TOTAL_FRAMES} ({(i/TOTAL_FRAMES)*100:.1f}%)")

        proc.stdin.close()
        proc.wait()

    if proc.returncode == 0:
        print(f"Successfully rendered video to {out_mp4}!")
        size_mb = os.path.getsize(out_mp4) / (1024 * 1024)
        print(f"Video size: {size_mb:.2f} MB")
    else:
        with open('ffmpeg_render.log', 'r') as err_log:
            print(f"FFmpeg error:\n{err_log.read()}")

if __name__ == '__main__':
    main()
