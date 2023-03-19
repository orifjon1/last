from .models import Sector, CustomUser
from rest_framework import serializers


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'sector', 'password', 'status']
        extra_kwargs = {'password': {'write_only': True}, 'status': {'read_only': True}}

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'sector', 'password', 'status',
                  'first_name', 'last_name', 'birth_date', 'phone_number',
                  'photo'
                  ]
        extra_kwargs = {'status': {'read_only': True}}


class UserStatSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    doing = serializers.SerializerMethodField()
    finished = serializers.SerializerMethodField()
    canceled = serializers.SerializerMethodField()
    missed = serializers.SerializerMethodField()
    doing_percent = serializers.SerializerMethodField()
    missed_percent = serializers.SerializerMethodField()
    canceled_percent = serializers.SerializerMethodField()
    finished_percent = serializers.SerializerMethodField()
    # sector = SectorSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'sector', 'status',
                  'total', 'doing', 'finished', 'canceled', 'missed',
                  'doing_percent', 'missed_percent', 'finished_percent', 'canceled_percent']
        extra_kwargs = {'status': {'read_only': True}}

    def get_total(self, obj):
        if obj.status != "director":
            total = obj.accepted_tasks.all().count()
            return total

    def get_doing(self, obj):
        if obj.status != "director":
            done_tasks = obj.accepted_tasks.all()
            x = 0
            for i in done_tasks:
                if i.status == 'doing':
                    x += 1
            return x

    def get_finished(self, obj):
        if obj.status != "director":
            done_tasks = obj.accepted_tasks.all()
            x = 0
            for i in done_tasks:
                if i.status == 'finished':
                    x += 1
            return x

    def get_canceled(self, obj):
        if obj.status != "director":
            done_tasks = obj.accepted_tasks.all()
            x = 0
            for i in done_tasks:
                if i.status == 'canceled':
                    x += 1
            return x

    def get_missed(self, obj):
        if obj.status != "director":
            done_tasks = obj.accepted_tasks.all()
            x = 0
            for i in done_tasks:
                if i.status == 'not_do':
                    x += 1
            return x

    def get_doing_percent(self, obj):
        total = self.get_total(obj)
        doing = self.get_doing(obj)
        if total != 0 and doing is not None:
            perc = (doing * 100.0) / total
            return perc
        else:
            return 0

    def get_missed_percent(self, obj):
        total = self.get_total(obj)
        doing = self.get_missed(obj)
        if total != 0 and doing is not None:
            perc = (doing * 100.0) / total
            return perc
        else:
            return 0

    def get_finished_percent(self, obj):
        total = self.get_total(obj)
        doing = self.get_finished(obj)
        if total != 0 and doing is not None:
            perc = (doing * 100.0) / total
            return perc
        else:
            return 0

    def get_canceled_percent(self, obj):
        total = self.get_total(obj)
        doing = self.get_canceled(obj)
        if total != 0 and doing is not None:
            perc = (doing * 100.0) / total
            return perc
        else:
            return 0
