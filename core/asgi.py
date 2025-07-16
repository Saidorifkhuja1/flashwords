# import os
# import django
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from django.core.asgi import get_asgi_application
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
#
# # ⚠️ Django'ni to‘liq yuklab olish
# django.setup()
#
# # 🟢 Endi routing import qilinadi
# from game.routing import websocket_urlpatterns
#
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             websocket_urlpatterns
#         )
#     ),
# })

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     # ⚠️ AuthMiddlewareStack ni olib tashlang, test uchun
#     "websocket": URLRouter(websocket_urlpatterns),
# })





import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from game.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})