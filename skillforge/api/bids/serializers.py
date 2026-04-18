from rest_framework import serializers
from bids.models import Bid

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = (
            'amount',
            'proposal',
            'status',
            'created_at',
        )

class BidAcceptSerializer(serializers.Serializer):
    bid_id = serializers.IntegerField()

class BidPlaceSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    amount = serializers.DecimalField()
    proposal = serializers.CharField()