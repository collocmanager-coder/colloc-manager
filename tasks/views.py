from datetime import timedelta
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from colloc import settings
from tasks.models import Task, TaskExecution
from tasks.forms import TaskForm, TaskUpdateForm
from users.models import RoomMember
from users.views import TitulorRequiredMixin,LoginRequiredHomeMixin
from django.core.mail import send_mail
from django.utils import timezone

# Liste des tâches
class TaskListView(LoginRequiredHomeMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'room'):
            return Task.objects.filter(room=user.room)
        return Task.objects.none()

# Détail d'une tâche
class TaskDetailView(LoginRequiredHomeMixin,DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

# Créer une tâche
class TaskCreateView(TitulorRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    def dispatch(self, request, *args, **kwargs):
        # Vérifie si la room du titulor est vérifiée
        if not request.user.room or request.user.room.roomStatus != 'verified':
            return redirect('room_not_verified')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.room = self.request.user.room
        task = form.save(commit=False)

        rotation_ids = self.request.POST.get('rotation_order_input', '').split(',')
        rotation_ids = [int(x) for x in rotation_ids if x]

        task.rotation_order = rotation_ids
        task.save()

        if rotation_ids:
            first_executor = RoomMember.objects.get(id=rotation_ids[0])
            TaskExecution.objects.create(roomTask=task, executor=first_executor, turn_index=0)

            # Envoi du mail
            send_mail(
                subject=f"Nouvelle tâche : {task.taskName}",
                message=f"Bonjour {first_executor.first_name},\n\n"
                        f"Vous êtes chargé(e) de la tâche : {task.taskName}.\n"
                        f"Durée : {task.durationDays} jours.\n"
                        f"Veuillez vous connecter sur l'appli Colloc-Manager pour voir les détails.\nMerci ! (*_*)",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[first_executor.email],
                fail_silently=False,
            )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = RoomMember.objects.filter(room=self.request.user.room)
        return context


      
# Modifier une tâche
class TaskUpdateView(TitulorRequiredMixin,UpdateView):
    model = Task
    form_class = TaskUpdateForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')


# Supprimer une tâche
class TaskDeleteView(TitulorRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        room = task.room
        members = RoomMember.objects.filter(room=room)

        # Préparer le mail
        mysubject = f"Tâche supprimée : {task.taskName}"
        mymessage = (
            f"Bonjour,\n\n"
            f"Le titulaire de votre colocation ({room.titulor.first_name} {room.titulor.last_name}) "
            f"a supprimé la tâche suivante : '{task.taskName}'.\n\n"
            f"Motif : hum il estime que la tache n'est plus importante j'imagine\n\n"
            f"Cette suppression est automatique pour garantir la transparence dans votre room.\n"
            f"Merci de votre compréhension.\n\n"
            f"L'équipe Colloc Manager (*_*)"
        )

        # Envoyer le mail à chaque membre individuellement
        for member in members:
            if member.email:
                try:
                    send_mail(
                        subject=mysubject,
                        message=mymessage,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[member.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print("Il y'a un probleme")

        # Supprimer la tâche
        return super().delete(request, *args, **kwargs)    

### Pour les taskExecutions
class TaskExecutionListView(LoginRequiredHomeMixin, ListView):
    model = TaskExecution
    template_name = 'tasks/task_execution_list.html'
    context_object_name = 'executions'

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'room'):
            executions = TaskExecution.objects.filter(
                roomTask__room=user.room,
                isDone=False
            ).order_by('execution_time')

            for exec in executions:
                # Date de fin prévue
                exec.date_fin_prevue = exec.execution_time.date() + timedelta(days=exec.roomTask.durationDays)

                # Prochaine personne
                rotation = exec.roomTask.rotation_order
                try:
                    next_index = (exec.turn_index + 1) % len(rotation)
                    next_member_id = rotation[next_index]
                    exec.next_executor_display = RoomMember.objects.get(id=next_member_id)
                except:
                    exec.next_executor_display = None

                # Liste complète des membres dans l'ordre du titulor
                exec.rotation_members_display = []
                for member_id in rotation:
                    try:
                        exec.rotation_members_display.append(RoomMember.objects.get(id=member_id))
                    except RoomMember.DoesNotExist:
                        continue
            return executions
        return TaskExecution.objects.none()
        
###### Pour mes tasks
class MyTasksListView(LoginRequiredHomeMixin, ListView):
    model = TaskExecution
    template_name = 'tasks/my_tasks.html'
    context_object_name = 'executions'

    def get_queryset(self):
        user = self.request.user
        # Affiche seulement les tâches assignées à l'utilisateur
        return TaskExecution.objects.filter(executor=user).order_by('execution_time')


##### Pour marquer une tache comme etant faite
class MarkTaskDoneView(LoginRequiredHomeMixin, View):
    def post(self, request, pk):
        execution = TaskExecution.objects.get(pk=pk)

        # Vérifier si la durée est écoulée
        now = timezone.now()
        deadline = execution.execution_time + timezone.timedelta(days=execution.roomTask.durationDays)
        if now < deadline:
            return render(request, 'tasks/task_not_done_yet.html', {
                'execution': execution,
                'deadline': deadline
            })

        # Marquer comme terminé
        # On verifie d'abord si la tache n'a pas deja ete faite
        if execution.isDone == False:
            execution.isDone = True
            execution.save()

            # Assigner la personne suivante dans la rotation
            rotation = execution.roomTask.rotation_order
            if rotation:
                current_index = execution.turn_index
                next_index = (current_index + 1) % len(rotation)

                # Créer TaskExecution pour la personne suivante
                try:
                    next_executor = RoomMember.objects.get(id=rotation[next_index])
                    TaskExecution.objects.create(
                        roomTask=execution.roomTask,
                        executor=next_executor,
                        turn_index=next_index
                    )

                    # Envoyer mail à la prochaine personne
                    send_mail(
                        subject=f"Nouvelle tâche à exécuter : {execution.roomTask.taskName}",
                        message=f"Bonjour {next_executor.first_name},\n\n"
                                f"Vous êtes maintenant chargé(e) de la tâche : {execution.roomTask.taskName}.\n"
                                f"Délai : {execution.roomTask.durationDays} jours.\n"
                                f"Connectez-vous sur Colloc Manager pour voir les détails.\nMerci !",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[next_executor.email],
                        fail_silently=False,
                    )
                except RoomMember.DoesNotExist:
                    pass

        return redirect('my_taks')