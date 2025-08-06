"""
MongoDB Utilities and Helper Functions
Provides common database operations and utilities
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorCollection
from .database import db

logger = logging.getLogger(__name__)


async def ensure_unique_index(collection: AsyncIOMotorCollection, field: str, sparse: bool = False):
    """
    Ensure a unique index exists on a field
    
    Args:
        collection: MongoDB collection
        field: Field name to index
        sparse: Whether the index should be sparse
    """
    try:
        await collection.create_index(
            field, 
            unique=True, 
            sparse=sparse,
            background=True
        )
        logger.info(f"Created unique index on {collection.name}.{field}")
    except Exception as e:
        logger.warning(f"Index creation failed for {collection.name}.{field}: {e}")


async def ensure_compound_index(collection: AsyncIOMotorCollection, fields: List[tuple], unique: bool = False):
    """
    Ensure a compound index exists
    
    Args:
        collection: MongoDB collection
        fields: List of (field_name, direction) tuples
        unique: Whether the index should be unique
    """
    try:
        await collection.create_index(
            fields,
            unique=unique,
            background=True
        )
        field_names = [f[0] for f in fields]
        logger.info(f"Created compound index on {collection.name}.{field_names}")
    except Exception as e:
        logger.warning(f"Compound index creation failed for {collection.name}: {e}")


async def ensure_text_index(collection: AsyncIOMotorCollection, fields: List[str]):
    """
    Ensure a text search index exists
    
    Args:
        collection: MongoDB collection
        fields: List of field names for text search
    """
    try:
        index_spec = [(field, "text") for field in fields]
        await collection.create_index(
            index_spec,
            background=True
        )
        logger.info(f"Created text index on {collection.name}.{fields}")
    except Exception as e:
        logger.warning(f"Text index creation failed for {collection.name}: {e}")


async def cleanup_old_documents(
    collection: AsyncIOMotorCollection, 
    date_field: str, 
    days_old: int,
    dry_run: bool = True
) -> int:
    """
    Clean up old documents from a collection
    
    Args:
        collection: MongoDB collection
        date_field: Field containing the date to check
        days_old: Number of days old to consider for deletion
        dry_run: If True, only count documents that would be deleted
        
    Returns:
        Number of documents deleted (or would be deleted in dry run)
    """
    try:
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        query = {date_field: {"$lt": cutoff_date}}
        
        if dry_run:
            count = await collection.count_documents(query)
            logger.info(f"Would delete {count} old documents from {collection.name}")
            return count
        else:
            result = await collection.delete_many(query)
            logger.info(f"Deleted {result.deleted_count} old documents from {collection.name}")
            return result.deleted_count
            
    except Exception as e:
        logger.error(f"Error cleaning up {collection.name}: {e}")
        return 0


async def create_backup_export(collection: AsyncIOMotorCollection, query: Dict = None) -> List[Dict]:
    """
    Export collection data for backup
    
    Args:
        collection: MongoDB collection
        query: Optional query filter
        
    Returns:
        List of documents
    """
    try:
        query = query or {}
        cursor = collection.find(query)
        documents = await cursor.to_list(length=None)
        
        logger.info(f"Exported {len(documents)} documents from {collection.name}")
        return documents
        
    except Exception as e:
        logger.error(f"Error exporting {collection.name}: {e}")
        return []


async def bulk_upsert(
    collection: AsyncIOMotorCollection, 
    documents: List[Dict],
    key_field: str = "_id"
) -> Dict[str, int]:
    """
    Perform bulk upsert operation
    
    Args:
        collection: MongoDB collection
        documents: List of documents to upsert
        key_field: Field to use as unique key for upsert
        
    Returns:
        Dictionary with counts of operations
    """
    try:
        from pymongo import UpdateOne
        
        operations = []
        for doc in documents:
            filter_query = {key_field: doc[key_field]}
            operations.append(
                UpdateOne(
                    filter_query,
                    {"$set": doc},
                    upsert=True
                )
            )
        
        if operations:
            result = await collection.bulk_write(operations)
            return {
                "matched": result.matched_count,
                "modified": result.modified_count,
                "upserted": result.upserted_count
            }
        else:
            return {"matched": 0, "modified": 0, "upserted": 0}
            
    except Exception as e:
        logger.error(f"Error in bulk upsert for {collection.name}: {e}")
        return {"error": str(e)}


async def aggregate_with_pagination(
    collection: AsyncIOMotorCollection,
    pipeline: List[Dict],
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """
    Execute aggregation pipeline with pagination
    
    Args:
        collection: MongoDB collection
        pipeline: Aggregation pipeline
        page: Page number (1-based)
        page_size: Number of documents per page
        
    Returns:
        Dictionary with results and pagination info
    """
    try:
        # Add pagination to pipeline
        skip = (page - 1) * page_size
        paginated_pipeline = pipeline + [
            {"$skip": skip},
            {"$limit": page_size}
        ]
        
        # Get total count
        count_pipeline = pipeline + [{"$count": "total"}]
        count_result = await collection.aggregate(count_pipeline).to_list(length=1)
        total_count = count_result[0]["total"] if count_result else 0
        
        # Get paginated results
        results = await collection.aggregate(paginated_pipeline).to_list(length=page_size)
        
        return {
            "data": results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        }
        
    except Exception as e:
        logger.error(f"Error in aggregation with pagination for {collection.name}: {e}")
        return {
            "data": [],
            "pagination": {"page": page, "page_size": page_size, "total_count": 0, "total_pages": 0},
            "error": str(e)
        }


async def get_collection_info(collection: AsyncIOMotorCollection) -> Dict[str, Any]:
    """
    Get detailed information about a collection
    
    Args:
        collection: MongoDB collection
        
    Returns:
        Dictionary with collection information
    """
    try:
        # Get collection stats
        stats = await collection.database.command("collStats", collection.name)
        
        # Get indexes
        indexes = await collection.list_indexes().to_list(length=None)
        
        return {
            "name": collection.name,
            "document_count": stats.get("count", 0),
            "storage_size": stats.get("storageSize", 0),
            "total_index_size": stats.get("totalIndexSize", 0),
            "average_object_size": stats.get("avgObjSize", 0),
            "indexes": [
                {
                    "name": idx.get("name"),
                    "key": idx.get("key"),
                    "unique": idx.get("unique", False)
                }
                for idx in indexes
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting collection info for {collection.name}: {e}")
        return {"error": str(e)}
