"""
Test data factory for generating realistic IoT device data and telemetry.
"""
import json
import random
from datetime import datetime
from typing import Dict, Any, List
from faker import Faker
from robot.api import logger
from robot.api.deco import keyword


class TestDataFactory:
    """
    Robot Framework library for generating test data.

    Provides keywords for creating realistic device data, telemetry, and user profiles.
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'

    def __init__(self):
        self.faker = Faker()
        self.device_types = ['light', 'thermostat', 'sensor', 'camera', 'lock', 'switch']
        self.sensor_types = ['temperature', 'humidity', 'motion', 'door', 'smoke', 'co2']

    @keyword("Generate Device Data")
    def generate_device_data(
        self,
        device_type: str = None,
        device_id: str = None,
        location: str = None
    ) -> Dict[str, Any]:
        """
        Generate realistic device registration data.

        Args:
            device_type: Type of device (light, thermostat, sensor, etc.)
            device_id: Device ID (auto-generated if not provided)
            location: Device location (auto-generated if not provided)

        Returns:
            Device data dictionary

        Example:
            | ${device}= | Generate Device Data | light | device001 |
        """
        if not device_type:
            device_type = random.choice(self.device_types)

        if not device_id:
            device_id = f"{device_type}_{self.faker.uuid4()[:8]}"

        if not location:
            location = random.choice([
                'living_room', 'bedroom', 'kitchen', 'bathroom',
                'garage', 'office', 'hallway', 'basement'
            ])

        device_data = {
            'device_id': device_id,
            'type': device_type,
            'name': f"{device_type.title()} - {location.replace('_', ' ').title()}",
            'location': location,
            'manufacturer': random.choice(['SmartHome Inc.', 'IoT Solutions', 'ConnectedDevices']),
            'model': f"{device_type.upper()}-{random.randint(100, 999)}",
            'firmware_version': f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 20)}",
            'mac_address': self.faker.mac_address(),
            'ip_address': self.faker.ipv4_private(),
            'registered_at': datetime.utcnow().isoformat() + 'Z'
        }

        logger.info(f"Generated device data: {device_data['device_id']}")
        return device_data

    @keyword("Generate Telemetry Data")
    def generate_telemetry_data(
        self,
        device_type: str,
        device_id: str
    ) -> Dict[str, Any]:
        """
        Generate realistic telemetry data for a device.

        Args:
            device_type: Type of device
            device_id: Device ID

        Returns:
            Telemetry data dictionary

        Example:
            | ${telemetry}= | Generate Telemetry Data | thermostat | device001 |
        """
        base_telemetry = {
            'device_id': device_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'battery_level': random.randint(20, 100),
            'signal_strength': random.randint(-80, -30),
            'uptime_seconds': random.randint(0, 86400 * 30)
        }

        # Device-specific telemetry
        if device_type == 'thermostat':
            base_telemetry.update({
                'temperature': round(random.uniform(18.0, 28.0), 1),
                'target_temperature': random.choice([20.0, 21.0, 22.0, 23.0]),
                'humidity': random.randint(30, 70),
                'mode': random.choice(['heat', 'cool', 'auto', 'off']),
                'fan_speed': random.choice(['low', 'medium', 'high', 'auto'])
            })

        elif device_type == 'light':
            base_telemetry.update({
                'status': random.choice(['on', 'off']),
                'brightness': random.randint(0, 100),
                'color_temp': random.randint(2700, 6500),
                'power_consumption_watts': round(random.uniform(5.0, 60.0), 1)
            })

        elif device_type == 'sensor':
            sensor_type = random.choice(self.sensor_types)
            base_telemetry.update({
                'sensor_type': sensor_type
            })

            if sensor_type == 'temperature':
                base_telemetry['value'] = round(random.uniform(15.0, 30.0), 1)
                base_telemetry['unit'] = 'celsius'
            elif sensor_type == 'humidity':
                base_telemetry['value'] = random.randint(20, 80)
                base_telemetry['unit'] = 'percent'
            elif sensor_type == 'motion':
                base_telemetry['detected'] = random.choice([True, False])
            elif sensor_type == 'door':
                base_telemetry['open'] = random.choice([True, False])
            elif sensor_type in ['smoke', 'co2']:
                base_telemetry['alarm'] = random.choice([True, False])
                base_telemetry['level'] = random.randint(0, 100)

        elif device_type == 'camera':
            base_telemetry.update({
                'recording': random.choice([True, False]),
                'motion_detected': random.choice([True, False]),
                'resolution': random.choice(['720p', '1080p', '4K']),
                'fps': random.choice([15, 24, 30, 60])
            })

        elif device_type == 'lock':
            base_telemetry.update({
                'locked': random.choice([True, False]),
                'last_accessed_by': self.faker.name(),
                'tamper_alert': False
            })

        logger.debug(f"Generated telemetry for {device_id}: {base_telemetry}")
        return base_telemetry

    @keyword("Generate User Data")
    def generate_user_data(self, role: str = 'user') -> Dict[str, Any]:
        """
        Generate realistic user registration data.

        Args:
            role: User role (admin, user, guest)

        Returns:
            User data dictionary

        Example:
            | ${user}= | Generate User Data | admin |
        """
        user_data = {
            'user_id': self.faker.uuid4(),
            'username': self.faker.user_name(),
            'email': self.faker.email(),
            'password': self.faker.password(length=12),
            'first_name': self.faker.first_name(),
            'last_name': self.faker.last_name(),
            'role': role,
            'phone': self.faker.phone_number(),
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }

        logger.info(f"Generated user data: {user_data['username']}")
        return user_data

    @keyword("Generate Automation Rule")
    def generate_automation_rule(
        self,
        trigger_device_id: str = None,
        action_device_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate automation rule data.

        Args:
            trigger_device_id: ID of device that triggers the rule
            action_device_id: ID of device to perform action

        Returns:
            Automation rule dictionary

        Example:
            | ${rule}= | Generate Automation Rule | sensor001 | light001 |
        """
        if not trigger_device_id:
            trigger_device_id = f"sensor_{self.faker.uuid4()[:8]}"

        if not action_device_id:
            action_device_id = f"light_{self.faker.uuid4()[:8]}"

        conditions = [
            {'field': 'temperature', 'operator': 'greater_than', 'value': 25},
            {'field': 'humidity', 'operator': 'less_than', 'value': 40},
            {'field': 'motion_detected', 'operator': 'equals', 'value': True},
            {'field': 'door.open', 'operator': 'equals', 'value': True}
        ]

        actions = [
            {'type': 'turn_on', 'device_id': action_device_id},
            {'type': 'turn_off', 'device_id': action_device_id},
            {'type': 'set_temperature', 'device_id': action_device_id, 'value': 22},
            {'type': 'send_notification', 'message': 'Alert triggered'}
        ]

        rule_data = {
            'rule_id': self.faker.uuid4(),
            'name': f"Automation Rule - {self.faker.catch_phrase()}",
            'enabled': True,
            'trigger': {
                'device_id': trigger_device_id,
                'condition': random.choice(conditions)
            },
            'actions': [random.choice(actions)],
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }

        logger.info(f"Generated automation rule: {rule_data['name']}")
        return rule_data

    @keyword("Generate Multiple Devices")
    def generate_multiple_devices(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate multiple device data objects.

        Args:
            count: Number of devices to generate

        Returns:
            List of device data dictionaries

        Example:
            | ${devices}= | Generate Multiple Devices | 10 |
        """
        devices = []
        for _ in range(int(count)):
            devices.append(self.generate_device_data())

        logger.info(f"Generated {len(devices)} devices")
        return devices

    @keyword("Convert To JSON String")
    def convert_to_json_string(self, data: Any) -> str:
        """
        Convert data to JSON string.

        Args:
            data: Data to convert

        Returns:
            JSON string

        Example:
            | ${json}= | Convert To JSON String | ${device_data} |
        """
        return json.dumps(data)

    @keyword("Parse JSON String")
    def parse_json_string(self, json_string: str) -> Any:
        """
        Parse JSON string to data structure.

        Args:
            json_string: JSON string to parse

        Returns:
            Parsed data

        Example:
            | ${data}= | Parse JSON String | ${json_string} |
        """
        return json.loads(json_string)
