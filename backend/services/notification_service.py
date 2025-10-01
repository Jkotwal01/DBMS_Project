# services/notification_service.py
from sqlalchemy.orm import Session
from typing import Optional, List
import models, schemas

class NotificationService:
    """Service layer for notification-related operations"""
    
    @staticmethod
    def create_notification(
        db: Session, 
        notification_data: schemas.NotificationCreate, 
        faculty_id: int
    ) -> models.Notification:
        """Create a new notification"""
        notification = models.Notification(
            title=notification_data.title,
            description=notification_data.description,
            created_by=faculty_id,
            visible_to=notification_data.visible_to,
            priority=notification_data.priority
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def get_notification_by_id(db: Session, notification_id: int) -> Optional[models.Notification]:
        """Get notification by ID"""
        return db.query(models.Notification).filter(
            models.Notification.notification_id == notification_id
        ).first()
    
    @staticmethod
    def get_notifications_for_role(
        db: Session, 
        role: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[models.Notification]:
        """Get notifications visible to a specific role"""
        return db.query(models.Notification).filter(
            (models.Notification.visible_to == role) | 
            (models.Notification.visible_to == "All"),
            models.Notification.is_active == True
        ).order_by(
            models.Notification.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_faculty_notifications(
        db: Session, 
        faculty_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[models.Notification]:
        """Get notifications created by a faculty member"""
        return db.query(models.Notification).filter(
            models.Notification.created_by == faculty_id
        ).order_by(
            models.Notification.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_notification(
        db: Session, 
        notification_id: int, 
        notification_data: schemas.NotificationUpdate
    ) -> models.Notification:
        """Update a notification"""
        notification = db.query(models.Notification).filter(
            models.Notification.notification_id == notification_id
        ).first()
        
        if not notification:
            raise ValueError("Notification not found")
        
        for key, value in notification_data.dict(exclude_unset=True).items():
            setattr(notification, key, value)
        
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def delete_notification(db: Session, notification_id: int) -> bool:
        """Delete a notification"""
        notification = db.query(models.Notification).filter(
            models.Notification.notification_id == notification_id
        ).first()
        
        if not notification:
            raise ValueError("Notification not found")
        
        db.delete(notification)
        db.commit()
        return True
    
    @staticmethod
    def deactivate_notification(db: Session, notification_id: int) -> models.Notification:
        """Soft delete notification by setting is_active to False"""
        notification = db.query(models.Notification).filter(
            models.Notification.notification_id == notification_id
        ).first()
        
        if not notification:
            raise ValueError("Notification not found")
        
        notification.is_active = False
        db.commit()
        db.refresh(notification)
        return notification
