from .models import Task, TaskReview
from rest_framework import serializers
from users.serializer import UserSerializer


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
        read_only_fields = ('status', 'boss', 'created_at', 'updated', 'financial_help')

    def get_remain_days(self, obj):
        return obj.remain_days

    def get_all_days(self, obj):
        return obj.all_days


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
        return instance


class TaskStatSerializer(serializers.Serializer):
    data = serializers.DictField(child=serializers.CharField())

    def to_representation(self, instance):
        return instance
