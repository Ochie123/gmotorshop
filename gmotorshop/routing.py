from channels.routing import ProtocolTypeRouter, URLRouter
from channels.http import AsgiHandler
from django.urls import re_path
from .auth import TokenGetAuthMiddlewareStack
import categories.routing


application = ProtocolTypeRouter(
    { 
        # (http->django views is added by default)
        "websocket": TokenGetAuthMiddlewareStack(
            URLRouter(categories.routing.websocket_urlpatterns)
        ),

    }
)