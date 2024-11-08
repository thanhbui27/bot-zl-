import time
import json
from threading import Lock
from config import ADMIN,ALLOWED_USER_ID,TIME_RESET_COUNT, COUNT_KICK
from zlapi._message import Message, MessageStyle, MultiMsgStyle
import os
import requests
from PIL import Image

class BOT:
    def __init__(self, zlapi):
        self.zlapi = zlapi
        self.admin_id = ADMIN
        self.lock = Lock()
        self.adminMode = False
        self.user_data = {}
        
    def isAdmin(self, admin_id):
        return self.admin_id == admin_id

    def setAdminMode(self, message ,author_id, messager_object, thread_id, thread_type):
        if (author_id == self.admin_id):
            if "on" in message.lower():
                self.adminMode = True
                self.replyMessageCus("Đã bật chế độ chỉ dành cho admin", messager_object, thread_id, thread_type)
            elif "off" in message.lower():
                self.adminMode = False
                self.replyMessageCus("Đã tắt chế độ chỉ dành cho admin", messager_object, thread_id, thread_type)
            else:
                self.replyMessageCus("Sử dụng lệnh '/admin on' hoặc '/admin off' để bật/tắt",message,thread_id,thread_type)
        else :
            self.replyMessageCus("Bạn ko có quyền admin",message,thread_id,thread_type)

    def replyMessageCus(self, message_input, message_reply, thread_id, thread_type):
        try :
            style = MessageStyle(offset=5, length=10, style="bold")
            message = Message(text=message_input, style=style)
            self.zlapi.replyMessage(message,message_reply,thread_id,thread_type)
        except Exception as e:
            print(f"Error reply message: {e}")

    def sendMessageCus(self, message_input, thread_id, thread_type):
        style = MessageStyle(offset=5, length=10, style="bold")
        message = Message(text=message_input, style=style)
        self.zlapi.sendMessage(message,thread_id,thread_type)   

    def kick_user(self,user_id, group_id, thread_type):
        self.zlapi.kickUsersInGroup(user_id, group_id)   
        self.zlapi.blockUsersInGroup(user_id, group_id)
        for msg in self.user_data[user_id]['messages']:
            self.remove_message_user(msg,user_id ,group_id, thread_type)
             
    def can_send_link(self,user_id):
        return int(user_id) in ALLOWED_USER_ID

    def handle_message(self, message,message_reply,thread_id, thread_type):
        with open("responses.json", "r", encoding="utf-8") as file:
            responses = json.load(file)

        message_lower = message.lower()
        for keyword, response in responses.items():
            if keyword in message_lower:
                content = response["content"]
                kcontent = f"{content}"
                self.sendMessageCus(kcontent,thread_id,thread_type)
                try:
                    file_path = response["file_path"]
                    if file_path is not None and file_path != "":
                        im = Image.open(file_path)
                        width, height = im.size
                        self.zlapi.sendLocalImage(file_path, thread_id, thread_type,width,height)  
                except KeyError:
                    print("Key 'file_path' not found in response")
                except Exception as e:
                    print(f"An error occurred: {e}")
          

    def remove_message_user(self,message_object, author_id,groupId, thread_type):

        if not message_object:
            msg = f"• Không thể xoá tin nhắn vì cú pháp không hợp lệ!\n\n"
            styles = MultiMsgStyle([
                MessageStyle(offset=0, length=2, style="color", color="#f38ba8", auto_format=False),
                MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
                MessageStyle(offset=msg.find("Command:"), length=11, style="bold", auto_format=False),
                MessageStyle(offset=msg.find("Command:"), length=1, style="color", color="#585b70", auto_format=False),
                MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
            ])
            self.zlapi.replyMessage(Message(text=msg, style=styles), message_object, groupId, thread_type)
            return
      
        if hasattr(message_object, 'quote') and message_object.quote:
            msg_obj = message_object.quote
        else :
            msg_obj = message_object
        
        self.zlapi.deleteGroupMsg(msg_obj.msgId, author_id, msg_obj.cliMsgId, groupId)  
    

    def handle_count_message(self, author_id, message_object):
        current_time = time.time()
        if author_id not in self.user_data:
            self.user_data[author_id] = {'count': 0, 'last_time': current_time, 'messages': []} 

        elapsed_time = current_time - self.user_data[author_id]['last_time']
        if elapsed_time > TIME_RESET_COUNT:
            self.user_data[author_id]['count'] = 1  
            self.user_data[author_id]['last_time'] = current_time  
            self.user_data[author_id]['messages'] = [message_object]
        else:
            self.user_data[author_id]['count'] += 1 
            self.user_data[author_id]['messages'].append(message_object) 

    def handle_remove_message_send_link(self, author_id, message, message_object, thread_id, thread_type):
        try:
            self.remove_message_user(message_object,author_id,thread_id,thread_type)
            self.handle_check_num_massage(author_id, message, message_object, thread_id, thread_type)
        except Exception as e : 
            print(f"error in handle_remove_message_send_link : {e} \n" )

    def handle_check_num_massage(self, author_id, message, message_object, thread_id, thread_type):
        try:
            if isinstance(message, list):
                if message[0].type == 3:
                    return  
            if isinstance(message, str):
                self.handle_message(message,message_object,thread_id,thread_type)
            self.handle_count_message(author_id,message_object)
            
            mess=None
            print(f"count {self.user_data[author_id]['count']} -  id : {author_id}")
            if self.user_data[author_id]['count'] >= COUNT_KICK:                     
                mess = f"Cảnh báo: thằng chó ({author_id}) Mày đã sủa quá nhiều"
                self.kick_user(author_id, thread_id, thread_type)
                del self.user_data[author_id]

            if mess : 
                self.replyMessageCus(mess,message_object,thread_id,thread_type)
            
        except Exception as e : 
            print(f"error in handle_check_num_massage : {e} \n" )


