from rest_framework.exceptions import APIException


class CustomException(APIException):
    status_code = 404
    default_detail = 'Bunday sahifa mavjud emas'
