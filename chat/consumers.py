from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message,Client,Room
from . import actions
from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string


class DmConsumer(JsonWebsocketConsumer):        
    #Client.objects.all().delete()
    def connect(self):
        #accept connection
        Client.objects.all().delete()
        usr_target = None
        self.accept()                   
        Client.objects.create(user=self.scope['user'],channel=self.channel_name)                                       
    def disconnect(self,close_code):
        """event when client disconnects"""
        # remove the client from the current room
        actions.remove_client_from_current_room(self)
        # deregister the client
        Client.objects.get(channel=self.channel_name).delete()
        #logout user
        #logout(self.scope,self.scope['user'])

    def receive_json(self,data_received):
        """
        event when data is received 
        all info will arrive in 2 variables
        'action' with the action to be taken
        'data' with the info
        """
        # get data
        try:
            data = data_received['data']
        except KeyError:
            pass
        #usnm = User.objects.get(username=data['groupName'])
        # depending on the action we will do one task or another
        match data_received['action']:
            case 'alldms':
                actions.alldms(self)                
            case 'recentdms':
                actions.recentdms(self)                
            case "Change group":
                """is group is false add to private 
                room with target user and the current user"""
                # get user whom youre going to speak to
                self.usr_target = None
                user_target = User.objects.filter(username=data['groupName']).first()
                self.usr_target = user_target
                # search for room where both users mathc                
                try:                    
                    room = Room.objects.filter(users_subscribed__in=[self.scope['user']],is_group=False).intersection(Room.objects.filter(users_subscribed__in=[user_target],is_group=False)).first()                                    
                    actions.add_client_to_room(self,room.name)                                        
                except:
                    room = Room.objects.filter(users_subscribed__in=[user_target],is_group=False).last()
                    if room and room.users_subscribed.count() == 1:
                        # there is a room, lets join
                        actions.add_client_to_room(self,room.name)                                        
                    else:
                        # no room where user target is alone, create a new room
                        name = get_random_string(10)
                        room_nm = f'private_rm{name}'
                        actions.add_client_to_room(self,room_nm)                                                                                   
                prof_pic = user_target.profile.picture

                data = {
                    'selector': '#userpic',
                    'html': render_to_string('components/_ppic.html',{'ppic':prof_pic,'usr':user_target})
                }
                self.send_html(data)
                actions.send_room_name(self)
                actions.list_room_messages(self)      
            case "New message":
                # we recieved a new message to save
                actions.save_message(self,data['message'])                
                actions.list_room_messages(self)      

    def send_html(self,event):
        """event: send html to client"""
        data = {
            'selector': event['selector'],
            'html': event['html'],
            "url": event["url"] if "url" in event else "",
            #"append": "append" in event and event["append"],
        }
        self.send_json(data)
    