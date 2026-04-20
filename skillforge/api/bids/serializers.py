from rest_framework import serializers
from bids.models import Bid

class BidListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = (
            'amount',
            'proposal',
            'status',
            'created_at',
        )

class BidSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10,decimal_places=2)
    proposal = serializers.CharField()
