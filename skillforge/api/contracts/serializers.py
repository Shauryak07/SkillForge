from rest_framework import serializers
from contracts.models import Contract

class ContractSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contract
        fields = (
            "job",
            "client",
            "freelancer",
            "amount",
            "status"
        )