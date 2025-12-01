from django import forms

from colloc import settings
from .models import RoomMember, Room
import string,secrets
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

class RoomTitulorCreationForm(forms.ModelForm):
    room_number = forms.CharField(
        max_length=20,
        label="Numéro de la chambre",
        widget=forms.TextInput(attrs={
            "class": "form-control mb-3",
            "placeholder": "Ex : 634"
        })
    )

    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            "class": "form-control mb-3",
            "placeholder": "Mot de passe sécurisé"
        })
    )

    class Meta:
        model = RoomMember
        fields = ['username', 'email', 'password']  # champs autorisés seulement
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': 'Nom d’utilisateur'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': 'Adresse email'
            }),
        }

    def save(self, commit=True):
        member = super().save(commit=False)
        member.memberStatus = RoomMember.MemberStatus.TITULOR
        member.set_password(self.cleaned_data['password'])

        if commit:
            member.save()
            room_number = self.cleaned_data.get('room_number')
            room = Room.objects.create(roomNumber=room_number, roomTitulor=member)
            member.room = room
            member.save()

        return member



class SimpleMemberCreationForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )

    class Meta:
        model = RoomMember
        fields = ['email']

    def save(self, commit=True, room=None):
        member = super().save(commit=False)
        member.memberStatus = RoomMember.MemberStatus.SIMPLE_MEMBER

        # Username automatique + password généré ⬇
        member.username = "user" + ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(12))
        member.set_password(temp_password)

        if room:
            member.room = room

        if commit:
            member.save()
            subject = "Bienvenue sur Colloc Manager"
            text = f"Voici votre compte:\nIdentifiant: {member.username}\nMot de passe: {temp_password}"
            send_mail(subject, text, settings.DEFAULT_FROM_EMAIL, [member.email])

        return member, temp_password



class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = RoomMember
        fields = ['username', 'email']  # réduit à ce qui existe
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
