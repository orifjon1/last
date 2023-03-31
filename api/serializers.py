from rest_framework import serializers
from rest_framework.serializers import BaseSerializer


class CurrencySerializer(BaseSerializer):
    def to_internal_value(self, data):
        return data

    def to_representation(self, instance):
        return {
            'usd': instance.get('usd'),
            'rub': instance.get('rub')
        }
