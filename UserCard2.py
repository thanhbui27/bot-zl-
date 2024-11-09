from datetime import datetime
import time
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from zlapi import ZaloAPI
from config import API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES, THREAD_ID, BLACK_LIST, ALLOWED_USER_ID

class UserCard:
    def __init__(self, name, gender, join_date, last_action,business, group_name, avatar_url, footer_text):
        self.name = name
        self.gender = gender
        self.join_date = join_date
        self.last_action = last_action
        self.business = business
        self.group_name = group_name
        self.avatar_url = avatar_url
        self.footer_text = footer_text
        self.width = 2000
        self.height = 800
        self.size_image = 300
        self.background_path = "./image/mặt 1.1.png"

        try:
            self.font_large = ImageFont.truetype("./font/Pangolin-Regular.ttf", 50)
            self.font_medium = ImageFont.truetype("./font/Pangolin-Regular.ttf", 40)
            self.font_small = ImageFont.truetype("./font/Pangolin-Regular.ttf", 30)
        except IOError:
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

    def load_background(self):
        try:
            background = Image.open(self.background_path).convert("RGB")
            if background.size != (self.width, self.height):
                background = background.resize((self.width, self.height), Image.LANCZOS)
            return background
        except IOError:
            print(f"Không thể tải ảnh nền từ {self.background_path}")
            return Image.new("RGB", (self.width, self.height), (255, 255, 255))

    def fetch_avatar(self):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }
            response = requests.get(self.avatar_url, headers=headers, timeout=0.5)
            response.raise_for_status()
            avatar = Image.open(BytesIO(response.content)).resize((self.size_image, self.size_image), Image.LANCZOS)

            mask = Image.new("L", (self.size_image, self.size_image), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, self.size_image, self.size_image), fill=255)
            avatar.putalpha(mask)
            return avatar
        
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tải ảnh avatar từ {self.avatar_url}: {e}")
            return Image.new("RGBA", (self.size_image, self.size_image), (255, 0, 0, 0))

    def draw_text(self, draw):
        xText = 350
        yText = 340
        color = (3, 177, 252)
        draw.text((xText, 340), f"{self.name}", font=self.font_large, fill=color)
        draw.text((xText - 20 , yText + 80), f"{self.gender}", font=self.font_medium, fill=color)
        draw.text((xText + 100, yText + 160), f"{self.business}", font=self.font_medium, fill=color)
        draw.text((xText + 100, yText + 240), f"{self.join_date}", font=self.font_small, fill=color)
        draw.text((xText  + 170, yText + 320), f"{self.last_action}", font=self.font_small, fill=color)
        draw.text((xText + 120 , yText + 380), f"{self.footer_text}", font=self.font_small, fill=color, align ="center")
        
    def create_card(self):
        background = self.load_background()
        draw = ImageDraw.Draw(background)
        avatar = self.fetch_avatar()
        background.paste(avatar, (735, 375), avatar)
        self.draw_text(draw)

        background.save("user_card.png")
        # background.show()

def convert_timestamp(timestamp):

    timestamp = int(timestamp)

    if timestamp > 1_000_000_000: 
        timestamp_seconds = timestamp / 1000 
    else:
        timestamp_seconds = timestamp  

    date_time = datetime.fromtimestamp(timestamp_seconds)

    return date_time.strftime("%Y-%m-%d %H:%M:%S")

# if __name__ == "__main__":
#     bot = ZaloAPI(API_KEY, SECRET_KEY, imei=IMEI, session_cookies=SESSION_COOKIES)
#     user_data = bot.fetchUserInfo(2159282708136685498)
#     profile = user_data.changed_profiles['2159282708136685498']

#     name = profile.get("displayName", "Không có tên hiển thị")
#     gender = "Nam" if profile.get("gender") == 0 else "Nữ" if profile.get("gender") == 1 else "Không thể hiển thị"
#     join_date = convert_timestamp(profile.get("createdTs", f"{time.time()}"))
#     last_action = convert_timestamp(profile.get("lastActionTime", f"{time.time()}"))
#     avatar_url = profile.get("avatar", "https://s120-ava-talk.zadn.vn/6/7/b/a/5/120/dea575169b69d38a56ea9527d7048806.jpg")
#     group_name = "Group honkai zaalo"
#     footer_text = f"{name} vừa rời khỏi \n nhóm {group_name}"
#     business = profile.get("oaInfo", "Không thể hiển thị")
#     user_card = UserCard(name, gender, join_date, last_action,business ,group_name, avatar_url, footer_text)
#     user_card.create_card()
