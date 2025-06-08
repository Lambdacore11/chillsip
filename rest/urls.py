from django.urls import path
from rest_framework import routers
from .views import *

app_name = 'rest'

router = routers.DefaultRouter()

router.register(r'posts',PostViewSet)
router.register(r'products',ProductViewSet)


urlpatterns = router.urls