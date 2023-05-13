from django.db.models import Q
from django.utils.text import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from config.exceptions import CustomException
from .models import Sector, CustomUser
from rest_framework import serializers
import re

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = "__all__"


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': _('Token is invalid or expired')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


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
    total_workers = serializers.SerializerMethodField(read_only=True)
    sector_boss = serializers.SerializerMethodField(read_only=True)
    boss = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'sector', 'status',
                  'shior', 'main_task',
                  'first_name', 'last_name', 'phone_number',
                  'total_workers', 'sector_boss', 'boss'
                  ]
        extra_kwargs = {'status': {'read_only': True}}

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.main_task = validated_data.get('main_task', instance.main_task)
        instance.shior = validated_data.get('shior', instance.shior)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()
        return instance

    def validate_phone_number(self, value):
        value = self.phone_number(value)
        return value

    def phone_number(self, value):
        pattern = re.compile(r'^\+998\d{2}\d{3}\d{2}\d{2}$')
        value = "+998" + str(value)
        if re.fullmatch(pattern, value):
            return value
        else:
            raise CustomException("Telefon raqam xato kiritildi!")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['total_workers'] = self.get_total_workers(instance)
        data['boss'] = self.get_boss(instance)
        data['sector_boss'] = self.get_sector_boss(instance)
        return data

    def get_total_workers(self, obj):
        if obj.status == 'manager':
            num = CustomUser.objects.filter(sector=obj.sector).count() - 1
        elif obj.status == 'director':
            num = CustomUser.objects.filter(Q(status='manager') | Q(status='employee')).count()
        else:
            num = 0
        return num

    def get_sector_boss(self, obj):
        if obj.status == 'director':
            boss = CustomUser.objects.filter(status='director').first()
        else:
            boss = CustomUser.objects.filter(Q(status='manager') & Q(sector=obj.sector)).first()
        return boss.first_name

    def get_boss(self, obj):
        boss = CustomUser.objects.filter(status='director').first()
        return boss.first_name


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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['total'] = self.get_total(instance)
        data['doing'] = self.get_doing(instance)
        data['finished'] = self.get_finished(instance)
        data['canceled'] = self.get_canceled(instance)
        data['missed'] = self.get_missed(instance)
        data['doing_percent'] = self.get_doing_percent(instance)
        data['missed_percent'] = self.get_missed_percent(instance)
        data['canceled_percent'] = self.get_canceled_percent(instance)
        data['finished_percent'] = self.get_finished_percent(instance)
        return data

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
                if i.status == 'missed':
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
