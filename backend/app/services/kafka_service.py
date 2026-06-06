import json
from typing import Dict, Any
from app.utils.config import settings

# Global Kafka producer
KAFKA_AVAILABLE = False
_kafka_producer = None

try:
    from kafka import KafkaProducer
    _kafka_producer = KafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        request_timeout_ms=1000
    )
    KAFKA_AVAILABLE = True
except Exception:
    pass

class KafkaService:
    @staticmethod
    def send_event(topic: str, payload: Dict[str, Any]) -> bool:
        """
        Sends event payloads to Kafka brokers.
        Falls back to local console logger if Kafka is offline.
        """
        if KAFKA_AVAILABLE and _kafka_producer:
            try:
                _kafka_producer.send(topic, payload)
                return True
            except Exception as e:
                print(f"Kafka send error: {e}. Logging event to fallback queue.")
                
        # Fallback console logger
        print(f"[EventStreamFallback] Topic: {topic} | Payload: {payload}")
        
        # Real-time WebSocket triggers can hook here for instant recommendation updates
        from app.api.websockets import websocket_manager
        
        # Trigger recommendations updates live in the frontend over WebSockets
        if topic == "user_activity" and payload.get("event_type") in ["click", "purchase"]:
            session_id = payload.get("session_id")
            if session_id:
                # Tell WebSocket manager to alert active session clients to refresh recommendations
                websocket_manager.broadcast_to_session(
                    session_id, 
                    {"event": "recommendation_refresh", "message": f"Activity {payload['event_type']} triggered refresh"}
                )
        return True

kafka_service = KafkaService()
