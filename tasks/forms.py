from django import forms
from tasks.models import Task
from users.models import RoomMember


class TaskForm(forms.ModelForm):
    rotation_order_input = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = Task
        fields = ['taskName', 'taskDescription', 'durationDays']
        labels = {
            'taskName': 'Nom de la tâche',
            'taskDescription': 'Description',
            'durationDays': 'Durée (en jours)',
        }
        help_texts = {
            'taskName': 'Donne un nom clair et court à la tâche (ex: Nettoyage de la cuisine).',
            'taskDescription': 'Explique en quelques lignes ce que la tâche implique.',
            'durationDays': 'Indique combien de jours la tâche doit durer.',
        }
        widgets = {
            'taskName': forms.TextInput(attrs={
                'class': 'form-control form-control-lg rounded-3 shadow-sm border-0 bg-light',
                'placeholder': 'Ex : Nettoyage de la cuisine',
            }),
            'taskDescription': forms.Textarea(attrs={
                'class': 'form-control rounded-3 shadow-sm border-0 bg-light',
                'rows': 4,
                'placeholder': 'Décris la tâche ici...',
            }),
            'durationDays': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm rounded-3 shadow-sm border-0 bg-light',
                'min': 1,
                'placeholder': 'Ex : 3',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['style'] = 'margin-bottom: 15px;'
            field.label_suffix = ' :'

class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['taskName', 'taskDescription', 'durationDays']  # rotation_order exclu
        labels = {
            'taskName': "Nom de la tâche",
            'taskDescription': "Description de la tâche",
            'durationDays': "Durée (en jours)"
        }
        widgets = {
            'taskName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Nettoyage de la cuisine'}),
            'taskDescription': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Décris la tâche ici...'}),
            'durationDays': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
