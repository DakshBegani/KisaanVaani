from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class Alert:
    def __init__(
        self,
        user_id: str,
        alert_type: str,
        message: str,
        condition: str,
        timestamp: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.alert_type = alert_type
        self.message = message
        self.condition = condition
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "alert_type": self.alert_type,
            "message": self.message,
            "condition": self.condition,
            "timestamp": self.timestamp.isoformat(),
        }


class AlertDatabase(ABC):
    @abstractmethod
    def save_alert(self, alert: Alert) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_user_alerts(self, user_id: str) -> list[Alert]:
        raise NotImplementedError


class DynamoAlertDB(AlertDatabase):
    def save_alert(self, alert: Alert) -> bool:
        print(f"[DynamoAlertDB] Saving alert for user {alert.user_id}: {alert.alert_type}")
        return True

    def get_user_alerts(self, user_id: str) -> list[Alert]:
        print(f"[DynamoAlertDB] Fetching alerts for user {user_id}")
        return []


class AlertService:
    def __init__(self, db: AlertDatabase):
        self.db = db

    def set_alert(self, user_id: str, alert_type: str, message: str, condition: str) -> bool:
        alert = Alert(user_id=user_id, alert_type=alert_type, message=message, condition=condition)
        return self.db.save_alert(alert)
