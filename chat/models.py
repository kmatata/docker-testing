from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

class Client(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='clnt_name')
    channel = models.CharField(max_length=200,blank=True,null=True,default=None)

    def __str__(self):
        return self.user.username

class Room(models.Model):
    users_subscribed = models.ManyToManyField(User,related_name='user_subd')
    client_active = models.ManyToManyField(Client,related_name='client_actv')
    name = models.CharField(max_length=200,blank=True,null=True, default=None)
    is_group = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User,related_name='sender',on_delete=models.CASCADE,blank=True,null=True,default=None)
    room = models.ForeignKey(Room,on_delete=models.CASCADE,blank=True,null=True,default=None)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return self.text