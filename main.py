from config import API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES, THREAD_ID, BLACK_LIST,ALLOWED_USER_ID
from bot import BOT
from zlapi import ZaloAPI
from colorama import Fore, Style, init
from zlapi.models import GroupEventType,ThreadType
from UserCard import UserCard
from datetime import datetime
import time

init(autoreset=True)

class Client(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies):
        super().__init__(api_key, secret_key, imei=imei, session_cookies=session_cookies)
        self.bot = BOT(self)

    def check_blacklist(self,title):
        for word in BLACK_LIST:
            if word in title:
                return True
        return False
    
    def can_send_link(self,user_id):
        return int(user_id) in ALLOWED_USER_ID
    
    def convert_timestamp(self,timestamp):

        timestamp = int(timestamp)

        if timestamp > 1_000_000_000: 
            timestamp_seconds = timestamp / 1000 
        else:
            timestamp_seconds = timestamp  

        date_time = datetime.fromtimestamp(timestamp_seconds)

        return date_time.strftime("%Y-%m-%d %H:%M:%S")
    
    def onEvent(self, event_data, event_type):
        try :
            # print(f"{Fore.GREEN}{Style.BRIGHT}------------------------------\n"
            #         f"- event_data: {Style.BRIGHT}{event_data} {Style.NORMAL}\n"
            #         f"- event_type: {Fore.MAGENTA}{Style.BRIGHT}{event_type} {Style.NORMAL}\n"
            #         f"{Fore.GREEN}{Style.BRIGHT}------------------------------\n"
            #     )
            if(event_type == GroupEventType.REMOVE_MEMBER):

                user_data = self.fetchUserInfo([member['id'] for member in event_data['updateMembers']][0])
                profile = user_data.changed_profiles[[member['id'] for member in event_data['updateMembers']][0]]
                display_name = profile.get("displayName", "Không có tên hiển thị")
                avatar = profile.get("avatar", "https://lumiere-a.akamaihd.net/v1/images/a_avatarpandorapedia_neytiri_16x9_1098_01_0e7d844a.jpeg?region=420%2C0%2C1080%2C1080")
                lastActionTime = self.convert_timestamp(profile.get("lastActionTime", f"{time.time()}"))
                lastUpdateTime = self.convert_timestamp(profile.get("lastUpdateTime", f"{time.time()}"))
                sdob = profile.get("sdob", "1/1/2000")

                user_card = UserCard(f"Tạm biệt, {display_name}", sdob, lastUpdateTime, lastActionTime, event_data["groupName"], avatar, f"{display_name} vừa rời khỏi nhóm \n {event_data.groupName} ")
                user_card.create_card()
                print(f"display_name : {display_name} - avatar : {avatar} - lastActionTime : {lastActionTime} - lastUpdateTime : {lastUpdateTime} - sdob : {sdob}")

                self.sendLocalImage("user_card.png", event_data['groupId'], ThreadType.GROUP, width = 2000, height = 800)

            elif(event_type == GroupEventType.JOIN):
                user_data = self.fetchUserInfo([member['id'] for member in event_data['updateMembers']][0])
                profile = user_data.changed_profiles[[member['id'] for member in event_data['updateMembers']][0]]
                display_name = profile.get("displayName", "Không có tên hiển thị")
                avatar = profile.get("avatar", "https://lumiere-a.akamaihd.net/v1/images/a_avatarpandorapedia_neytiri_16x9_1098_01_0e7d844a.jpeg?region=420%2C0%2C1080%2C1080")
                lastActionTime = self.convert_timestamp(profile.get("lastActionTime", f"{time.time()}"))
                lastUpdateTime = self.convert_timestamp(profile.get("lastUpdateTime", f"{time.time()}"))
                sdob = profile.get("sdob", "1/1/2000")

                user_card = UserCard(f"Chào mừng, {display_name}", sdob, lastUpdateTime, lastActionTime, event_data["groupName"], avatar, f"{display_name} vừa Tham gia vào \n nhóm {event_data.groupName}")
                user_card.create_card()

                print(f"display_name : {display_name} - avatar : {avatar} - lastActionTime : {lastActionTime} - lastUpdateTime : {lastUpdateTime} - sdob : {sdob}")

                self.sendLocalImage("user_card.png", event_data['groupId'], ThreadType.GROUP, width = 2000, height = 800)

        except Exception as e :
            print(f"error in on lisstion : {e}")




    def onMessage(self, mid , author_id, message, message_object, thread_id, thread_type):
        # thread_id = 6973176668452888712
        try: 
            if thread_id not in THREAD_ID:
                return
            
            if isinstance(message, list):
                if message[0].type == 3 : 
                    return
            
            print(f"{Fore.GREEN}{Style.BRIGHT}------------------------------\n"
                f"- Message: {Style.BRIGHT}{message} {Style.NORMAL}\n"
                f"- ID NGƯỜI DÙNG: {Fore.MAGENTA}{Style.BRIGHT}{author_id} {Style.NORMAL}\n"
                f"- ID NHÓM: {Fore.YELLOW}{Style.BRIGHT}{thread_id}{Style.NORMAL}\n"
                f"- Message Object : {message_object}\n"
                f"{Fore.GREEN}{Style.BRIGHT}------------------------------\n"
            )
            
            if isinstance(message, str):
                self.bot.handle_check_num_massage(author_id,message, message_object, thread_id, thread_type)    
            elif(hasattr(message, 'title') and message.title):
                if not self.can_send_link(author_id):
                    self.bot.handle_remove_message_send_link(author_id,message,message_object,thread_id,thread_type)
                if(self.check_blacklist(message.title)):          
                    self.bot.handle_check_num_massage(author_id,message, message_object, thread_id, thread_type) 
            elif all(hasattr(message, attr) for attr in ['id', 'catId', 'type', 'extInfo']):
                    self.bot.handle_check_num_massage(author_id,message, message_object, thread_id, thread_type) 
        except Exception as e:
            print(f"error onMessage : {e}")

if __name__ == "__main__":
    client = Client(API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES)
    client.listen(thread=True)
