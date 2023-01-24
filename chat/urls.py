from django.urls import path
from .views import getAllDms,getRecentDms

app_name = 'ims'

urlpatterns = [
    path('',getAllDms,name='alldms'),
    path('recent-chats/',getRecentDms,name='recentdms'),
    #path('livechats/<str:room_name>/',ChatRoom.as_view(),name='room'),
]