from django.urls import reverse
from asgiref.sync import async_to_sync
from django.template.loader import render_to_string
from .models import Message,Client,Room
from django.contrib.auth.models import User

def get_name_room_active(self):
    """get the name of the group from login user"""
    #client = Client.objects.get(user=self.scope['user'])
    room = Room.objects.filter(client_active__user_id=self.scope["user"].id).first()
    return room.name

def remove_client_from_current_room(self):
    """remove client from current group"""
    client = Client.objects.get(user=self.scope['user'])
    # get the current group
    rooms = Room.objects.filter(client_active__in=[client])
    for room in rooms:
        # remove the client from the group
        async_to_sync(self.channel_layer.group_discard)(room.name, self.channel_name)
        # remove the client from the room instance
        room.client_active.remove(client)
        room.save()
        

def list_room_messages(self):
    """list all messages from a group"""
    room_name = get_name_room_active(self)
    
    #get room inst
    room =  Room.objects.get(name=room_name)
    # get all messages from the room
    messages = Message.objects.filter(room=room).order_by('timestamp')
    user = self.scope['user']
    sent_usr = self.usr_target
    # render to the html and send to client
    async_to_sync(self.channel_layer.group_send)(
        room_name, {
            'type':'send.html', #run send_html method
            'selector': '#message-list',            
            'html': render_to_string('components/_list_messages.html',{'messages':messages,'sent':sent_usr,'user':user})                        
        }
    )      

def save_message(self,text):
    """save a message in the database"""
    # get room 
    room = Room.objects.get(name=get_name_room_active(self))
    # save messae
    Message.objects.create(user=self.scope['user'],room=room,text=text)

def send_room_name(self):
    """send room name to client"""                    
    room_name = get_name_room_active(self)
    room = Room.objects.get(name=room_name)
    data = {
        'selector': '#group-name',
        'html': ('#' if room.is_group else '') + room_name,
    }
    self.send_json(data)
    
def add_client_to_room(self, room_name=None, is_group=False):
    """add customer to a room within channels and save the reference in the room model"""
    # get the user client    
    client = Client.objects.get(user=self.scope['user'])    
    # remove the client from the previous room
    remove_client_from_current_room(self)
    # get or create a room inst
    try:
        room = Room.objects.get(name=room_name,is_group=is_group)        
    except Room.DoesNotExist:
        room = Room.objects.create(is_group=is_group,name=room_name)                
        room.users_subscribed.add(client.user,self.usr_target)
    room.client_active.add(client)
    room.save()
    # add client to room
    async_to_sync(self.channel_layer.group_add)(room.name, self.channel_name)
    # send group name to client
    send_room_name(self)

def alldms(self):
    users = User.objects.all().exclude(id=self.scope['user'].id)
    data = {
        'selector': '#dmusers',
        'html': render_to_string('components/_aside.html',{'users':users}),
        'url': reverse('ims:alldms'),
    }
    self.send_html(data)

def recentdms(self):
    usrs = []
    chats = []
    ot_users = User.objects.all().exclude(id=self.scope['user'].id)    
    for ot in ot_users:
        usr = Room.objects.filter(users_subscribed__in=[ot]).intersection(Room.objects.filter(users_subscribed__in=[self.scope['user'].id])).first()       
        chat = Message.objects.filter(room=usr,user=ot).last()
        if chat:            
            usrs.append(ot)
            chats.append(chat)    
    context = {'cht_usrs':usrs,'chats':chats}
    data = {
        'selector': '#dmusers',
        'html': render_to_string('components/_currdms.html',context),
        'url': reverse('ims:recentdms')
    }
    self.send_html(data)                       


