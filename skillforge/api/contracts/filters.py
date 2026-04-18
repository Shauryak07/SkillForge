import django_filters
from contracts.models import Contract

class ContractFilter(django_filters.FilterSet):
    class Meta:
        model = Contract
        fields = {
            'amount' : ['iexact','lte','gte','range'],
            'status' : ['iexact','icontains'],
        }