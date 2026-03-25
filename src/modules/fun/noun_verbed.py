from PIL import Image, ImageDraw, ImageFont, ImageFilter
from enum import Enum
from pathlib import Path
import logging
from dataclasses import dataclass
import enum


@enum.unique
class TextTypes(Enum):
    victory_achieved = "victory achieved"
    you_died = "you died"
    area_entered = "Blighttown"
    humanity_restored = "Humanity restored"
    bonfire_lit = "bonfire lit"
    retrieval = "retrieval"
    target_destroyed = "target destroyed"



def color_picker(input:TextTypes):

    alpha = 120
    match input:
        case TextTypes.victory_achieved:
            return ColorScheme(textcolor=(255, 248, 85),
                               glowcolor=(255, 248, 85, alpha))
        case TextTypes.you_died:
            return ColorScheme(textcolor=(100, 10, 10),
                               glowcolor=(0, 0, 0, 0))
        case TextTypes.area_entered:
            return ColorScheme(textcolor=(227, 226, 224),
                               glowcolor=(0, 0, 0, 0))
        case TextTypes.humanity_restored:
            return ColorScheme(textcolor=(129,187,153),
                               glowcolor=(187, 201, 192, alpha))
        case TextTypes.bonfire_lit:
            return ColorScheme(textcolor=(255, 228, 92),
                               glowcolor=(251, 149, 131, alpha))

        case TextTypes.retrieval:
            return ColorScheme(textcolor=(161, 217, 226),
                               glowcolor=(154, 158, 167, alpha))
        case TextTypes.target_destroyed:
            return ColorScheme(textcolor=(250, 201, 91),
                               glowcolor=(231, 133, 115, alpha))
        
@dataclass
class ColorScheme:
    textcolor: tuple
    glowcolor: tuple

@dataclass
class ImageInfoContainer:
    text:str
    text_type: TextTypes

    width:int
    height:int
    font_size: int

    font: ImageFont.FreeTypeFont 

    color_scheme:ColorScheme
    
    @property
    def text_bbox(self):
        return self.font.getbbox(self.text, anchor="mm")
    
    @property
    def text_height(self):
        return self.text_bbox[3] - self.text_bbox[1]


    @property
    def x_center(self):
        return self.width//2

    @property
    def y_center(self):
        return self.height//2
    
    @property
    def dims_vec(self):
        return (self.width, self.height)
    
    @property
    def img_center(self):
        return (self.x_center, self.y_center)


def noun_verbed(text:str|None, text_type: TextTypes, user_image: Image.Image|None = None):

    if text is None:
        text=text_type.value

    text= text.upper()

    if user_image is None:
        width = 1280
        height = width * 9 // 16
        bg_image = Image.new("RGBA", (width, height), color=(0,0,0,0))
    else:
        width = user_image.width
        height = user_image.height
        bg_image = user_image.convert("RGBA")



    font_size = height//10
    font = ImageFont.truetype(Path("assets/fonts/AGaramondPro-Regular.otf"), size = font_size)

    info = ImageInfoContainer(
        text=text,
        text_type=text_type,
        width= width,
        height=height,
        font_size=font_size,
        font=font,
        color_scheme=color_picker(text_type)
    )

    
    img = bg_image

    if not text_type == TextTypes.area_entered:
        shadow = generate_black_shadow(info)
        img = Image.alpha_composite(img, shadow)

    if not text_type in (TextTypes.area_entered, TextTypes.you_died):
        text_img = generate_text_glow(info)
        img = Image.alpha_composite(img, text_img)


    draw = ImageDraw.Draw(img)

    draw.text(info.img_center, text, fill=info.color_scheme.textcolor, font=font, anchor="mm")

    if info.text_type == TextTypes.area_entered:
        draw_underline(info=info, draw=draw)
        
    

    return img


def draw_underline(info:ImageInfoContainer, draw:ImageDraw.ImageDraw):
    width = 4
    offset = 2

    x1 = (info.text_bbox[0]*1.5) +info.x_center
    x2 = info.text_bbox[3]+info.y_center+offset
    y1 = (info.text_bbox[2] * 1.5)+info.x_center 
    y2 = info.text_bbox[3]+info.y_center+width+offset

    draw.ellipse(xy=[x1,x2 ,y1 ,y2 ], fill=info.color_scheme.textcolor, width=0)


def generate_black_shadow(info:ImageInfoContainer):

    black_padding = info.text_height + info.height//18

    overlay = Image.new("RGBA", info.dims_vec, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    overlay_draw.rectangle(
        [
            (-100, info.y_center - black_padding),
            (info.width + 100, info.y_center + black_padding)
        ],
        fill=(0, 0, 0, 225) 
    )
    
    overlay = overlay.filter(ImageFilter.GaussianBlur(20))

    return overlay



def generate_text_glow(info:ImageInfoContainer):

    overlay = Image.new("RGBA", info.dims_vec, color=(0,0,0,0))
    for i in range(info.font_size//2):
        edgesize = i

        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.text(info.img_center, info.text, fill=info.color_scheme.glowcolor, font=info.font, anchor="mm")
        temp = overlay.resize(info.dims_vec, box = (edgesize, edgesize, info.width-edgesize, info.height-edgesize))


        r, g, b, a = temp.split()
        opacity = 0.1

        lut = [0 if i == 0 else int(i * opacity) for i in range(256)]
        a = a.point(lut)

        temp = Image.merge("RGBA", (r, g, b, a))

        overlay = Image.alpha_composite(overlay, temp)

    return overlay


