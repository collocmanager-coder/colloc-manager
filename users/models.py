from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Room(models.Model):

    class RoomStatus(models.TextChoices):
        VERIFIED = 'verified','Verifie'
        PENDING =  'pending','En cours de verification'
        REJECTED = 'rejected','Verification Refusee'

    roomTitulor = models.ForeignKey(
        'RoomMember',
        on_delete=models.CASCADE,
        related_name='owned_rooms',
        null=True,
        blank=True

    )
    roomNumber = models.CharField(max_length=20)
    roomStatus = models.CharField(
        max_length=50,
        choices=RoomStatus.choices,
        default=RoomStatus.PENDING
    )

    def __str__(self):
        return "Chambre "+self.roomNumber+" de "+self.roomTitulor.username

class RoomMember(AbstractUser):

    class MemberStatus(models.TextChoices):
        TITULOR = 'titulor','Titulaire de la maison'
        SIMPLE_MEMBER = 'simple_member','Simple membre'
    room = models.ForeignKey(Room,on_delete=models.CASCADE, related_name="members",null=True, blank=True)
    phoneNumber = models.CharField(max_length=15)
    memberStatus = models.CharField(
        max_length=50,
        choices= MemberStatus.choices,
        default= MemberStatus.SIMPLE_MEMBER,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.memberStatus == self.MemberStatus.TITULOR and self.room:
            if self.room.roomTitulor != self:
                self.room.roomTitulor = self
                self.room.save()
            if self not in self.room.members.all():
                self.room.members.add(self)

