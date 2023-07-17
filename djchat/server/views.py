from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response

from .models import Server
from .serializer import ServerSerializer

# Create your views here.


class ServerListViewSet(viewsets.ViewSet):
    queryset = Server.objects.all()

    def list(self, request):
        category = request.query_params.get("category")
        qty = request.query_params.get("qty")
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid")

        if by_user and not request.user.is_authenticated:
            raise AuthenticationFailed(detail="User must be authenticated to use this endpoint")

        if category is not None:
            self.queryset = self.queryset.filter(category__name=category)

        if by_user:
            user_id = request.user.id
            self.queryset = self.queryset.filter(member=user_id)

        if qty is not None:
            self.queryset = self.queryset[: int(qty)]

        if by_serverid is not None:
            try:  # if server id is valid
                self.queryset = self.queryset.filter(id=int(by_serverid))
                if not self.queryset.exists():
                    raise ValidationError({"error": "Server does not exist"})
            except ValueError:  # if server id is invalid
                raise ValidationError(detail=f"Server with id {by_serverid} does not exist")

        serializer = ServerSerializer(self.queryset, many=True)
        return Response(serializer.data)
