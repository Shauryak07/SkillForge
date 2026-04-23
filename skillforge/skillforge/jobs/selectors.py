from jobs.models import Job

def get_open_jobs():
    return Job.objects.filter(status=Job.Status.OPEN).annotate(
        bid_count=Count("bids")
    )

def get_client_jobs(client):
    return Job.objects.filter(client=client)

def get_job_by_id(job_id):
    return Job.objects.get(id=job_id)