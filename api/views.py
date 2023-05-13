from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin

from task.models import Task
from task.serializer import TaskSerializer, TaskCancelSerializer
from users.serializer import UserProfileSerializer
from users.models import CustomUser, Sector


class TaskCancelView(GenericAPIView, UpdateModelMixin):
    serializer_class = TaskCancelSerializer
    def patch(self, request, id):
        task = Task.objects.get(id=id)
        serializer = TaskCancelSerializer(instance=task, data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.instance.status != 'canceled':
            serializer.instance.status = 'canceled'
        else:
            serializer.instance.status = 'doing'
        serializer.save()
        return Response(serializer.data)


class TaskFinishView(GenericAPIView, UpdateModelMixin):
    serializer_class = TaskCancelSerializer
    def patch(self, request, id):
        task = Task.objects.get(id=id)
        serializer = TaskCancelSerializer(task, data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.instance.status != 'finished':
            serializer.instance.status = 'finished'
        else:
            serializer.instance.status = 'doing'
        serializer.save()
        return Response(serializer.data)


class ManagerToWorkerView(APIView):
    serializer_class = TaskSerializer

    # def get_queryset(self):
    #     return Task.objects.all()

    def post(self, request, id, pk):
        task = Task.objects.get(id=id)
        # task = get_object_or_404(task, id)
        user = CustomUser.objects.get(pk=pk)
        new_task = Task.objects.create(
            boss=request.user,
            worker=user,
            deadline=task.deadline,
            problem=task.problem,
            event=task.event,
            reason=task.reason
        )
        serializer = TaskSerializer(new_task)
        return Response(serializer.data)


class SectorLeftDataView(APIView):
    def get(self, request, id):
        manager = CustomUser.objects.get(id=id)
        serializer = UserProfileSerializer(manager)
