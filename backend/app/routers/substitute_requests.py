from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.models import SubstituteRequest, CourseSchedule
from app.schemas.schemas import SubstituteRequestOut, SubstituteRequestCreate, SubstituteRequestAssign
from app.routers.auth import get_current_user, require_role

router = APIRouter()

@router.get("", response_model=List[SubstituteRequestOut])
def list_requests(status: Optional[str] = None, teacher_id: Optional[int] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(SubstituteRequest)
    if status: q = q.filter(SubstituteRequest.status == status)
    if teacher_id: q = q.filter((SubstituteRequest.original_teacher_id == teacher_id) | (SubstituteRequest.substitute_teacher_id == teacher_id))
    return q.order_by(SubstituteRequest.created_at.desc()).all()

@router.post("", response_model=SubstituteRequestOut)
def create_request(data: SubstituteRequestCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    schedule = db.query(CourseSchedule).filter(CourseSchedule.id == data.schedule_id).first()
    if not schedule: raise HTTPException(status_code=404, detail="排课不存在")
    req = SubstituteRequest(
        schedule_id=data.schedule_id,
        original_teacher_id=schedule.teacher_id,
        start_date=data.start_date,
        end_date=data.end_date,
        reason=data.reason
    )
    db.add(req); db.commit(); db.refresh(req); return req

@router.put("/{rid}/assign", response_model=SubstituteRequestOut)
def assign_substitute(rid: int, data: SubstituteRequestAssign, db: Session = Depends(get_db), _=require_role("admin", "manager")):
    req = db.query(SubstituteRequest).filter(SubstituteRequest.id == rid).first()
    if not req: raise HTTPException(status_code=404, detail="申请不存在")
    if req.status != 'pending': raise HTTPException(status_code=400, detail="只能处理待处理的申请")
    req.substitute_teacher_id = data.substitute_teacher_id
    req.remark = data.remark
    req.status = 'approved'
    db.commit(); db.refresh(req); return req

@router.put("/{rid}/reject")
def reject_request(rid: int, remark: Optional[str] = None, db: Session = Depends(get_db), _=require_role("admin", "manager")):
    req = db.query(SubstituteRequest).filter(SubstituteRequest.id == rid).first()
    if not req: raise HTTPException(status_code=404, detail="申请不存在")
    if req.status != 'pending': raise HTTPException(status_code=400, detail="只能处理待处理的申请")
    req.remark = remark
    req.status = 'rejected'
    db.commit(); db.refresh(req); return {"message": "申请已拒绝"}

@router.delete("/{rid}")
def delete_request(rid: int, db: Session = Depends(get_db), _=require_role("admin", "manager")):
    req = db.query(SubstituteRequest).filter(SubstituteRequest.id == rid).first()
    if not req: raise HTTPException(status_code=404, detail="申请不存在")
    db.delete(req); db.commit()
    return {"message": "申请已删除"}