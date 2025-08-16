"""
API routes for the Azure Compute service, using a database for persistence
and realistic, structured API paths.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.db import get_session
from app.models import VirtualMachine
from app.security import verify_token

# Pydantic models for request bodies, separating them from the DB model
from pydantic import BaseModel
class VirtualMachineCreate(BaseModel):
    location: str
    properties: dict # A simple dict to capture vmSize, etc.

router = APIRouter(
    prefix="/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute",
    tags=["compute"],
    dependencies=[Depends(verify_token)],
)

@router.put("/virtualMachines/{vm_name}", response_model=VirtualMachine)
def create_or_update_vm(
    *,
    session: Session = Depends(get_session),
    resourceGroupName: str,
    vm_name: str,
    vm_body: VirtualMachineCreate,
):
    """
    Create or update a virtual machine (upsert).
    This mimics the standard Azure PUT-as-upsert pattern.
    """
    statement = select(VirtualMachine).where(
        VirtualMachine.name == vm_name,
        VirtualMachine.resource_group == resourceGroupName,
    )
    db_vm = session.exec(statement).first()

    if db_vm:
        # Update existing VM
        db_vm.location = vm_body.location
        db_vm.vm_size = vm_body.properties.get("hardwareProfile", {}).get("vmSize", "Unknown")
        db_vm.provisioning_state = "Succeeded"
    else:
        # Create new VM
        db_vm = VirtualMachine(
            name=vm_name,
            resource_group=resourceGroupName,
            location=vm_body.location,
            vm_size=vm_body.properties.get("hardwareProfile", {}).get("vmSize", "Unknown"),
            provisioning_state="Succeeded",
        )

    session.add(db_vm)
    session.commit()
    session.refresh(db_vm)
    return db_vm

@router.get("/virtualMachines/{vm_name}", response_model=VirtualMachine)
def get_vm(
    *,
    session: Session = Depends(get_session),
    resourceGroupName: str,
    vm_name: str,
):
    """
    Get a specific virtual machine by name and resource group.
    """
    statement = select(VirtualMachine).where(
        VirtualMachine.name == vm_name,
        VirtualMachine.resource_group == resourceGroupName,
    )
    vm = session.exec(statement).first()
    if not vm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Virtual machine not found")
    return vm

@router.get("/virtualMachines", response_model=List[VirtualMachine])
def list_vms_in_rg(
    *,
    session: Session = Depends(get_session),
    resourceGroupName: str,
):
    """
    List all virtual machines within a specific resource group.
    """
    statement = select(VirtualMachine).where(VirtualMachine.resource_group == resourceGroupName)
    vms = session.exec(statement).all()
    return vms

@router.delete("/virtualMachines/{vm_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vm(
    *,
    session: Session = Depends(get_session),
    resourceGroupName: str,
    vm_name: str,
):
    """
    Delete a specific virtual machine.
    """
    statement = select(VirtualMachine).where(
        VirtualMachine.name == vm_name,
        VirtualMachine.resource_group == resourceGroupName,
    )
    vm_to_delete = session.exec(statement).first()

    if not vm_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Virtual machine not found")

    session.delete(vm_to_delete)
    session.commit()
    return None
