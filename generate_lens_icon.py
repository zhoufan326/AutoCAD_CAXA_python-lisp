"""
根据 Lens.svg 设计生成高质量的 Lens.ico 图标
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os


def draw_gradient_rounded_rect(draw, rect, radius, color1, color2):
    """绘制带渐变色的圆角矩形"""
    x1, y1, x2, y2 = rect
    h = y2 - y1

    for i in range(h):
        ratio = i / h
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        y = y1 + i

        # 左圆角裁剪
        if y - y1 < radius:
            dx = int(math.sqrt(radius**2 - (y - y1 - radius) ** 2))
            x_start = x1 + radius - dx
        else:
            x_start = x1

        # 右圆角裁剪
        if y2 - y < radius:
            dx = int(math.sqrt(radius**2 - (y2 - y - radius) ** 2))
            x_end = x2 - radius + dx
        else:
            x_end = x2

        if x_end > x_start:
            draw.rectangle([x_start, y, x_end, y + 1], fill=(r, g, b, 255))


def draw_anti_aliased_line(draw, points, color, width=3):
    """绘制抗锯齿曲线（用多个小圆点模拟）"""
    step = 0.5  # 子像素步长
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        dist = math.hypot(x2 - x1, y2 - y1)
        steps = max(1, int(dist / step))
        for t in range(steps + 1):
            frac = t / steps
            x = x1 + (x2 - x1) * frac
            y = y1 + (y2 - y1) * frac
            draw.ellipse([x - width / 2, y - width / 2, x + width / 2, y + width / 2], fill=color)


def main():
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # === 1. 渐变圆角背景 ===
    color_top = (74, 144, 217)  # #4A90D9
    color_bot = (30, 58, 110)  # #1E3A6E
    draw_gradient_rounded_rect(draw, [8, 8, 248, 248], 40, color_top, color_bot)

    # === 2. 镜片形状（双凸透镜）===
    white = (255, 255, 255, 220)
    white_light = (255, 255, 255, 120)

    # 上弧线：从 (60,128) 到 (196,128) 向上拱
    # 使用贝塞尔近似：控制点为 (128, 55)
    arc1_pts = []
    for t in range(0, 101):
        frac = t / 100
        # 二次贝塞尔 P0=(60,128), P1=(128,55), P2=(196,128)
        x = (1 - frac) ** 2 * 60 + 2 * (1 - frac) * frac * 128 + frac**2 * 196
        y = (1 - frac) ** 2 * 128 + 2 * (1 - frac) * frac * 55 + frac**2 * 128
        arc1_pts.append((x, y))
    draw_anti_aliased_line(draw, arc1_pts, white, width=4)

    # 下弧线：从 (60,128) 到 (196,128) 向下拱
    # 控制点为 (128, 201)
    arc2_pts = []
    for t in range(0, 101):
        frac = t / 100
        x = (1 - frac) ** 2 * 60 + 2 * (1 - frac) * frac * 128 + frac**2 * 196
        y = (1 - frac) ** 2 * 128 + 2 * (1 - frac) * frac * 201 + frac**2 * 128
        arc2_pts.append((x, y))
    draw_anti_aliased_line(draw, arc2_pts, white, width=4)

    # === 3. 中心线（虚线）===
    for y in range(95, 162, 8):
        draw.rectangle([58, y, 62, y + 4], fill=white_light)

    draw.line([60, 128, 196, 128], fill=(255, 255, 255, 80), width=2)

    # === 4. 文字 "Lens" ===
    font_size = 48
    font = None
    for font_name in ["arial.ttf", "Arial.ttf", "C:\\Windows\\Fonts\\Arial.ttf"]:
        try:
            font = ImageFont.truetype(font_name, font_size)
            break
        except (IOError, OSError):
            continue
    if font is None:
        font = ImageFont.load_default()

    # 白色粗体文字
    text = "Lens"
    # 通过多次绘制模拟粗体效果
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
        draw.text((128 + dx, 140 + dy), text, fill=(255, 255, 255, 255), font=font, anchor="mm")

    # === 5. 保存 ===
    ico_path = "lens_package/icons/Lens.ico"
    # 同时保存 PNG 方便查看
    png_path = "lens_package/icons/Lens.png"
    img.save(ico_path, format="ICO", sizes=[(256, 256)])
    img.save(png_path, format="PNG")
    print(f"✓ Lens.ico 已生成 ({os.path.getsize(ico_path)} 字节)")
    print(f"✓ Lens.png 已生成 ({os.path.getsize(png_path)} 字节)")


if __name__ == "__main__":
    main()
