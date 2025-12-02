from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, DeleteView, ListView,UpdateView
from users.models import RoomMember
from users.forms import RoomTitulorCreationForm,SimpleMemberCreationForm,ProfileUpdateForm
from django.contrib.auth.views import LoginView, LogoutView,PasswordChangeView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from users.models import Room
from django.core.mail import send_mail
from colloc import settings

# Create your views here.

## Vu pour la page d'accueil
def home(request):
    return render(request,'home.html')



###### Les vus pour la verification des status de la personne et autre
class LoginRequiredHomeMixin(LoginRequiredMixin):
    login_url = 'login'

#Une vue qui verifie si on est un superuser enfaite
class AdminRequiredMixin(LoginRequiredMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.is_superuser

    def handle_no_permission(self):
        # Redirige si pas de permission hum on va personnaliser ca par apres
        return redirect('home')

class RoomList(AdminRequiredMixin, ListView):
    model = Room
    template_name = 'users/room_list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        return Room.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Room.RoomStatus.choices
        return context
    
class RoomStatusUpdateView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        room_id = kwargs.get('pk')
        new_status = request.POST.get('new_status')

        room = get_object_or_404(Room, pk=room_id)

        valid_statuses = [status[0] for status in Room.RoomStatus.choices]
        if new_status in valid_statuses:
            room.roomStatus = new_status
            object = 'Changement de statut de votre room'
            message = f'Bonjour, \nLe statut de votre room a été modifié avec succès. Veuillez vous connecter maintenant sur notre application https://colloc-manager.com/ pour constater les modifications.\n\n Merci ce message est automatique nous vous prions de ne pas repondre. '
            send_mail(object, message, settings.DEFAULT_FROM_EMAIL, [room.roomTitulor.email])
            room.save()
        
        return redirect('room_list')
    
class TitulorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.memberStatus == self.request.user.MemberStatus.TITULOR

    def handle_no_permission(self):
        # Redirige si pas de permission hum on va personnaliser ca par apres
        return redirect('home')
    
class SimpleMemberRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.memberStatus == self.request.user.MemberStatus.SIMPLE_MEMBER

    def handle_no_permission(self):
        return redirect('home')
    
    
#### Les vu pour la creations des membres de la room titulor et simple members 
class CreateTitulor(CreateView):
    model = RoomMember
    form_class = RoomTitulorCreationForm
    template_name = 'users/create_titulor.html'
    success_url = reverse_lazy('list_members')


class CreateSimpleMemberView(TitulorRequiredMixin, CreateView):
    model = RoomMember
    form_class = SimpleMemberCreationForm
    template_name = 'users/create_simple_member.html'

    def dispatch(self, request, *args, **kwargs):
        # Vérifie si la room du titulor est vérifiée
        if not request.user.room or request.user.room.roomStatus != 'verified':
            return redirect('room_not_verified')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Associe le membre à la chambre du titulor
        room = self.request.user.room
        member, temp_password = form.save(room=room)  # On récupère le mot de passe
        context = {
            'member': member,
            'temp_password': temp_password
        }
        return render(self.request, 'users/simple_member_created.html', context)


def room_not_verified(request):
    return render(request,'users/room_not_verified.html')

def simple_member_created(request):
    return render(request,'simple_member_created.html')

################################## Vu pour permettre a l'utilisateur la gestion de son profil ##########
class ProfileDetailView(LoginRequiredHomeMixin, DetailView):
    model = RoomMember
    template_name = 'users/profile_detail.html'
    context_object_name = 'user_profile'

    def get_object(self):
        # Toujours retourner l'utilisateur connecté
        return self.request.user


# Modifier le profil
class ProfileUpdateView(LoginRequiredHomeMixin, UpdateView):
    model = RoomMember
    form_class = ProfileUpdateForm
    template_name = 'users/profile_update.html'
    success_url = reverse_lazy('profile_detail')

    def get_object(self):
        return self.request.user

class UserPasswordChangeView(LoginRequiredHomeMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('profile_detail')


##### Vu pour le RUD des membres de la home
class MemberDetaiView(LoginRequiredHomeMixin, DetailView):
    model = RoomMember
    template_name = 'users/detail_member.html'
    context_object_name = 'member'

class MemberDeleteView(TitulorRequiredMixin, DeleteView):
    model = RoomMember
    template_name = 'users/member_confirm_delete.html'
    context_object_name = 'member'
    success_url = reverse_lazy('list_members')

    def delete(self, request, *args, **kwargs):
        member = self.get_object()

        # Vérifie si le titulaire essaie de se supprimer lui-même
        if member == request.user:
            #Si c'est le cas on le renvoi dans la liste des membres
            return redirect('list_members')

        return super().delete(request, *args, **kwargs)


class MemberListView(LoginRequiredHomeMixin, ListView):
    model = RoomMember
    template_name = 'users/list_members.html'
    context_object_name = 'members'

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'room'):
            return RoomMember.objects.filter(room=user.room)
        return RoomMember.objects.none()





##### Maintenant Gerons les connexions et autres
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.memberStatus == user.MemberStatus.TITULOR:
            return reverse_lazy('list_members')
        else:
            return reverse_lazy('list_members')

class CustomLogoutView(LoginRequiredHomeMixin, LogoutView):
    next_page = 'login'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


def help(request):
    return render(request,'users/help.html')


#Une vu qui est base sur la confidentialite
def confidentiality(request):
    return render(request,'users/confidentiality.html')