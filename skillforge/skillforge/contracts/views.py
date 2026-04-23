from django.shortcuts import render, get_object_or_404
from contracts.models import Contract
from contracts.workflows import *
from contracts.permissions import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q

# Create your views here.

@login_required
def contract_detail_view(request,contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)

    if not can_view_contract(contract,request.user):
        return HttpResponseForbidden("You cannot view this contract.")

    return render(request, "contracts/detail.html", {
        "contract": contract
    })

@login_required
def contract_list_view(request):
    contracts = Contract.objects.filter(
        Q(client=request.user) | Q(freelancer=request.user)
    )

    return render(request, "contracts/contracts_list.html", {
        "contracts": contracts
    })

# Action Views

@login_required
def submit_work_view(request,contract_id):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid request method")

    contract = get_object_or_404(Contract,pk=contract_id)
    freelancer=request.user

    if not can_submit_work(contract, freelancer):
        return HttpResponseForbidden("Permission Denied.")

    submit_work(contract, freelancer)
    return HttpResponseRedirect(
        reverse("contract_detail",args=[contract.id])
    )

@login_required
def approve_work_view(request,contract_id):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid request method")

    contract = get_object_or_404(Contract,pk=contract_id)
    client = request.user

    if not can_approve_work(contract, client):
        return HttpResponseForbidden("Permission Denied.")
    
    approve_work(contract, client)

    return HttpResponseRedirect(
        reverse("contract_detail",args=[contract.id])
    )

@login_required
def  reject_work_view(request,contract_id):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid request method")

    contract = get_object_or_404(Contract,pk=contract_id)
    client = request.user

    if not can_reject_work(contract, client):
        return HttpResponseForbidden("Permission Denied.")

    reject_work(contract, client)
    return HttpResponseRedirect(
        reverse("contract_detail", args=[contract.id])
    )

@login_required
def cancel_contract_view(request,contract_id):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid request method")

    contract = get_object_or_404(Contract,pk=contract_id)
    client = request.user

    if not can_cancel_contract(contract, client):
        return HttpResponseForbidden("Permission Denied")

    cancel_contract(contract, client)
    return HttpResponseRedirect(
        reverse("contract_detail", args=[contract.id])
    )

@login_required
def activate_contract_view(request,contract_id):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid request method")

    contract = get_object_or_404(Contract,pk=contract_id)
    client = request.user

    if not can_activate_contract(contract, client):
        return HttpResponseForbidden("Permission Denied")

    activate_contract(contract, client)
    return HttpResponseRedirect(
        reverse("contract_detail", args=[contract.id])
    )