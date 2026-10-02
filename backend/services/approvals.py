"""
SOAR Platform - Approval Service
Handles action approvals and workflow.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy.orm import Session
from models.approvals import ApprovalRequest, ApprovalComment


class ActionRisk(Enum):
    READ = "READ"
    ENRICH = "ENRICH"
    MODIFY = "MODIFY"
    CONTAIN = "CONTAIN"
    EXECUTE = "EXECUTE"
    DESTRUCTIVE = "DESTRUCTIVE"


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApproverType(Enum):
    USER = "user"
    ROLE = "role"
    GROUP = "group"
    AI_ASSIST = "ai_assist"


class ApprovalService:
    """
    Approval service for handling action approvals.
    
    MODIFY, CONTAIN, EXECUTE and DESTRUCTIVE should normally require authorization.
    """
    
    def __init__(self, default_expiry_hours: int = 24):
        self.default_expiry_hours = default_expiry_hours
    
    async def initialize(self, db_session: Session):
        """Initialize approval service."""
        pass
    
    def requires_approval(self, risk_level: str) -> bool:
        """Check if risk level requires approval."""
        requires_approval = {
            "READ": False,
            "ENRICH": False,
            "MODIFY_LOW": False,
            "MODIFY": True,
            "CONTAIN": True,
            "EXECUTE": True,
            "DESTRUCTIVE": True,
        }
        return requires_approval.get(risk_level, False)
    
    def create_approval_request(
        self,
        db_session: Session,
        request_type: str,
        description: str,
        incident_id: Optional[int] = None,
        action_type: Optional[str] = None,
        action_target: Optional[str] = None,
        action_metadata: Optional[str] = None,
        risk_level: str = "MODIFY",
        requested_by: Optional[int] = None,
        requested_by_type: Optional[str] = "analyst",
        ai_recommendation: Optional[str] = None,
        ai_reasoning: Optional[str] = None,
        approver_type: ApproverType = ApproverType.USER,
    ) -> ApprovalRequest:
        """
        Create an approval request.
        
        Dangerous actions must enter the normal approval workflow.
        """
        approval_id = self.generate_approval_id()
        
        request = ApprovalRequest(
            approval_id=approval_id,
            request_type=request_type,
            description=description,
            incident_id=incident_id,
            action_type=action_type,
            action_target=action_target,
            action_metadata=action_metadata,
            risk_level=risk_level,
            status=ApprovalStatus.PENDING,
            requested_by=requested_by,
            requested_by_type=requested_by_type,
            requested_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=self.default_expiry_hours),
            approver_type=approver_type,
            ai_recommendation=ai_recommendation,
            ai_reasoning=ai_reasoning,
        )
        
        db_session.add(request)
        db_session.commit()
        
        return request
    
    def approve_request(
        self,
        db_session: Session,
        approval_id: str,
        approved_by: int,
        approved_by_type: ApproverType = ApproverType.USER,
    ) -> ApprovalRequest:
        """Approve an action request."""
        request = db_session.query(ApprovalRequest).get(approval_id)
        
        if request:
            request.status = ApprovalStatus.APPROVED
            request.approved_by = approved_by
            request.approved_by_type = approved_by_type
            request.approved_at = datetime.utcnow()
            
            db_session.commit()
        
        return request
    
    def reject_request(
        self,
        db_session: Session,
        approval_id: str,
        rejected_by: int,
        rejection_reason: str,
        rejected_by_type: ApproverType = ApproverType.USER,
    ) -> ApprovalRequest:
        """Reject an action request."""
        request = db_session.query(ApprovalRequest).get(approval_id)
        
        if request:
            request.status = ApprovalStatus.REJECTED
            request.rejected_by = rejected_by
            request.rejected_by_type = rejected_by_type
            request.rejected_at = datetime.utcnow()
            request.rejection_reason = rejection_reason
            
            db_session.commit()
        
        return request
    
    def add_approval_comment(
        self,
        db_session: Session,
        approval_id: str,
        content: str,
        comment_type: str = "analyst",
        user_id: Optional[int] = None,
    ) -> ApprovalComment:
        """Add comment to approval request."""
        request = db_session.query(ApprovalRequest).get(approval_id)
        
        if request:
            comment = ApprovalComment(
                approval_id=approval_id,
                content=content,
                comment_type=comment_type,
                user_id=user_id,
                created_at=datetime.utcnow(),
            )
            
            db_session.add(comment)
            db_session.commit()
        
        return comment
    
    def generate_approval_id(self) -> str:
        """Generate an approval ID."""
        import random
        number = random.randint(10000, 99999)
        return f"APR-{number:05d}"
