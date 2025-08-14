"""
API routes for the Azure Compute service, using a database for persistence.

This module provides CRUD operations for compute resources, starting with
Virtual Machines. It has been refactored to use SQLModel and a PostgreSQL
database, replacing the previous in-memory, dynamically generated routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.db import get_session
from app.models import VirtualMachine
from app.security import verify_token


router = APIRouter(
    prefix="/compute",
    tags=["compute"],
    dependencies=[Depends(verify_token)],
)

@router.post("/virtualmachines/", response_model=VirtualMachine)
def create_virtual_machine(
    *,
    session: Session = Depends(get_session),
    vm: VirtualMachine
):
    """
    Create a new virtual machine resource in the database.
    """
    session.add(vm)
    session.commit()
    session.refresh(vm)
    return vm

@router.get("/virtualmachines/", response_model=List[VirtualMachine])
def list_virtual_machines(
    *,
    session: Session = Depends(get_session)
):
    """
    List all virtual machine resources in the database.
    """
    vms = session.exec(select(VirtualMachine)).all()
    return vms

@router.get("/virtualmachines/{vm_id}", response_model=VirtualMachine)
def get_virtual_machine_by_id(
    *,
    session: Session = Depends(get_session),
    vm_id: int
):
    """
    Retrieve a virtual machine by its database ID.
    """
    vm = session.get(VirtualMachine, vm_id)
    if not vm:
        raise HTTPException(status_code=404, detail="Virtual machine not found")
    return vm
