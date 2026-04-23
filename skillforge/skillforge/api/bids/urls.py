from api.bids.views import BidViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"", BidViewSet, basename="bids")

urlpatterns = router.urls