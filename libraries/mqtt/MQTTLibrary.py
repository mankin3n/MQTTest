"""
Custom Robot Framework library for MQTT operations with certificate-based authentication.
Supports publish/subscribe, QoS levels, retained messages, and message queue handling.
"""

import json
import time
import queue
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
import paho.mqtt.client as mqtt
from robot.api import logger
from robot.api.deco import keyword


class MQTTLibrary:
    """
    Robot Framework library for MQTT testing with mTLS support.

    Provides keywords for connecting to MQTT broker, publishing/subscribing to topics,
    and validating messages with proper QoS handling and certificate authentication.
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = "1.0.0"

    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.message_queues: Dict[str, queue.Queue] = {}
        self.subscriptions: Dict[str, int] = {}
        self.connection_status = False
        self.lock = threading.Lock()
        self.metrics = {
            "messages_published": 0,
            "messages_received": 0,
            "connection_time": None,
            "last_message_time": None,
        }

    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when client connects to broker."""
        if rc == 0:
            self.connection_status = True
            self.metrics["connection_time"] = datetime.now()
            logger.info(f"Connected to MQTT broker with result code: {rc}")

            # Resubscribe to topics on reconnect
            with self.lock:
                for topic, qos in self.subscriptions.items():
                    client.subscribe(topic, qos)
                    logger.info(f"Resubscribed to topic: {topic} (QoS: {qos})")
        else:
            self.connection_status = False
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorized",
            }
            error_msg = error_messages.get(rc, f"Unknown error code: {rc}")
            logger.error(f"Failed to connect to MQTT broker: {error_msg}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback for when client disconnects from broker."""
        self.connection_status = False
        if rc != 0:
            logger.warn(f"Unexpected disconnection from MQTT broker. Code: {rc}")
        else:
            logger.info("Disconnected from MQTT broker")

    def _on_message(self, client, userdata, message):
        """Callback for when a message is received."""
        topic = message.topic
        payload = message.payload.decode("utf-8")
        qos = message.qos
        retained = message.retain

        self.metrics["messages_received"] += 1
        self.metrics["last_message_time"] = datetime.now()

        logger.info(
            f"Message received - Topic: {topic}, QoS: {qos}, "
            f"Retained: {retained}, Payload: {payload[:100]}"
        )

        # Store message in topic-specific queue
        with self.lock:
            if topic not in self.message_queues:
                self.message_queues[topic] = queue.Queue()
            self.message_queues[topic].put(
                {
                    "topic": topic,
                    "payload": payload,
                    "qos": qos,
                    "retained": retained,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def _on_publish(self, client, userdata, mid):
        """Callback for when a message is published."""
        logger.debug(f"Message published with message ID: {mid}")

    @keyword("Connect To MQTT Broker")
    def connect_to_broker(
        self,
        broker_host: str,
        broker_port: int = 1883,
        client_id: str = None,
        username: str = None,
        password: str = None,
        ca_cert: str = None,
        client_cert: str = None,
        client_key: str = None,
        keepalive: int = 60,
        clean_session: bool = True,
    ):
        """
        Connect to MQTT broker with optional mTLS authentication.

        Args:
            broker_host: MQTT broker hostname or IP
            broker_port: MQTT broker port (default: 1883, TLS: 8883)
            client_id: Unique client identifier
            username: Username for authentication
            password: Password for authentication
            ca_cert: Path to CA certificate for TLS
            client_cert: Path to client certificate for mTLS
            client_key: Path to client private key for mTLS
            keepalive: Keep-alive interval in seconds
            clean_session: Whether to start a clean session

        Example:
            | Connect To MQTT Broker | localhost | 8883 |
            | ...  | ca_cert=certs/ca/ca.crt |
            | ...  | client_cert=certs/clients/test-client.crt |
            | ...  | client_key=certs/clients/test-client.key |
        """
        if not client_id:
            client_id = f"robot_test_{int(time.time())}"

        logger.info(f"Connecting to MQTT broker at {broker_host}:{broker_port}")

        self.client = mqtt.Client(client_id=client_id, clean_session=clean_session)

        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish

        # Configure authentication
        if username and password:
            self.client.username_pw_set(username, password)
            logger.info("Using username/password authentication")

        # Configure TLS/mTLS
        if ca_cert:
            logger.info(f"Configuring TLS with CA cert: {ca_cert}")
            self.client.tls_set(
                ca_certs=ca_cert, certfile=client_cert, keyfile=client_key
            )

        # Connect to broker
        try:
            self.client.connect(broker_host, int(broker_port), int(keepalive))
            self.client.loop_start()

            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.connection_status and (time.time() - start_time) < timeout:
                time.sleep(0.1)

            if not self.connection_status:
                raise ConnectionError(
                    f"Failed to connect to broker within {timeout} seconds"
                )

            logger.info("Successfully connected to MQTT broker")

        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {str(e)}")
            raise

    @keyword("Disconnect From MQTT Broker")
    def disconnect_from_broker(self):
        """
        Disconnect from MQTT broker and clean up resources.

        Example:
            | Disconnect From MQTT Broker |
        """
        if self.client:
            logger.info("Disconnecting from MQTT broker")
            self.client.loop_stop()
            self.client.disconnect()
            self.connection_status = False
            logger.info("Disconnected successfully")

    @keyword("Subscribe To Topic")
    def subscribe_to_topic(self, topic: str, qos: int = 1):
        """
        Subscribe to an MQTT topic.

        Args:
            topic: MQTT topic to subscribe to (supports wildcards)
            qos: Quality of Service level (0, 1, or 2)

        Example:
            | Subscribe To Topic | home/+/telemetry | 1 |
        """
        if not self.client or not self.connection_status:
            raise ConnectionError("Not connected to MQTT broker")

        logger.info(f"Subscribing to topic: {topic} with QoS: {qos}")

        result, mid = self.client.subscribe(topic, int(qos))

        if result == mqtt.MQTT_ERR_SUCCESS:
            with self.lock:
                self.subscriptions[topic] = int(qos)
                if topic not in self.message_queues:
                    self.message_queues[topic] = queue.Queue()
            logger.info(f"Successfully subscribed to topic: {topic}")
        else:
            raise RuntimeError(f"Failed to subscribe to topic: {topic}")

    @keyword("Unsubscribe From Topic")
    def unsubscribe_from_topic(self, topic: str):
        """
        Unsubscribe from an MQTT topic.

        Args:
            topic: MQTT topic to unsubscribe from

        Example:
            | Unsubscribe From Topic | home/device001/telemetry |
        """
        if not self.client or not self.connection_status:
            raise ConnectionError("Not connected to MQTT broker")

        logger.info(f"Unsubscribing from topic: {topic}")
        result, mid = self.client.unsubscribe(topic)

        if result == mqtt.MQTT_ERR_SUCCESS:
            with self.lock:
                if topic in self.subscriptions:
                    del self.subscriptions[topic]
            logger.info(f"Successfully unsubscribed from topic: {topic}")
        else:
            raise RuntimeError(f"Failed to unsubscribe from topic: {topic}")

    @keyword("Publish Message")
    def publish_message(
        self, topic: str, payload: str, qos: int = 1, retain: bool = False
    ):
        """
        Publish a message to an MQTT topic.

        Args:
            topic: MQTT topic to publish to
            payload: Message payload (string or JSON)
            qos: Quality of Service level (0, 1, or 2)
            retain: Whether to retain the message on the broker

        Example:
            | Publish Message | home/device001/command | {"action": "turn_on"} | 1 |
        """
        if not self.client or not self.connection_status:
            raise ConnectionError("Not connected to MQTT broker")

        logger.info(f"Publishing to topic: {topic}, QoS: {qos}, Retain: {retain}")
        logger.debug(f"Payload: {payload}")

        result = self.client.publish(topic, payload, int(qos), retain)

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            self.metrics["messages_published"] += 1
            logger.info(f"Message published successfully (mid: {result.mid})")

            # Wait for publish completion if QoS > 0
            if int(qos) > 0:
                result.wait_for_publish(timeout=5)
        else:
            raise RuntimeError(f"Failed to publish message. Error code: {result.rc}")

    @keyword("Wait For Message")
    def wait_for_message(
        self, topic: str, timeout: int = 10, clear_queue: bool = False
    ) -> Dict[str, Any]:
        """
        Wait for a message on a subscribed topic.

        Args:
            topic: MQTT topic to wait for messages on
            timeout: Maximum time to wait in seconds
            clear_queue: Whether to clear the message queue before waiting (default: False)

        Returns:
            Dictionary containing message details

        Example:
            | ${message}= | Wait For Message | home/device001/status | 5 |
        """
        logger.info(f"Waiting for message on topic: {topic} (timeout: {timeout}s)")

        with self.lock:
            if topic not in self.message_queues:
                self.message_queues[topic] = queue.Queue()

            msg_queue = self.message_queues[topic]

            # Optionally clear existing messages
            if clear_queue:
                while not msg_queue.empty():
                    try:
                        msg_queue.get_nowait()
                    except queue.Empty:
                        break

        # Wait for new message
        try:
            message = msg_queue.get(timeout=int(timeout))
            logger.info(f"Received message: {message}")
            return message
        except queue.Empty:
            raise TimeoutError(
                f"No message received on topic '{topic}' within {timeout} seconds"
            )

    @keyword("Get All Messages")
    def get_all_messages(self, topic: str) -> List[Dict[str, Any]]:
        """
        Get all messages from a topic's queue without waiting.

        Args:
            topic: MQTT topic to get messages from

        Returns:
            List of message dictionaries

        Example:
            | ${messages}= | Get All Messages | home/device001/telemetry |
        """
        messages = []

        with self.lock:
            if topic in self.message_queues:
                msg_queue = self.message_queues[topic]
                while not msg_queue.empty():
                    try:
                        messages.append(msg_queue.get_nowait())
                    except queue.Empty:
                        break

        logger.info(f"Retrieved {len(messages)} messages from topic: {topic}")
        return messages

    @keyword("Clear Message Queue")
    def clear_message_queue(self, topic: str):
        """
        Clear all messages from a topic's queue.

        Args:
            topic: MQTT topic to clear messages from

        Example:
            | Clear Message Queue | home/device001/telemetry |
        """
        with self.lock:
            if topic in self.message_queues:
                while not self.message_queues[topic].empty():
                    try:
                        self.message_queues[topic].get_nowait()
                    except queue.Empty:
                        break
        logger.info(f"Cleared message queue for topic: {topic}")

    @keyword("Verify Message Payload")
    def verify_message_payload(self, message: Dict[str, Any], expected_payload: str):
        """
        Verify that a message payload matches the expected value.

        Args:
            message: Message dictionary from Wait For Message
            expected_payload: Expected payload string

        Example:
            | Verify Message Payload | ${message} | {"status": "online"} |
        """
        actual_payload = message.get("payload", "")
        if actual_payload != expected_payload:
            raise AssertionError(
                f"Payload mismatch.\nExpected: {expected_payload}\nActual: {actual_payload}"
            )
        logger.info("Message payload verified successfully")

    @keyword("Verify JSON Message Field")
    def verify_json_message_field(
        self, message: Dict[str, Any], field_path: str, expected_value: Any
    ):
        """
        Verify a specific field in a JSON message payload.

        Args:
            message: Message dictionary from Wait For Message
            field_path: Dot-notation path to field (e.g., "device.status")
            expected_value: Expected field value

        Example:
            | Verify JSON Message Field | ${message} | device.temperature | 22.5 |
        """
        payload = message.get("payload", "{}")

        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON payload: {payload}")

        # Navigate through nested fields
        fields = field_path.split(".")
        value = data
        for field in fields:
            if isinstance(value, dict) and field in value:
                value = value[field]
            else:
                raise KeyError(f"Field '{field_path}' not found in message payload")

        if str(value) != str(expected_value):
            raise AssertionError(
                f"Field '{field_path}' mismatch.\nExpected: {expected_value}\nActual: {value}"
            )

        logger.info(f"Field '{field_path}' verified: {value}")

    @keyword("Get MQTT Metrics")
    def get_mqtt_metrics(self) -> Dict[str, Any]:
        """
        Get MQTT connection and message metrics.

        Returns:
            Dictionary containing metrics

        Example:
            | ${metrics}= | Get MQTT Metrics |
            | Log | Published: ${metrics['messages_published']} |
        """
        logger.info(f"MQTT Metrics: {self.metrics}")
        return self.metrics.copy()

    @keyword("Connection Should Be Active")
    def connection_should_be_active(self):
        """
        Verify that MQTT connection is active.

        Example:
            | Connection Should Be Active |
        """
        if not self.connection_status:
            raise AssertionError("MQTT connection is not active")
        logger.info("MQTT connection is active")
