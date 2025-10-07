"""
PixelLedger Backend API

Flask-based REST API for the PixelLedger watermarking system.
Provides endpoints for watermark embedding, extraction, and user management.

Author: PixelLedger Team
"""

from flask import Flask, request, jsonify, send_file, session
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
    client = MongoClient(MONGODB_URI)
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
     origins=['http://localhost:5500', 'http://127.0.0.1:5500', 'http://localhost:5000', 'http://127.0.0.1:5000', 'http://localhost:8080', 'http://127.0.0.1:8080'],
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['Content-Type', 'Authorization', 'Set-Cookie'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize watermarking systems
# Use semantic watermarking by default (falls back to basic if AI models unavailable)
try:
    watermark_system = SemanticWatermarkSystem(
        delta=60.0,  # Increased for robustness with semantic data (slight quality trade-off)
        wavelet='haar',
        level=2
    )
    logger.info("Semantic Watermark System initialized successfully")
except Exception as e:
    logger.warning(f"Failed to initialize Semantic Watermark System: {e}")
    logger.info("Falling back to basic watermark system")
    watermark_system = FinalWatermarkSystem(
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
        
        # Generate unique image ID first
        image_id = str(uuid.uuid4())
        secret_key = generate_secret_key(user_id, image_id)
        
        # Get watermark metadata
        watermark_data = {
            'owner': request.form.get('owner', user['full_name'] or user['username']),
            'creator': request.form.get('creator', ''),
            'date_created': request.form.get('dateCreated', datetime.now().strftime('%Y-%m-%d')),
            'copyright': request.form.get('copyright', ''),
            'description': request.form.get('description', ''),
            'image_id': image_id,  # Use the generated image_id
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
        watermarked_image, metadata = watermark_system.embed(
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
            'image_id': image_id,
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
        print(f"[BACKEND] ❌ ERROR: {e}")
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
        # Get image data
        image_data = request.form.get('image')
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Convert base64 to image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        uploaded_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        uploaded_image = cv2.cvtColor(uploaded_image, cv2.COLOR_BGR2RGB)
        
        # Try to extract watermark with all possible keys
        verification_result = None
        all_images = watermarked_images_collection.find()
        
        for image_record in all_images:
            try:
                secret_key = generate_secret_key(str(image_record['user_id']), image_record['image_id'])
                
                # Load original image for geometric correction
                original_bytes = get_image_from_gridfs(image_record['original_file_id'])
                if original_bytes:
                    original_nparr = np.frombuffer(original_bytes, np.uint8)
                    original_image = cv2.imdecode(original_nparr, cv2.IMREAD_COLOR)
                    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
                else:
                    original_image = None
                
                # Extract watermark
                extraction_results = watermark_system.extract(
                    uploaded_image, secret_key)
                
                if extraction_results['success']:
                    # Found a match! Build result and break
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
                    
                    # Stop searching after first match
                    break
                    
            except Exception as e:
                logger.warning(f"Verification failed for image {image_record['image_id']}: {e}")
                continue
        
        # Log verification attempt
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
        
        verification_logs_collection.insert_one(verification_log)
        
        logger.info(f"Watermark verification completed: {'Match found' if verification_result else 'No match'}")
        
        if verification_result:
            # Watermark found
            extracted_data = verification_result['extraction_results'].get('payload', {})
            
            # Add semantic features if available
            if 'semantic_features' in verification_result:
                extracted_data['semantic_features'] = verification_result['semantic_features']
            
            # Add fingerprint if available
            if 'fingerprint' in verification_result:
                extracted_data['perceptual_hash'] = verification_result['fingerprint'].get('perceptual_hash')
                extracted_data['master_fingerprint'] = verification_result['fingerprint'].get('master_fingerprint')
            
            # Add database record info
            db_record = verification_result['image_record']
            extracted_data['database_record'] = {
                'creator': db_record.get('creator'),
                'title': db_record.get('title'),
                'copyright': db_record.get('copyright_info'),
                'medium': db_record.get('medium'),
                'category': db_record.get('category')
            }
            
            return jsonify({
                'message': 'Watermark found and verified',
                'verification_id': verification_id,
                'watermark_found': True,
                'tampered': False,  # You can add tamper detection logic here
                'extracted_data': extracted_data
            }), 200
        else:
            # No watermark found
            return jsonify({
                'message': 'No watermark detected',
                'verification_id': verification_id,
                'watermark_found': False,
                'tampered': False,
                'extracted_data': None
            }), 200
        
    except Exception as e:
        logger.error(f"Watermark verification error: {e}")
        import traceback
        logger.error(traceback.format_exc())
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

@app.route('/api/images/<image_id>/download', methods=['GET'])
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
