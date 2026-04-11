#!/usr/bin/env python3
"""
LobeIndex - SQLite + FTS5 full-text search index for lobes.

Provides fast text search across all lobe contents with metadata filtering.
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


class LobeIndex:
    """
    SQLite-based full-text search index for lobes.

    Features:
    - FTS5 full-text search with ranking
    - Metadata storage (tags, status, module, etc.)
    - Fast filtering by metadata
    - Incremental updates
    - Connection pooling (single connection per instance)
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize LobeIndex.

        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Default location: project_root/.neocortex/cache/lobe_index.db
            from ..config import get_config

            config = get_config()
            db_path = config.project_root / ".neocortex" / "cache" / "lobe_index.db"

        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.connection = None

        # Initialize database
        self._init_database()

        logger.info(f"LobeIndex initialized at {db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            # Enable foreign keys and WAL mode for better performance
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.connection.execute("PRAGMA journal_mode = WAL")
            self.connection.execute("PRAGMA synchronous = NORMAL")

        return self.connection

    def _init_database(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()

        # Create metadata table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS lobe_metadata (
            lobe_id TEXT PRIMARY KEY,
            lobe_name TEXT NOT NULL,
            module TEXT,
            status TEXT,
            tags TEXT,  -- JSON array
            checkpoints TEXT,  -- JSON array
            file_path TEXT NOT NULL,
            file_size INTEGER,
            line_count INTEGER,
            word_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_indexed_at TIMESTAMP
        )
        """)

        # Create FTS5 virtual table for full-text search
        # Check if FTS5 is available
        try:
            conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS lobe_fts USING fts5(
                lobe_id,
                content,
                title,
                tokenize = 'porter unicode61'  -- English stemming + Unicode support
            )
            """)
        except sqlite3.OperationalError as e:
            if "no such module: fts5" in str(e):
                logger.error("FTS5 not available in SQLite. Full-text search disabled.")
                # Create a dummy table for compatibility
                conn.execute("""
                CREATE TABLE IF NOT EXISTS lobe_fts (
                    lobe_id TEXT PRIMARY KEY,
                    content TEXT,
                    title TEXT
                )
                """)
            else:
                raise

        # Create indexes
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_lobe_metadata_module ON lobe_metadata(module)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_lobe_metadata_status ON lobe_metadata(status)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_lobe_metadata_tags ON lobe_metadata(tags)"
        )

        conn.commit()

    def index_lobe(
        self,
        lobe_id: str,
        lobe_name: str,
        content: str,
        file_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Index a lobe.

        Args:
            lobe_id: Unique lobe identifier
            lobe_name: Human-readable lobe name
            content: Full lobe content
            file_path: Path to lobe file
            metadata: Optional metadata dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            current_time = datetime.now().isoformat()

            # Parse metadata from content if not provided
            if metadata is None:
                metadata = self._extract_metadata(content)

            # Extract title (first # header)
            title = self._extract_title(content)

            # Prepare metadata values
            module = metadata.get("module", "")
            status = metadata.get("status", "active")
            tags = json.dumps(metadata.get("tags", []))
            checkpoints = json.dumps(metadata.get("checkpoints", []))

            # File statistics
            file_size = len(content.encode("utf-8"))
            line_count = content.count("\n") + 1
            word_count = len(content.split())

            # Insert or update metadata
            conn.execute(
                """
            INSERT OR REPLACE INTO lobe_metadata 
            (lobe_id, lobe_name, module, status, tags, checkpoints, file_path, 
             file_size, line_count, word_count, updated_at, last_indexed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    lobe_id,
                    lobe_name,
                    module,
                    status,
                    tags,
                    checkpoints,
                    str(file_path),
                    file_size,
                    line_count,
                    word_count,
                    current_time,
                    current_time,
                ),
            )

            # Insert or replace in FTS table
            conn.execute(
                """
            INSERT OR REPLACE INTO lobe_fts (lobe_id, content, title)
            VALUES (?, ?, ?)
            """,
                (lobe_id, content, title),
            )

            conn.commit()
            logger.debug(f"Indexed lobe: {lobe_id} ({lobe_name})")
            return True

        except Exception as e:
            logger.error(f"Failed to index lobe {lobe_id}: {e}")
            return False

    def search(
        self,
        query: str,
        module: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Search lobes with full-text and metadata filters.

        Args:
            query: Full-text search query (FTS5 syntax)
            module: Filter by module
            status: Filter by status
            tags: Filter by tags (AND logic)
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of matching lobes with metadata and relevance scores
        """
        try:
            conn = self._get_connection()

            # Build WHERE clauses
            where_clauses = []
            params = []

            # Full-text search
            if query.strip():
                where_clauses.append("lobe_fts MATCH ?")
                params.append(query)

            # Metadata filters
            if module:
                where_clauses.append("lobe_metadata.module = ?")
                params.append(module)

            if status:
                where_clauses.append("lobe_metadata.status = ?")
                params.append(status)

            if tags:
                for tag in tags:
                    where_clauses.append("lobe_metadata.tags LIKE ?")
                    params.append(f'%"{tag}"%')

            # Build SQL
            if where_clauses:
                where_sql = "WHERE " + " AND ".join(where_clauses)
            else:
                where_sql = ""

            # Check if FTS5 is available (by checking if lobe_fts is a virtual table)
            fts_available = self._is_fts5_available()

            if fts_available and query.strip():
                # Use FTS5 ranking
                sql = f"""
                SELECT 
                    lobe_metadata.*,
                    lobe_fts.content,
                    lobe_fts.title,
                    bm25(lobe_fts) as relevance
                FROM lobe_fts
                JOIN lobe_metadata ON lobe_fts.lobe_id = lobe_metadata.lobe_id
                {where_sql}
                ORDER BY relevance
                LIMIT ? OFFSET ?
                """
            else:
                # Simple search without ranking
                sql = f"""
                SELECT 
                    lobe_metadata.*,
                    lobe_fts.content,
                    lobe_fts.title,
                    1.0 as relevance
                FROM lobe_fts
                JOIN lobe_metadata ON lobe_fts.lobe_id = lobe_metadata.lobe_id
                {where_sql}
                ORDER BY lobe_metadata.updated_at DESC
                LIMIT ? OFFSET ?
                """

            params.extend([limit, offset])

            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()

            # Convert to dictionaries
            results = []
            for row in rows:
                result = dict(row)
                # Parse JSON fields
                for field in ["tags", "checkpoints"]:
                    if result[field]:
                        try:
                            result[field] = json.loads(result[field])
                        except Exception:
                            result[field] = []
                    else:
                        result[field] = []

                results.append(result)

            logger.debug(f"Search returned {len(results)} results for query: {query}")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_lobe(self, lobe_id: str) -> Optional[Dict[str, Any]]:
        """Get a lobe by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.execute(
                """
            SELECT 
                lobe_metadata.*,
                lobe_fts.content,
                lobe_fts.title
            FROM lobe_metadata
            LEFT JOIN lobe_fts ON lobe_metadata.lobe_id = lobe_fts.lobe_id
            WHERE lobe_metadata.lobe_id = ?
            """,
                (lobe_id,),
            )

            row = cursor.fetchone()
            if row:
                result = dict(row)
                # Parse JSON fields
                for field in ["tags", "checkpoints"]:
                    if result[field]:
                        try:
                            result[field] = json.loads(result[field])
                        except Exception:
                            result[field] = []
                    else:
                        result[field] = []

                return result

            return None

        except Exception as e:
            logger.error(f"Failed to get lobe {lobe_id}: {e}")
            return None

    def delete_lobe(self, lobe_id: str) -> bool:
        """Delete a lobe from index."""
        try:
            conn = self._get_connection()
            conn.execute("DELETE FROM lobe_metadata WHERE lobe_id = ?", (lobe_id,))
            conn.execute("DELETE FROM lobe_fts WHERE lobe_id = ?", (lobe_id,))
            conn.commit()
            logger.debug(f"Deleted lobe from index: {lobe_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete lobe {lobe_id}: {e}")
            return False

    def update_lobe_metadata(self, lobe_id: str, metadata: Dict[str, Any]) -> bool:
        """Update lobe metadata."""
        try:
            conn = self._get_connection()
            current_time = datetime.now().isoformat()

            # Build update SQL
            updates = []
            params = []

            for key, value in metadata.items():
                if key in ["module", "status"]:
                    updates.append(f"{key} = ?")
                    params.append(str(value))
                elif key in ["tags", "checkpoints"]:
                    updates.append(f"{key} = ?")
                    params.append(json.dumps(value if isinstance(value, list) else []))
                elif key == "lobe_name":
                    updates.append("lobe_name = ?")
                    params.append(str(value))

            if not updates:
                return False

            updates.append("updated_at = ?")
            params.append(current_time)

            params.append(lobe_id)

            sql = f"UPDATE lobe_metadata SET {', '.join(updates)} WHERE lobe_id = ?"
            conn.execute(sql, params)
            conn.commit()

            logger.debug(f"Updated metadata for lobe: {lobe_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update lobe metadata {lobe_id}: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            conn = self._get_connection()

            stats = {
                "total_lobes": 0,
                "by_module": {},
                "by_status": {},
                "total_size_bytes": 0,
                "last_indexed": None,
            }

            # Total lobes
            cursor = conn.execute("SELECT COUNT(*) as count FROM lobe_metadata")
            stats["total_lobes"] = cursor.fetchone()[0]

            # By module
            cursor = conn.execute("""
            SELECT module, COUNT(*) as count 
            FROM lobe_metadata 
            WHERE module IS NOT NULL AND module != ''
            GROUP BY module
            """)
            for row in cursor:
                stats["by_module"][row[0]] = row[1]

            # By status
            cursor = conn.execute("""
            SELECT status, COUNT(*) as count 
            FROM lobe_metadata 
            WHERE status IS NOT NULL AND status != ''
            GROUP BY status
            """)
            for row in cursor:
                stats["by_status"][row[0]] = row[1]

            # Total size
            cursor = conn.execute("SELECT SUM(file_size) as total FROM lobe_metadata")
            total = cursor.fetchone()[0]
            stats["total_size_bytes"] = total if total else 0

            # Last indexed
            cursor = conn.execute("SELECT MAX(last_indexed_at) FROM lobe_metadata")
            stats["last_indexed"] = cursor.fetchone()[0]

            return stats

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    def rebuild_index(self) -> bool:
        """
        Rebuild the entire index from lobe files.

        This should be called when lobe files change outside of normal indexing.
        """
        try:
            from ..repositories import FileSystemLobeRepository

            lobe_repo = FileSystemLobeRepository()
            lobe_names = lobe_repo.list_lobes()

            count = 0
            for lobe_name in lobe_names:
                content = lobe_repo.read_lobe(lobe_name)
                if content:
                    # Generate lobe ID from name
                    lobe_id = lobe_name.replace(".mdc", "").replace("/", "_")

                    # Extract file path (approximate)
                    from ..config import get_config

                    config = get_config()
                    file_path = (
                        config.core_central / ".agents" / "rules" / f"{lobe_name}.mdc"
                    )
                    if not file_path.exists():
                        file_path = (
                            config.core_central / ".agents" / "rules" / lobe_name
                        )

                    if self.index_lobe(
                        lobe_id=lobe_id,
                        lobe_name=lobe_name,
                        content=content,
                        file_path=file_path,
                    ):
                        count += 1

            logger.info(f"Rebuilt index with {count} lobes")
            return True

        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            return False

    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from lobe content."""
        metadata = {"module": "", "status": "active", "tags": [], "checkpoints": []}

        lines = content.split("\n")

        for line in lines:
            line = line.strip()

            # HTML comments: <!-- key: value -->
            if line.startswith("<!--") and line.endswith("-->"):
                inner = line[4:-3].strip()
                if ":" in inner:
                    key, value = inner.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if key == "module":
                        metadata["module"] = value
                    elif key == "status":
                        metadata["status"] = value

            # Tags line: ## Tags\n#tag1, #tag2
            elif line.startswith("#"):
                # Skip header markers
                pass

            # Extract tags from lines containing #
            if "#" in line and not line.startswith("<!--"):
                # Find hashtags
                hashtags = re.findall(r"#(\w+)", line)
                if hashtags:
                    metadata["tags"].extend(hashtags)

            # Extract checkpoints: - CP-XXX: description
            if line.startswith("- CP-"):
                checkpoint = line[2:].split(":", 1)[0].strip()
                if checkpoint:
                    metadata["checkpoints"].append(checkpoint)

        # Deduplicate
        metadata["tags"] = list(set(metadata["tags"]))
        metadata["checkpoints"] = list(set(metadata["checkpoints"]))

        return metadata

    def _extract_title(self, content: str) -> str:
        """Extract title from lobe content."""
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("# ") and not line.startswith("<!--"):
                return line[2:].strip()

        return ""

    def _is_fts5_available(self) -> bool:
        """Check if FTS5 is available in SQLite."""
        try:
            conn = self._get_connection()
            # Try to create a temporary FTS5 table
            conn.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS temp_test_fts USING fts5(test)"
            )
            conn.execute("DROP TABLE temp_test_fts")
            return True
        except Exception:
            return False

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        """Cleanup on destruction."""
        self.close()


# Factory function
def create_lobe_index(db_path: Optional[Path] = None) -> LobeIndex:
    """
    Create a LobeIndex instance.

    Args:
        db_path: Optional custom database file path

    Returns:
        LobeIndex instance
    """
    return LobeIndex(db_path=db_path)


# Integration helper
class LobeIndexService:
    """
    Service wrapper for LobeIndex with integration to LobeRepository.
    """

    def __init__(self, lobe_index: Optional[LobeIndex] = None):
        self.index = lobe_index or create_lobe_index()
        from ..repositories import FileSystemLobeRepository

        self.lobe_repo = FileSystemLobeRepository()

    def index_all_lobes(self) -> int:
        """Index all lobes from repository."""
        lobe_names = self.lobe_repo.list_lobes()
        count = 0

        for lobe_name in lobe_names:
            if self.index_lobe(lobe_name):
                count += 1

        return count

    def index_lobe(self, lobe_name: str) -> bool:
        """Index a single lobe."""
        content = self.lobe_repo.read_lobe(lobe_name)
        if not content:
            return False

        # Determine file path
        from ..config import get_config

        config = get_config()
        file_path = config.core_central / ".agents" / "rules" / f"{lobe_name}.mdc"
        if not file_path.exists():
            file_path = config.core_central / ".agents" / "rules" / lobe_name

        lobe_id = lobe_name.replace(".mdc", "").replace("/", "_")

        return self.index.index_lobe(
            lobe_id=lobe_id, lobe_name=lobe_name, content=content, file_path=file_path
        )

    def search_lobes(
        self,
        query: str,
        module: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search lobes with the index."""
        return self.index.search(
            query=query, module=module, status=status, tags=tags, limit=limit
        )


# Test function
def test_lobe_index():
    """Test LobeIndex functionality."""
    import tempfile
    import shutil

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    db_path = temp_dir / "test_index.db"

    try:
        index = LobeIndex(db_path=db_path)

        # Create test lobe content
        test_content = """<!-- module: test -->
<!-- status: active -->

# Test Lobe

This is a test lobe for testing the index.

## Tags
#testing, #index, #lobe

## Checkpoints
- CP-TEST-001: Initial test
- CP-TEST-002: Second test

Some more content with keywords: search, test, lobe.
"""

        # Test indexing
        assert index.index_lobe(
            lobe_id="test_lobe",
            lobe_name="Test Lobe",
            content=test_content,
            file_path=temp_dir / "test_lobe.mdc",
        )

        # Test search
        results = index.search("test")
        assert len(results) > 0
        assert results[0]["lobe_name"] == "Test Lobe"

        # Test search with metadata filter
        results = index.search("lobe", module="test")
        assert len(results) > 0

        # Test get lobe
        lobe = index.get_lobe("test_lobe")
        assert lobe is not None
        assert "test" in [t.lower() for t in lobe["tags"]]

        # Test stats
        stats = index.get_stats()
        assert stats["total_lobes"] == 1

        # Test update metadata
        assert index.update_lobe_metadata("test_lobe", {"status": "archived"})
        updated = index.get_lobe("test_lobe")
        assert updated["status"] == "archived"

        # Test delete
        assert index.delete_lobe("test_lobe")
        assert index.get_lobe("test_lobe") is None

        print("✓ LobeIndex tests passed")

    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


if __name__ == "__main__":
    test_lobe_index()
