"""
Check Database Status
Verify database space and current state

Author: PixelLedger Team
"""

from pymongo import MongoClient
import gridfs

# MongoDB connection
MONGODB_URI = "mongodb+srv://shanejacob2312:$Shane2312@cluster0.uxda6.mongodb.net/"
DATABASE_NAME = "pixelledger"

def check_status():
    """Check current database status"""
    print("\n" + "="*80)
    print("DATABASE STATUS CHECK")
    print("="*80 + "\n")
    
    try:
        # Connect
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=30000)
        db = client[DATABASE_NAME]
        fs = gridfs.GridFS(db)
        
        # Get stats
        watermarked_images = db.watermarked_images
        users = db.users
        
        print("1. Current Statistics:")
        print("-" * 60)
        
        total_images = watermarked_images.count_documents({})
        total_users = users.count_documents({})
        gridfs_files = db['fs.files'].count_documents({})
        gridfs_chunks = db['fs.chunks'].count_documents({})
        
        print(f"  Total Images: {total_images}")
        print(f"  Total Users: {total_users}")
        print(f"  GridFS Files: {gridfs_files}")
        print(f"  GridFS Chunks: {gridfs_chunks}")
        
        # Calculate approximate size
        if gridfs_chunks > 0:
            # Get sample chunk size
            sample_chunk = db['fs.chunks'].find_one()
            if sample_chunk and 'data' in sample_chunk:
                chunk_size = len(sample_chunk['data'])
                total_size_mb = (gridfs_chunks * chunk_size) / (1024 * 1024)
                print(f"\n  Estimated GridFS Size: {total_size_mb:.2f} MB")
        
        # Get database stats
        try:
            stats = db.command("dbStats")
            print(f"\n2. Database Stats:")
            print("-" * 60)
            print(f"  Storage Size: {stats.get('storageSize', 0) / (1024*1024):.2f} MB")
            print(f"  Data Size: {stats.get('dataSize', 0) / (1024*1024):.2f} MB")
            print(f"  Index Size: {stats.get('indexSize', 0) / (1024*1024):.2f} MB")
        except Exception as e:
            print(f"  Could not get database stats: {e}")
        
        # List recent images
        print(f"\n3. Recent Images (last 10):")
        print("-" * 60)
        
        recent = list(watermarked_images.find().sort('created_at', -1).limit(10))
        
        for i, img in enumerate(recent, 1):
            created = img.get('created_at', 'Unknown')
            owner = img.get('owner_name', 'Unknown')[:20]
            size = img.get('file_size', 0) / 1024
            
            print(f"  {i:2d}. {created} | {owner:<20s} | {size:.1f} KB")
        
        # Test users
        print(f"\n4. Test Users:")
        print("-" * 60)
        
        test_usernames = ['testuser', 'diagtest', 'shane']
        for username in test_usernames:
            user = users.find_one({'username': username})
            if user:
                user_images = watermarked_images.count_documents({'user_id': user['_id']})
                print(f"  {username:<15s}: {user_images} images")
        
        # Try to insert a test document to check quota
        print(f"\n5. Testing Write Access:")
        print("-" * 60)
        
        try:
            test_collection = db.test_quota
            test_doc = {'test': 'quota_check', 'timestamp': 'now'}
            test_collection.insert_one(test_doc)
            test_collection.delete_one({'test': 'quota_check'})
            print(f"  Write Access: OK")
        except Exception as e:
            print(f"  Write Access: FAILED")
            print(f"  Error: {str(e)}")
            
            if 'quota' in str(e).lower():
                print(f"\n  [CRITICAL] Storage quota still exceeded!")
                print(f"  You need to delete more data or upgrade your plan.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("STATUS CHECK COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    check_status()

