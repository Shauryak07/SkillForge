import django_filters
from contracts.models import Contract

class ContractFilter(django_filters.FilterSet):
    class Meta:
        model = Contract
        fields = {
            'amount' : ['iexact','lte','gte','range'],
            'status' : ['iexact','icontains'],
        }

class ContractFilter(django_filters.FilterSet):

    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Contract
        fields = ["status"]