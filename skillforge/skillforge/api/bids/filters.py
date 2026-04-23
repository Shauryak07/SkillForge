import django_filters
from bids.models import Bid

class BidFilter(django_filters.FilterSet):

    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    proposal = django_filters.CharFilter(field_name="proposal", lookup_expr="icontains")

    class Meta:
        model = Bid
        fields = ["status"]
