from api.contracts.views import ContractViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"", ContractViewSet, basename="contracts")

urlpatterns = router.urls