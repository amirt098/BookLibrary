import random
from io import BytesIO
from PIL import ImageFilter, Image, ImageDraw


def generate_captcha_image(text: str) -> bytes:
    img = Image.new('RGB', (90, 60), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((2, 10), text, fill=(38, 38, 38), font_size=28)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    draw = ImageDraw.Draw(img)
    for i in range(5, 11):
        draw.line((_rand_point(), _rand_point()), fill="gray", width=random.randrange(1, 3))

    for i in range(10, random.randrange(11, 20)):
        draw.point(
            (_rand_point(), _rand_point(), _rand_point(),
             _rand_point(), _rand_point(), _rand_point(),
             _rand_point(), _rand_point(), _rand_point(),
             _rand_point()),
            fill='black'
        )

    out = BytesIO()
    img.save(out, 'png')
    out.seek(0)

    return out.getvalue()


def _rand_point():
    return random.randrange(5, 85), random.randrange(5, 55)
