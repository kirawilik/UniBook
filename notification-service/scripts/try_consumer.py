import json
import pika

from app.database import SessionLocal
from app.schemas import ReservationEvent
from app.services.notification_service import process_event

connection = pika.BlockingConnection(pika.URLParameters("amqp://guest:guest@localhost:5672/"))
channel = connection.channel()
channel.queue_declare(queue="notification_queue", durable=True)


def on_message(ch, method, properties, body):
    try:
        event = ReservationEvent(**json.loads(body))
    except Exception as e:
        print("Message invalide:", e)
        ch.basic_nack(method.delivery_tag, requeue=False)
        return
    db = SessionLocal()
    try:
        n = process_event(db, event)
        print("Notification enregistrée:", n.message)
        ch.basic_ack(method.delivery_tag)
    finally:
        db.close()


channel.basic_consume(queue="notification_queue", on_message_callback=on_message)
print("En attente de messages... (Ctrl+C pour arrêter)")
channel.start_consuming()