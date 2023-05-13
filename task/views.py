from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
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
from config.exceptions import CustomException


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
        try:
            tasks = Task.objects.filter(Q(is_active=True) & Q(boss=request.user))
        except Task.DoesNotExist:
            raise CustomException("Hozircha vazifalar berilmagan!")
        queryset = self.filter_queryset(tasks)
        serializer = TaskSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(boss=request.user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class TaskDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfTask]
    queryset = Task.objects.filter(is_active=True)
    serializer_class = TaskSerializer


class TaskIsActiveOrNotView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOfTask]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_object(self):
        task_id = self.kwargs['id']
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise CustomException("Bu topshiriq topilmadi")
        return task

    def perform_update(self, serializer):
        task = serializer.instance
        task.is_active = not task.is_active
        task.save()

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
        sectors = Sector.objects.all()
        data = []
        for s in sectors:
            dic = {}
            dic['sector'] = s.name

            tasks = Task.objects.filter(Q(worker__sector=s) & Q(is_active=True))

            tasks = self.filter_queryset(tasks)
            finished = tasks.filter(status='finished').count()
            canceled = tasks.filter(status='canceled').count()
            missed = tasks.filter(status='missed').count()
            doing = tasks.filter(status='doing').count()
            dic['done'] = finished
            dic['canceled'] = canceled
            dic['missed'] = missed
            dic['doing'] = doing
            all = tasks.count()
            if tasks:
                dic['done_percent'] = finished * 100 / all
                dic['missed_percent'] = missed * 100 / all
                dic['canceled_percent'] = canceled * 100 / all
                dic['doing_percent'] = doing * 100 / all
            else:
                dic['done_percent'] = 0
                dic['missed_percent'] = 0
                dic['canceled_percent'] = 0
                dic['doing_percent'] = 0
            data.append(dic)

        serializer = SectorStatSerializer(data={'data': data})
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors)


class TaskStatView(APIView):
    filter_backends = [DjangoFilterBackend, DateRangeFilter]
    filterset_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker']
    ordering_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker']

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def get(self, request):
        try:
            tasks = Task.objects.filter(Q(boss__status='director') & Q(is_active=True))
        except Task.DoesNotExist:
            raise CustomException("Hozircha topshiriqlar mavjud emas!")
        tasks = self.filter_queryset(tasks)
        all = tasks.count()
        dic={}
        if all:
            dic['finished'] = tasks.filter(status='finished').count() * 100 / all
            dic['canceled'] = tasks.filter(status='canceled').count() * 100 / all
            dic['missed'] = tasks.filter(status='missed').count() * 100 / all
            dic['doing'] = tasks.filter(status='doing').count() * 100 / all

        serializer = TaskStatSerializer(data={'data': dic})
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors)


# each sector VIEWS
class TaskSectorView(APIView):
    filter_backends = [DjangoFilterBackend, DateRangeFilter]
    filterset_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker']
    ordering_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker']

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def get(self, request, id):
        try:
            sector = Sector.objects.get(id=id)
        except Sector.DoesNotExist:
            raise CustomException("Bunday bo'lim mavjud emas!")
        try:
            tasks = Task.objects.filter(Q(worker__sector=sector) & Q(is_active=True))
        except Task.DoesNotExist:
            raise CustomException(f"Bu {sector}da topshiriqlar mavjud emas!")
        tasks = self.filter_queryset(tasks)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class UserSectorView(APIView):
    def get(self, request, id):
        try:
            sector = Sector.objects.get(id=id)
        except Sector.DoesNotExist:
            raise CustomException("Bo'lim mavjud emas!")
        try:
            users = CustomUser.objects.filter(sector=sector)
        except CustomUser.DoesNotExist:
            raise CustomException("Bu bo'limga tegishli foydalanuvchilar mavjud emas!")

        serializer = UserStatSerializer(users, many=True)
        return Response(serializer.data)


class TaskSectorStatView(APIView):
    filter_backends = [DjangoFilterBackend, DateRangeFilter]
    filterset_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker']
    ordering_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker']

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def get(self, request, id):
        try:
            sector = Sector.objects.get(id=id)
        except Sector.DoesNotExist:
            raise CustomException("Bo'lim mavjud emas!")
        try:
            tasks = Task.objects.filter(Q(worker__sector=sector) and Q(is_active=True))
        except Task.DoesNotExist:
            raise CustomException("Bo'limda topshiriqlar yo'q!")
        tasks = self.filter_queryset(tasks)
        dic = {}
        all = tasks.count()
        finished = tasks.filter(status='finished').count()
        canceled = tasks.filter(status='canceled').count()
        missed = tasks.filter(status='missed').count()
        doing = tasks.filter(status='doing').count()

        dic['finished'] = tasks.filter(status='finished').count()
        dic['canceled'] = tasks.filter(status='canceled').count()
        dic['missed'] = tasks.filter(status='missed').count()
        dic['doing'] = tasks.filter(status='doing').count()
        dic['finished_procent'] = finished * 100 / all
        dic['canceled_procent'] = canceled * 100 / all
        dic['missed_procent'] = missed * 100 / all
        dic['doing_procent'] = doing * 100 / all

        serializer = TaskStatSerializer(data={'data': dic})
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors)


# cabinet page
class OneUserView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserStatSerializer

    def get_object(self):
        user_id = self.kwargs['id']
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise CustomException("Bunday foydalanuvchi yo'q!")
        return user


class OneUserTaskView(APIView):
    filter_backends = [DjangoFilterBackend, DateRangeFilter]
    filterset_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker']
    ordering_fields = ['id', 'problem', 'event', 'status', 'deadline', 'worker']

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def get(self, request, id):
        try:
            tasks = Task.objects.filter(Q(worker__id=id) & Q(is_active=True))
        except Task.DoesNotExist:
            raise CustomException("Bu xodimda topshiriqlar mavjud emas!")
        tasks = self.filter_queryset(tasks)
        serializer = TaskSerializer(tasks, many=True)
        return Response(data=serializer.data)


# write a review for a task
class ReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsBossOrWorker]
    
    def get(self, request, id):
        try:
           task = Task.objects.get(id=id)
        except Task.DoesNotExist:
            raise CustomException("Mavjud bo'lmagan topshiriq!")
        try:
            reviews = TaskReview.objects.filter(task=task)
        except TaskReview.DoesNotExist:
            reviews = None
        serializer = TaskReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, id):
        try:
            task = Task.objects.get(id=id)
        except Task.DoesNotExist:
            raise CustomException("Bu topshiriq topilmadi!")
        # reviews = TaskReview.objects.all()
        serializer = TaskReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, task=task)
            return Response(serializer.data)
        return Response(serializer.errors)


class ReviewEditDelete(RetrieveUpdateDestroyAPIView):
    queryset = TaskReview.objects.all()
    serializer_class = TaskReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsBossOrWorker]

