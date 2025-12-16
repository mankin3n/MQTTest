#!/usr/bin/env python3
"""
Mock REST API server for SmartHome IoT platform testing.
Provides endpoints for device management, authentication, and automation rules.
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt

app = Flask(__name__)
CORS(app)

# In-memory storage
devices = {}
automation_rules = {}
users = {}

# Configuration
SECRET_KEY = os.getenv('JWT_SECRET', 'dev-secret-key')
PORT = int(os.getenv('API_PORT', 8000))


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token."""
    try:
        if not token:
            return None
        if token.startswith('Bearer '):
            token = token[7:]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Decorator to require authentication."""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization required'}), 401

        user = verify_token(auth_header)
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401

        return f(user, *args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


def require_admin(f):
    """Decorator to require admin role."""
    def decorated_function(user, *args, **kwargs):
        if user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(user, *args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


# Authentication endpoints
@app.route('/api/v1/auth/token', methods=['POST'])
def generate_token():
    """Generate JWT token."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    # Simple auth for testing
    role = 'admin' if 'admin' in username else 'user'

    token_data = {
        'user_id': str(uuid.uuid4()),
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }

    token = jwt.encode(token_data, SECRET_KEY, algorithm='HS256')

    return jsonify({
        'token': token,
        'user_id': token_data['user_id'],
        'username': username,
        'role': role,
        'expires_in': 3600
    }), 200


# Device endpoints
@app.route('/api/v1/devices', methods=['POST'])
@require_auth
def register_device(user):
    """Register a new device."""
    data = request.json

    if not data or 'device_id' not in data:
        return jsonify({'error': 'device_id is required'}), 400

    device_id = data['device_id']

    if device_id in devices:
        return jsonify({'error': 'Device already exists'}), 409

    device = {
        **data,
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z',
        'status': 'registered'
    }

    devices[device_id] = device

    return jsonify(device), 201


@app.route('/api/v1/devices/<device_id>', methods=['GET'])
@require_auth
def get_device(user, device_id):
    """Get device details."""
    device = devices.get(device_id)

    if not device:
        return jsonify({'error': 'Device not found'}), 404

    return jsonify(device), 200


@app.route('/api/v1/devices/<device_id>/status', methods=['GET'])
@require_auth
def get_device_status(user, device_id):
    """Get device status."""
    device = devices.get(device_id)

    if not device:
        return jsonify({'error': 'Device not found'}), 404

    return jsonify({
        'device_id': device_id,
        'status': device.get('status', 'unknown'),
        'last_seen': datetime.utcnow().isoformat() + 'Z',
        'online': True
    }), 200


@app.route('/api/v1/devices/<device_id>', methods=['PUT'])
@require_auth
def update_device(user, device_id):
    """Update device configuration."""
    device = devices.get(device_id)

    if not device:
        return jsonify({'error': 'Device not found'}), 404

    data = request.json
    device.update(data)
    device['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    device['updated'] = True

    devices[device_id] = device

    return jsonify(device), 200


@app.route('/api/v1/devices/<device_id>', methods=['DELETE'])
@require_auth
@require_admin
def delete_device(user, device_id):
    """Delete a device."""
    if device_id not in devices:
        return jsonify({'error': 'Device not found'}), 404

    del devices[device_id]

    return '', 204


@app.route('/api/v1/devices', methods=['GET'])
@require_auth
def list_devices(user):
    """List all devices."""
    return jsonify({
        'devices': list(devices.values()),
        'count': len(devices)
    }), 200


# Automation rules endpoints
@app.route('/api/v1/automation-rules', methods=['POST'])
@require_auth
def create_automation_rule(user):
    """Create automation rule."""
    data = request.json

    rule_id = data.get('rule_id', str(uuid.uuid4()))

    rule = {
        **data,
        'rule_id': rule_id,
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z'
    }

    automation_rules[rule_id] = rule

    return jsonify(rule), 201


@app.route('/api/v1/automation-rules/<rule_id>', methods=['GET'])
@require_auth
def get_automation_rule(user, rule_id):
    """Get automation rule."""
    rule = automation_rules.get(rule_id)

    if not rule:
        return jsonify({'error': 'Rule not found'}), 404

    return jsonify(rule), 200


@app.route('/api/v1/automation-rules/<rule_id>', methods=['PUT'])
@require_auth
def update_automation_rule(user, rule_id):
    """Update automation rule."""
    if rule_id not in automation_rules:
        return jsonify({'error': 'Rule not found'}), 404

    data = request.json
    automation_rules[rule_id].update(data)
    automation_rules[rule_id]['updated_at'] = datetime.utcnow().isoformat() + 'Z'

    return jsonify(automation_rules[rule_id]), 200


@app.route('/api/v1/automation-rules/<rule_id>', methods=['PATCH'])
@require_auth
def patch_automation_rule(user, rule_id):
    """Partially update automation rule."""
    if rule_id not in automation_rules:
        return jsonify({'error': 'Rule not found'}), 404

    data = request.json
    automation_rules[rule_id].update(data)
    automation_rules[rule_id]['updated_at'] = datetime.utcnow().isoformat() + 'Z'

    return jsonify(automation_rules[rule_id]), 200


@app.route('/api/v1/automation-rules/<rule_id>', methods=['DELETE'])
@require_auth
def delete_automation_rule(user, rule_id):
    """Delete automation rule."""
    if rule_id not in automation_rules:
        return jsonify({'error': 'Rule not found'}), 404

    del automation_rules[rule_id]

    return '', 204


# Certificate provisioning endpoints
@app.route('/api/v1/certificates/provision', methods=['POST'])
@require_auth
@require_admin
def provision_certificate(user):
    """Provision device certificate."""
    data = request.json

    device_id = data.get('device_id')
    csr = data.get('csr')

    if not device_id or not csr:
        return jsonify({'error': 'device_id and csr are required'}), 400

    # Mock certificate response
    certificate = f"-----BEGIN CERTIFICATE-----\nMOCK_CERT_FOR_{device_id}\n-----END CERTIFICATE-----"

    return jsonify({
        'device_id': device_id,
        'certificate': certificate,
        'issued_at': datetime.utcnow().isoformat() + 'Z',
        'expires_at': (datetime.utcnow() + timedelta(days=365)).isoformat() + 'Z'
    }), 201


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'devices_count': len(devices),
        'rules_count': len(automation_rules)
    }), 200


if __name__ == '__main__':
    print(f"Starting Mock API Server on port {PORT}")
    print(f"Health check: http://localhost:{PORT}/health")
    app.run(host='0.0.0.0', port=PORT, debug=True)
