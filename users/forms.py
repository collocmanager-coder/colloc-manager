from django import forms

from colloc import settings
from .models import RoomMember, Room
import string,secrets
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

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

            # --- Envoi de l'email via Django / Zoho SMTP ---
            subject = "Bienvenue sur Colloc Manager"
            text_content = f"""
Bonjour {member.first_name},

Votre compte a été créé.

Nom d’utilisateur : {member.username}
Mot de passe : {temp_password}

Vous pouvez vous connecter ici : https://colloc-manager.onrender.com

Merci ! (*_*)
"""
            html_content = f"""
<h2>Bonjour {member.first_name},</h2>
<p>Votre compte a été créé.</p>
<ul>
<li><strong>Nom d’utilisateur :</strong> {member.username}</li>
<li><strong>Mot de passe :</strong> {temp_password}</li>
</ul>
<p>Vous pouvez vous connecter ici : <a href="https://colloc-manager.onrender.com">Colloc Manager</a></p>
<p>Merci ! (*_*)</p>
"""

            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=None,  # Utilise DEFAULT_FROM_EMAIL de settings.py
                    to=[member.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                print(f"Email envoyé avec succès à {member.email}")
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email : {e}")

        return member, temp_password        

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
