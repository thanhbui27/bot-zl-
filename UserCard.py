from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

class UserCard:
    def __init__(self, name, birth_date, join_date, activity_date, group_name, avatar_url, foodext):
        self.name = name
        self.birth_date = birth_date
        self.join_date = join_date
        self.activity_date = activity_date
        self.group_name = group_name
        self.avatar_url = avatar_url
        self.foodext = foodext
        self.width = 2000
        self.height = 800
        self.size_image = 300
        self.background = None
        # Colors  đổi màu ở đây
        self.gradient_start = (255, 0, 0)  # Red
        self.gradient_end = (0, 0, 255)    # Blue
        self.font_large = ImageFont.truetype("arialbd.ttf", 100)
        self.font_medium = ImageFont.truetype("arialbd.ttf", 60)
        self.font_small = ImageFont.truetype("arialbd.ttf", 40)

    def draw_gradient(self):
        background = Image.new("RGB", (self.width, self.height), self.gradient_start)
        draw = ImageDraw.Draw(background)

        for y in range(self.height):
            r = int(self.gradient_start[0] + (self.gradient_end[0] - self.gradient_start[0]) * y / self.height)
            g = int(self.gradient_start[1] + (self.gradient_end[1] - self.gradient_start[1]) * y / self.height)
            b = int(self.gradient_start[2] + (self.gradient_end[2] - self.gradient_start[2]) * y / self.height)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        return background

    def fetch_avatar(self):
        try:
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }
            response = requests.get(self.avatar_url,headers=headers, timeout=0.5) 
            response.raise_for_status()  
            avatar = Image.open(BytesIO(response.content)).resize((self.size_image, self.size_image), Image.LANCZOS)
            
            mask = Image.new("L", (self.size_image, self.size_image), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, self.size_image, self.size_image), fill=255)
            avatar.putalpha(mask)
            return avatar
        
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tải ảnh từ {self.avatar_url}: {e}")
            return Image.new("RGBA", (self.size_image, self.size_image), (255, 0, 0, 0))


    def draw_text(self, draw):
        xText = 500
        yText = 200
        color = (95, 0, 163)
        draw.text((xText, 60), f"{self.name}!", font=self.font_large, fill=color)
        draw.text((xText, yText + 30), f"Ngày sinh: {self.birth_date}", font=self.font_small, fill=color)
        draw.text((xText, yText + 100), f"Tham gia zalo: {self.join_date}", font=self.font_small, fill=color)
        draw.text((xText, yText + 170), f"Ngày hoạt động: {self.activity_date}", font=self.font_small, fill=color)

        footer_text = self.foodext
        return footer_text

    def draw_footer(self, draw, footer_text):
        color = (163, 0, 0)
        footer_text_width, footer_text_height = draw.textbbox((0, 0), footer_text, font=self.font_medium)[2:4]

        footer_box_padding = 20
        footer_left = footer_box_padding
        footer_right = self.width - footer_box_padding
        footer_bottom = self.height - footer_box_padding
        corner_radius = 30

        footer_background_color = (0, 51, 102)
        
        draw.rounded_rectangle(
            [footer_left, footer_bottom - footer_text_height - footer_box_padding * 2, 
             footer_right, footer_bottom],
            radius=corner_radius, fill=footer_background_color, outline=(139, 0, 0), width=3
        )

        draw.text((footer_left + (footer_right - footer_left - footer_text_width) // 2, 
             footer_bottom - footer_text_height - footer_box_padding), 
            footer_text, font=self.font_medium, fill=color,align = "center")

    def create_card(self):
        background = self.draw_gradient()
        draw = ImageDraw.Draw(background)
        avatar = self.fetch_avatar()

        background.paste(avatar, (100, 100), avatar)

        footer_text = self.draw_text(draw)
        self.draw_footer(draw, footer_text)

        background.save("user_card.png")
        #background.show()

# Sử dụng lớp UserCard
# if __name__ == "__main__":
#     name = "super me"
#     birth_date = "28 01 2002"
#     join_date = "01/11/2024"
#     activity_date = "02/11/2024"
#     group_name = "Group honkai zaalo"
#     avatar_url = "https://s120-ava-talk.zadn.vn/6/7/b/a/5/120/dea575169b69d38a56ea9527d7048806.jpg"

#     user_card = UserCard(name, birth_date, join_date, activity_date, group_name, avatar_url, f"{name} vừa rời khỏi nhóm \n{group_name}")
#     user_card.create_card()
