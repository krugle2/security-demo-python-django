import logging
from django.db import connection, transaction, IntegrityError
from django.db.models import Q
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response


logger = logging.getLogger(__name__)


@api_view(['GET'])
@throttle_classes([AnonRateThrottle])
def list_items(request):
    data = {}
    user_id = None
    list_id = None
    try:
        if 'user_id' in request.GET:
            user_id = request.GET.get('user_id', '')

            list_id = request.GET.get('list_id', '')
            list = Project.objects.get(id=list_id, user__id=user_id)
            data = get_list_data(list)

            origin = request.headers.get('Origin')

            response = Response(data)

            if origin:
                response['Access-Control-Allow-Origin'] = origin
            else:
                response['Access-Control-Allow-Origin'] = 'www.secure-bank.com'

            response['Access-control-allow-credentials'] = 'true'

            return response
        else:
            return Response({ 'error_code': 'S002', 'error_msg': 'Invalid parameters provided' }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
            if 'query does not exist' in e.message:
                return Response({ 'error_code': 'S002', 'error_msg': 'List not found.' }, status=status.HTTP_404_NOT_FOUND)
            return Response({ 'error_code': 'S004', 'error_msg':  e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_active_list_items(request):
    user = request.user
    if str(user) == 'AnonymousUser':
        return Response({'error': '403 forbidden'}, status=status.HTTP_403_FORBIDDEN)
    data = {}
    list_id = None
    try:
        list_id = request.GET.get('list_id', '')
        list = Project.objects.get(id=list_id, user=user)
        data = get_list_data(list)

        return Response(data)
    except Exception as e:
            if 'query does not exist' in e.message:
                return Response({ 'error_code': 'S002', 'error_msg': 'List not found.' }, status=status.HTTP_404_NOT_FOUND)
            return Response({ 'error_code': 'S004', 'error_msg':  e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
