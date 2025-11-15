from django.urls import path
from users import views

urlpatterns = [
    path('create-titulor/', views.CreateTitulor.as_view(), name='create_titulor'),
    path('',views.home,name='home'),
    path('all/members/',views.MemberListView.as_view(),name='list_members'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(next_page='login'), name='logout'),
    path('create/members/',views.CreateSimpleMemberView.as_view(),name='create_member'),
    path('show/member/<int:pk>/', views.MemberDetaiView.as_view(), name='show_member'),
    path('delete/member/<int:pk>/',views.MemberDeleteView.as_view(),name='delete_member'),
    path('rom/not/verified/',views.room_not_verified,name='room_not_verified'),
    path('profile/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/password/', views.UserPasswordChangeView.as_view(), name='change_password'),
    path('help/',views.help,name='help'),
    path('rooms/', views.RoomList.as_view(), name='room_list'),
    path('rooms/<int:pk>/update_status/', views.RoomStatusUpdateView.as_view(), name='room_status_update'),
    path('simple/members/created',views.simple_member_created,name='simple_member_created'),
]