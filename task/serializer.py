from .models import Task, TaskReview
from rest_framework import serializers
from users.serializer import UserSerializer
from users.models import CustomUser
from config.exceptions import CustomException
from datetime import date


class TaskSerializer(serializers.ModelSerializer):
    boss = serializers.ReadOnlyField(source='boss.username')
    remain_days = serializers.SerializerMethodField()
    all_days = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'problem', 'reason', 'event',
                  'deadline', 'boss', 'worker',
                  'remain_days', 'all_days', 'status',
                  'financial_help', 'created_at', 'updated'
                  ]
        read_only_fields = ('status', 'created_at', 'updated', 'financial_help')

    def validate_worker(self, value):
        boss = self.context['request'].user
        if boss and boss.status == 'manager' and value and value.sector != boss.sector:
            raise CustomException('Bunday xodim sizning bo\'limingizda mavjud emas!')
        return value

    def validate_deadline(self, value):
        if value.date() <= date.today():
            raise CustomException('Topshiriq Muddati - bugungi sanadan keyingi sana bo\'lishi kerak!')
        return value

    def get_remain_days(self, obj):
        return obj.remain_days

    def get_all_days(self, obj):
        return obj.all_days


class TaskCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'problem', 'reason', 'event',
                  'deadline', 'boss', 'worker',
                  'remain_days', 'all_days', 'status',
                  'financial_help', 'created_at', 'updated'
                  ]
        read_only_fields = ('status', 'created_at', 'updated', 'financial_help', 'boss')


class TaskReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    task = TaskSerializer(read_only=True)

    class Meta:
        model = TaskReview
        fields = ['id', 'user', 'task', 'content', 'created']
        read_only_fields = ('created',)


class SectorStatSerializer(serializers.Serializer):
    data = serializers.ListSerializer(child=serializers.DictField(child=serializers.CharField()))

    def to_representation(self, instance):
        print(instance)
        return instance


class TaskStatSerializer(serializers.Serializer):
    data = serializers.DictField(child=serializers.CharField())

    def to_representation(self, instance):
        return instance
