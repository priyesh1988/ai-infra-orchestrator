import os, json
from confluent_kafka import Producer, Consumer

def producer():
    conf = {"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")}
    return Producer(conf)

def consumer(group_id: str):
    conf = {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        "group.id": group_id,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    }
    return Consumer(conf)

def publish_event(topic: str, event: dict):
    p = producer()
    p.produce(topic, json.dumps(event).encode("utf-8"))
    p.flush()
