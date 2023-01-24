from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Room,Message




# Create your views here.
def getAllDms(request):    
    #rooms = Room.objects.all().exclude(users_subscribed__in=[request.user])
    users = User.objects.all().exclude(id=request.user.id)
    context = {'users':users,'page':'components/_aside.html'}
         
    return render(request,'base.html',context)

def getRecentDms(request):    
    usrs = []
    chats = []
    ot_users = User.objects.all().exclude(id=request.user.id)    
    for ot in ot_users:
        usr = Room.objects.filter(users_subscribed__in=[ot]).intersection(Room.objects.filter(users_subscribed__in=[request.user.id])).first()       
        chat = Message.objects.filter(room=usr,user=ot).last()
        if chat:            
            usrs.append(ot)
            chats.append(chat)            
    context = {'cht_usrs':usrs,'chats':chats}
    context.update({'page':'components/_currdms.html'})
    return render(request,'base.html',context)  





