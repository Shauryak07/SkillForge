from rest_framework import serializers
from contracts.models import Contract

class ContractSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contract
        fields = (
            "id",
            "job",
            "client",
            "freelancer",
            "amount",
            "status",
            "created_at"
        )