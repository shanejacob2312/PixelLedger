"""
Cleanup Orphaned GridFS Files
Delete GridFS files that don't have corresponding database records

Author: PixelLedger Team
"""

from pymongo import MongoClient
import gridfs
from bson import ObjectId

# MongoDB connection
MONGODB_URI = "mongodb+srv://shanejacob2312:$Shane2312@cluster0.uxda6.mongodb.net/"
DATABASE_NAME = "pixelledger"

def cleanup_orphaned_gridfs():
    """Clean up orphaned GridFS files"""
    print("\n" + "="*80)
    print("CLEANUP ORPHANED GRIDFS FILES")
    print("="*80 + "\n")
    
    try:
        # Connect
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=30000)
        db = client[DATABASE_NAME]
        fs = gridfs.GridFS(db)
        
        watermarked_images = db.watermarked_images
        
        print("1. Scanning for orphaned files...")
        print("-" * 60)
        
        # Get all GridFS file IDs
        all_gridfs_files = list(db['fs.files'].find({}, {'_id': 1}))
        total_gridfs = len(all_gridfs_files)
        print(f"  Total GridFS files: {total_gridfs}")
        
        # Get all file IDs referenced in database
        all_images = list(watermarked_images.find({}, {'watermarked_file_id': 1, 'original_file_id': 1}))
        
        referenced_file_ids = set()
        for img in all_images:
            if 'watermarked_file_id' in img:
                referenced_file_ids.add(img['watermarked_file_id'])
            if 'original_file_id' in img:
                referenced_file_ids.add(img['original_file_id'])
        
        print(f"  Referenced file IDs: {len(referenced_file_ids)}")
        
        # Find orphaned files
        orphaned_files = []
        for gridfs_file in all_gridfs_files:
            file_id = gridfs_file['_id']
            if file_id not in referenced_file_ids:
                orphaned_files.append(file_id)
        
        print(f"  Orphaned files found: {len(orphaned_files)}")
        print(f"  Space to free: ~{len(orphaned_files) * 2.5:.1f} MB (estimated)")
        
        if len(orphaned_files) == 0:
            print("\n  No orphaned files to clean up!")
            return
        
        # Confirm deletion
        print(f"\n2. Cleanup Confirmation:")
        print("-" * 60)
        print(f"  This will delete {len(orphaned_files)} orphaned GridFS files")
        print(f"  These files have no corresponding database records")
        print(f"  Estimated space to free: ~{len(orphaned_files) * 2.5:.1f} MB")
        
        confirm = input(f"\n  Proceed with deletion? (yes/no): ").lower()
        
        if confirm == 'yes':
            print(f"\n3. Deleting orphaned files...")
            print("-" * 60)
            
            deleted = 0
            errors = 0
            
            for i, file_id in enumerate(orphaned_files):
                try:
                    fs.delete(file_id)
                    deleted += 1
                    
                    if (i + 1) % 10 == 0:
                        print(f"  Deleted {i + 1}/{len(orphaned_files)}...")
                except Exception as e:
                    errors += 1
                    if errors == 1:
                        print(f"  Error deleting file: {e}")
            
            print(f"\n  Deleted: {deleted} files")
            print(f"  Errors: {errors}")
            
            # Check new stats
            print(f"\n4. New Statistics:")
            print("-" * 60)
            
            remaining_files = db['fs.files'].count_documents({})
            remaining_chunks = db['fs.chunks'].count_documents({})
            
            print(f"  Remaining GridFS Files: {remaining_files}")
            print(f"  Remaining GridFS Chunks: {remaining_chunks}")
            
            # Test write access
            print(f"\n5. Testing Write Access:")
            print("-" * 60)
            
            try:
                test_collection = db.test_quota
                test_doc = {'test': 'quota_check_after_cleanup'}
                test_collection.insert_one(test_doc)
                test_collection.delete_one({'test': 'quota_check_after_cleanup'})
                print(f"  Write Access: OK ✓")
                print(f"  Storage quota issue RESOLVED!")
            except Exception as e:
                print(f"  Write Access: STILL FAILED")
                print(f"  Error: {str(e)}")
                
                if 'quota' in str(e).lower():
                    print(f"\n  Storage still over quota.")
                    print(f"  You may need to:")
                    print(f"    1. Wait a few minutes for MongoDB to update")
                    print(f"    2. Delete more data")
                    print(f"    3. Upgrade your MongoDB plan")
        else:
            print("\n  Cleanup cancelled")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("CLEANUP COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    cleanup_orphaned_gridfs()

