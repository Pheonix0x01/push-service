import firebase_admin
from firebase_admin import messaging, credentials
from app.core.config import settings
from app.core.circuit_breaker import circuit_breaker
from app.utils.logger import logger

cred = credentials.Certificate(settings.fcm_credentials_path)
firebase_admin.initialize_app(cred)

async def send_push_notification(msg):
    if not circuit_breaker.can_call():
        raise Exception("Circuit breaker is open")
    
    try:
        message = messaging.Message(
            token=msg.variables.get("push_token"),
            notification=messaging.Notification(
                title=msg.variables.get("title", "Notification"),
                body=msg.variables.get("body", ""),
                image=msg.variables.get("image")
            ),
            data={"link": msg.variables.get("link", "")}
        )
        response = messaging.send(message)
        logger.info(f"Push sent successfully: {response}")
        return response
    except Exception as e:
        circuit_breaker.record_failure()
        raise e