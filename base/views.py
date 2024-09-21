from rest_framework import viewsets


class BaseViewSet(viewsets.ModelViewSet):
    serializer_class = None
    serializer_map = {}
    permission_map = {}

    def get_serializer_class(self):
        """
        Get action's serializer base on `serializer_map`
        :return: Serializer
        """
        return self.serializer_map.get(self.action, self.serializer_class)

    def get_permissions(self):
        return [permission() for permission in self.permission_map.get(self.action, self.permission_classes)]