from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from app.models import *
from lib import redis
from .serializers import *


class PrinterViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = PrinterSerializer

    def get_queryset(self):
        return Printer.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def cancel_print(self, request, pk=None):
        self.current_printer_or_404(pk).queue_octoprint_command('cancel', clear_alert=True)
        return Response({'status': 'OK'})

    @action(detail=True, methods=['get'])
    def pause_print(self, request, pk=None):
        self.current_printer_or_404(pk).queue_octoprint_command('pause', clear_alert=True)
        return Response({'status': 'OK'})

    @action(detail=True, methods=['get'])
    def resume_print(self, request, pk=None):
        printer = self.current_printer_or_404(pk)
        if request.GET.get('mute_alert', None):
            printer.current_print_alert_muted = True
            printer.save()

        printer.queue_octoprint_command('restore_temps', clear_alert=True)
        printer.queue_octoprint_command('resume', clear_alert=True)
        return Response({'status': 'OK'})

    def current_printer_or_404(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)
