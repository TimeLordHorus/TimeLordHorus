"""
Archive.org API service for accessing public domain books and educational content
Enables Sanctuary VR to fetch and display classic texts, audio, and media from Internet Archive
"""

import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class ArchiveService:
    """Service for querying and fetching content from Archive.org"""

    def __init__(self):
        self.base_url = "https://archive.org"
        self.api_base = f"{self.base_url}/advancedsearch.php"
        self.metadata_base = f"{self.base_url}/metadata"
        self.download_base = f"{self.base_url}/download"

        # Default query parameters
        self.default_fields = ["identifier", "title", "creator", "description",
                              "date", "mediatype", "format", "downloads", "item_size"]

        print("[Archive] Archive.org service initialized")

    # ========== Search Operations ==========

    def search_books(self, query: str, limit: int = 20, page: int = 1) -> Dict[str, Any]:
        """
        Search for public domain books on Archive.org

        Args:
            query: Search query (author, title, subject, etc.)
            limit: Number of results per page
            page: Page number

        Returns:
            Dict with 'results', 'total_count', 'page', 'pages_total'
        """
        try:
            # Build query for books
            search_query = f"({query}) AND mediatype:texts AND language:eng"

            params = {
                'q': search_query,
                'fl[]': self.default_fields,
                'rows': limit,
                'page': page,
                'output': 'json',
                'sort[]': 'downloads desc'  # Most popular first
            }

            response = requests.get(self.api_base, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            results = []
            for doc in data.get('response', {}).get('docs', []):
                results.append({
                    'identifier': doc.get('identifier'),
                    'title': doc.get('title'),
                    'creator': doc.get('creator'),
                    'description': doc.get('description'),
                    'date': doc.get('date'),
                    'downloads': doc.get('downloads', 0),
                    'size': doc.get('item_size', 0)
                })

            total_count = data.get('response', {}).get('numFound', 0)
            pages_total = (total_count + limit - 1) // limit

            print(f"[Archive] Found {len(results)} books for query: {query}")

            return {
                'status': 'success',
                'results': results,
                'total_count': total_count,
                'page': page,
                'pages_total': pages_total,
                'query': query
            }

        except Exception as e:
            print(f"[Archive] Search failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'results': []
            }

    def search_audio(self, query: str, limit: int = 20, page: int = 1) -> Dict[str, Any]:
        """
        Search for public domain audio on Archive.org

        Args:
            query: Search query
            limit: Number of results
            page: Page number

        Returns:
            Dict with search results
        """
        try:
            search_query = f"({query}) AND mediatype:audio AND language:eng"

            params = {
                'q': search_query,
                'fl[]': self.default_fields,
                'rows': limit,
                'page': page,
                'output': 'json',
                'sort[]': 'downloads desc'
            }

            response = requests.get(self.api_base, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            results = []
            for doc in data.get('response', {}).get('docs', []):
                results.append({
                    'identifier': doc.get('identifier'),
                    'title': doc.get('title'),
                    'creator': doc.get('creator'),
                    'description': doc.get('description'),
                    'date': doc.get('date'),
                    'downloads': doc.get('downloads', 0)
                })

            total_count = data.get('response', {}).get('numFound', 0)

            return {
                'status': 'success',
                'results': results,
                'total_count': total_count,
                'page': page,
                'query': query
            }

        except Exception as e:
            print(f"[Archive] Audio search failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'results': []
            }

    def search_by_author(self, author: str, limit: int = 20) -> Dict[str, Any]:
        """Search for works by a specific author"""
        query = f'creator:"{author}"'
        return self.search_books(query, limit)

    def search_by_subject(self, subject: str, limit: int = 20) -> Dict[str, Any]:
        """Search for works on a specific subject"""
        query = f'subject:"{subject}"'
        return self.search_books(query, limit)

    # ========== Metadata Operations ==========

    def get_item_metadata(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed metadata for a specific item

        Args:
            identifier: Archive.org item identifier (e.g., 'walden00thor')

        Returns:
            Dict with metadata or None if not found
        """
        try:
            url = f"{self.metadata_base}/{identifier}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('is_dark', False):
                print(f"[Archive] Item is dark (unavailable): {identifier}")
                return None

            metadata = data.get('metadata', {})
            files = data.get('files', [])

            # Extract key information
            result = {
                'identifier': identifier,
                'title': metadata.get('title'),
                'creator': metadata.get('creator'),
                'description': metadata.get('description'),
                'date': metadata.get('date'),
                'language': metadata.get('language'),
                'subject': metadata.get('subject'),
                'mediatype': metadata.get('mediatype'),
                'collection': metadata.get('collection'),
                'files': self._extract_file_info(files)
            }

            print(f"[Archive] Retrieved metadata for: {identifier}")
            return result

        except Exception as e:
            print(f"[Archive] Failed to get metadata for {identifier}: {e}")
            return None

    def _extract_file_info(self, files: List[Dict]) -> List[Dict[str, Any]]:
        """Extract relevant file information"""
        file_info = []

        for file in files:
            name = file.get('name', '')
            format = file.get('format', '')
            size = file.get('size', 0)

            # Filter for useful formats
            useful_formats = ['Text PDF', 'DjVu', 'EPUB', 'MOBI', 'MP3', 'VBR MP3',
                            'JPEG', 'PNG', 'MPEG4']

            if format in useful_formats or name.endswith(('.pdf', '.epub', '.mp3', '.txt')):
                file_info.append({
                    'name': name,
                    'format': format,
                    'size': size,
                    'url': f"{self.download_base}/{file.get('identifier', '')}/{name}"
                })

        return file_info

    # ========== Download Operations ==========

    def get_download_url(self, identifier: str, filename: str) -> str:
        """
        Get direct download URL for a file

        Args:
            identifier: Item identifier
            filename: Filename (e.g., 'walden00thor.pdf')

        Returns:
            Direct download URL
        """
        return f"{self.download_base}/{identifier}/{filename}"

    def get_text_download_url(self, identifier: str) -> Optional[str]:
        """Get PDF download URL for a text item"""
        metadata = self.get_item_metadata(identifier)

        if not metadata:
            return None

        # Find PDF file
        for file in metadata.get('files', []):
            if file.get('format') == 'Text PDF':
                return file.get('url')

        print(f"[Archive] No PDF found for: {identifier}")
        return None

    def get_audio_download_url(self, identifier: str) -> Optional[str]:
        """Get MP3 download URL for an audio item"""
        metadata = self.get_item_metadata(identifier)

        if not metadata:
            return None

        # Find MP3 file
        for file in metadata.get('files', []):
            if 'MP3' in file.get('format', ''):
                return file.get('url')

        print(f"[Archive] No MP3 found for: {identifier}")
        return None

    # ========== Featured Collections ==========

    def get_walden_collection(self) -> Dict[str, Any]:
        """Get Thoreau's Walden and related works"""
        return self.search_by_author("Thoreau, Henry David", limit=10)

    def get_spinoza_collection(self) -> Dict[str, Any]:
        """Get Spinoza's Ethics and related works"""
        return self.search_by_author("Spinoza, Benedictus de", limit=10)

    def get_muir_collection(self) -> Dict[str, Any]:
        """Get John Muir's works on nature and glaciers"""
        return self.search_by_author("Muir, John", limit=10)

    def get_philosophy_collection(self) -> Dict[str, Any]:
        """Get classic philosophy texts"""
        return self.search_by_subject("Philosophy", limit=20)

    def get_science_collection(self) -> Dict[str, Any]:
        """Get classic science texts"""
        return self.search_by_subject("Science", limit=20)

    # ========== Text Extraction ==========

    def get_text_content(self, identifier: str, max_chars: int = 50000) -> Optional[str]:
        """
        Attempt to get plain text content from an item

        Args:
            identifier: Item identifier
            max_chars: Maximum characters to return

        Returns:
            Plain text content or None
        """
        try:
            # Try to get _djvu.txt file (plain text version)
            url = f"{self.download_base}/{identifier}/{identifier}_djvu.txt"

            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                text = response.text[:max_chars]
                print(f"[Archive] Retrieved text content for: {identifier} ({len(text)} chars)")
                return text
            else:
                print(f"[Archive] No plain text available for: {identifier}")
                return None

        except Exception as e:
            print(f"[Archive] Failed to get text content: {e}")
            return None


# Singleton instance
_archive_service = None

def get_archive_service() -> ArchiveService:
    """Get singleton Archive service instance"""
    global _archive_service
    if _archive_service is None:
        _archive_service = ArchiveService()
    return _archive_service
