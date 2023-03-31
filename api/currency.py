import requests
import json
from .serializers import CurrencySerializer
from rest_framework.views import APIView
from rest_framework.response import Response


class Currency(APIView):
    def currency(self):
        dic = {}
        cur = ['rub', 'usd']
        results = []
        for unit in cur:
            url = f"https://api.apilayer.com/exchangerates_data/convert?to=uzs&from={unit}&amount=1"
            payload = {}
            headers = {
                "apikey": "q4mVLni4N9E5PHZrCNYGIoXFxqeJBaFs"
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            status_code = response.status_code
            if status_code == 200:
                dict = json.loads(response.text)
                dic[str(unit)] = dict['result']
                print(dic)
        return dic

    def get(self, request):
        results = self.currency()
        serializer = CurrencySerializer(data=results)
        serializer.is_valid(raise_exception=ValueError)
        return Response(serializer.data)

