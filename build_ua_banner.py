import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
FPS = 30
TOTAL_SECONDS = 8.0
TOTAL_FRAMES = int(FPS * TOTAL_SECONDS)

# Fonts
font_title_large = ImageFont.truetype('segoeuib.ttf', 92)
font_title_med = ImageFont.truetype('segoeuib.ttf', 50)
font_title_slide3 = ImageFont.truetype('segoeuib.ttf', 62)
font_sub = ImageFont.truetype('segoeui.ttf', 24)
font_sub_small = ImageFont.truetype('segoeui.ttf', 20)
font_pill_large = ImageFont.truetype('segoeuib.ttf', 18)
font_badge = ImageFont.truetype('segoeuib.ttf', 13)
font_phone = ImageFont.truetype('segoeuib.ttf', 15)
font_phone_small = ImageFont.truetype('segoeui.ttf', 12)

font_emoji_large = ImageFont.truetype('seguiemj.ttf', 76)
font_emoji_pill = ImageFont.truetype('seguiemj.ttf', 20)
font_emoji_shield = ImageFont.truetype('seguiemj.ttf', 42)
font_emoji_phone = ImageFont.truetype('seguiemj.ttf', 16)

# Pre-render Waving Hand
def get_waving_hand(angle_deg):
    hand_raw = Image.new('RGBA', (130, 130), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hand_raw)
    hd.text((10, 10), '👋', font=font_emoji_large, embedded_color=True)
    # Convert to grayscale luminance
    hand_l = hand_raw.convert('L')
    hand_a = hand_raw.split()[3]
    hand_bw = Image.merge('RGBA', (hand_l, hand_l, hand_l, hand_a))
    rotated = hand_bw.rotate(angle_deg, resample=Image.BICUBIC, center=(65, 65))
    return rotated

# Pre-render Base Background
base_bg = Image.new('RGBA', (W, H), (8, 8, 10, 255))
base_draw = ImageDraw.Draw(base_bg)
grid_step = 44
for x in range(0, W, grid_step):
    base_draw.line([(x, 0), (x, H)], fill=(20, 20, 24, 255), width=1)
for y in range(0, H, grid_step):
    base_draw.line([(0, y), (W, y)], fill=(20, 20, 24, 255), width=1)
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
glow_draw = ImageDraw.Draw(glow)
glow_draw.ellipse([W//2 - 400, H//2 - 280, W//2 + 400, H//2 + 280], fill=(30, 30, 40, 140))
glow = glow.filter(ImageFilter.GaussianBlur(120))
base_bg.alpha_composite(glow)


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def render_slide_1(t_phase, t_global):
    # t_phase in [0, 1]
    img = base_bg.copy()
    d = ImageDraw.Draw(img)

    # Top Pill
    bw, bh = 220, 36
    bx, by = (W - bw)//2, 175
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=18, fill=(20, 20, 26, 255), outline=(45, 45, 55, 255), width=1)
    d.ellipse([bx + 14, by + 13, bx + 24, by + 23], fill=(255, 255, 255, 255))
    d.text((bx + 34, by + 8), 'SEO STORE BOT', font=font_badge, fill=(200, 200, 210, 255))

    # Title "Привіт" + Waving Hand
    title_text = 'Привіт'
    bb = d.textbbox((0, 0), title_text, font=font_title_large)
    tw = bb[2] - bb[0]
    total_w = tw + 110
    start_x = (W - total_w) // 2

    d.text((start_x, 250), title_text, font=font_title_large, fill=(255, 255, 255, 255))

    wave_angle = math.sin(t_global * 2 * math.pi * 1.5) * 16
    hand_img = get_waving_hand(wave_angle)
    img.alpha_composite(hand_img, (start_x + tw + 15, 235))

    # Subtitle
    sub_text = 'Твій надійний маркетплейс цифрових товарів та ліцензій'
    bb_sub = d.textbbox((0, 0), sub_text, font=font_sub)
    sw = bb_sub[2] - bb_sub[0]
    d.text(((W - sw)//2, 390), sub_text, font=font_sub, fill=(155, 155, 165, 255))

    # 3 Pills below
    pills = [
        ('⚡', 'Моментальна видача'),
        ('🛡', '100% Гарантія'),
        ('💳', 'Гривня & Крипта')
    ]
    pill_w = 230
    px_start = (W - (len(pills)*pill_w + (len(pills)-1)*18)) // 2
    for i, (icon, text) in enumerate(pills):
        px = px_start + i * (pill_w + 18)
        d.rounded_rectangle([px, 480, px + pill_w, 526], radius=23, fill=(18, 18, 24, 255), outline=(42, 42, 52, 255), width=1)
        # Icon
        icon_img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        idraw = ImageDraw.Draw(icon_img)
        idraw.text((5, 5), icon, font=font_emoji_pill, embedded_color=True)
        icon_bw = icon_img.convert('L')
        icon_a = icon_img.split()[3]
        icon_final = Image.merge('RGBA', (icon_bw, icon_bw, icon_bw, icon_a))
        img.alpha_composite(icon_final, (px + 16, 484))
        # Text
        d.text((px + 52, 493), text, font=font_pill_large, fill=(215, 215, 225, 255))

    return img


def render_slide_2(t_phase, t_global):
    img = base_bg.copy()
    d = ImageDraw.Draw(img)

    # Top Shield Icon
    ix, iy = (W - 80)//2, 105
    d.rounded_rectangle([ix, iy, ix + 80, iy + 80], radius=24, fill=(22, 22, 28, 255), outline=(52, 52, 64, 255), width=1)
    shield_img = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shield_img)
    sdraw.text((8, 4), '🛡', font=font_emoji_shield, embedded_color=True)
    s_l = shield_img.convert('L')
    s_a = shield_img.split()[3]
    shield_bw = Image.merge('RGBA', (s_l, s_l, s_l, s_a))
    img.alpha_composite(shield_bw, (ix + 10, iy + 8))

    # Headline
    t2_1 = 'Отримуй будь-яку підписку'
    t2_2 = 'чи софт за лічені секунди'
    bb1 = d.textbbox((0, 0), t2_1, font=font_title_med)
    bb2 = d.textbbox((0, 0), t2_2, font=font_title_med)
    d.text(((W - (bb1[2]-bb1[0]))//2, 215), t2_1, font=font_title_med, fill=(255, 255, 255, 255))
    d.text(((W - (bb2[2]-bb2[0]))//2, 285), t2_2, font=font_title_med, fill=(255, 255, 255, 255))

    # 4 Pills (2x2 grid)
    pills = [
        [('⚡', 'Моментальний запуск'), ('🌐', 'Автоматична видача 24/7')],
        [('🛡', '100% Офіційні ліцензії'), ('💳', 'Оплата: UAH & Crypto')]
    ]
    gw, gh = 360, 58
    gap_x, gap_y = 20, 16
    total_w = gw * 2 + gap_x
    start_gx = (W - total_w) // 2
    start_gy = 395

    for r, row in enumerate(pills):
        for c, (icon, text) in enumerate(row):
            px = start_gx + c * (gw + gap_x)
            py = start_gy + r * (gh + gap_y)
            d.rounded_rectangle([px, py, px + gw, py + gh], radius=29, fill=(18, 18, 24, 255), outline=(42, 42, 52, 255), width=1)
            icon_img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
            idraw = ImageDraw.Draw(icon_img)
            idraw.text((4, 4), icon, font=font_emoji_pill, embedded_color=True)
            i_l = icon_img.convert('L')
            i_a = icon_img.split()[3]
            icon_bw = Image.merge('RGBA', (i_l, i_l, i_l, i_a))
            img.alpha_composite(icon_bw, (px + 22, py + 10))
            d.text((px + 62, py + 16), text, font=font_pill_large, fill=(225, 225, 235, 255))

    return img


def render_slide_3(t_phase, t_global):
    img = base_bg.copy()
    d = ImageDraw.Draw(img)

    # Left Side
    lx = 90
    d.rounded_rectangle([lx, 115, lx + 195, 151], radius=18, fill=(20, 20, 26, 255), outline=(45, 45, 55, 255), width=1)
    d.ellipse([lx + 14, 128, lx + 24, 138], fill=(255, 255, 255, 255))
    d.text((lx + 34, 123), 'СИСТЕМА АКТИВНА', font=font_badge, fill=(200, 200, 210, 255))

    d.text((lx, 185), 'Усе необхідне\nв один клік.', font=font_title_slide3, fill=(255, 255, 255, 255), spacing=12)

    d.text((lx, 365), 'Миттєва автоматична видача цифрових товарів,\nпідписок та ліцензій одразу після сплати.', font=font_sub_small, fill=(150, 150, 160, 255), spacing=8)

    # CTA Button
    btn_w, btn_h = 280, 60
    d.rounded_rectangle([lx, 470, lx + btn_w, 470 + btn_h], radius=30, fill=(240, 240, 245, 255))
    icon_img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
    idraw = ImageDraw.Draw(icon_img)
    idraw.text((4, 4), '🚀', font=font_emoji_pill, embedded_color=True)
    i_l = icon_img.convert('L')
    i_a = icon_img.split()[3]
    icon_bw = Image.merge('RGBA', (i_l, i_l, i_l, i_a))
    img.alpha_composite(icon_bw, (lx + 24, 481))
    d.text((lx + 62, 487), 'Запустити магазин', font=font_pill_large, fill=(15, 15, 20, 255))

    # Right Side: Modern Phone Mockup
    phone_w, phone_h = 350, 580
    phone_x, phone_y = 810, 70
    d.rounded_rectangle([phone_x, phone_y, phone_x + phone_w, phone_y + phone_h], radius=46, fill=(14, 14, 18, 255), outline=(50, 50, 62, 255), width=4)
    sc_x, sc_y, sc_w, sc_h = phone_x + 8, phone_y + 8, phone_w - 16, phone_h - 16
    d.rounded_rectangle([sc_x, sc_y, sc_x + sc_w, sc_y + sc_h], radius=40, fill=(8, 8, 12, 255))
    d.rounded_rectangle([sc_x + (sc_w - 84)//2, sc_y + 10, sc_x + (sc_w + 84)//2, sc_y + 32], radius=11, fill=(0, 0, 0, 255))

    # Phone UI
    d.text((sc_x + 20, sc_y + 44), '‹ Назад', font=font_phone_small, fill=(150, 150, 160, 255))
    d.text((sc_x + sc_w//2 - 34, sc_y + 44), 'SEO Store', font=font_phone, fill=(255, 255, 255, 255))
    d.text((sc_x + sc_w - 44, sc_y + 44), '•••', font=font_phone, fill=(150, 150, 160, 255))

    # Hero Banner in Phone
    d.rounded_rectangle([sc_x + 18, sc_y + 80, sc_x + sc_w - 18, sc_y + 140], radius=16, fill=(20, 20, 26, 255), outline=(38, 38, 48, 255), width=1)
    d.text((sc_x + 32, sc_y + 92), 'Головне меню бота', font=font_phone, fill=(255, 255, 255, 255))
    d.text((sc_x + 32, sc_y + 116), 'Миттєва автовидача 24/7', font=font_phone_small, fill=(140, 140, 150, 255))

    # Categories
    items = [
        ('💎', 'Telegram Premium', 'від 149 ₴'),
        ('🤖', 'ChatGPT & AI Софт', 'від 250 ₴'),
        ('🛡', 'VPN & Безпека', 'від 99 ₴'),
        ('🎮', 'Ігри & Steam', 'від 199 ₴'),
        ('🔑', 'Windows & Office', 'від 180 ₴'),
    ]
    for idx, (icon, ititle, iprice) in enumerate(items):
        iy_pos = sc_y + 155 + idx * 56
        d.rounded_rectangle([sc_x + 18, iy_pos, sc_x + sc_w - 18, iy_pos + 46], radius=14, fill=(18, 18, 22, 255), outline=(34, 34, 42, 255), width=1)
        icon_img = Image.new('RGBA', (30, 30), (0, 0, 0, 0))
        idraw = ImageDraw.Draw(icon_img)
        idraw.text((2, 2), icon, font=font_emoji_phone, embedded_color=True)
        i_l = icon_img.convert('L')
        i_a = icon_img.split()[3]
        icon_bw = Image.merge('RGBA', (i_l, i_l, i_l, i_a))
        img.alpha_composite(icon_bw, (sc_x + 28, iy_pos + 9))
        d.text((sc_x + 60, iy_pos + 13), ititle, font=font_phone, fill=(240, 240, 245, 255))
        bb_pr = d.textbbox((0, 0), iprice, font=font_phone_small)
        d.text((sc_x + sc_w - 28 - (bb_pr[2]-bb_pr[0]), iy_pos + 16), iprice, font=font_phone_small, fill=(140, 140, 150, 255))

    # Bottom button in phone
    d.rounded_rectangle([sc_x + 18, sc_y + sc_h - 75, sc_x + sc_w - 18, sc_y + sc_h - 25], radius=25, fill=(240, 240, 245, 255))
    bag_img = Image.new('RGBA', (30, 30), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(bag_img)
    bdraw.text((2, 2), '🛍', font=font_emoji_phone, embedded_color=True)
    b_l = bag_img.convert('L')
    b_a = bag_img.split()[3]
    bag_bw = Image.merge('RGBA', (b_l, b_l, b_l, b_a))
    img.alpha_composite(bag_bw, (sc_x + sc_w//2 - 76, sc_y + sc_h - 64))
    d.text((sc_x + sc_w//2 - 46, sc_y + sc_h - 60), 'Перейти в каталог', font=font_phone, fill=(10, 10, 15, 255))

    return img


def get_frame(f):
    t_global = f / FPS
    # 3 slides:
    # Slide 1: [0.0s, 2.6s] (frames 0 .. 78)
    # Slide 2: [2.6s, 5.3s] (frames 78 .. 159)
    # Slide 3: [5.3s, 8.0s] (frames 159 .. 240)
    trans_len = int(0.35 * FPS) # 10 frames transition crossfade

    if f < 78:
        frame1 = render_slide_1(f / 78, t_global)
        if f > (78 - trans_len):
            alpha = (f - (78 - trans_len)) / trans_len
            frame2 = render_slide_2(0.0, t_global)
            return Image.blend(frame1, frame2, alpha)
        return frame1
    elif f < 159:
        f_rel = f - 78
        len_rel = 159 - 78
        frame2 = render_slide_2(f_rel / len_rel, t_global)
        if f > (159 - trans_len):
            alpha = (f - (159 - trans_len)) / trans_len
            frame3 = render_slide_3(0.0, t_global)
            return Image.blend(frame2, frame3, alpha)
        return frame2
    else:
        f_rel = f - 159
        len_rel = 240 - 159
        frame3 = render_slide_3(f_rel / len_rel, t_global)
        if f > (240 - trans_len):
            alpha = (f - (240 - trans_len)) / trans_len
            frame1 = render_slide_1(0.0, t_global)
            return Image.blend(frame3, frame1, alpha)
        return frame3


def main():
    assets_dir = Path('assets')
    assets_dir.mkdir(exist_ok=True)
    mp4_out = assets_dir / 'welcome.mp4'
    gif_out = assets_dir / 'welcome.gif'

    print(f'Starting rendering {TOTAL_FRAMES} frames into ffmpeg...')
    cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{W}x{H}',
        '-pix_fmt', 'rgba',
        '-r', str(FPS),
        '-i', '-',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '20',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        '-an',
        str(mp4_out)
    ]

    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(TOTAL_FRAMES):
        frame = get_frame(f)
        # Ensure pure grayscale (zero chroma)
        frame_l = frame.convert('L')
        frame_rgba = Image.merge('RGBA', (frame_l, frame_l, frame_l, frame.split()[3]))
        p.stdin.write(frame_rgba.tobytes())
    p.stdin.close()
    p.wait()
    print('MP4 generated successfully!')

    # Generate high quality GIF
    print('Generating GIF...')
    gif_cmd = [
        'ffmpeg', '-y',
        '-i', str(mp4_out),
        '-vf', 'fps=15,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse',
        str(gif_out)
    ]
    subprocess.run(gif_cmd, check=True)
    print('GIF generated successfully!')


if __name__ == '__main__':
    main()
