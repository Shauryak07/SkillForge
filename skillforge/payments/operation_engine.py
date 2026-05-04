from django.db import transaction,IntegrityError
from payments.models import OperationLog
from django.utils import timezone
from datetime import timedelta
from contracts.models import Contract

@transaction.atomic
def execute_operation(operation_key, contract, actor, fn):
        try:
            op,created = OperationLog.objects.get_or_create(
                operation_key=operation_key,
                status = "STARTED",
                contract = contract,
                actor = actor,
            )
        except IntegrityError:
            op = OperationLog.objects.select_for_update().get(operation_key=operation_key)
            created = False

        if not created: 
            if op.status == "SUCCESS":
                return Contract.objects.get(id=contract.id)
            if op.status == "STARTED":
                if timezone.now() - op.updated_at < timedelta(seconds=50):
                    raise Exception('Operation already in progress...')

        try:
            result = fn(contract,actor)
            op.status = "SUCCESS"
            return result

        except Exception:
            op.status = "FAILED"
            raise

        finally:
            op.save()