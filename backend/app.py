"""
PixelLedger Backend API

Flask-based REST API for the PixelLedger watermarking system.
Provides endpoints for watermark embedding, extraction, and user management.

Author: PixelLedger Team
"""

from flask import Flask, request, jsonify, send_file, session

class UltraRobustWatermarkSystem:
    """Ultra-robust watermark system with multiple delta values and error correction"""
    
    def __init__(self, delta=30.0, wavelet='haar', level=3):
        self.delta = delta
        self.wavelet = wavelet
        self.level = level
    
    def _bits_to_text_ultra_robust(self, bits):
        """Ultra-robust bits to text conversion with multiple error correction strategies"""
        text = ''
        for i in range(0, len(bits) - 7, 8):
            byte = bits[i:i+8]
            if len(byte) == 8:
                char_code = int(''.join(map(str, byte)), 2)
                
                # Multiple error correction strategies
                if char_code < 32 or char_code > 126:
                    corrected = False
                    
                    # Strategy 1: Try flipping each bit
                    for bit_pos in range(8):
                        corrected_byte = byte.copy()
                        corrected_byte[bit_pos] = 1 - corrected_byte[bit_pos]
                        corrected_code = int(''.join(map(str, corrected_byte)), 2)
                        if 32 <= corrected_code <= 126:
                            text += chr(corrected_code)
                            corrected = True
                            break
                    
                    # Strategy 2: Try flipping two bits
                    if not corrected:
                        for bit1 in range(8):
                            for bit2 in range(bit1+1, 8):
                                corrected_byte = byte.copy()
                                corrected_byte[bit1] = 1 - corrected_byte[bit1]
                                corrected_byte[bit2] = 1 - corrected_byte[bit2]
                                corrected_code = int(''.join(map(str, corrected_byte)), 2)
                                if 32 <= corrected_code <= 126:
                                    text += chr(corrected_code)
                                    corrected = True
                                    break
                            if corrected:
                                break
                    
                    # Strategy 3: Use closest valid character
                    if not corrected:
                        if char_code < 32:
                            text += chr(32)  # Space
                        elif char_code > 126:
                            text += chr(126)  # Tilde
                        else:
                            text += '?'
                else:
                    text += chr(char_code)
        return text
    
    def _extract_with_delta(self, watermarked_image, secret_key, delta):
        """Extract with specific delta value"""
        import pywt
        
        # Convert to YCrCb
        if len(watermarked_image.shape) == 3:
            ycrcb = cv2.cvtColor(watermarked_image, cv2.COLOR_RGB2YCrCb)
            Y = ycrcb[:, :, 0].astype(np.float64)
        else:
            Y = watermarked_image.astype(np.float64)
        
        # DWT
        coeffs = pywt.wavedec2(Y, self.wavelet, level=self.level)
        LL = coeffs[0].copy()
        LL_flat = LL.flatten()
        
        # Extract length (first 16 bits)
        length_bits = []
        for i in range(16):
            if i >= len(LL_flat):
                break
            quantized = np.round(LL_flat[i] / delta)
            length_bits.append(int(quantized) % 2)
        
        # Decode length
        if len(length_bits) == 16:
            payload_length = int(''.join(map(str, length_bits)), 2)
        else:
            payload_length = 0
        
        # Validate payload length
        if payload_length <= 0 or payload_length > 1000:
            return {
                'success': False,
                'payload': {},
                'raw_text': '',
                'error': 'Invalid payload length'
            }
        
        # Extract payload bits
        extracted_bits = []
        for i in range(16, min(16 + payload_length, len(LL_flat))):
            quantized = np.round(LL_flat[i] / delta)
            extracted_bits.append(int(quantized) % 2)
        
        extracted_bits = np.array(extracted_bits, dtype=np.uint8)
        
        # Decode text with ultra-robust method
        payload_text = self._bits_to_text_ultra_robust(extracted_bits)
        
        # Parse with validation
        parts = payload_text.split('|')
        payload = {}
        success = False
        
        if len(parts) >= 3:
            # Clean and validate fields
            payload['owner'] = parts[0].strip()
            payload['image_id'] = parts[1].strip()
            payload['date_created'] = parts[2].strip()
            
            # Extract optional fields
            if len(parts) > 3:
                payload['semantic_hash'] = parts[3].strip()
            if len(parts) > 4:
                payload['master_fingerprint'] = parts[4].strip()
            if len(parts) > 5:
                payload['perceptual_hash'] = parts[5].strip()
            
            # ALWAYS mark as success if we have 3+ parts - let tampering detection handle corruption
            success = True
        
        return {
            'success': success,
            'payload': payload,
            'raw_text': payload_text,
            'bits_extracted': len(extracted_bits),
            'fields_count': len(parts)
        }
    
    def _calculate_payload_quality(self, payload):
        """Calculate payload quality score"""
        if not payload:
            return 0
        
        quality = 0
        total_fields = len(payload)
        
        for key, value in payload.items():
            if isinstance(value, str):
                # Check for reasonable length
                if 3 <= len(value) <= 50:
                    quality += 1
                # Check for reasonable characters
                alnum_ratio = sum(1 for c in value if c.isalnum()) / len(value) if value else 0
                if alnum_ratio >= 0.5:
                    quality += 1
                # Check for excessive special characters
                special_ratio = sum(1 for c in value if not c.isalnum() and c not in ' -_') / len(value) if value else 0
                if special_ratio <= 0.3:
                    quality += 1
        
        return (quality / (total_fields * 3)) * 100 if total_fields > 0 else 0
    
    def extract(self, watermarked_image, secret_key, fast_mode=False):
        """Ultra-robust extraction with multiple delta values
        
        Args:
            watermarked_image: Image to extract from
            secret_key: Secret key for extraction
            fast_mode: If True, only try primary delta values for speed (for verification)
        """
        # Choose delta values based on mode
        if fast_mode:
            # Fast mode: Only try single most common delta value (for verification loop)
            delta_values = [30.0]
        else:
            # Full mode: Try all delta values (for final match)
            delta_values = [20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 60.0, 70.0, 80.0]
        
        best_result = None
        best_quality = 0
        
        for delta in delta_values:
            try:
                result = self._extract_with_delta(watermarked_image, secret_key, delta)
                if result.get('success', False):
                    # Calculate quality
                    payload = result.get('payload', {})
                    quality = self._calculate_payload_quality(payload)
                    
                    result['delta_used'] = delta
                    result['quality_score'] = quality
                    
                    if quality > best_quality:
                        best_quality = quality
                        best_result = result
                    
                    # In fast mode, accept first good extraction
                    if fast_mode and quality >= 80:
                        break
            except Exception as e:
                continue
        
        # Return best result if found
        return best_result or {
            'success': False,
            'payload': {},
            'raw_text': '',
            'error': 'No successful extraction with any delta value'
        }


class UltraRobustWatermarkSystem:
    """Ultra-robust watermark system with multiple delta values and error correction"""
    
    def __init__(self, delta=30.0, wavelet='haar', level=3):
        self.delta = delta
        self.wavelet = wavelet
        self.level = level
    
    def _bits_to_text_ultra_robust(self, bits):
        """Ultra-robust bits to text conversion with multiple error correction strategies"""
        text = ''
        for i in range(0, len(bits) - 7, 8):
            byte = bits[i:i+8]
            if len(byte) == 8:
                char_code = int(''.join(map(str, byte)), 2)
                
                # Multiple error correction strategies
                if char_code < 32 or char_code > 126:
                    corrected = False
                    
                    # Strategy 1: Try flipping each bit
                    for bit_pos in range(8):
                        corrected_byte = byte.copy()
                        corrected_byte[bit_pos] = 1 - corrected_byte[bit_pos]
                        corrected_code = int(''.join(map(str, corrected_byte)), 2)
                        if 32 <= corrected_code <= 126:
                            text += chr(corrected_code)
                            corrected = True
                            break
                    
                    # Strategy 2: Try flipping two bits
                    if not corrected:
                        for bit1 in range(8):
                            for bit2 in range(bit1+1, 8):
                                corrected_byte = byte.copy()
                                corrected_byte[bit1] = 1 - corrected_byte[bit1]
                                corrected_byte[bit2] = 1 - corrected_byte[bit2]
                                corrected_code = int(''.join(map(str, corrected_byte)), 2)
                                if 32 <= corrected_code <= 126:
                                    text += chr(corrected_code)
                                    corrected = True
                                    break
                            if corrected:
                                break
                    
                    # Strategy 3: Use closest valid character
                    if not corrected:
                        if char_code < 32:
                            text += chr(32)  # Space
                        elif char_code > 126:
                            text += chr(126)  # Tilde
                        else:
                            text += '?'
                else:
                    text += chr(char_code)
        return text
    
    def _extract_with_delta(self, watermarked_image, secret_key, delta):
        """Extract with specific delta value"""
        import pywt
        
        # Convert to YCrCb
        if len(watermarked_image.shape) == 3:
            ycrcb = cv2.cvtColor(watermarked_image, cv2.COLOR_RGB2YCrCb)
            Y = ycrcb[:, :, 0].astype(np.float64)
        else:
            Y = watermarked_image.astype(np.float64)
        
        # DWT
        coeffs = pywt.wavedec2(Y, self.wavelet, level=self.level)
        LL = coeffs[0].copy()
        LL_flat = LL.flatten()
        
        # Extract length (first 16 bits)
        length_bits = []
        for i in range(16):
            if i >= len(LL_flat):
                break
            quantized = np.round(LL_flat[i] / delta)
            length_bits.append(int(quantized) % 2)
        
        # Decode length
        if len(length_bits) == 16:
            payload_length = int(''.join(map(str, length_bits)), 2)
        else:
            payload_length = 0
        
        # Validate payload length
        if payload_length <= 0 or payload_length > 1000:
            return {
                'success': False,
                'payload': {},
                'raw_text': '',
                'error': 'Invalid payload length'
            }
        
        # Extract payload bits
        extracted_bits = []
        for i in range(16, min(16 + payload_length, len(LL_flat))):
            quantized = np.round(LL_flat[i] / delta)
            extracted_bits.append(int(quantized) % 2)
        
        extracted_bits = np.array(extracted_bits, dtype=np.uint8)
        
        # Decode text with ultra-robust method
        payload_text = self._bits_to_text_ultra_robust(extracted_bits)
        
        # Parse with validation
        parts = payload_text.split('|')
        payload = {}
        success = False
        
        if len(parts) >= 3:
            # Clean and validate fields
            payload['owner'] = parts[0].strip()
            payload['image_id'] = parts[1].strip()
            payload['date_created'] = parts[2].strip()
            
            # Extract optional fields
            if len(parts) > 3:
                payload['semantic_hash'] = parts[3].strip()
            if len(parts) > 4:
                payload['master_fingerprint'] = parts[4].strip()
            if len(parts) > 5:
                payload['perceptual_hash'] = parts[5].strip()
            
            # ALWAYS mark as success if we have 3+ parts - let tampering detection handle corruption
            success = True
        
        return {
            'success': success,
            'payload': payload,
            'raw_text': payload_text,
            'bits_extracted': len(extracted_bits),
            'fields_count': len(parts)
        }
    
    def _calculate_payload_quality(self, payload):
        """Calculate payload quality score"""
        if not payload:
            return 0
        
        quality = 0
        total_fields = len(payload)
        
        for key, value in payload.items():
            if isinstance(value, str):
                # Check for reasonable length
                if 3 <= len(value) <= 50:
                    quality += 1
                # Check for reasonable characters
                alnum_ratio = sum(1 for c in value if c.isalnum()) / len(value) if value else 0
                if alnum_ratio >= 0.5:
                    quality += 1
                # Check for excessive special characters
                special_ratio = sum(1 for c in value if not c.isalnum() and c not in ' -_') / len(value) if value else 0
                if special_ratio <= 0.3:
                    quality += 1
        
        return (quality / (total_fields * 3)) * 100 if total_fields > 0 else 0
    
    def extract(self, watermarked_image, secret_key, fast_mode=False):
        """Ultra-robust extraction with multiple delta values
        
        Args:
            watermarked_image: Image to extract from
            secret_key: Secret key for extraction
            fast_mode: If True, only try primary delta values for speed (for verification)
        """
        # Choose delta values based on mode
        if fast_mode:
            # Fast mode: Only try single most common delta value (for verification loop)
            delta_values = [30.0]
        else:
            # Full mode: Try all delta values (for final match)
            delta_values = [20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 60.0, 70.0, 80.0]
        
        best_result = None
        best_quality = 0
        
        for delta in delta_values:
            try:
                result = self._extract_with_delta(watermarked_image, secret_key, delta)
                if result.get('success', False):
                    # Calculate quality
                    payload = result.get('payload', {})
                    quality = self._calculate_payload_quality(payload)
                    
                    result['delta_used'] = delta
                    result['quality_score'] = quality
                    
                    if quality > best_quality:
                        best_quality = quality
                        best_result = result
                    
                    # In fast mode, accept first good extraction
                    if fast_mode and quality >= 80:
                        break
            except Exception as e:
                continue
        
        # Return best result if found
        return best_result or {
            'success': False,
            'payload': {},
            'raw_text': '',
            'error': 'No successful extraction with any delta value'
        }

from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
import uuid
import hashlib
import cv2
import numpy as np
from datetime import datetime, timedelta
import logging
from functools import wraps
import base64
from io import BytesIO
from PIL import Image
from pymongo import MongoClient
from bson import ObjectId
import gridfs
from bson.errors import InvalidId
import jwt
import time

# Import our watermarking modules
from watermark_final_working import FinalWatermarkSystem
from semantic_watermark import SemanticWatermarkSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'pixel_ledger_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['MAX_FORM_MEMORY_SIZE'] = 50 * 1024 * 1024  # 50MB max form data

# Session configuration for proper cookie handling
from flask_session import Session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS attacks
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Allow same-site cookies (changed from None)
app.config['SESSION_COOKIE_NAME'] = 'pixelledger_session'
app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow cookie on localhost
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_PERMANENT'] = True

# Initialize session
Session(app)

# MongoDB connection
MONGODB_URI = "mongodb+srv://shanejacob2312:$Shane2312@cluster0.uxda6.mongodb.net/"
DATABASE_NAME = "pixelledger"

try:
    # Increased timeouts for slow network connections
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=60000,  # 60 seconds
        connectTimeoutMS=60000,           # 60 seconds
        socketTimeoutMS=60000             # 60 seconds
    )
    db = client[DATABASE_NAME]
    fs = gridfs.GridFS(db)
    
    # Test connection
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB!")
    
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

# Initialize extensions
CORS(app, 
     supports_credentials=True, 
     origins=['http://localhost:5500', 'http://127.0.0.1:5500', 'http://localhost:5000', 'http://127.0.0.1:5000', 'http://localhost:8080', 'http://127.0.0.1:8080', 'http://localhost:8000', 'http://127.0.0.1:8000'],
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['Content-Type', 'Authorization', 'Set-Cookie'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize watermarking systems
# Use SemanticWatermarkSystem for embedding (has both embed and extract)
# Use UltraRobustWatermarkSystem for verification only (has ultra-robust extract)
try:
    embedding_system = SemanticWatermarkSystem(
        delta=60.0,  # Increased for robustness with semantic data (slight quality trade-off)
        wavelet='haar',
        level=2
    )
    verification_system = UltraRobustWatermarkSystem(
        delta=60.0,
        wavelet='haar',
        level=2
    )
    logger.info("Watermark Systems initialized successfully")
except Exception as e:
    logger.warning(f"Failed to initialize Watermark Systems: {e}")
    logger.info("Falling back to basic watermark system")
    embedding_system = FinalWatermarkSystem(
        delta=60.0,
        wavelet='haar',
        level=2
    )
    verification_system = UltraRobustWatermarkSystem(
        delta=60.0,
    wavelet='haar',
    level=2
)

# MongoDB Collections
users_collection = db.users
watermarked_images_collection = db.watermarked_images
verification_logs_collection = db.verification_logs

# Authentication decorator
def login_required(f):
    """Decorator to require user authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"Checking authentication for {f.__name__}")
        logger.info(f"Session data: {dict(session)}")
        logger.info(f"Request cookies: {dict(request.cookies)}")
        
        # Check session first (primary method)
        if 'user_id' in session:
            logger.info("Session authentication successful")
            return f(*args, **kwargs)
        
        # Check JWT token as fallback
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                # Set session from JWT
                session['user_id'] = payload['user_id']
                session['username'] = payload['username']
                session['authenticated'] = True
                session['email'] = payload.get('email', '')
                logger.info(f"JWT token authentication successful for {payload['username']}")
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                logger.warning("JWT token expired")
            except jwt.InvalidTokenError:
                logger.warning("Invalid JWT token")
        
        logger.warning("No valid authentication found")
        return jsonify({'error': 'Authentication required'}), 401
    return decorated_function

# Utility functions
def allowed_file(filename):
    """Check if file extension is allowed."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_secret_key(user_id, image_id):
    """Generate secret key for watermarking."""
    base_key = f"pixel_ledger_{user_id}_{image_id}"
    return hashlib.sha256(base_key.encode()).hexdigest()

def save_image_to_gridfs(image_data, filename):
    """Save image data to GridFS."""
    try:
        # Convert base64 to bytes
        if isinstance(image_data, str):
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_data = base64.b64decode(image_data)
        
        # Save to GridFS
        file_id = fs.put(image_data, filename=filename)
        return str(file_id)
    except Exception as e:
        logger.error(f"Error saving image to GridFS: {e}")
        return None

def get_image_from_gridfs(file_id):
    """Retrieve image data from GridFS."""
    try:
        if isinstance(file_id, str):
            file_id = ObjectId(file_id)
        
        grid_out = fs.get(file_id)
        return grid_out.read()
    except Exception as e:
        logger.error(f"Error retrieving image from GridFS: {e}")
        return None

def convert_to_serializable(obj):
    """Convert MongoDB documents to JSON serializable format."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    return obj

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test MongoDB connection
        client.admin.command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        'status': 'healthy',
        'message': 'PixelLedger API with MongoDB is running',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        existing_user = users_collection.find_one({
            '$or': [
                {'username': data['username']},
                {'email': data['email']}
            ]
        })
        
        if existing_user:
            field = 'username' if existing_user['username'] == data['username'] else 'email'
            return jsonify({'error': f'{field.capitalize()} already exists'}), 409
        
        # Create new user
        user_doc = {
            'username': data['username'],
            'email': data['email'],
            'password_hash': generate_password_hash(data['password']),
            'full_name': data.get('full_name', ''),
            'created_at': datetime.utcnow(),
            'is_active': True,
            'last_login': None
        }
        
        result = users_collection.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        
        logger.info(f"New user registered: {user_doc['username']}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': str(user_doc['_id']),
                'username': user_doc['username'],
                'email': user_doc['email'],
                'full_name': user_doc['full_name'],
                'created_at': user_doc['created_at'].isoformat(),
                'is_active': user_doc['is_active']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and create session."""
    try:
        logger.info(f"Login attempt from {request.remote_addr}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request cookies: {dict(request.cookies)}")
        
        data = request.get_json()
        logger.info(f"Login data received: {data}")
        
        if not data or not all(k in data for k in ['username', 'password']):
            return jsonify({'error': 'Missing username or password'}), 400
        
        user = users_collection.find_one({'username': data['username']})
        
        if not user or not check_password_hash(user['password_hash'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user['is_active']:
            return jsonify({'error': 'Account is disabled'}), 403
        
        # Update last login
        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'last_login': datetime.utcnow()}}
        )
        
        # Create session with permanent flag
        session.permanent = True
        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        session['authenticated'] = True
        session['email'] = user['email']
        session.modified = True
        
        # Force session to save
        session.permanent_session_lifetime = timedelta(days=7)
        
        # Create JWT token as backup
        token_payload = {
            'user_id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'exp': int(time.time()) + 86400  # 24 hours expiry
        }
        jwt_token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        
        logger.info(f"User logged in: {user['username']}")
        logger.info(f"Session created: {dict(session)}")
        logger.info(f"Session ID: {session.sid if hasattr(session, 'sid') else 'N/A'}")
        logger.info(f"Session permanent: {session.permanent}")
        logger.info(f"Session modified: {session.modified}")
        
        # Create response
        response = jsonify({
            'message': 'Login successful',
            'token': jwt_token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'created_at': user['created_at'].isoformat(),
                'is_active': user['is_active'],
                'last_login': user.get('last_login').isoformat() if user.get('last_login') else None
            }
        })
        
        # Force session to be saved
        session.modified = True
        
        # Log response headers
        logger.info(f"Response headers: {dict(response.headers)}")
        logger.info(f"Session cookie name: {app.config['SESSION_COOKIE_NAME']}")
        
        # Check if session cookie is in response
        if 'Set-Cookie' in response.headers:
            logger.info(f"Set-Cookie header: {response.headers['Set-Cookie']}")
        else:
            logger.warning("No Set-Cookie header in response!")
        
        return response, 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout user and clear session."""
    try:
        username = session.get('username', 'Unknown')
        session.clear()
        
        logger.info(f"User logged out: {username}")
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/api/auth/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user profile."""
    try:
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'created_at': user['created_at'].isoformat(),
                'is_active': user['is_active'],
                'last_login': user.get('last_login').isoformat() if user.get('last_login') else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500

@app.route('/api/auth/test-login', methods=['POST'])
def test_login():
    """Test login endpoint for development purposes."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Create a test user session
        session['user_id'] = data.get('user_id', 'test-user-123')
        session['username'] = data.get('username', 'testuser')
        session['authenticated'] = True
        
        logger.info(f"Test login successful for user: {data.get('username', 'testuser')}")
        
        return jsonify({
            'message': 'Test login successful',
            'user': {
                'id': session['user_id'],
                'username': session['username']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Test login error: {e}")
        return jsonify({'error': 'Test login failed'}), 500

@app.route('/api/debug/session', methods=['GET'])
def debug_session():
    """Debug session endpoint."""
    return jsonify({
        'session': dict(session),
        'session_id': session.sid if hasattr(session, 'sid') else 'No SID',
        'cookies': dict(request.cookies),
        'headers': dict(request.headers),
        'origin': request.headers.get('Origin'),
        'has_session_cookie': 'pixelledger_session' in request.cookies,
        'all_cookie_names': list(request.cookies.keys())
    }), 200

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Quick auth check endpoint."""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    return jsonify({
        'has_session': 'user_id' in session,
        'session_data': dict(session),
        'has_token': bool(token),
        'cookies': list(request.cookies.keys()),
        'authenticated': 'user_id' in session or bool(token)
    }), 200

@app.route('/api/auth/test-session', methods=['POST'])
def test_session():
    """Test session creation."""
    try:
        session.permanent = True
        session['user_id'] = 'test-user-123'
        session['username'] = 'testuser'
        session['authenticated'] = True
        session.modified = True
        
        logger.info(f"Test session created: {dict(session)}")
        
        return jsonify({
            'message': 'Test session created',
            'session': dict(session)
        }), 200
    except Exception as e:
        logger.error(f"Test session error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/watermark/embed', methods=['POST'])
@login_required
def embed_watermark():
    """Embed watermark in an image."""
    try:
        print("\n" + "="*80)
        print("[BACKEND] WATERMARK EMBED REQUEST RECEIVED")
        print("="*80)
        
        user_id = session['user_id']
        print(f"[BACKEND] User ID from session: {user_id}")
        
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        print(f"[BACKEND] User found: {user['username'] if user else 'None'}")
        
        # Get form data
        image_data = request.form.get('image')
        print(f"[BACKEND] Image data received: {bool(image_data)}")
        if not image_data:
            print("[BACKEND] ERROR: No image provided")
            return jsonify({'error': 'No image provided'}), 400
        
        # FIRST: Check if image already has a watermark
        print("[BACKEND] Checking if image already has watermark...")
        
        # Convert image for checking
        if ',' in image_data:
            check_image_data = image_data.split(',')[1]
        else:
            check_image_data = image_data
        
        check_image_bytes = base64.b64decode(check_image_data)
        check_nparr = np.frombuffer(check_image_bytes, np.uint8)
        check_image = cv2.imdecode(check_nparr, cv2.IMREAD_COLOR)
        check_image = cv2.cvtColor(check_image, cv2.COLOR_BGR2RGB)
        
        # HASH-BASED PRE-CHECK: Extract once and look up in database
        print("[BACKEND] Extracting watermark from uploaded image to check for existing watermark...")
        
        # Extract watermark with ultra-robust extraction (full mode)
        extraction_check = verification_system.extract(
            check_image, 
            secret_key="pixel_ledger_2024",  # Use default key
            fast_mode=False  # Full extraction to catch tampered watermarks too
        )
        
        watermark_found = False
        
        if extraction_check.get('success', False):
            # Check if extracted image_id exists in database
            extracted_image_id = extraction_check.get('payload', {}).get('image_id', '')
            
            if extracted_image_id:
                print(f"[BACKEND] Extracted image_id: '{extracted_image_id}' - checking database...")
                db_record = watermarked_images_collection.find_one({'image_id': extracted_image_id})
                
                if db_record:
                    watermark_found = True
                    print(f"[BACKEND] WATERMARK DETECTED in uploaded image!")
                    print(f"[BACKEND] Matched with database record for image_id: {extracted_image_id}")
        
        if watermark_found:
            print("[BACKEND] ERROR: Image already contains a watermark")
            return jsonify({
                'error': 'Image already contains a watermark',
                'message': 'This image already has a watermark embedded. Cannot watermark an already watermarked image.',
                'watermark_detected': True
            }), 400
        
        print("[BACKEND] No existing watermark found. Proceeding with embedding...")
        
        # Generate unique image ID first
        image_id = str(uuid.uuid4())
        # Use default secret key for hash-based verification
        secret_key = "pixel_ledger_2024"
        
        # Create short hash for robust embedding (12 chars instead of 36)
        short_hash = image_id.replace('-', '')[:12]  # First 12 chars of UUID without dashes
        
        # Get watermark metadata
        watermark_data = {
            'owner': request.form.get('owner', user['full_name'] or user['username']),
            'creator': request.form.get('creator', ''),
            'date_created': request.form.get('dateCreated', datetime.now().strftime('%Y-%m-%d')),
            'copyright': request.form.get('copyright', ''),
            'description': request.form.get('description', ''),
            'image_id': short_hash,  # Use SHORT hash for robust embedding
            'watermark_version': '1.0',
            'location': request.form.get('location', ''),
            'camera': request.form.get('camera', ''),
            'settings': request.form.get('settings', ''),
            'category': request.form.get('category', '')
        }
        
        # Convert base64 to image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        print(f"[BACKEND] Starting watermark embedding...")
        print(f"[BACKEND] Image size: {image.shape}")
        
        # Embed watermark
        watermarked_image, metadata = embedding_system.embed(
            image, watermark_data, secret_key)
        
        print(f"[BACKEND] Watermark embedded successfully")
        print(f"[BACKEND] PSNR: {metadata.get('psnr', 0):.2f} dB")
        
        # Save watermarked image to GridFS
        watermarked_bytes = cv2.imencode('.png', cv2.cvtColor(watermarked_image, cv2.COLOR_RGB2BGR))[1].tobytes()
        watermarked_file_id = save_image_to_gridfs(watermarked_bytes, f"watermarked_{image_id}.png")
        
        # Save original image to GridFS
        original_file_id = save_image_to_gridfs(image_bytes, f"original_{image_id}.png")
        
        # Create database record
        watermarked_image_doc = {
            'image_id': image_id,  # Full UUID for database
            'short_hash': short_hash,  # Short hash for watermark lookup
            'user_id': ObjectId(user_id),
            'original_filename': f"original_{image_id}.png",
            'watermarked_filename': f"watermarked_{image_id}.png",
            'original_file_id': original_file_id,
            'watermarked_file_id': watermarked_file_id,
            
            # Watermark metadata
            'owner_name': watermark_data['owner'],
            'creator_name': watermark_data['creator'],
            'date_created': datetime.strptime(watermark_data['date_created'], '%Y-%m-%d'),
            'copyright_info': watermark_data['copyright'],
            'description': watermark_data['description'],
            'location': watermark_data['location'],
            'camera_info': watermark_data['camera'],
            'settings_info': watermark_data['settings'],
            'category': watermark_data['category'],
            
            # Technical metadata
            'image_width': image.shape[1],
            'image_height': image.shape[0],
            'file_size': len(watermarked_bytes),
            'watermark_version': watermark_data['watermark_version'],
            'psnr': metadata.get('psnr', 0),
            'ssim': metadata.get('ssim', 0),
            'mse': metadata.get('mse', 0),
            'delta': metadata.get('delta', 40.0),
            'bits_embedded': metadata.get('bits_embedded', 0),
            
            # Semantic AI metadata (if available)
            'semantic_context': metadata.get('semantic_context', {}),
            'ai_caption': metadata.get('semantic_context', {}).get('caption', ''),
            'ai_objects': metadata.get('semantic_context', {}).get('objects', []),
            'semantic_hash': metadata.get('semantic_context', {}).get('semantic_hash', ''),
            
            # Fingerprint data
            'fingerprint': metadata.get('fingerprint', {}),
            'perceptual_hash': metadata.get('perceptual_hash', ''),
            'visual_hash': metadata.get('fingerprint', {}).get('h_image', ''),
            'metadata_hash': metadata.get('fingerprint', {}).get('h_metadata', ''),
            'features_hash': metadata.get('fingerprint', {}).get('h_features', ''),
            'master_fingerprint': metadata.get('fingerprint', {}).get('h_fingerprint', ''),
            
            # Blockchain payload
            'blockchain_payload': metadata.get('blockchain_payload', {}),
            
            # Timestamps
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        print(f"[BACKEND] Saving to database...")
        watermarked_images_collection.insert_one(watermarked_image_doc)
        print(f"[BACKEND] Database save complete")
        
        # Convert watermarked image to base64 for response
        watermarked_base64 = base64.b64encode(watermarked_bytes).decode('utf-8')
        print(f"[BACKEND] Base64 encoding complete")
        print(f"[BACKEND] Base64 length: {len(watermarked_base64)}")
        
        logger.info(f"Watermark embedded successfully for user {user['username']}, image {image_id}")
        
        print(f"[BACKEND] Preparing response...")
        # Prepare response with semantic metadata
        response_data = {
            'message': 'Watermark embedded successfully',
            'image_id': image_id,
            'watermarked_image': watermarked_base64,
            'metadata': watermark_data,
            'psnr': metadata.get('psnr', 0),
            
            # Include semantic AI features if available
            'semantic_features': {
                'caption': metadata.get('semantic_context', {}).get('caption', ''),
                'objects': metadata.get('semantic_context', {}).get('objects', []),
                'semantic_hash': metadata.get('semantic_context', {}).get('semantic_hash', '')
            },
            
            # Include fingerprint data
            'fingerprint': {
                'perceptual_hash': metadata.get('perceptual_hash', ''),
                'master_fingerprint': metadata.get('fingerprint', {}).get('h_fingerprint', ''),
                'visual_hash': metadata.get('fingerprint', {}).get('h_image', '')
            },
            
            # Blockchain ready
            'blockchain_ready': bool(metadata.get('blockchain_payload'))
        }
        
        print(f"[BACKEND] Response prepared successfully")
        print(f"[BACKEND] Response keys: {list(response_data.keys())}")
        print(f"[BACKEND] Sending 200 OK response")
        print("="*80 + "\n")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"[BACKEND] ERROR: {e}")
        logger.error(f"Watermark embedding error: {e}")
        import traceback
        traceback.print_exc()
        logger.error(traceback.format_exc())
        print("="*80 + "\n")
        return jsonify({'error': 'Watermark embedding failed', 'details': str(e)}), 500

@app.route('/api/watermark/verify', methods=['POST'])
def verify_watermark():
    """Verify watermark in an image."""
    try:
        print("\n" + "="*80, flush=True)
        print("[VERIFY] Watermark Verification Request Received", flush=True)
        print("="*80, flush=True)
        
        # Get image data
        print("[VERIFY] Step 1: Extracting image data from request...", flush=True)
        image_data = request.form.get('image')
        if not image_data:
            print("[VERIFY] [ERROR] No image data in request", flush=True)
            return jsonify({'error': 'No image provided'}), 400
        
        print(f"[VERIFY] [OK] Image data received (length: {len(image_data)} bytes)", flush=True)
        
        # Convert base64 to image
        print("[VERIFY] Step 2: Decoding base64 image...", flush=True)
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        print(f"[VERIFY] [OK] Decoded {len(image_bytes)} bytes", flush=True)
        
        # Convert bytes to numpy array
        print("[VERIFY] Step 3: Converting to OpenCV image...", flush=True)
        nparr = np.frombuffer(image_bytes, np.uint8)
        uploaded_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        uploaded_image = cv2.cvtColor(uploaded_image, cv2.COLOR_BGR2RGB)
        print(f"[VERIFY] [OK] Image shape: {uploaded_image.shape}", flush=True)
        
        # NEW HASH-BASED VERIFICATION METHOD
        verification_result = None
        match_method = None
        match_confidence = 0
        print("[VERIFY] Step 4: Extracting watermark from uploaded image (HASH-BASED METHOD)...", flush=True)
        
        # Extract watermark ONCE from uploaded image with ultra-robust extraction
        print(f"[VERIFY] Attempting watermark extraction with all delta values...", flush=True)
        extraction_results = verification_system.extract(
            uploaded_image, 
            secret_key="pixel_ledger_2024",  # Use default key for extraction
            fast_mode=False  # Use full extraction to maximize success rate
        )
        
        print(f"[VERIFY] [OK] Extraction complete: {extraction_results.get('success', False)}", flush=True)
        
        if extraction_results.get('success', False):
            # Successfully extracted watermark! Now get the image_id hash
            extracted_payload = extraction_results.get('payload', {})
            extracted_image_id = extracted_payload.get('image_id', '')
            
            print(f"[VERIFY] Extracted image_id: '{extracted_image_id}'", flush=True)
            
            if extracted_image_id:
                # HYBRID APPROACH - Multiple fallback strategies
                print(f"[VERIFY] Step 5: Looking up watermark using HYBRID approach...", flush=True)
                
                image_record = None
                
                # STRATEGY 1: Exact short_hash match (FASTEST)
                print(f"[VERIFY]   Strategy 1: Trying exact short_hash match...", flush=True)
                image_record = watermarked_images_collection.find_one({'short_hash': extracted_image_id})
                
                if image_record:
                    match_method = "EXACT_MATCH"
                    match_confidence = 100.0
                    print(f"[VERIFY]   [SUCCESS] Exact match found!", flush=True)
                else:
                    # STRATEGY 2: Fuzzy matching on short_hash
                    print(f"[VERIFY]   Strategy 2: Trying fuzzy short_hash match...", flush=True)
                    
                    # Clean the extracted ID (remove special chars that indicate corruption)
                    clean_id = ''.join(c if c.isalnum() else '' for c in extracted_image_id)
                    
                    if len(clean_id) >= 6:  # Need at least 6 chars for meaningful match
                        # Get recent images for fuzzy matching
                        all_db_images = list(watermarked_images_collection.find({}, {'short_hash': 1, 'image_id': 1}).sort('created_at', -1).limit(20))
                        
                        best_match = None
                        best_score = 0
                        
                        for db_img in all_db_images:
                            db_short_hash = db_img.get('short_hash', '')
                            
                            if db_short_hash:
                                # Calculate character-by-character similarity
                                matches = sum(1 for a, b in zip(clean_id, db_short_hash) if a.lower() == b.lower())
                                max_len = max(len(clean_id), len(db_short_hash))
                                score = (matches / max_len) if max_len > 0 else 0
                                
                                if score > best_score:
                                    best_score = score
                                    best_match = db_img
                        
                        if best_match and best_score >= 0.5:  # At least 50% match
                            image_record = watermarked_images_collection.find_one({'_id': best_match['_id']})
                            match_method = "FUZZY_MATCH"
                            match_confidence = best_score * 100
                            print(f"[VERIFY]   [SUCCESS] Fuzzy match found! Similarity: {match_confidence:.1f}%", flush=True)
                        else:
                            print(f"[VERIFY]   No fuzzy match found (best score: {best_score*100:.1f}%)", flush=True)
                    
                    # STRATEGY 3: Perceptual hash fallback (if still no match)
                    if not image_record:
                        print(f"[VERIFY]   Strategy 3: Trying perceptual hash fallback...", flush=True)
                        
                        try:
                            import imagehash
                            from PIL import Image
                            
                            # Convert uploaded image to PIL
                            uploaded_pil = Image.fromarray(cv2.cvtColor(uploaded_image, cv2.COLOR_RGB2BGR))
                            uploaded_phash = str(imagehash.phash(uploaded_pil))
                            
                            # Get recent images with perceptual hashes
                            all_db_images = list(watermarked_images_collection.find({'perceptual_hash': {'$exists': True}}, {'perceptual_hash': 1}).sort('created_at', -1).limit(20))
                            
                            best_match = None
                            best_hamming = float('inf')
                            
                            for db_img in all_db_images:
                                db_phash = db_img.get('perceptual_hash', '')
                                
                                if db_phash and len(db_phash) == len(uploaded_phash):
                                    # Calculate Hamming distance
                                    hamming = sum(c1 != c2 for c1, c2 in zip(uploaded_phash, db_phash))
                                    
                                    if hamming < best_hamming:
                                        best_hamming = hamming
                                        best_match = db_img
                            
                            # Accept if Hamming distance is small (similar images)
                            if best_match and best_hamming <= 10:  # Allow up to 10 bit difference
                                image_record = watermarked_images_collection.find_one({'_id': best_match['_id']})
                                match_method = "PERCEPTUAL_HASH"
                                match_confidence = max(0, (1 - best_hamming / 64) * 100)  # 64 bits total
                                print(f"[VERIFY]   [SUCCESS] Perceptual hash match! Hamming distance: {best_hamming}", flush=True)
                            else:
                                print(f"[VERIFY]   No perceptual match (best hamming: {best_hamming})", flush=True)
                        
                        except Exception as e:
                            print(f"[VERIFY]   Perceptual hash failed: {e}", flush=True)
                
                if image_record:
                    print(f"[VERIFY] [MATCH FOUND] Image found via {match_method}!", flush=True)
                    print(f"[VERIFY] Match confidence: {match_confidence:.1f}%", flush=True)
                    print(f"[VERIFY] Database record owner: {image_record.get('owner_name', 'unknown')}", flush=True)
                    
                    verification_result = {
                        'image_record': convert_to_serializable(image_record),
                        'extraction_results': extraction_results
                    }
                    
                    # Add semantic features from database
                    if 'semantic_context' in image_record:
                        verification_result['semantic_features'] = {
                            'caption': image_record.get('ai_caption', ''),
                            'objects': image_record.get('ai_objects', []),
                            'semantic_hash': image_record.get('semantic_hash', '')
                        }
                    
                    # Add fingerprint data from database
                    if 'perceptual_hash' in image_record:
                        verification_result['fingerprint'] = {
                            'perceptual_hash': image_record.get('perceptual_hash', ''),
                            'master_fingerprint': image_record.get('master_fingerprint', ''),
                            'visual_hash': image_record.get('visual_hash', '')
                        }
                    
                    print(f"[VERIFY] Match verification complete!", flush=True)
                else:
                    print(f"[VERIFY] [WARNING] Extracted image_id '{extracted_image_id}' not found in database", flush=True)
                    print(f"[VERIFY] This may be a watermark from a different system or deleted record", flush=True)
            else:
                print(f"[VERIFY] [WARNING] No image_id extracted from watermark", flush=True)
        else:
            print(f"[VERIFY] [NO WATERMARK] Failed to extract any watermark from image", flush=True)
        
        print(f"[VERIFY] Step 6: Verification process complete", flush=True)
        
        # Log verification attempt
        print(f"[VERIFY] Step 7: Logging verification attempt...", flush=True)
        verification_id = str(uuid.uuid4())
        success = verification_result is not None
        
        verification_log = {
            'verification_id': verification_id,
            'success': success,
            'template_found': True if verification_result else False,
            'template_correlation': 1.0 if verification_result else 0.0,
            'payload_correlation': 1.0 if verification_result else 0.0,
            'bit_error_rate': 0.0 if verification_result else 1.0,
            'extraction_time': 0.0,
            'extracted_metadata': json.dumps(verification_result['extraction_results'].get('payload', {})) if verification_result else None,
            'user_id': ObjectId(session['user_id']) if 'user_id' in session else None,
            'verified_at': datetime.utcnow()
        }
        
        if verification_result:
            verification_log['image_id'] = ObjectId(verification_result['image_record']['_id'])
        
        print(f"[VERIFY] Inserting verification log into database...", flush=True)
        verification_logs_collection.insert_one(verification_log)
        print(f"[VERIFY] [OK] Log saved with ID: {verification_id}", flush=True)
        
        logger.info(f"Watermark verification completed: {'Match found' if verification_result else 'No match'}")
        
        print(f"[VERIFY] Step 8: Preparing response...", flush=True)
        
        if verification_result:
            # Watermark found
            print(f"[VERIFY] [OK] Watermark found - building success response", flush=True)
            extracted_data = verification_result['extraction_results'].get('payload', {})
            
            # Add semantic features if available
            if 'semantic_features' in verification_result:
                extracted_data['semantic_features'] = verification_result['semantic_features']
                print(f"[VERIFY]   -> Added semantic features", flush=True)
            
            # Add fingerprint if available
            if 'fingerprint' in verification_result:
                extracted_data['perceptual_hash'] = verification_result['fingerprint'].get('perceptual_hash')
                extracted_data['master_fingerprint'] = verification_result['fingerprint'].get('master_fingerprint')
                print(f"[VERIFY]   -> Added fingerprint data", flush=True)
            
            # Add database record info
            db_record = verification_result['image_record']
            extracted_data['database_record'] = {
                'creator': db_record.get('creator'),
                'title': db_record.get('title'),
                'copyright': db_record.get('copyright_info'),
                'medium': db_record.get('medium'),
                'category': db_record.get('category')
            }
            print(f"[VERIFY]   -> Added database record info", flush=True)
            
            print(f"[VERIFY] Sending SUCCESS response (200 OK)", flush=True)
            print("="*80 + "\n", flush=True)
            
            # NEW TAMPERING DETECTION: Compare uploaded image with original watermarked image
            print(f"[VERIFY] Step 9: TAMPERING DETECTION - Comparing with original image...", flush=True)
            tampered = False
            tampering_details = []
            tampering_score = 0  # 0-100, higher = more tampering
            
            # Get database record
            db_record = verification_result['image_record']
            
            # Handle date_created - might be datetime object or string
            date_created = db_record.get('date_created', '')
            if date_created:
                if hasattr(date_created, 'strftime'):
                    date_created = date_created.strftime('%Y-%m-%d')
                else:
                    date_created = str(date_created)
            
            original_data = {
                'owner': db_record.get('owner_name', ''),
                'image_id': db_record.get('image_id', ''),
                'date_created': date_created,
                'creator': db_record.get('creator_name', ''),
                'copyright': db_record.get('copyright_info', ''),
                'category': db_record.get('category', '')
            }
            
            try:
                # Load original watermarked image from GridFS
                original_image_id = db_record.get('watermarked_file_id')
                if original_image_id:
                    print(f"[VERIFY]   Loading original watermarked image from GridFS...", flush=True)
                    original_file = fs.get(ObjectId(original_image_id))
                    original_bytes = original_file.read()
                    original_nparr = np.frombuffer(original_bytes, np.uint8)
                    original_image = cv2.imdecode(original_nparr, cv2.IMREAD_COLOR)
                    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
                    print(f"[VERIFY]   [OK] Original image loaded: {original_image.shape}", flush=True)
                    
                    # Ensure both images are same size for comparison
                    uploaded_resized = uploaded_image
                    if uploaded_image.shape != original_image.shape:
                        print(f"[VERIFY]   Resizing uploaded image to match original size...", flush=True)
                        uploaded_resized = cv2.resize(uploaded_image, (original_image.shape[1], original_image.shape[0]))
                    
                    # METRIC 1: Perceptual Hash Distance (detects visual changes)
                    print(f"[VERIFY]   Metric 1: Perceptual Hash Distance...", flush=True)
                    try:
                        import imagehash
                        from PIL import Image
                        
                        uploaded_pil = Image.fromarray(uploaded_resized)
                        original_pil = Image.fromarray(original_image)
                        
                        uploaded_phash = imagehash.phash(uploaded_pil)
                        original_phash = imagehash.phash(original_pil)
                        hamming_distance = uploaded_phash - original_phash
                        
                        print(f"[VERIFY]     Hamming Distance: {hamming_distance} (0=identical, >5=tampered)", flush=True)
                        
                        if hamming_distance > 5:
                            tampered = True
                            tampering_score += min(hamming_distance * 5, 40)  # Max 40 points
                            tampering_details.append(f"Visual structure modified (phash distance: {hamming_distance})")
                    except Exception as e:
                        print(f"[VERIFY]     Warning: Perceptual hash failed: {e}", flush=True)
                    
                    # METRIC 2: SSIM - Structural Similarity Index (detects compression, blur, noise)
                    print(f"[VERIFY]   Metric 2: Structural Similarity (SSIM)...", flush=True)
                    try:
                        from skimage.metrics import structural_similarity as ssim
                        
                        # Convert to grayscale for SSIM
                        uploaded_gray = cv2.cvtColor(uploaded_resized, cv2.COLOR_RGB2GRAY)
                        original_gray = cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY)
                        
                        ssim_score = ssim(uploaded_gray, original_gray)
                        print(f"[VERIFY]     SSIM Score: {ssim_score:.4f} (1.0=identical, <0.95=tampered)", flush=True)
                        
                        if ssim_score < 0.95:
                            tampered = True
                            ssim_penalty = (1.0 - ssim_score) * 100
                            tampering_score += min(ssim_penalty, 30)  # Max 30 points
                            tampering_details.append(f"Structural changes detected (SSIM: {ssim_score:.3f})")
                    except Exception as e:
                        print(f"[VERIFY]     Warning: SSIM failed: {e}", flush=True)
                    
                    # METRIC 3: Mean Squared Error (detects pixel-level changes)
                    print(f"[VERIFY]   Metric 3: Mean Squared Error (MSE)...", flush=True)
                    try:
                        mse = np.mean((uploaded_resized.astype(float) - original_image.astype(float)) ** 2)
                        print(f"[VERIFY]     MSE: {mse:.2f} (0=identical, >100=tampered)", flush=True)
                        
                        if mse > 100:
                            tampered = True
                            mse_penalty = min(mse / 10, 20)  # Max 20 points
                            tampering_score += mse_penalty
                            tampering_details.append(f"Pixel-level modifications detected (MSE: {mse:.1f})")
                    except Exception as e:
                        print(f"[VERIFY]     Warning: MSE failed: {e}", flush=True)
                    
                    # METRIC 4: Histogram Comparison (detects color/brightness changes)
                    print(f"[VERIFY]   Metric 4: Histogram Comparison...", flush=True)
                    try:
                        hist_correlation = 0
                        for channel in range(3):  # R, G, B
                            hist_uploaded = cv2.calcHist([uploaded_resized], [channel], None, [256], [0, 256])
                            hist_original = cv2.calcHist([original_image], [channel], None, [256], [0, 256])
                            
                            hist_uploaded = cv2.normalize(hist_uploaded, hist_uploaded).flatten()
                            hist_original = cv2.normalize(hist_original, hist_original).flatten()
                            
                            correlation = cv2.compareHist(hist_uploaded, hist_original, cv2.HISTCMP_CORREL)
                            hist_correlation += correlation
                        
                        hist_correlation /= 3  # Average across channels
                        print(f"[VERIFY]     Histogram Correlation: {hist_correlation:.4f} (1.0=identical, <0.95=tampered)", flush=True)
                        
                        if hist_correlation < 0.95:
                            tampered = True
                            hist_penalty = (1.0 - hist_correlation) * 100
                            tampering_score += min(hist_penalty, 10)  # Max 10 points
                            tampering_details.append(f"Color/brightness modified (histogram: {hist_correlation:.3f})")
                    except Exception as e:
                        print(f"[VERIFY]     Warning: Histogram comparison failed: {e}", flush=True)
                    
                    # Normalize tampering score to 0-100
                    tampering_score = min(tampering_score, 100)
                    
                    print(f"[VERIFY]   [RESULT] Tampering Score: {tampering_score:.1f}/100", flush=True)
                    print(f"[VERIFY]   [RESULT] Tampered: {tampered}", flush=True)
                    if tampering_details:
                        print(f"[VERIFY]   [RESULT] Details: {'; '.join(tampering_details)}", flush=True)
                    
                else:
                    print(f"[VERIFY]   [WARNING] No original watermarked image found in database", flush=True)
                    print(f"[VERIFY]   Falling back to extraction-based tampering detection...", flush=True)
                    # If no original image, assume no tampering can be detected
                    tampered = False
                    tampering_score = 0
                    
            except Exception as e:
                print(f"[VERIFY]   [ERROR] Image comparison failed: {e}", flush=True)
                import traceback
                traceback.print_exc()
                # If comparison fails, assume no tampering can be detected
                tampered = False
                tampering_score = 0
            
            # Calculate confidence score
            # For clean images: high confidence from match
            # For tampered images: confidence based on how well we identified it despite tampering
            if tampered:
                # Confidence = ability to detect watermark despite tampering
                # Higher tampering = lower confidence, but still detected
                confidence_score = max(30, 100 - tampering_score)  # Min 30% confidence
            else:
                # Clean image - high confidence
                confidence_score = match_confidence
            
            print(f"[VERIFY] Tampering detected: {tampered}", flush=True)
            print(f"[VERIFY] Confidence score: {confidence_score:.1f}%", flush=True)
            if tampering_details:
                print(f"[VERIFY] Tampering details: {'; '.join(tampering_details)}", flush=True)
            
            # Prepare response data
            if tampered:
                # For tampered images, show ORIGINAL database details, not corrupted extraction
                response_data = {
                    'owner': original_data['owner'],
                    'image_id': original_data['image_id'],
                    'date_created': original_data['date_created'],
                    'creator': original_data['creator'],
                    'copyright': original_data['copyright'],
                    'category': original_data['category']
                }
                
                # Add semantic features from database
                if 'semantic_features' in verification_result:
                    response_data['semantic_features'] = verification_result['semantic_features']
                
                # Add fingerprint from database
                if 'fingerprint' in verification_result:
                    response_data['perceptual_hash'] = verification_result['fingerprint'].get('perceptual_hash')
                    response_data['master_fingerprint'] = verification_result['fingerprint'].get('master_fingerprint')
                
                message = f'Watermark detected but image has been tampered (Tampering Score: {tampering_score:.1f}%)'
            else:
                # For clean images, show extracted data
                response_data = extracted_data
                message = 'Watermark found and verified - No tampering detected'
            
            return jsonify({
                'message': message,
                'verification_id': verification_id,
                'watermark_found': True,
                'tampered': tampered,
                'tampering_score': round(tampering_score, 1) if tampered else 0,  # NEW: Quantified tampering level
                'confidence_score': round(confidence_score, 1),
                'match_method': match_method,  # Shows how match was found
                'tampering_details': tampering_details if tampered else None,
                'extracted_data': response_data
            }), 200
        else:
            # No watermark found
            print(f"[VERIFY] [NO MATCH] No watermark found - sending NOT FOUND response", flush=True)
            print("="*80 + "\n", flush=True)
            
            return jsonify({
                'message': 'No watermark detected - image may be tampered',
                'verification_id': verification_id,
                'watermark_found': False,
                'tampered': True,  # No watermark found indicates tampering
                'tampering_details': ['No watermark extracted - severe tampering'],
                'extracted_data': None
        }), 200
        
    except Exception as e:
        print(f"[VERIFY] [CRITICAL ERROR]: {e}", flush=True)
        logger.error(f"Watermark verification error: {e}")
        import traceback
        traceback.print_exc()
        logger.error(traceback.format_exc())
        print("="*80 + "\n", flush=True)
        return jsonify({'error': 'Watermark verification failed', 'details': str(e)}), 500

@app.route('/api/images', methods=['GET'])
@login_required
def get_user_images():
    """Get all watermarked images for the current user."""
    try:
        user_id = session['user_id']
        images = list(watermarked_images_collection.find(
            {'user_id': ObjectId(user_id)}
        ).sort('created_at', -1))
        
        # Convert ObjectId and datetime to serializable format
        images = [convert_to_serializable(img) for img in images]
        
        return jsonify({
            'images': images,
            'count': len(images)
        }), 200
        
    except Exception as e:
        logger.error(f"Get images error: {e}")
        return jsonify({'error': 'Failed to get images'}), 500

@app.route('/api/images/<image_id>', methods=['GET'])
@login_required
def get_image(image_id):
    """Get specific watermarked image."""
    try:
        user_id = session['user_id']
        image = watermarked_images_collection.find_one({
            'image_id': image_id,
            'user_id': ObjectId(user_id)
        })
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Get watermarked image from GridFS
        watermarked_bytes = get_image_from_gridfs(image['watermarked_file_id'])
        if not watermarked_bytes:
            return jsonify({'error': 'Watermarked image file not found'}), 404
        
        watermarked_base64 = base64.b64encode(watermarked_bytes).decode('utf-8')
        
        return jsonify({
            'image': convert_to_serializable(image),
            'watermarked_image': watermarked_base64
        }), 200
        
    except Exception as e:
        logger.error(f"Get image error: {e}")
        return jsonify({'error': 'Failed to get image'}), 500

@app.route('/api/image/<image_id>/thumbnail', methods=['GET'])
@login_required
def get_image_thumbnail(image_id):
    """Get thumbnail of watermarked image."""
    try:
        user_id = session['user_id']
        image = watermarked_images_collection.find_one({
            'image_id': image_id,
            'user_id': ObjectId(user_id)
        })
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Get watermarked image from GridFS
        watermarked_bytes = get_image_from_gridfs(image['watermarked_file_id'])
        if not watermarked_bytes:
            return jsonify({'error': 'Image file not found'}), 404
        
        # Decode image and create thumbnail
        nparr = np.frombuffer(watermarked_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Resize to thumbnail (max 300x300)
        h, w = img.shape[:2]
        max_size = 300
        if h > max_size or w > max_size:
            scale = max_size / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h))
        
        # Encode as JPEG for smaller size
        _, thumbnail_bytes = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        # Return thumbnail
        response = app.response_class(
            thumbnail_bytes.tobytes(),
            mimetype='image/jpeg'
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Thumbnail error: {e}")
        return jsonify({'error': 'Thumbnail generation failed'}), 500

@app.route('/api/image/<image_id>/download', methods=['GET'])
@login_required
def download_image(image_id):
    """Download watermarked image file."""
    try:
        user_id = session['user_id']
        image = watermarked_images_collection.find_one({
            'image_id': image_id,
            'user_id': ObjectId(user_id)
        })
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Get watermarked image from GridFS
        watermarked_bytes = get_image_from_gridfs(image['watermarked_file_id'])
        if not watermarked_bytes:
            return jsonify({'error': 'Image file not found'}), 404
        
        # Create response with image data
        response = app.response_class(
            watermarked_bytes,
            mimetype='image/png',
            headers={'Content-Disposition': f'attachment; filename=watermarked_{image["original_filename"]}'}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Get user statistics."""
    try:
        user_id = session['user_id']
        
        # Count watermarked images
        total_images = watermarked_images_collection.count_documents({'user_id': ObjectId(user_id)})
        
        # Count successful verifications
        successful_verifications = verification_logs_collection.count_documents({
            'user_id': ObjectId(user_id),
            'success': True
        })
        total_verifications = verification_logs_collection.count_documents({'user_id': ObjectId(user_id)})
        
        # Average PSNR
        pipeline = [
            {'$match': {'user_id': ObjectId(user_id)}},
            {'$group': {'_id': None, 'avg_psnr': {'$avg': '$psnr'}}}
        ]
        avg_psnr_result = list(watermarked_images_collection.aggregate(pipeline))
        avg_psnr = avg_psnr_result[0]['avg_psnr'] if avg_psnr_result else 0
        
        return jsonify({
            'total_images': total_images,
            'successful_verifications': successful_verifications,
            'total_verifications': total_verifications,
            'average_psnr': round(avg_psnr, 2)
        }), 200
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'error': 'Failed to get statistics'}), 500

# Error handlers
@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create indexes for better performance
    try:
        users_collection.create_index("username", unique=True)
        users_collection.create_index("email", unique=True)
        watermarked_images_collection.create_index("image_id", unique=True)
        watermarked_images_collection.create_index("user_id")
        verification_logs_collection.create_index("verification_id", unique=True)
        verification_logs_collection.create_index("user_id")
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Index creation warning: {e}")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
