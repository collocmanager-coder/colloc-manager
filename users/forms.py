from django import forms

from colloc import settings
from .models import RoomMember, Room
import string,secrets
from django.core.mail import send_mail

class RoomTitulorCreationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        label="Prénom",
        widget=forms.TextInput(attrs={
            "class": "form-control mb-3",
            "placeholder": "Entrez votre prénom"
        })
    )

    last_name = forms.CharField(
        max_length=50,
        label="Nom",
        widget=forms.TextInput(attrs={
            "class": "form-control mb-3",
            "placeholder": "Entrez votre nom"
        })
    )

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
        fields = ['first_name', 'last_name', 'username', 'email', 'phoneNumber', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': 'Nom d’utilisateur'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': 'Adresse email'
            }),
            'phoneNumber': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': 'Numéro de téléphone'
            }),
        }

    def save(self, commit=True):
        member = super().save(commit=False)
        member.memberStatus = RoomMember.MemberStatus.TITULOR
        member.set_password(self.cleaned_data['password'])

        if commit:
            member.save()
            room_number = self.cleaned_data.get('room_number')
            room = Room.objects.create(
                roomNumber=room_number,
                roomTitulor=member
            )
            member.room = room
            member.save()

        return member


class SimpleMemberCreationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        label="Prénom",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez le prénom"})
    )
    last_name = forms.CharField(
        max_length=50,
        label="Nom",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez le nom"})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )
    phoneNumber = forms.CharField(
        max_length=15,
        label="Téléphone",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Numéro de téléphone"})
    )

    class Meta:
        model = RoomMember
        fields = ['first_name', 'last_name', 'email', 'phoneNumber']

    def save(self, commit=True, room=None):
        member = super().save(commit=False)
        member.memberStatus = RoomMember.MemberStatus.SIMPLE_MEMBER

        # Génération aléatoire du username
        member.username = "user" + ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))

        # Génération aléatoire du mot de passe
        alphabet = string.ascii_letters + string.digits + string.punctuation
        temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
        member.set_password(temp_password)

        if room:
            member.room = room

        if commit:
            member.save()

            # Envoi du mot de passe par mail
            send_mail(
                subject="Bienvenue sur Colloc Manager",
                message=f"Bonjour {member.first_name},\n\nVotre compte a été créé.\n\nNom d’utilisateur : {member.username}\nMot de passe : {temp_password}\n\nVous pouvez vous connecter ici : sur notre site colloc-manager\n\nMerci ! (*_*)",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[member.email],
                fail_silently=False,
            )

        return member
    

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = RoomMember
        fields = ['first_name', 'last_name', 'username', 'email', 'phoneNumber']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d’utilisateur'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phoneNumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
        }
