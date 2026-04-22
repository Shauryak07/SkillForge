from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter,OrderingFilter

from api.jobs.filters import JobFilter
from api.jobs.permissions import JobAccessPermission
from rest_framework.permissions import IsAuthenticated
from api.jobs.serializers import JobSerializer, JobListSerializer
from jobs.models import Job
from jobs.services import *
from rest_framework.exceptions import MethodNotAllowed

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobListSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter,SearchFilter]
    filterset_class = JobFilter
    search_fields = ['title','description']
    ordering_fields = ['budget','-created_at']
    http_method_names = ["get", "post", "patch", "delete"]
    

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return JobSerializer
        return JobListSerializer

    def get_permissions(self):
        if self.action in ["partial_update","destroy"]:
            return [JobAccessPermission,IsAuthenticated]
        else:
            return [IsAuthenticated]

    def list(self,request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)

        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(detail=False,methods=['get'])
    def my_jobs(self,request):
        queryset = Job.objects.filter(client=request.user)
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset,many=True)

        return Response(serializer.data,status=status.HTTP_200_OK)

    def create(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = create_job(
            title=serializer.validated_data['title'],
            description=serializer.validated_data['description'],
            client=request.user,
            budget=serializer.validated_data['budget'],
        )

        return Response({
            "message" : "Job Created",
            "job_id" : job.id
        },status = status.HTTP_201_CREATED)

    def update(self,request,*args,**kwargs):
        raise MethodNotAllowed("PUT")

    def partial_update(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)

        updated_job = update_job(
            actor=request.user,
            job=self.get_object(),
            **serializer.validated_data
        )

        return Response({
            "message" : "Job Updated",
            'updated_job' : updated_job.id
        },status=status.HTTP_200_OK)

    def destroy(self,request,*args,**kwargs):
        job = self.get_object()

        cancelled_job = cancel_job(actor=request.user,job=job)

        return Response({
            "message" : "Job Cancelled",
            "job_id" : cancelled_job.id,
        },
            status= status.HTTP_200_OK
        )
