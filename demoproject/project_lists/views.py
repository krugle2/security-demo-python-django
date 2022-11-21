from django.db import connection, transaction, IntegrityError
from django.db.models import Q
from django.core.urlresolvers import reverse
import datetime
import json

from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response

@api_view(['POST'])
@transaction.atomic
def delete_list(request):
    user = request.user
    if str(user) == 'AnonymousUser':
        return Response({'error': '403 forbidden'}, status=status.HTTP_403_FORBIDDEN)
    list_ids = None
    
    try:
        list_ids = request.DATA['id']
        
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM projects_item where project_id in %s', [list_ids])
                cursor.execute('DELETE FROM projects_projectparameter where project_id in %s', [list_ids])
                cursor.execute('DELETE FROM projects_project where id in %s AND user_id=%s', [list_ids])
                row = cursor.fetchone()
        return Response({ 'status': 'OK'})
    except IntegrityError as e:
        logger.error(e)
        return Response({ 'error_code': 'S099', 'error_msg':  e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(e)
        return Response({ 'error_code': 'S002', 'error_msg':  'Invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)