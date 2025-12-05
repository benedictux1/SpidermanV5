"""
ChromaDB Client
Manages vector database connections and collections for RAG pipeline
"""

import os
import logging
import chromadb
from chromadb.config import Settings
from typing import Optional

logger = logging.getLogger(__name__)

# Global ChromaDB client
_chroma_client = None
_chroma_dir = None


def get_chroma_dir():
    """Get ChromaDB directory from environment or use default"""
    global _chroma_dir
    if _chroma_dir is None:
        chroma_dir = os.getenv('CHROMA_DB_DIR')
        if not chroma_dir:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            chroma_dir = os.path.join(project_root, 'chroma_db')
        os.makedirs(chroma_dir, exist_ok=True)
        _chroma_dir = chroma_dir
        logger.info(f"ChromaDB directory: {chroma_dir}")
    return _chroma_dir


def get_chroma_client():
    """Get or create ChromaDB client"""
    global _chroma_client
    if _chroma_client is None:
        try:
            chroma_dir = get_chroma_dir()
            _chroma_client = chromadb.PersistentClient(
                path=chroma_dir,
                settings=Settings(anonymized_telemetry=False, allow_reset=True)
            )
            logger.info("ChromaDB client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
    return _chroma_client


def get_contact_collection(contact_id: int, prefix: str = "contact_") -> chromadb.Collection:
    """Get or create ChromaDB collection for a specific contact"""
    try:
        client = get_chroma_client()
        collection_name = f"{prefix}{contact_id}"
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"contact_id": contact_id}
        )
        return collection
    except Exception as e:
        logger.error(f"Failed to get contact collection for contact {contact_id}: {e}")
        raise


def store_note_in_chromadb(contact_id: int, note_content: str, note_id: int):
    """Store a note in ChromaDB for RAG retrieval"""
    try:
        collection = get_contact_collection(contact_id)
        collection.add(
            documents=[note_content],
            ids=[f"note_{note_id}"],
            metadatas=[{
                "contact_id": contact_id,
                "note_id": note_id,
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            }]
        )
        logger.debug(f"Stored note {note_id} in ChromaDB for contact {contact_id}")
    except Exception as e:
        logger.warning(f"Failed to store note in ChromaDB: {e}")


def get_relevant_history(contact_id: int, query_text: str, n_results: int = 3) -> str:
    """Retrieve relevant history from ChromaDB for RAG context"""
    try:
        collection = get_contact_collection(contact_id)
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        if results['documents'] and len(results['documents'][0]) > 0:
            retrieved_docs = results['documents'][0]
            retrieved_history = "\n---\n".join(retrieved_docs)
            logger.debug(f"Retrieved {len(retrieved_docs)} relevant notes for contact {contact_id}")
            return retrieved_history
        else:
            logger.debug(f"No relevant history found for contact {contact_id}")
            return "No relevant history found."
    except Exception as e:
        logger.warning(f"RAG retrieval failed for contact {contact_id}: {e}")
        return "No relevant history found."


def delete_contact_collection(contact_id: int, prefix: str = "contact_"):
    """Delete ChromaDB collection for a contact (cleanup on contact deletion)
    
    Args:
        contact_id: ID of contact whose collection should be deleted
        prefix: Collection name prefix (default: "contact_")
        
    Returns:
        bool: True if deleted successfully, False if collection doesn't exist or deletion failed
    """
    try:
        client = get_chroma_client()
        collection_name = f"{prefix}{contact_id}"
        
        try:
            # Try to get the collection first
            collection = client.get_collection(name=collection_name)
            # Delete the collection
            client.delete_collection(name=collection_name)
            logger.info(f"✅ Deleted ChromaDB collection {collection_name} for contact {contact_id}")
            return True
        except Exception as e:
            # Collection doesn't exist - that's okay, just log it
            if "does not exist" in str(e).lower() or "not found" in str(e).lower():
                logger.info(f"ChromaDB collection {collection_name} doesn't exist (already deleted or never created)")
                return True
            else:
                raise
                
    except Exception as e:
        # CRITICAL: Don't fail contact deletion if ChromaDB cleanup fails
        logger.error(f"❌ Failed to delete ChromaDB collection for contact {contact_id}: {e}")
        logger.warning(f"⚠️ Contact deleted from database but ChromaDB collection cleanup failed - orphaned collection may remain")
        # Don't raise - allow operation to continue
        return False

