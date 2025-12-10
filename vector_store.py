"""
Vector Store for Code Understanding
Provides semantic search over codebase using embeddings.

Supports multiple embedding providers:
- Local: sentence-transformers (free, no API needed)
- OpenAI: text-embedding-3-small/large
- Ollama: nomic-embed-text, all-minilm, etc.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
import numpy as np


@dataclass
class CodeChunk:
    """A chunk of code with metadata."""
    id: str
    content: str
    file_path: str
    chunk_type: str  # 'function', 'class', 'module', 'config', 'doc'
    start_line: int = 0
    end_line: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


class EmbeddingProvider:
    """Base class for embedding providers."""
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError
    
    def embed_single(self, text: str) -> List[float]:
        return self.embed([text])[0]


class LocalEmbeddingProvider(EmbeddingProvider):
    """Local embeddings using sentence-transformers (free, no API)."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._dimension = 384  # Default for all-MiniLM-L6-v2
    
    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                # Get actual dimension from model
                self._dimension = self._model.get_sentence_embedding_dimension()
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. Run: pip install sentence-transformers"
                )
        return self._model
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            model = self._load_model()
            embeddings = model.encode(texts, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            print(f"⚠️  Embedding error: {e}")
            # Return zero vectors as fallback
            return [[0.0] * self._dimension for _ in texts]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embeddings."""
    
    def __init__(self, model: str = "text-embedding-3-small", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required for embeddings")
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            # Process in batches of 100
            all_embeddings = []
            for i in range(0, len(texts), 100):
                batch = texts[i:i+100]
                response = client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai")


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Ollama local embeddings."""
    
    def __init__(self, model: str = "nomic-embed-text"):
        self.model = model
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        import subprocess
        import json
        
        embeddings = []
        for text in texts:
            try:
                result = subprocess.run(
                    ["ollama", "embeddings", self.model],
                    input=json.dumps({"prompt": text}).encode(),
                    capture_output=True,
                    timeout=30
                )
                if result.returncode == 0:
                    response = json.loads(result.stdout)
                    embeddings.append(response.get("embedding", []))
                else:
                    # Fallback to zero vector
                    embeddings.append([0.0] * 384)
            except Exception:
                embeddings.append([0.0] * 384)
        
        return embeddings


class VectorStore:
    """
    Simple in-memory vector store for code search.
    Uses cosine similarity for retrieval.
    """
    
    def __init__(self, embedding_provider: Optional[EmbeddingProvider] = None):
        self.chunks: List[CodeChunk] = []
        self.embedding_provider = embedding_provider
        self._embeddings_matrix: Optional[np.ndarray] = None
    
    def add_chunk(self, chunk: CodeChunk):
        """Add a code chunk to the store."""
        self.chunks.append(chunk)
        self._embeddings_matrix = None  # Invalidate cache
    
    def add_chunks(self, chunks: List[CodeChunk]):
        """Add multiple chunks."""
        self.chunks.extend(chunks)
        self._embeddings_matrix = None
    
    def build_embeddings(self):
        """Build embeddings for all chunks."""
        if not self.embedding_provider:
            print("⚠️  No embedding provider configured")
            return
        
        # Get chunks without embeddings
        chunks_to_embed = [c for c in self.chunks if c.embedding is None]
        
        if not chunks_to_embed:
            return
        
        print(f"🔢 Generating embeddings for {len(chunks_to_embed)} chunks...")
        
        texts = [c.content for c in chunks_to_embed]
        embeddings = self.embedding_provider.embed(texts)
        
        for chunk, embedding in zip(chunks_to_embed, embeddings):
            chunk.embedding = embedding
        
        # Build matrix for fast search
        self._build_matrix()
        print("✅ Embeddings ready!")
    
    def _build_matrix(self):
        """Build numpy matrix for fast similarity search."""
        if not self.chunks:
            self._embeddings_matrix = None
            return
        
        embeddings = [c.embedding for c in self.chunks if c.embedding and len(c.embedding) > 0]
        if not embeddings:
            self._embeddings_matrix = None
            return
            
        self._embeddings_matrix = np.array(embeddings)
        
        # Handle NaN values
        self._embeddings_matrix = np.nan_to_num(self._embeddings_matrix, nan=0.0)
        
        # Normalize for cosine similarity
        norms = np.linalg.norm(self._embeddings_matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        self._embeddings_matrix = self._embeddings_matrix / norms
    
    def search(self, query: str, top_k: int = 5, chunk_types: Optional[List[str]] = None) -> List[Tuple[CodeChunk, float]]:
        """
        Search for relevant code chunks.
        
        Args:
            query: Search query
            top_k: Number of results to return
            chunk_types: Filter by chunk types (e.g., ['function', 'class'])
        
        Returns:
            List of (chunk, similarity_score) tuples
        """
        if not self.embedding_provider or self._embeddings_matrix is None or len(self._embeddings_matrix) == 0:
            # Fallback to keyword search
            return self._keyword_search(query, top_k, chunk_types)
        
        # Get query embedding
        query_embedding = np.array(self.embedding_provider.embed_single(query))
        
        # Handle zero norm (avoid division by zero)
        norm = np.linalg.norm(query_embedding)
        if norm == 0 or np.isnan(norm):
            return self._keyword_search(query, top_k, chunk_types)
        query_embedding = query_embedding / norm
        
        # Compute similarities
        similarities = np.dot(self._embeddings_matrix, query_embedding)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1]
        
        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            
            # Filter by chunk type if specified
            if chunk_types and chunk.chunk_type not in chunk_types:
                continue
            
            results.append((chunk, float(similarities[idx])))
            
            if len(results) >= top_k:
                break
        
        return results
    
    def _keyword_search(self, query: str, top_k: int, chunk_types: Optional[List[str]] = None) -> List[Tuple[CodeChunk, float]]:
        """Fallback keyword-based search."""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_chunks = []
        for chunk in self.chunks:
            if chunk_types and chunk.chunk_type not in chunk_types:
                continue
            
            content_lower = chunk.content.lower()
            
            # Simple scoring: count matching words
            score = sum(1 for word in query_words if word in content_lower)
            
            # Boost for exact phrase match
            if query_lower in content_lower:
                score += 5
            
            if score > 0:
                scored_chunks.append((chunk, score))
        
        # Sort by score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        return scored_chunks[:top_k]
    
    def get_context_for_query(self, query: str, max_tokens: int = 4000) -> str:
        """
        Get relevant code context for a query.
        Returns formatted string of relevant code chunks.
        """
        results = self.search(query, top_k=10)
        
        context_parts = []
        total_chars = 0
        char_limit = max_tokens * 4  # Rough estimate
        
        for chunk, score in results:
            chunk_text = f"=== {chunk.file_path} ({chunk.chunk_type}) ===\n{chunk.content}\n"
            
            if total_chars + len(chunk_text) > char_limit:
                break
            
            context_parts.append(chunk_text)
            total_chars += len(chunk_text)
        
        return "\n".join(context_parts)
    
    def save(self, path: str):
        """Save vector store to disk."""
        data = {
            'chunks': [
                {
                    'id': c.id,
                    'content': c.content,
                    'file_path': c.file_path,
                    'chunk_type': c.chunk_type,
                    'start_line': c.start_line,
                    'end_line': c.end_line,
                    'metadata': c.metadata,
                    'embedding': c.embedding
                }
                for c in self.chunks
            ]
        }
        with open(path, 'w') as f:
            json.dump(data, f)
    
    def load(self, path: str):
        """Load vector store from disk."""
        with open(path, 'r') as f:
            data = json.load(f)
        
        self.chunks = [
            CodeChunk(
                id=c['id'],
                content=c['content'],
                file_path=c['file_path'],
                chunk_type=c['chunk_type'],
                start_line=c.get('start_line', 0),
                end_line=c.get('end_line', 0),
                metadata=c.get('metadata', {}),
                embedding=c.get('embedding')
            )
            for c in data['chunks']
        ]
        self._build_matrix()


class CodeChunker:
    """Chunks code files into meaningful segments."""
    
    def __init__(self, repo_dir: str = "cloned_repo"):
        self.repo_dir = Path(repo_dir)
    
    def chunk_repository(self) -> List[CodeChunk]:
        """Chunk all relevant files in the repository."""
        chunks = []
        
        source_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.rb', '.php'}
        config_extensions = {'.json', '.yaml', '.yml', '.toml', '.xml', '.env'}
        doc_extensions = {'.md', '.rst', '.txt'}
        
        ignore_dirs = {'node_modules', '.git', '__pycache__', 'venv', 'env', 'dist', 'build', '.venv', 'vendor'}
        
        for file_path in self.repo_dir.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Skip ignored directories
            if any(ignored in file_path.parts for ignored in ignore_dirs):
                continue
            
            suffix = file_path.suffix.lower()
            rel_path = str(file_path.relative_to(self.repo_dir))
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Skip very large files
                if len(content) > 100000:
                    continue
                
                if suffix in source_extensions:
                    chunks.extend(self._chunk_source_file(rel_path, content, suffix))
                elif suffix in config_extensions or file_path.name.lower() in ['dockerfile', 'makefile', 'gemfile']:
                    chunks.extend(self._chunk_config_file(rel_path, content))
                elif suffix in doc_extensions:
                    chunks.extend(self._chunk_doc_file(rel_path, content))
                    
            except Exception as e:
                continue
        
        return chunks
    
    def _chunk_source_file(self, file_path: str, content: str, suffix: str) -> List[CodeChunk]:
        """Chunk a source code file into functions/classes."""
        chunks = []
        
        if suffix == '.py':
            chunks.extend(self._chunk_python(file_path, content))
        elif suffix in {'.js', '.ts', '.jsx', '.tsx'}:
            chunks.extend(self._chunk_javascript(file_path, content))
        else:
            # Generic chunking for other languages
            chunks.extend(self._chunk_generic(file_path, content, 'module'))
        
        return chunks
    
    def _chunk_python(self, file_path: str, content: str) -> List[CodeChunk]:
        """Chunk Python file into functions and classes."""
        import re
        chunks = []
        lines = content.split('\n')
        
        # Find class definitions
        class_pattern = r'^class\s+(\w+)'
        func_pattern = r'^(?:async\s+)?def\s+(\w+)'
        
        current_chunk = []
        current_type = 'module'
        current_name = file_path
        current_start = 0
        
        for i, line in enumerate(lines):
            class_match = re.match(class_pattern, line)
            func_match = re.match(func_pattern, line)
            
            if class_match or func_match:
                # Save previous chunk if substantial
                if current_chunk and len('\n'.join(current_chunk)) > 50:
                    chunks.append(CodeChunk(
                        id=self._make_id(file_path, current_name),
                        content='\n'.join(current_chunk),
                        file_path=file_path,
                        chunk_type=current_type,
                        start_line=current_start,
                        end_line=i,
                        metadata={'name': current_name}
                    ))
                
                current_chunk = [line]
                current_start = i
                
                if class_match:
                    current_type = 'class'
                    current_name = class_match.group(1)
                else:
                    current_type = 'function'
                    current_name = func_match.group(1)
            else:
                current_chunk.append(line)
        
        # Save last chunk
        if current_chunk and len('\n'.join(current_chunk)) > 50:
            chunks.append(CodeChunk(
                id=self._make_id(file_path, current_name),
                content='\n'.join(current_chunk),
                file_path=file_path,
                chunk_type=current_type,
                start_line=current_start,
                end_line=len(lines),
                metadata={'name': current_name}
            ))
        
        # If no chunks found, add whole file as module
        if not chunks and len(content) > 50:
            chunks.append(CodeChunk(
                id=self._make_id(file_path, 'module'),
                content=content[:5000],  # Limit size
                file_path=file_path,
                chunk_type='module',
                metadata={'name': file_path}
            ))
        
        return chunks
    
    def _chunk_javascript(self, file_path: str, content: str) -> List[CodeChunk]:
        """Chunk JavaScript/TypeScript file."""
        import re
        chunks = []
        
        # Find exported functions and classes
        patterns = [
            (r'export\s+(?:default\s+)?(?:async\s+)?function\s+(\w+)', 'function'),
            (r'export\s+(?:default\s+)?class\s+(\w+)', 'class'),
            (r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', 'function'),
            (r'(?:const|let|var)\s+(\w+)\s*=\s*function', 'function'),
        ]
        
        for pattern, chunk_type in patterns:
            for match in re.finditer(pattern, content):
                name = match.group(1)
                start = match.start()
                
                # Find the end of the function/class (simplified)
                end = self._find_block_end(content, start)
                chunk_content = content[start:end]
                
                if len(chunk_content) > 50:
                    chunks.append(CodeChunk(
                        id=self._make_id(file_path, name),
                        content=chunk_content[:3000],
                        file_path=file_path,
                        chunk_type=chunk_type,
                        metadata={'name': name}
                    ))
        
        # If no chunks found, add whole file
        if not chunks and len(content) > 50:
            chunks.append(CodeChunk(
                id=self._make_id(file_path, 'module'),
                content=content[:5000],
                file_path=file_path,
                chunk_type='module',
                metadata={'name': file_path}
            ))
        
        return chunks
    
    def _find_block_end(self, content: str, start: int) -> int:
        """Find the end of a code block (simplified brace matching)."""
        brace_count = 0
        in_block = False
        
        for i in range(start, min(start + 5000, len(content))):
            char = content[i]
            if char == '{':
                brace_count += 1
                in_block = True
            elif char == '}':
                brace_count -= 1
                if in_block and brace_count == 0:
                    return i + 1
        
        return min(start + 2000, len(content))
    
    def _chunk_generic(self, file_path: str, content: str, chunk_type: str) -> List[CodeChunk]:
        """Generic chunking by size."""
        chunks = []
        
        # Split into ~1000 char chunks with overlap
        chunk_size = 1000
        overlap = 100
        
        for i in range(0, len(content), chunk_size - overlap):
            chunk_content = content[i:i + chunk_size]
            if len(chunk_content) > 50:
                chunks.append(CodeChunk(
                    id=self._make_id(file_path, str(i)),
                    content=chunk_content,
                    file_path=file_path,
                    chunk_type=chunk_type,
                    metadata={'offset': i}
                ))
        
        return chunks
    
    def _chunk_config_file(self, file_path: str, content: str) -> List[CodeChunk]:
        """Chunk configuration files."""
        return [CodeChunk(
            id=self._make_id(file_path, 'config'),
            content=content[:5000],
            file_path=file_path,
            chunk_type='config',
            metadata={'name': file_path}
        )]
    
    def _chunk_doc_file(self, file_path: str, content: str) -> List[CodeChunk]:
        """Chunk documentation files."""
        # Split by headers for markdown
        if file_path.endswith('.md'):
            import re
            sections = re.split(r'\n(?=#{1,3}\s)', content)
            chunks = []
            
            for i, section in enumerate(sections):
                if len(section.strip()) > 50:
                    chunks.append(CodeChunk(
                        id=self._make_id(file_path, str(i)),
                        content=section[:2000],
                        file_path=file_path,
                        chunk_type='doc',
                        metadata={'section': i}
                    ))
            
            return chunks
        
        return [CodeChunk(
            id=self._make_id(file_path, 'doc'),
            content=content[:5000],
            file_path=file_path,
            chunk_type='doc',
            metadata={'name': file_path}
        )]
    
    def _make_id(self, file_path: str, name: str) -> str:
        """Generate unique ID for a chunk."""
        return hashlib.md5(f"{file_path}:{name}".encode()).hexdigest()[:12]


def create_embedding_provider(provider_type: str = "local", model: Optional[str] = None, api_key: Optional[str] = None) -> EmbeddingProvider:
    """
    Factory function to create embedding provider.
    
    Args:
        provider_type: 'local', 'openai', or 'ollama'
        model: Model name (optional)
        api_key: API key for OpenAI
    """
    if provider_type == "local":
        return LocalEmbeddingProvider(model or "all-MiniLM-L6-v2")
    elif provider_type == "openai":
        return OpenAIEmbeddingProvider(model or "text-embedding-3-small", api_key)
    elif provider_type == "ollama":
        return OllamaEmbeddingProvider(model or "nomic-embed-text")
    else:
        raise ValueError(f"Unknown embedding provider: {provider_type}")
