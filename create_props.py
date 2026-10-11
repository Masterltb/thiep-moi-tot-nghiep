import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

os.makedirs('assets/props', exist_ok=True)

# Common color palette
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
WOOD_LIGHT = (229, 171, 107, 255)
WOOD_DARK = (168, 106, 52, 255)
WOOD_DEEP = (112, 66, 30, 255)

FONT_PATH = r'C:\Windows\Fonts\arialbd.ttf'
FONT_TITLE_PATH = r'C:\Windows\Fonts\segoeuib.ttf'

def get_font(size, title=False):
    path = FONT_TITLE_PATH if title else FONT_PATH
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def draw_pill(d, box, fill, outline, width=4):
    x0, y0, x1, y1 = box
    r = (y1 - y0) // 2
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=outline, width=width)

def draw_star(d, cx, cy, r_out, r_in, fill, outline, width=3, points=5):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        angle = i * math.pi / points - math.pi / 2
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    d.polygon(pts, fill=fill, outline=outline, width=width)

# ==========================================
# 1. COURTROOM BACKGROUND (720 x 1280)
# ==========================================
def create_courtroom_bg():
    img = Image.new('RGBA', (720, 1280), CREAM)
    d = ImageDraw.Draw(img)
    
    # Top wall: subtle cream-to-warm-yellow gradient stripes or soft panels
    for y in range(0, 750, 40):
        c = (255, 240 - int(y * 0.03), 205 - int(y * 0.04), 255)
        d.rectangle([0, y, 720, y + 36], fill=c)
        d.line([(0, y + 36), (720, y + 36)], fill=(240, 225, 195, 255), width=2)

    # Decorative courtroom crest on the wall: scales of justice inside oval
    cx, cy = 360, 230
    d.ellipse([cx - 100, cy - 100, cx + 100, cy + 100], fill=WHITE, outline=INK, width=6)
    d.ellipse([cx - 86, cy - 86, cx + 86, cy + 86], fill=YELLOW, outline=INK, width=4)
    # Scales of justice symbol
    # Beam
    d.rectangle([cx - 50, cy - 25, cx + 50, cy - 17], fill=NAVY, outline=INK, width=2)
    # Center pillar
    d.rectangle([cx - 6, cy - 40, cx + 6, cy + 45], fill=NAVY, outline=INK, width=2)
    # Base
    d.polygon([(cx - 30, cy + 45), (cx + 30, cy + 45), (cx + 20, cy + 35), (cx - 20, cy + 35)], fill=NAVY, outline=INK, width=2)
    # Left pan
    d.line([(cx - 45, cy - 17), (cx - 65, cy + 15)], fill=INK, width=3)
    d.line([(cx - 45, cy - 17), (cx - 25, cy + 15)], fill=INK, width=3)
    d.chord([cx - 70, cy + 10, cx - 20, cy + 30], start=0, end=180, fill=NAVY, outline=INK, width=3)
    # Right pan
    d.line([(cx + 45, cy - 17), (cx + 25, cy + 15)], fill=INK, width=3)
    d.line([(cx + 45, cy - 17), (cx + 65, cy + 15)], fill=INK, width=3)
    d.chord([cx + 20, cy + 10, cx + 70, cy + 30], start=0, end=180, fill=NAVY, outline=INK, width=3)

    # Wall banner: "TÒA ÁN HẠNH PHÚC" / "LỄ TỐT NGHIỆP"
    banner_w, banner_h = 340, 48
    bx0, by0 = cx - banner_w // 2, cy + 115
    d.rectangle([bx0, by0, bx0 + banner_w, by0 + banner_h], fill=NAVY, outline=INK, width=4)
    f_banner = get_font(22, title=True)
    d.text((cx, by0 + banner_h // 2), "PHIÊN TÒA TỐT NGHIỆP", fill=WHITE, font=f_banner, anchor="mm")

    # Lower wooden courtroom wall wainscoting
    d.rectangle([0, 750, 720, 1280], fill=WOOD_DARK, outline=INK, width=5)
    # Wooden panel inserts
    for px in [30, 205, 380, 555]:
        d.rounded_rectangle([px, 780, px + 140, 1240], radius=12, fill=WOOD_LIGHT, outline=INK, width=4)
        d.rounded_rectangle([px + 10, 790, px + 130, 1230], radius=8, outline=WOOD_DEEP, width=3)

    img.save('assets/props/courtroom_bg.png')
    print("Saved courtroom_bg.png")

# ==========================================
# 2. WITNESS STAND & PODIUM (with microphone)
# ==========================================
def create_witness_stand():
    # 720 x 500 transparent overlay
    img = Image.new('RGBA', (720, 500), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Witness podium
    # Top desk slab
    desk_x0, desk_y0, desk_x1, desk_y1 = 60, 140, 660, 200
    d.rounded_rectangle([desk_x0 - 10, desk_y0, desk_x1 + 10, desk_y1], radius=16, fill=WOOD_LIGHT, outline=INK, width=6)
    d.rectangle([desk_x0, desk_y1 - 10, desk_x1, desk_y1], fill=WOOD_DARK, outline=INK, width=3)

    # Main podium body
    d.rounded_rectangle([100, desk_y1, 620, 500], radius=20, fill=WOOD_DEEP, outline=INK, width=6)
    # Inner decorative panel
    d.rounded_rectangle([140, desk_y1 + 30, 580, 480], radius=14, fill=WOOD_DARK, outline=INK, width=5)
    
    # Plaque: "BỤC NHÂN CHỨNG"
    plaque_w, plaque_h = 320, 64
    px0, py0 = 360 - plaque_w // 2, desk_y1 + 60
    d.rounded_rectangle([px0, py0, px0 + plaque_w, py0 + plaque_h], radius=12, fill=YELLOW, outline=INK, width=5)
    f_plaque = get_font(26, title=True)
    d.text((360, py0 + plaque_h // 2), "BỤC NHÂN CHỨNG ⚖️", fill=INK, font=f_plaque, anchor="mm")

    # Document paper lying on the stand
    pap_x, pap_y = 440, desk_y0 + 10
    d.rectangle([pap_x, pap_y, pap_x + 130, pap_y + 90], fill=WHITE, outline=INK, width=4)
    # Document lines
    for ly in range(pap_y + 16, pap_y + 80, 14):
        d.line([(pap_x + 12, ly), (pap_x + 118, ly)], fill=INK, width=3)
    # Stamp icon on document
    d.ellipse([pap_x + 85, pap_y + 50, pap_x + 115, pap_y + 80], fill=None, outline=RED, width=3)

    # Microphone: retro gooseneck mic
    mic_base_x, mic_base_y = 240, desk_y0 + 20
    d.ellipse([mic_base_x - 22, mic_base_y - 10, mic_base_x + 22, mic_base_y + 10], fill=NAVY, outline=INK, width=4)
    # Neck curving up
    d.arc([mic_base_x - 30, mic_base_y - 120, mic_base_x + 40, mic_base_y + 10], start=180, end=320, fill=INK, width=8)
    # Mic capsule
    mic_head_x, mic_head_y = mic_base_x + 25, mic_base_y - 110
    d.rounded_rectangle([mic_head_x - 18, mic_head_y - 30, mic_head_x + 18, mic_head_y + 15], radius=10, fill=SKY, outline=INK, width=5)
    # Mic grill lines
    for gy in range(mic_head_y - 20, mic_head_y + 10, 8):
        d.line([(mic_head_x - 12, gy), (mic_head_x + 12, gy)], fill=INK, width=3)

    img.save('assets/props/witness_stand.png')
    print("Saved witness_stand.png")

# ==========================================
# 3. GAVEL & COMIC "BANG!" BURST
# ==========================================
def create_gavel_bang():
    # 400 x 400 burst
    img = Image.new('RGBA', (440, 440), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx, cy = 220, 220
    # Outer jagged starburst in ORANGE
    draw_star(d, cx, cy, r_out=200, r_in=120, fill=ORANGE, outline=INK, width=7, points=12)
    # Inner jagged starburst in YELLOW
    draw_star(d, cx, cy, r_out=150, r_in=95, fill=YELLOW, outline=INK, width=5, points=12)

    # Action speed lines radiating out
    for angle_deg in [15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345]:
        rad = math.radians(angle_deg)
        x1 = cx + 160 * math.cos(rad)
        y1 = cy + 160 * math.sin(rad)
        x2 = cx + 215 * math.cos(rad)
        y2 = cy + 215 * math.sin(rad)
        d.line([(x1, y1), (x2, y2)], fill=INK, width=5)

    # "BANG!" comic text
    f_bang = get_font(68, title=True)
    # Shadow
    d.text((cx + 5, cy + 5), "BANG!", fill=INK, font=f_bang, anchor="mm")
    # Red fill
    d.text((cx, cy), "BANG!", fill=RED, font=f_bang, anchor="mm")

    img.save('assets/props/gavel_bang.png')
    print("Saved gavel_bang.png")

    # Gavel mallet sprite
    g_img = Image.new('RGBA', (320, 260), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g_img)
    # Mallet head
    gd.rounded_rectangle([40, 40, 160, 110], radius=18, fill=WOOD_LIGHT, outline=INK, width=6)
    # Mallet metal rings
    gd.rectangle([65, 40, 80, 110], fill=YELLOW, outline=INK, width=3)
    gd.rectangle([120, 40, 135, 110], fill=YELLOW, outline=INK, width=3)
    # Handle angled down
    gd.line([(100, 110), (280, 220)], fill=WOOD_DARK, width=22)
    gd.line([(100, 110), (280, 220)], fill=INK, width=26)
    gd.line([(100, 110), (280, 220)], fill=WOOD_DARK, width=18)
    gd.ellipse([270, 210, 295, 235], fill=WOOD_DEEP, outline=INK, width=4)

    g_img.save('assets/props/gavel.png')
    print("Saved gavel.png")

# ==========================================
# 4. POLAROIDS FOR MONTAGE (Baby, Uniform, Library, 23:59)
# ==========================================
def draw_washi_tape(d, x, y, width=120, height=36, color=YELLOW):
    # Textured tape with zig-zag / torn ends
    pts = [(x, y + 6), (x + 8, y), (x + width - 8, y), (x + width, y + 6),
           (x + width - 6, y + height), (x + width - 12, y + height - 4),
           (x + 10, y + height), (x, y + height - 6)]
    d.polygon(pts, fill=color, outline=INK, width=3)

def create_polaroid(title, subtitle, emoji_sym, render_content_fn, filename, tape_color=YELLOW):
    w, h = 460, 540
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Polaroid white frame
    d.rounded_rectangle([20, 30, w - 20, h - 30], radius=16, fill=WHITE, outline=INK, width=6)
    # Inner photo area (400 x 360)
    px0, py0, px1, py1 = 40, 50, w - 40, 410
    d.rectangle([px0, py0, px1, py1], fill=CREAM, outline=INK, width=4)

    # Draw specific illustration inside photo area
    render_content_fn(d, px0, py0, px1, py1)

    # Caption text at bottom
    f_cap = get_font(28, title=True)
    d.text((w // 2, 445), title, fill=INK, font=f_cap, anchor="mm")
    f_sub = get_font(18, title=False)
    d.text((w // 2, 485), subtitle, fill=RED, font=f_sub, anchor="mm")

    # Washi tape at top
    draw_washi_tape(d, (w - 140) // 2, 10, width=140, height=36, color=tape_color)

    img.save(f'assets/props/{filename}')
    print(f"Saved {filename}")

def draw_baby_content(d, x0, y0, x1, y1):
    # Pastel background
    d.rectangle([x0, y0, x1, y1], fill=SKY)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    # Baby face
    d.ellipse([cx - 80, cy - 70, cx + 80, cy + 90], fill=(255, 224, 189, 255), outline=INK, width=5)
    # Cute hair tuft
    d.arc([cx - 15, cy - 100, cx + 15, cy - 70], start=180, end=360, fill=INK, width=5)
    # Rosy cheeks
    d.ellipse([cx - 65, cy + 15, cx - 35, cy + 35], fill=PINK)
    d.ellipse([cx + 35, cy + 15, cx + 65, cy + 35], fill=PINK)
    # Eyes (happy closed curves)
    d.arc([cx - 50, cy - 15, cx - 20, cy + 10], start=180, end=360, fill=INK, width=5)
    d.arc([cx + 20, cy - 15, cx + 50, cy - 10], start=180, end=360, fill=INK, width=5)
    # Pacifier
    d.ellipse([cx - 25, cy + 30, cx + 25, cy + 70], fill=YELLOW, outline=INK, width=4)
    d.ellipse([cx - 12, cy + 42, cx + 12, cy + 58], fill=ORANGE, outline=INK, width=3)
    # Floating baby toys / rattle
    d.text((x0 + 30, y0 + 30), "🍼", font=get_font(44))
    d.text((x1 - 70, y0 + 30), "⭐", font=get_font(44))

def draw_school_content(d, x0, y0, x1, y1):
    # Pastel green/mint background
    d.rectangle([x0, y0, x1, y1], fill=MINT)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    # School backpack
    d.rounded_rectangle([cx - 90, cy - 70, cx + 90, cy + 110], radius=24, fill=ORANGE, outline=INK, width=5)
    d.rounded_rectangle([cx - 70, cy + 10, cx + 70, cy + 90], radius=16, fill=YELLOW, outline=INK, width=4)
    # Straps
    d.line([(cx - 60, cy - 70), (cx - 60, cy - 100), (cx - 30, cy - 100)], fill=NAVY, width=8)
    d.line([(cx + 60, cy - 70), (cx + 60, cy - 100), (cx + 30, cy - 100)], fill=NAVY, width=8)
    # Cute ruler and pencil sticking out
    d.rectangle([cx + 35, cy - 120, cx + 55, cy - 60], fill=YELLOW, outline=INK, width=3)
    d.polygon([(cx - 50, cy - 130), (cx - 35, cy - 130), (cx - 42, cy - 150)], fill=RED, outline=INK, width=3)
    # Keychain
    d.ellipse([cx + 80, cy + 20, cx + 110, cy + 50], fill=PINK, outline=INK, width=3)
    # School emblem badge
    d.text((cx, cy + 50), "12A1", fill=INK, font=get_font(24, title=True), anchor="mm")

def draw_library_content(d, x0, y0, x1, y1):
    # Warm library background
    d.rectangle([x0, y0, x1, y1], fill=YELLOW)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    # Huge stack of law books
    colors = [NAVY, RED, WOOD_DARK, ORANGE, MINT]
    labels = ["LUẬT DÂN SỰ", "LUẬT HÌNH SỰ", "HIẾN PHÁP", "TỐ TỤNG", "NGHỊ ĐỊNH"]
    by = y1 - 35
    for i in range(5):
        bw = 300 - i * 15
        bh = 46
        bx = cx - bw // 2 + (i % 2 * 12 - 6)
        d.rounded_rectangle([bx, by - bh, bx + bw, by], radius=8, fill=colors[i], outline=INK, width=4)
        # Gold spine text
        d.text((cx, by - bh // 2), labels[i], fill=WHITE, font=get_font(18, title=True), anchor="mm")
        by -= bh + 4
    # Floating sweat drops / question marks
    d.text((x0 + 35, y0 + 35), "📚", font=get_font(46))
    d.text((x1 - 75, y0 + 35), "💥", font=get_font(46))

def draw_deadline_content(d, x0, y0, x1, y1):
    # Dark navy room at midnight
    d.rectangle([x0, y0, x1, y1], fill=NAVY)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    # Glowing digital clock showing 23:59
    clock_w, clock_h = 240, 80
    clock_x, clock_y = cx - clock_w // 2, y0 + 40
    d.rounded_rectangle([clock_x, clock_y, clock_x + clock_w, clock_y + clock_h], radius=14, fill=INK, outline=RED, width=5)
    f_clock = get_font(52, title=True)
    d.text((cx, clock_y + clock_h // 2), "23:59", fill=RED, font=f_clock, anchor="mm")
    
    # 4 coffee cups lined up on desk
    desk_y = y1 - 90
    d.rectangle([x0, desk_y, x1, y1], fill=WOOD_LIGHT, outline=INK, width=4)
    # Laptop screen
    d.rounded_rectangle([cx - 80, desk_y - 100, cx + 80, desk_y], radius=8, fill=SKY, outline=INK, width=4)
    d.text((cx, desk_y - 50), "DEADLINE!!", fill=RED, font=get_font(20, title=True), anchor="mm")
    
    # Coffee cups
    for i, cx_cup in enumerate([x0 + 45, x0 + 105, x1 - 105, x1 - 45]):
        d.polygon([(cx_cup - 18, desk_y - 55), (cx_cup + 18, desk_y - 55), 
                   (cx_cup + 14, desk_y + 5), (cx_cup - 14, desk_y + 5)], fill=WHITE, outline=INK, width=3)
        # Straw
        d.line([(cx_cup, desk_y - 55), (cx_cup + 6, desk_y - 75)], fill=ORANGE, width=4)
        # Coffee logo
        d.ellipse([cx_cup - 8, desk_y - 35, cx_cup + 8, desk_y - 19], fill=MINT, outline=INK, width=2)

def create_all_polaroids():
    create_polaroid("Thuở còn ngây thơ", "Chứng cứ số 1", "👶", draw_baby_content, "polaroid_baby.png", tape_color=YELLOW)
    create_polaroid("Cấp 3 nổi loạn", "Chứng cứ số 2", "🎒", draw_school_content, "polaroid_school.png", tape_color=SKY)
    create_polaroid("Núi giáo trình", "Chứng cứ số 3", "📚", draw_library_content, "polaroid_library.png", tape_color=PINK)
    create_polaroid("Đêm trắng 23:59", "Chứng cứ số 4", "☕", draw_deadline_content, "polaroid_deadline.png", tape_color=ORANGE)

# ==========================================
# 5. GIẤY TRIỆU TẬP (Summons Paper)
# ==========================================
def create_summons_paper():
    w, h = 640, 880
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Cream double border parchment paper
    d.rounded_rectangle([15, 15, w - 15, h - 15], radius=12, fill=(255, 253, 246, 255), outline=NAVY, width=6)
    d.rounded_rectangle([25, 25, w - 25, h - 25], radius=8, outline=NAVY, width=2)

    # Header
    cx = w // 2
    f_h1 = get_font(18, title=True)
    f_h2 = get_font(15, title=False)
    d.text((cx, 60), "CỘNG HÒA XÃ HỘI CHỦ NGHĨA... TỐT NGHIỆP", fill=NAVY, font=f_h1, anchor="mm")
    d.text((cx, 85), "Độc lập · Tự do · Có đồ ăn", fill=NAVY, font=f_h2, anchor="mm")
    d.line([(cx - 120, 102), (cx + 120, 102)], fill=NAVY, width=2)
    d.text((cx, 120), "Số: 01/2026/TN-CHÍNH THỨC", fill=INK, font=get_font(14), anchor="mm")

    # Title
    f_summons = get_font(42, title=True)
    d.text((cx, 175), "GIẤY TRIỆU TẬP", fill=NAVY, font=f_summons, anchor="mm")
    f_sub = get_font(20, title=True)
    d.text((cx, 220), "DỰ LỄ TỐT NGHIỆP ĐẠI HỌC", fill=RED, font=f_sub, anchor="mm")

    # Legal contents
    body_y = 265
    f_body = get_font(20, title=False)
    f_bold = get_font(22, title=True)

    lines = [
        "Kính gửi: TẤT CẢ CÁC BẠN THÂN YÊU ♡",
        "",
        "Căn cứ: Đương sự đã hoàn thành xuất sắc 4 năm đèn sách,",
        "vượt qua hàng ngàn deadline và đồ án,",
        "",
        "NAY CHÍNH THỨC TRIỆU TẬP:",
        "• Đến dự Lễ Trao Bằng Tốt Nghiệp",
        "• Cùng chụp những bức ảnh kỷ niệm xịn xò nhất",
        "• Thưởng thức tiệc mừng siêu ngon (Có đồ ăn nha!)",
        "",
        "Thời hạn thi hành: Có mặt đúng giờ, mang theo nụ cười!"
    ]
    for line in lines:
        if line.startswith("Kính") or line.startswith("NAY"):
            d.text((50, body_y), line, fill=NAVY, font=f_bold)
            body_y += 34
        elif line.startswith("•"):
            d.text((70, body_y), line, fill=INK, font=f_bold)
            body_y += 32
        elif line.startswith("Thời"):
            d.text((50, body_y + 10), line, fill=RED, font=f_bold)
            body_y += 36
        else:
            d.text((50, body_y), line, fill=INK, font=f_body)
            body_y += 28

    # Signatures
    d.text((w - 180, h - 140), "ĐƯƠNG SỰ", fill=NAVY, font=f_bold, anchor="mm")
    d.text((w - 180, h - 110), "(Đã ký tên & đóng dấu)", fill=INK, font=get_font(16), anchor="mm")

    img.save('assets/props/summons_paper.png')
    print("Saved summons_paper.png")

# ==========================================
# 6. GIANT RED CIRCULAR STAMP "ĐÃ DUYỆT"
# ==========================================
def create_stamp_da_duyet():
    size = 420
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    r_outer = 190
    r_inner = 170

    # Red double circle
    d.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill=None, outline=RED, width=10)
    d.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill=None, outline=RED, width=4)

    # Stars
    draw_star(d, cx - 115, cy, r_out=22, r_in=10, fill=RED, outline=RED, width=1)
    draw_star(d, cx + 115, cy, r_out=22, r_in=10, fill=RED, outline=RED, width=1)

    # Top arched text "ỦY BAN TỐT NGHIỆP"
    f_curved = get_font(26, title=True)
    d.text((cx, cy - 115), "★ ỦY BAN TỐT NGHIỆP ★", fill=RED, font=f_curved, anchor="mm")

    # Main Center Text: "ĐÃ DUYỆT"
    f_center = get_font(72, title=True)
    d.text((cx, cy), "ĐÃ DUYỆT", fill=RED, font=f_center, anchor="mm")

    # Bottom arched text: "CHÍNH THỨC 2026"
    f_bottom = get_font(22, title=True)
    d.text((cx, cy + 115), "HIỆU LỰC TOÀN QUỐC 2026", fill=RED, font=f_bottom, anchor="mm")

    # Subtle grunge / ink texture effect
    arr = np.array(img)
    noise = np.random.uniform(0.75, 1.05, arr.shape[:2])
    mask = arr[:, :, 3] > 0
    # Add slight stamp roughness
    arr[:, :, 3] = (arr[:, :, 3] * noise).astype(np.uint8)
    stamped = Image.fromarray(arr, 'RGBA')

    stamped.save('assets/props/stamp_da_duyet.png')
    print("Saved stamp_da_duyet.png")

# ==========================================
# 7. END CARD "Hẹn gặp bạn nha ♡"
# ==========================================
def create_end_card():
    w, h = 600, 360
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Pastel yellow pill container with bold sticker outline
    d.rounded_rectangle([20, 20, w - 20, h - 20], radius=36, fill=YELLOW, outline=INK, width=8)
    d.rounded_rectangle([32, 32, w - 32, h - 32], radius=26, fill=CREAM, outline=INK, width=4)

    cx, cy = w // 2, h // 2 - 15
    f_main = get_font(46, title=True)
    d.text((cx + 4, cy + 4), "Hẹn gặp bạn nha ♡", fill=INK, font=f_main, anchor="mm")
    d.text((cx, cy), "Hẹn gặp bạn nha ♡", fill=RED, font=f_main, anchor="mm")

    f_sub = get_font(24, title=True)
    d.text((cx, cy + 70), "LỄ TỐT NGHIỆP ĐANG CHỜ BẠN! 🎓✨", fill=NAVY, font=f_sub, anchor="mm")

    # Corner sticker decorations
    draw_star(d, 65, 65, 24, 12, fill=ORANGE, outline=INK, width=3)
    draw_star(d, w - 65, 65, 24, 12, fill=MINT, outline=INK, width=3)
    d.text((w // 2, h - 50), "🎉 Có đồ ăn & đồ uống siêu ngon 🎉", fill=INK, font=get_font(18, title=True), anchor="mm")

    img.save('assets/props/end_card.png')
    print("Saved end_card.png")

# ==========================================
# 8. PASTEL STICKERS (Stars, Hearts, Caps)
# ==========================================
def create_stickers():
    # Mini Star
    star_img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    sd = ImageDraw.Draw(star_img)
    draw_star(sd, 60, 60, 52, 26, fill=YELLOW, outline=INK, width=5)
    sd.ellipse([45, 52, 53, 62], fill=INK)
    sd.ellipse([67, 52, 75, 62], fill=INK)
    star_img.save('assets/props/sticker_star.png')

    # Mini Heart
    heart_img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    hd = ImageDraw.Draw(heart_img)
    hd.text((60, 60), "💖", font=get_font(80), anchor="mm")
    heart_img.save('assets/props/sticker_heart.png')

    # Mini Grad Cap
    cap_img = Image.new('RGBA', (140, 140), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cap_img)
    cd.text((70, 70), "🎓", font=get_font(90), anchor="mm")
    cap_img.save('assets/props/sticker_cap.png')

    print("Saved stickers")

if __name__ == '__main__':
    create_courtroom_bg()
    create_witness_stand()
    create_gavel_bang()
    create_all_polaroids()
    create_summons_paper()
    create_stamp_da_duyet()
    create_end_card()
    create_stickers()
    print("All props created successfully!")
