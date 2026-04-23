from rest_framework import serializers
from jobs.models import Job


class JobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            'title',
            'client',
            'description',
            'budget',
            'status',
            'created_at',
        )

class JobSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    budget = serializers.DecimalField(decimal_places=2,max_digits=10)

