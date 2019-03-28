from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from . import views


from graphene_django.views import GraphQLView
from graphql_jwt.decorators import jwt_cookie

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', jwt_cookie(GraphQLView.as_view(graphiql=True))),
    path('csrf/', views.csrf),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
