#!/usr/bin/env python3
"""
SearchEngine - Unified search engine with SQLite FTS5 and Tantivy backends.

Provides fast full-text search across documents with metadata filtering.
"""

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class SearchEngine:
    """
    Unified search engine supporting multiple backends.

    Primary backend: SQLite FTS5 (fast, embedded, supports metadata)
    Fallback backend: Tantivy (more advanced features, optional)
    """

    def __init__(self, db_path: Optional[Path] = None, use_tantivy: bool = False):
        """
        Initialize SearchEngine.

        Args:
            db_path: Path to SQLite database file. If None, uses default location.
            use_tantivy: Whether to enable Tantivy backend (requires tantivy installed).
        """
        if db_path is None:
            # Default location: project_root/.neocortex/cache/search.db
            from ..config import get_config

            config = get_config()
            db_path = config.project_root / ".neocortex" / "cache" / "search.db"

        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.connection = None
        self.use_tantivy = use_tantivy
        self.tantivy_index = None

        # Initialize database
        self._init_database()

        # Initialize Tantivy if requested
        if use_tantivy:
            self._init_tantivy()

        logger.info(f"SearchEngine initialized at {db_path}")
        logger.info(f"Backend: {'SQLite FTS5' + (' + Tantivy' if use_tantivy else '')}")

    def _init_database(self) -> None:
        """Initialize SQLite database with FTS5 tables."""
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row

        # Enable foreign keys and WAL mode for better concurrency
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.execute("PRAGMA synchronous = NORMAL")

        # Create main documents table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                document_type TEXT,
                source_path TEXT,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata_json TEXT DEFAULT '{}'
            )
        """)

        # Create FTS5 virtual table for full-text search
        self.connection.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts 
            USING fts5(
                id UNINDEXED,
                title,
                content,
                document_type,
                language,
                tokenize = 'porter unicode61'
            )
        """)

        # Create tags table for filtering
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS document_tags (
                document_id TEXT,
                tag TEXT,
                PRIMARY KEY (document_id, tag),
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            )
        """)

        # Create indexes for performance
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_tags_tag ON document_tags(tag)"
        )

        self.connection.commit()

    def _init_tantivy(self) -> None:
        """Initialize Tantivy search index (optional)."""
        try:
            import tantivy

            # Create schema
            schema_builder = tantivy.SchemaBuilder()
            schema_builder.add_text_field("id", stored=True)
            schema_builder.add_text_field(
                "title", stored=True, tokenizer_name="en_stem"
            )
            schema_builder.add_text_field(
                "content", stored=True, tokenizer_name="en_stem"
            )
            schema_builder.add_text_field("document_type", stored=True)
            schema_builder.add_text_field("tags", stored=True)
            schema_builder.add_json_field("metadata")

            schema = schema_builder.build()

            # Create index directory
            tantivy_dir = self.db_path.parent / "tantivy_index"
            tantivy_dir.mkdir(exist_ok=True)

            # Create index
            self.tantivy_index = tantivy.Index(schema, str(tantivy_dir))
            self.tantivy_writer = self.tantivy_index.writer()

            logger.info(f"Tantivy index initialized at {tantivy_dir}")

        except ImportError:
            logger.warning(
                "Tantivy not installed. Falling back to SQLite FTS5 only. "
                "Install with: pip install tantivy"
            )
            self.use_tantivy = False
        except Exception as e:
            logger.warning(
                f"Failed to initialize Tantivy: {e}. Using SQLite FTS5 only."
            )
            self.use_tantivy = False

    def index_document(
        self,
        doc_id: str,
        content: str,
        title: str = "",
        document_type: str = "unknown",
        source_path: str = "",
        language: str = "en",
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> bool:
        """
        Index a document for searching.

        Args:
            doc_id: Unique document identifier
            content: Document content text
            title: Document title (optional)
            document_type: Type of document (e.g., 'lobe', 'manifest', 'cortex')
            source_path: Path to source file (optional)
            language: Document language (default: 'en')
            tags: List of tags for filtering
            metadata: Additional metadata as dictionary

        Returns:
            True if successful, False otherwise
        """
        if tags is None:
            tags = []
        if metadata is None:
            metadata = {}

        try:
            cursor = self.connection.cursor()

            # Check if document already exists
            cursor.execute("SELECT id FROM documents WHERE id = ?", (doc_id,))
            exists = cursor.fetchone() is not None

            metadata_json = json.dumps(metadata, ensure_ascii=False)

            if exists:
                # Update existing document
                cursor.execute(
                    """
                    UPDATE documents 
                    SET title = ?, content = ?, document_type = ?, source_path = ?,
                        language = ?, updated_at = CURRENT_TIMESTAMP, metadata_json = ?
                    WHERE id = ?
                    """,
                    (
                        title,
                        content,
                        document_type,
                        source_path,
                        language,
                        metadata_json,
                        doc_id,
                    ),
                )

                # Update FTS5
                cursor.execute(
                    "DELETE FROM documents_fts WHERE id = ?",
                    (doc_id,),
                )
            else:
                # Insert new document
                cursor.execute(
                    """
                    INSERT INTO documents 
                    (id, title, content, document_type, source_path, language, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        doc_id,
                        title,
                        content,
                        document_type,
                        source_path,
                        language,
                        metadata_json,
                    ),
                )

            # Insert into FTS5
            cursor.execute(
                """
                INSERT INTO documents_fts 
                (id, title, content, document_type, language)
                VALUES (?, ?, ?, ?, ?)
                """,
                (doc_id, title, content, document_type, language),
            )

            # Update tags
            cursor.execute("DELETE FROM document_tags WHERE document_id = ?", (doc_id,))
            for tag in tags:
                cursor.execute(
                    "INSERT INTO document_tags (document_id, tag) VALUES (?, ?)",
                    (doc_id, tag),
                )

            # Update Tantivy if enabled
            if self.use_tantivy and self.tantivy_writer:
                try:
                    import tantivy

                    # Delete existing document
                    self.tantivy_writer.delete_documents(tantivy.Term("id", doc_id))

                    # Add new document
                    doc = tantivy.Document()
                    doc.add_text("id", doc_id)
                    doc.add_text("title", title)
                    doc.add_text("content", content)
                    doc.add_text("document_type", document_type)
                    doc.add_text("tags", " ".join(tags))
                    doc.add_json("metadata", json.dumps(metadata))

                    self.tantivy_writer.add_document(doc)
                except Exception as e:
                    logger.warning(f"Failed to update Tantivy index: {e}")

            self.connection.commit()
            logger.debug(f"Indexed document: {doc_id} ({document_type})")
            return True

        except Exception as e:
            logger.error(f"Failed to index document {doc_id}: {e}")
            self.connection.rollback()
            return False

    def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        document_type: str = None,
        tags: List[str] = None,
        min_date: datetime = None,
        max_date: datetime = None,
        language: str = None,
        use_tantivy: bool = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for documents.

        Args:
            query: Search query string
            limit: Maximum number of results
            offset: Result offset for pagination
            document_type: Filter by document type
            tags: Filter by tags (all tags must match)
            min_date: Filter by minimum creation date
            max_date: Filter by maximum creation date
            language: Filter by language
            use_tantivy: Override default Tantivy usage

        Returns:
            List of matching documents with metadata and relevance score
        """
        if use_tantivy is None:
            use_tantivy = self.use_tantivy

        if use_tantivy and self.tantivy_index:
            return self._search_tantivy(
                query, limit, offset, document_type, tags, min_date, max_date, language
            )
        else:
            return self._search_fts5(
                query, limit, offset, document_type, tags, min_date, max_date, language
            )

    def _search_fts5(
        self,
        query: str,
        limit: int,
        offset: int,
        document_type: str,
        tags: List[str],
        min_date: datetime,
        max_date: datetime,
        language: str,
    ) -> List[Dict[str, Any]]:
        """Search using SQLite FTS5."""
        try:
            cursor = self.connection.cursor()

            # Build query with filters
            conditions = ["1=1"]
            params = []

            # Full-text search condition
            if query.strip():
                # Use FTS5 match syntax
                fts_query = query.replace('"', '""').replace("'", "''")
                conditions.append(
                    "documents.id IN (SELECT id FROM documents_fts WHERE documents_fts MATCH ?)"
                )
                params.append(fts_query)

            # Document type filter
            if document_type:
                conditions.append("documents.document_type = ?")
                params.append(document_type)

            # Language filter
            if language:
                conditions.append("documents.language = ?")
                params.append(language)

            # Date filters
            if min_date:
                conditions.append("documents.created_at >= ?")
                params.append(min_date.isoformat())
            if max_date:
                conditions.append("documents.created_at <= ?")
                params.append(max_date.isoformat())

            # Tags filter (all tags must match)
            if tags:
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append(
                        "EXISTS (SELECT 1 FROM document_tags WHERE document_id = documents.id AND tag = ?)"
                    )
                    params.append(tag)
                conditions.extend(tag_conditions)

            where_clause = " AND ".join(conditions)

            # Execute query with ranking
            sql = f"""
                SELECT 
                    documents.*,
                    snippet(documents_fts, 2, '<b>', '</b>', '...', 64) as snippet,
                    bm25(documents_fts) as relevance
                FROM documents
                LEFT JOIN documents_fts ON documents.id = documents_fts.id
                WHERE {where_clause}
                ORDER BY relevance ASC, documents.created_at DESC
                LIMIT ? OFFSET ?
            """

            params.extend([limit, offset])
            cursor.execute(sql, params)

            results = []
            for row in cursor.fetchall():
                doc = dict(row)
                # Parse metadata JSON
                if doc.get("metadata_json"):
                    try:
                        doc["metadata"] = json.loads(doc["metadata_json"])
                    except:
                        doc["metadata"] = {}
                else:
                    doc["metadata"] = {}

                # Get tags for this document
                cursor.execute(
                    "SELECT tag FROM document_tags WHERE document_id = ?",
                    (doc["id"],),
                )
                doc["tags"] = [row[0] for row in cursor.fetchall()]

                results.append(doc)

            logger.debug(f"FTS5 search for '{query}' returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"FTS5 search failed: {e}")
            return []

    def _search_tantivy(
        self,
        query: str,
        limit: int,
        offset: int,
        document_type: str,
        tags: List[str],
        min_date: datetime,
        max_date: datetime,
        language: str,
    ) -> List[Dict[str, Any]]:
        """Search using Tantivy (if available)."""
        try:
            import tantivy

            # Build Tantivy query
            query_parser = self.tantivy_index.searcher().parse_query(
                query, ["title", "content"]
            )

            # Execute search
            searcher = self.tantivy_index.searcher()
            results = searcher.search(query_parser, limit + offset)

            # Process results
            docs = []
            for i, (score, doc_address) in enumerate(results):
                if i < offset:
                    continue
                if len(docs) >= limit:
                    break

                retrieved_doc = searcher.doc(doc_address)
                if retrieved_doc:
                    doc_dict = {}
                    for field, value in retrieved_doc.items():
                        if isinstance(value, list):
                            doc_dict[field] = value[0] if value else ""
                        else:
                            doc_dict[field] = value

                    # Apply additional filters in Python
                    if document_type and doc_dict.get("document_type") != document_type:
                        continue
                    if language and doc_dict.get("language") != language:
                        continue

                    # Parse metadata
                    if "metadata" in doc_dict:
                        try:
                            doc_dict["metadata"] = json.loads(doc_dict["metadata"])
                        except:
                            doc_dict["metadata"] = {}

                    doc_dict["relevance"] = score
                    docs.append(doc_dict)

            logger.debug(f"Tantivy search for '{query}' returned {len(docs)} results")
            return docs

        except Exception as e:
            logger.error(f"Tantivy search failed: {e}. Falling back to FTS5.")
            return self._search_fts5(
                query, limit, offset, document_type, tags, min_date, max_date, language
            )

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the index."""
        try:
            cursor = self.connection.cursor()

            # Delete from main table (cascades to FTS5 and tags)
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))

            # Also delete from FTS5 directly (should cascade, but just in case)
            cursor.execute("DELETE FROM documents_fts WHERE id = ?", (doc_id,))

            # Delete from Tantivy if enabled
            if self.use_tantivy and self.tantivy_writer:
                try:
                    import tantivy

                    self.tantivy_writer.delete_documents(tantivy.Term("id", doc_id))
                except Exception as e:
                    logger.warning(f"Failed to delete from Tantivy: {e}")

            self.connection.commit()
            logger.debug(f"Deleted document: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            self.connection.rollback()
            return False

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by ID."""
        try:
            cursor = self.connection.cursor()

            cursor.execute(
                """
                SELECT documents.*, 
                       GROUP_CONCAT(document_tags.tag) as tag_list
                FROM documents
                LEFT JOIN document_tags ON documents.id = document_tags.document_id
                WHERE documents.id = ?
                GROUP BY documents.id
                """,
                (doc_id,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            doc = dict(row)
            if doc.get("metadata_json"):
                try:
                    doc["metadata"] = json.loads(doc["metadata_json"])
                except:
                    doc["metadata"] = {}
            else:
                doc["metadata"] = {}

            # Parse tag list
            if doc.get("tag_list"):
                doc["tags"] = doc["tag_list"].split(",")
            else:
                doc["tags"] = []

            return doc

        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics."""
        try:
            cursor = self.connection.cursor()

            stats = {}

            # Document counts by type
            cursor.execute(
                "SELECT document_type, COUNT(*) as count FROM documents GROUP BY document_type"
            )
            stats["by_type"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Total document count
            cursor.execute("SELECT COUNT(*) FROM documents")
            stats["total_documents"] = cursor.fetchone()[0]

            # Tag statistics
            cursor.execute(
                "SELECT tag, COUNT(*) as count FROM document_tags GROUP BY tag ORDER BY count DESC LIMIT 20"
            )
            stats["top_tags"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Database size
            if self.db_path.exists():
                stats["database_size_mb"] = self.db_path.stat().st_size / (1024 * 1024)

            # Tantivy stats
            if self.use_tantivy and self.tantivy_index:
                try:
                    stats["tantivy_enabled"] = True
                    stats["tantivy_docs"] = self.tantivy_index.searcher().num_docs
                except:
                    stats["tantivy_enabled"] = False

            return stats

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    def close(self) -> None:
        """Close database connection and commit Tantivy changes."""
        if self.connection:
            self.connection.close()
            self.connection = None

        if self.use_tantivy and self.tantivy_writer:
            try:
                self.tantivy_writer.commit()
                self.tantivy_writer = None
            except Exception as e:
                logger.warning(f"Failed to commit Tantivy changes: {e}")

        logger.info("SearchEngine closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience function
def get_search_engine(
    db_path: Optional[Path] = None, use_tantivy: bool = False
) -> SearchEngine:
    """Get a SearchEngine instance (singleton pattern)."""
    from ..config import get_config

    config = get_config()
    cache_dir = config.project_root / ".neocortex" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    if db_path is None:
        db_path = cache_dir / "search.db"

    return SearchEngine(db_path, use_tantivy)
