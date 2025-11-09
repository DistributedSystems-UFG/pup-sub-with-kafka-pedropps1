from kafka import KafkaConsumer, KafkaProducer
import threading
import sys
import time
import uuid
import json

def receiver_thread(consumer, stop_event):
    try:
        while not stop_event.is_set():
            for msg in consumer:
                if stop_event.is_set():
                    break
                if msg.value['sender'] == username:
                    continue
                display_msg = f"[{msg.value['sender']} @ {msg.value['topic']}]: {msg.value['text']}"
                sys.stdout.write('\r' + ' ' * 80 + '\r')
                print(display_msg)
                sys.stdout.write(f'[{username} @ {current_topic}]> ')
                sys.stdout.flush()
    finally:
        consumer.close()
        print("Consumidor encerrado.")

def main():
    global username, current_topic

    username = input("Digite seu nome de usuário: ")
    initial_topic = input("Digite o canal inicial que deseja entrar (ex: geral): ")
    initial_topic = initial_topic.lstrip('#')
    unique_group_id = f'chat-group-{username}-{uuid.uuid4()}'
    subscribed_topics = {initial_topic}
    current_topic = initial_topic
    stop_event = threading.Event()

    producer = KafkaProducer(
        bootstrap_servers=[f'{BROKER_ADDR}:{BROKER_PORT}'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    consumer = KafkaConsumer(
        bootstrap_servers=[f'{BROKER_ADDR}:{BROKER_PORT}'],
        group_id=unique_group_id,
        auto_offset_reset='latest',
        consumer_timeout_ms=1000,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    consumer.subscribe(topics=list(subscribed_topics))

    receiver = threading.Thread(target=receiver_thread, args=(consumer, stop_event))
    receiver.start()

    print("\nBem-vindo ao chat Kafka! Digite /help para ver os comandos.")

    try:
        while not stop_event.is_set():
            prompt = f'[{username} @ {current_topic}]> '
            message_input = input(prompt)

            if message_input.startswith('/'):
                parts = message_input.split(' ', 1)
                command = parts[0].lower()

                if command == '/quit':
                    stop_event.set()
                    continue

                elif command == '/help':
                    print("\nComandos: /join <canal>, /switch <canal>, /quit")

                elif command == '/join':
                    if len(parts) > 1:
                        new_topic = parts[1].lstrip('#')
                        if new_topic not in subscribed_topics:
                            subscribed_topics.add(new_topic)
                            consumer.subscribe(topics=list(subscribed_topics))
                            print(f"Você entrou no canal: {new_topic}")
                    else:
                        print("Uso: /join <canal>")

                elif command == '/switch':
                    if len(parts) > 1:
                        new_topic = parts[1].lstrip('#')
                        if new_topic in subscribed_topics:
                            current_topic = new_topic
                        else:
                            print(f"Você não está no canal {new_topic}. Use /join primeiro.")
                    else:
                        print("Uso: /switch <canal>")
                continue

            if message_input:
                payload = {
                    "sender": username,
                    "topic": current_topic,
                    "text": message_input
                }
                producer.send(topic=current_topic, value=payload)
                producer.flush()

    except KeyboardInterrupt:
        stop_event.set()
    finally:
        print("\nEncerrando...")
        stop_event.set()
        receiver.join()
        producer.close()
        print("Até logo!")

if __name__ == "__main__":
    from const import BROKER_ADDR, BROKER_PORT
    main()
