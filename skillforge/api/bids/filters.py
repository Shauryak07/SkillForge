from django_filters import FilterSet
from bids.models import Bid

class BidFilter(FilterSet):
    class Meta:
        model = Bid
        fields = {
            'amount' : ['iexact','lte','gte','range'],
            'proposal' : ['iexact','icontains'],
            'status' : ['iexact','icontains'],
            'created_at' : ['date','day','month','year'],
        }