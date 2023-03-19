from rest_framework.response import Response
from rest_framework.views import APIView

from task.models import Task
from task.serializer import TaskSerializer

from users.models import CustomUser


class TaskCancelView(APIView):
    def patch(self, request, id):
        task = Task.objects.get(id=id)
        serializer = TaskSerializer(task, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.instance.status = 'canceled'
        serializer.save()
        return Response(serializer.data)


class TaskFinishView(APIView):
    def patch(self, request, id):
        task = Task.objects.get(id=id)
        serializer = TaskSerializer(task, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.instance.status = 'finished'
        serializer.save()
        return Response(serializer.data)


class ManagerToWorkerView(APIView):
    def post(self, request, id, pk):
        task = Task.objects.get(id=id)
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
