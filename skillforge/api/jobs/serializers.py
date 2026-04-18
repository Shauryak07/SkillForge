from rest_framework import serializers
from jobs.models import Job


class JobSerializer(serializers.ModelSerializer):
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

class JobUpdateSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()

