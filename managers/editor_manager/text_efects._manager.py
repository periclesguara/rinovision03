import os
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip


class TextEffects:
    def __init__(self, fonts_dir="fonts"):
        self.fonts_dir = fonts_dir
        self.default_duration = 5  # segundos
        self.default_fontsize = 48
        self.default_color = "white"
        self.supported_fonts = {
            "arial": "Arial.ttf",
            "arial_black": "Arial Black.ttf",
            "times": "Times New Roman.ttf",
            "verdana": "Verdana.ttf",
            "typewriter": "Courier New.ttf",
            "comic_sans": "Comic Sans MS.ttf",
            "impact": "Impact.ttf",
            "georgia": "Georgia.ttf",
        }

    def get_font_path(self, font_name):
        if font_name not in self.supported_fonts:
            raise ValueError(f"Fonte '{font_name}' não suportada.")
        return os.path.join(self.fonts_dir, self.supported_fonts[font_name])

    def apply_text_overlay(
        self,
        video_path,
        text,
        font="arial",
        effect="fadein",
        output_path="output_video.mp4",
    ):
        font_path = self.get_font_path(font)
        video = VideoFileClip(video_path)

        txt_clip = TextClip(
            txt=text,
            fontsize=self.default_fontsize,
            font=font_path,
            color=self.default_color,
            method="label",
            size=(video.w * 0.8, None),
        )

        txt_clip = txt_clip.set_duration(self.default_duration).set_position(
            ("center", "bottom")
        )

        if effect == "fadein":
            txt_clip = txt_clip.crossfadein(1)
        elif effect == "slide":
            txt_clip = txt_clip.set_start(0).set_position(
                lambda t: ("center", int(100 + t * 50))
            )
        elif effect == "zoom_jump":
            txt_clip = txt_clip.resize(lambda t: 1 + 0.5 * abs(t - 2))
        elif effect == "typewriter":
            txt_clip = txt_clip.set_duration(self.default_duration).fl_time(
                lambda t: min(t, len(text) / 10)
            )
        elif effect == "pixel":
            txt_clip = txt_clip.resize(0.5).resize(2)

        final = CompositeVideoClip([video, txt_clip.set_start(0)])
        final.write_videofile(output_path, codec="libx264", audio_codec="aac")

        print(f"[TextEffects] Vídeo com texto salvo em {output_path}")
