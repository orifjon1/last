from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework import permissions
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from django.db.models import Q
from .models import Task, TaskReview
from .serializer import TaskSerializer, TaskReviewSerializer, SectorStatSerializer, TaskStatSerializer
from users.models import Sector, CustomUser
from users.serializer import UserStatSerializer
from .permission import IsDirectorOrManager, IsOwnerOfTask, IsBossOrWorker

from .ordering import DateRangeFilter


# Tahlil bosh menu
class TaskListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDirectorOrManager]
    filter_backends = [DjangoFilterBackend, DateRangeFilter]
    filterset_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker', 'date_range']
    ordering_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker', 'date_range']

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def get(self, request):
        tasks = Task.objects.filter(Q(is_active=True) and Q(boss__status='director'))
        queryset = self.filter_queryset(tasks)
        serializer = TaskSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(boss=request.user)
        return Response(serializer.data)


class TaskDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfTask]
    queryset = Task.objects.filter(is_active=True)
    serializer_class = TaskSerializer


# class TaskListView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get(self, request):
#         tasks = Task.objects.filter(Q(boss=request.user) & Q(is_active=True))
#         serializer = TaskSerializer(tasks, many=True)
#         return Response(serializer.data)


class SectorStatView(APIView):
    filter_backends = [DjangoFilterBackend, DateRangeFilter]
    filterset_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker', 'date_range']
    ordering_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker', 'date_range']

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def get(self, request):
        sector = Sector.objects.all()
        data = []
        for s in sector:
            dic = {}
            dic.sector = s
            tasks = Task.objects.filter(Q(worker__sector=s) & Q(is_active=True))
            tasks = self.filter_queryset(tasks)
            dic.done = tasks.filter(status='finished').count()
            dic.canceled = tasks.filter(status='canceled').count()
            dic.missed = tasks.filter(status='missed').count()
            data.append(dic)

        serializer = SectorStatSerializer(data={'data': data})
        return Response(serializer.data)


class TaskStatView(APIView):
    filter_backends = [DjangoFilterBackend, DateRangeFilter]
    filterset_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker', 'date_range']
    ordering_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker', 'date_range']

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def get(self, request):
        tasks = Task.objects.filter(Q(boss__status='director') and Q(is_active=True))
        tasks = self.filter_queryset(tasks)
        dic = {}
        dic.finished = tasks.filter(status='finished').count()
        dic.canceled = tasks.filter(status='canceled').count()
        dic.missed = tasks.filter(status='missed').count()
        dic.doing = tasks.filter(status='doing').count()

        serializer = TaskStatSerializer(data={'data': dic})
        return Response(serializer.data)


# each sector VIEWS
class TaskSectorView(APIView):
    filter_backends = [DjangoFilterBackend, DateRangeFilter]
    filterset_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker', 'date_range']
    ordering_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker', 'date_range']

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def get(self, request, id):
        sector = Sector.objects.get(id=id)
        tasks = Task.objects.filter(Q(worker_sector=sector) and Q(is_active=True))
        tasks = self.filter_queryset(tasks)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class UserSectorView(APIView):
    def get(self, request, id):
        sector = Sector.objects.get(id=id)
        users = CustomUser.objects.filter(sector=sector)
        serializer = UserStatSerializer(users, many=True)
        return Response(serializer.data)


class TaskSectorStatView(APIView):
    filter_backends = [DjangoFilterBackend, DateRangeFilter]
    filterset_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker', 'date_range']
    ordering_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker', 'date_range']

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def get(self, request, id):
        sector = Sector.objects.get(id=id)
        tasks = Task.objects.filter(Q(worker__sector=sector) and Q(is_active=True))
        tasks = self.filter_queryset(tasks)
        dic = {}
        dic.finished = tasks.filter(status='finished').count()
        dic.canceled = tasks.filter(status='canceled').count()
        dic.missed = tasks.filter(status='missed').count()
        dic.doing = tasks.filter(status='doing').count()

        serializer = TaskStatSerializer(data={'data': dic})
        return Response(serializer.data)


# cabinet page
class OneUserView(APIView):
    def get(self, request, id):
        user = CustomUser.objects.get(id=id)
        serializer = UserStatSerializer(user)
        return Response(serializer.data)


class OneUserTaskView(APIView):
    filter_backends = [DjangoFilterBackend, DateRangeFilter]
    filterset_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker', 'date_range']
    ordering_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker', 'date_range']

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def get(self, request, id):
        tasks = Task.objects.filter(Q(worker__id=id) and Q(is_active=True))
        tasks = self.filter_queryset(tasks)
        serializer = TaskSerializer(tasks)
        return Response(serializer.data)


# write a review for a task
class ReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsBossOrWorker]

    def get(self, request, id):
        task = Task.objects.get(id=id)
        reviews = TaskReview.objects.filter(task=task)
        serializer = TaskReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, id):
        task = Task.objects.get(id=id)
        reviews = TaskReview.objects.all()
        serializer = TaskReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, task=task)
        return Response(serializer.data)


class ReviewEditDelete(RetrieveUpdateDestroyAPIView):
    queryset = TaskReview.objects.all()
    serializer_class = TaskReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsBossOrWorker]
