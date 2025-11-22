#!/usr/bin/env python3
"""
Chronos Knowledge Base - Document Upload and Management
Self-contained knowledge base with local storage for privacy

Features:
- Upload and parse documents (PDF, TXT, MD, DOCX, HTML)
- Build searchable local knowledge base
- Extract and index document content
- Semantic search and retrieval
- Privacy-first (all data stored locally)
- No cloud dependencies
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import mimetypes

class ChronosKnowledgeBase:
    """Local knowledge base for document storage and retrieval"""

    def __init__(self, storage_path=None):
        """Initialize knowledge base"""
        if storage_path is None:
            storage_path = Path.home() / '.config' / 'tl-linux' / 'chronos-ai' / 'knowledge-base'

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Storage directories
        self.documents_dir = self.storage_path / 'documents'
        self.documents_dir.mkdir(exist_ok=True)

        self.index_dir = self.storage_path / 'index'
        self.index_dir.mkdir(exist_ok=True)

        # Index file
        self.index_file = self.index_dir / 'document_index.json'
        self.load_index()

    def load_index(self):
        """Load document index"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {
                'documents': {},  # doc_id -> metadata
                'keywords': defaultdict(list),  # keyword -> [doc_ids]
                'stats': {
                    'total_documents': 0,
                    'total_words': 0,
                    'last_updated': None
                }
            }

    def save_index(self):
        """Save document index"""
        # Convert defaultdict to regular dict for JSON serialization
        index_to_save = {
            'documents': self.index['documents'],
            'keywords': dict(self.index['keywords']),
            'stats': self.index['stats']
        }

        with open(self.index_file, 'w') as f:
            json.dump(index_to_save, f, indent=2)

    def upload_document(self, file_path, metadata=None):
        """Upload and process a document"""
        file_path = Path(file_path)

        if not file_path.exists():
            return {'success': False, 'error': 'File not found'}

        # Generate document ID
        doc_id = self._generate_doc_id(file_path)

        # Check if already uploaded
        if doc_id in self.index['documents']:
            return {
                'success': False,
                'error': 'Document already uploaded',
                'doc_id': doc_id
            }

        # Parse document
        content = self._parse_document(file_path)
        if content is None:
            return {'success': False, 'error': 'Failed to parse document'}

        # Save document content
        doc_storage_path = self.documents_dir / f"{doc_id}.txt"
        with open(doc_storage_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Extract keywords and index
        keywords = self._extract_keywords(content)

        # Store metadata
        doc_metadata = {
            'id': doc_id,
            'filename': file_path.name,
            'original_path': str(file_path),
            'upload_date': datetime.now().isoformat(),
            'file_type': file_path.suffix,
            'file_size': file_path.stat().st_size,
            'word_count': len(content.split()),
            'keywords': keywords[:50],  # Top 50 keywords
            'custom_metadata': metadata or {}
        }

        self.index['documents'][doc_id] = doc_metadata

        # Update keyword index
        for keyword in keywords:
            if keyword not in self.index['keywords']:
                self.index['keywords'][keyword] = []
            self.index['keywords'][keyword].append(doc_id)

        # Update stats
        self.index['stats']['total_documents'] += 1
        self.index['stats']['total_words'] += doc_metadata['word_count']
        self.index['stats']['last_updated'] = datetime.now().isoformat()

        self.save_index()

        return {
            'success': True,
            'doc_id': doc_id,
            'metadata': doc_metadata
        }

    def _generate_doc_id(self, file_path):
        """Generate unique document ID"""
        content_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
        return f"doc_{content_hash[:16]}"

    def _parse_document(self, file_path):
        """Parse document content based on file type"""
        suffix = file_path.suffix.lower()

        try:
            if suffix == '.txt':
                return self._parse_text(file_path)
            elif suffix == '.md':
                return self._parse_markdown(file_path)
            elif suffix == '.pdf':
                return self._parse_pdf(file_path)
            elif suffix in ['.doc', '.docx']:
                return self._parse_docx(file_path)
            elif suffix in ['.html', '.htm']:
                return self._parse_html(file_path)
            else:
                # Try as text
                return self._parse_text(file_path)
        except Exception as e:
            print(f"Error parsing document: {e}")
            return None

    def _parse_text(self, file_path):
        """Parse plain text file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _parse_markdown(self, file_path):
        """Parse markdown file"""
        # For now, treat as text (could enhance with markdown parsing)
        return self._parse_text(file_path)

    def _parse_pdf(self, file_path):
        """Parse PDF file"""
        try:
            import PyPDF2
            text = []
            with open(file_path, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                for page in pdf.pages:
                    text.append(page.extract_text())
            return '\n'.join(text)
        except ImportError:
            print("PyPDF2 not available. Install: pip3 install PyPDF2")
            return None
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return None

    def _parse_docx(self, file_path):
        """Parse DOCX file"""
        try:
            import docx
            doc = docx.Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except ImportError:
            print("python-docx not available. Install: pip3 install python-docx")
            return None
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
            return None

    def _parse_html(self, file_path):
        """Parse HTML file"""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                return soup.get_text()
        except ImportError:
            print("BeautifulSoup not available. Install: pip3 install beautifulsoup4")
            # Fallback to basic text parsing
            return self._parse_text(file_path)
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            return None

    def _extract_keywords(self, content, min_length=4, max_keywords=100):
        """Extract keywords from content"""
        # Convert to lowercase and split into words
        words = re.findall(r'\b[a-z]{' + str(min_length) + r',}\b', content.lower())

        # Common stop words to filter out
        stop_words = {
            'this', 'that', 'with', 'from', 'have', 'been', 'were', 'they',
            'what', 'when', 'where', 'which', 'while', 'there', 'their',
            'would', 'could', 'should', 'about', 'these', 'those', 'other',
            'more', 'than', 'into', 'some', 'such', 'very', 'also', 'just',
            'then', 'them', 'will', 'each', 'much', 'make', 'made', 'many'
        }

        # Count word frequency
        word_freq = defaultdict(int)
        for word in words:
            if word not in stop_words:
                word_freq[word] += 1

        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]

    def search(self, query, max_results=5):
        """Search knowledge base for relevant documents"""
        query_lower = query.lower()
        query_words = re.findall(r'\b[a-z]{3,}\b', query_lower)

        # Score documents based on keyword matches
        doc_scores = defaultdict(int)

        for word in query_words:
            # Exact match
            if word in self.index['keywords']:
                for doc_id in self.index['keywords'][word]:
                    doc_scores[doc_id] += 10

            # Partial match
            for keyword in self.index['keywords']:
                if word in keyword or keyword in word:
                    for doc_id in self.index['keywords'][keyword]:
                        doc_scores[doc_id] += 5

        # Sort by score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

        # Get document details
        results = []
        for doc_id, score in sorted_docs[:max_results]:
            if doc_id in self.index['documents']:
                doc_meta = self.index['documents'][doc_id]

                # Get snippet
                snippet = self._get_snippet(doc_id, query_words)

                results.append({
                    'doc_id': doc_id,
                    'filename': doc_meta['filename'],
                    'score': score,
                    'snippet': snippet,
                    'metadata': doc_meta
                })

        return results

    def _get_snippet(self, doc_id, query_words, snippet_length=200):
        """Get a snippet from document containing query words"""
        doc_path = self.documents_dir / f"{doc_id}.txt"

        if not doc_path.exists():
            return ""

        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find first occurrence of any query word
        content_lower = content.lower()
        earliest_pos = len(content)

        for word in query_words:
            pos = content_lower.find(word)
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos

        if earliest_pos == len(content):
            # No query words found, return beginning
            return content[:snippet_length] + "..."

        # Get snippet around the query word
        start = max(0, earliest_pos - 50)
        end = min(len(content), earliest_pos + snippet_length)

        snippet = content[start:end]

        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def get_document(self, doc_id):
        """Get full document content"""
        doc_path = self.documents_dir / f"{doc_id}.txt"

        if not doc_path.exists():
            return None

        with open(doc_path, 'r', encoding='utf-8') as f:
            return f.read()

    def list_documents(self):
        """List all documents in knowledge base"""
        return list(self.index['documents'].values())

    def delete_document(self, doc_id):
        """Delete a document from knowledge base"""
        if doc_id not in self.index['documents']:
            return {'success': False, 'error': 'Document not found'}

        # Remove file
        doc_path = self.documents_dir / f"{doc_id}.txt"
        if doc_path.exists():
            doc_path.unlink()

        # Remove from index
        doc_meta = self.index['documents'][doc_id]

        # Update stats
        self.index['stats']['total_documents'] -= 1
        self.index['stats']['total_words'] -= doc_meta['word_count']

        # Remove from keyword index
        for keyword in doc_meta['keywords']:
            if keyword in self.index['keywords']:
                if doc_id in self.index['keywords'][keyword]:
                    self.index['keywords'][keyword].remove(doc_id)
                if not self.index['keywords'][keyword]:
                    del self.index['keywords'][keyword]

        # Remove document
        del self.index['documents'][doc_id]

        self.save_index()

        return {'success': True}

    def get_stats(self):
        """Get knowledge base statistics"""
        return self.index['stats']

if __name__ == '__main__':
    # Test the knowledge base
    kb = ChronosKnowledgeBase()
    print(f"Knowledge Base initialized at: {kb.storage_path}")
    print(f"Total documents: {kb.index['stats']['total_documents']}")
