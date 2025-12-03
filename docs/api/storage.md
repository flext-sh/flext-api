# Storage API Reference

This section covers the HTTP storage and caching system for file uploads, downloads, and distributed storage backends.

## HTTP Storage System

### FlextApiStorage - File Storage Management

Main storage interface for handling file uploads, downloads, and metadata operations.

```python
from flext_api.storage import FlextApiStorage
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

# Create storage instance
storage = FlextApiStorage(
    backend="s3",  # or "local", "gcs", "azure"
    config={
        "bucket": "my-bucket",
        "region": "us-east-1",
        "access_key": "your-access-key",
        "secret_key": "your-secret-key"
    }
)

# Upload file
with open("document.pdf", "rb") as file:
    upload_result = storage.upload_file(
        file=file,
        filename="document.pdf",
        content_type="application/pdf",
        metadata={"author": "John Doe", "category": "documents"}
    )

if upload_result.is_success:
    file_url = upload_result.unwrap()
    print(f"File uploaded: {file_url}")
else:
    print(f"Upload failed: {upload_result.error}")
```

**Key Features:**

- Multiple storage backend support
- Automatic content type detection
- Metadata management
- File versioning
- Access control integration

### Storage Configuration

```python
# Local filesystem storage
local_storage = FlextApiStorage(
    backend="local",
    config={
        "base_path": "/var/app/uploads",
        "allowed_extensions": [".pdf", ".doc", ".docx"],
        "max_file_size": 10 * 1024 * 1024  # 10MB
    }
)

# Amazon S3 storage
s3_storage = FlextApiStorage(
    backend="s3",
    config={
        "bucket": "my-app-bucket",
        "region": "us-east-1",
        "access_key": os.getenv("AWS_ACCESS_KEY"),
        "secret_key": os.getenv("AWS_SECRET_KEY"),
        "cdn_url": "https://cdn.myapp.com"
    }
)

# Google Cloud Storage
gcs_storage = FlextApiStorage(
    backend="gcs",
    config={
        "bucket": "my-app-bucket",
        "project_id": "my-gcp-project",
        "credentials_path": "/path/to/credentials.json"
    }
)
```

## File Operations

### Upload Operations

Upload files with automatic validation and metadata handling.

```python
# Upload from file path
upload_result = storage.upload_from_path(
    local_path="/path/to/document.pdf",
    remote_path="documents/document.pdf",
    content_type="application/pdf"
)

# Upload from bytes
file_bytes = b"file content here"
upload_result = storage.upload_from_bytes(
    data=file_bytes,
    filename="data.txt",
    content_type="text/plain"
)

# Upload with custom metadata
metadata = {
    "author": "Jane Smith",
    "department": "engineering",
    "tags": ["important", "review-needed"]
}

upload_result = storage.upload_file(
    file=open("report.pdf", "rb"),
    filename="report.pdf",
    content_type="application/pdf",
    metadata=metadata
)
```

### Download Operations

Download files with caching and access control.

```python
# Download file
download_result = storage.download_file(
    remote_path="documents/report.pdf",
    local_path="/tmp/downloaded_report.pdf"
)

if download_result.is_success:
    file_path = download_result.unwrap()
    print(f"File downloaded to: {file_path}")

# Download to bytes
download_result = storage.download_to_bytes("documents/report.pdf")
if download_result.is_success:
    file_bytes = download_result.unwrap()
    # Process file bytes
    print(f"Downloaded {len(file_bytes)} bytes")
```

### File Management

List, delete, and manage stored files.

```python
# List files in directory
files_result = storage.list_files("documents/")
if files_result.is_success:
    files = files_result.unwrap()
    for file_info in files:
        print(f"File: {file_info.name}, Size: {file_info.size} bytes")

# Delete file
delete_result = storage.delete_file("documents/old_report.pdf")
if delete_result.is_success:
    print("File deleted successfully")

# Move/rename file
move_result = storage.move_file(
    source_path="documents/report.pdf",
    destination_path="documents/reports/2024/q1_report.pdf"
)
```

## Caching System

### FlextApiCache - Response Caching

HTTP response caching with multiple backend support.

```python
from flext_api.storage import FlextApiCache

# Create cache instance
cache = FlextApiCache(
    backend="redis",  # or "memory", "filesystem"
    config={
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": "cache_password"
    }
)

# Cache responses
@app.get("/users/{user_id}")
@cache.cached(ttl=300)  # Cache for 5 minutes
async def get_user(user_id: str):
    # Expensive database operation
    user = await database.get_user(user_id)
    return UserResponse(**user.dict())

# Manual cache operations
cache.set("user_123", user_data, ttl=300)
cached_data = cache.get("user_123")

if cached_data:
    print(f"Cache hit: {cached_data}")
else:
    print("Cache miss")
```

**Key Features:**

- Multiple cache backend support (Redis, Memory, Filesystem)
- TTL-based expiration
- Cache warming and preloading
- Cache invalidation strategies
- Cache metrics and monitoring

### Cache Strategies

```python
# Time-based caching
@cache.cached(ttl=3600)  # Cache for 1 hour
@app.get("/slow-endpoint")
async def slow_endpoint():
    # Expensive operation
    return {"data": "expensive_result"}

# Conditional caching
@cache.conditional_cache(condition=lambda response: response.status_code == 200)
@app.get("/users")
async def get_users():
    return await user_service.get_all_users()

# Cache with custom key
@cache.cached(key_func=lambda request: f"user_{request.path_params['user_id']}")
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    return await user_service.get_user(user_id)
```

## Distributed Storage

### Multi-Backend Storage

Support for multiple storage backends with failover and load balancing.

```python
from flext_api.storage import MultiBackendStorage

# Configure multiple backends
storage_config = {
    "primary": {
        "backend": "s3",
        "bucket": "primary-bucket",
        "region": "us-east-1"
    },
    "fallback": {
        "backend": "gcs",
        "bucket": "fallback-bucket",
        "project_id": "my-project"
    }
}

# Create multi-backend storage
multi_storage = MultiBackendStorage(storage_config)

# Upload with automatic failover
upload_result = multi_storage.upload_file(
    file=open("important.pdf", "rb"),
    filename="important.pdf"
)

if upload_result.is_success:
    # File uploaded to primary backend
    file_url = upload_result.unwrap()
else:
    # Fallback to secondary backend
    print(f"Upload failed on primary, trying fallback: {upload_result.error}")
```

## File Processing

### FlextFileProcessor - File Processing Pipeline

Process files during upload/download with transformation and validation.

```python
from flext_api.storage import FlextFileProcessor

# Create file processor
processor = FlextFileProcessor()

# Add processing steps
processor.add_processor(ImageResizer(max_width=1920, max_height=1080))
processor.add_processor(ImageOptimizer(quality=85))
processor.add_processor(VirusScanner())

# Process uploaded file
@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    # Process file through pipeline
    processed_result = await processor.process_upload(file)

    if processed_result.is_success:
        processed_file = processed_result.unwrap()

        # Store processed file
        storage_result = await storage.upload_file(
            file=processed_file,
            filename=file.filename,
            content_type=file.content_type
        )

        return {"filename": file.filename, "url": storage_result.unwrap()}
    else:
        raise HTTPException(status_code=400, detail=processed_result.error)
```

**Processing Steps:**

- Image resizing and optimization
- Virus scanning
- Content validation
- Metadata extraction
- Format conversion

## Quality Metrics

| Module                 | Coverage | Status    | Description                     |
| ---------------------- | -------- | --------- | ------------------------------- |
| `storage/__init__.py`  | 92%      | ✅ Stable | Main storage interface          |
| `storage/cache.py`     | 88%      | ✅ Good   | HTTP response caching           |
| `storage/backends.py`  | 85%      | ✅ Good   | Storage backend implementations |
| `storage/processor.py` | 80%      | ✅ Good   | File processing pipeline        |

## Usage Examples

### Complete File Upload System

```python
from flext_api.storage import FlextApiStorage, FlextFileProcessor
from flext_api.middleware import FileUploadMiddleware
from fastapi import UploadFile, File, HTTPException

# Initialize storage and processing
storage = FlextApiStorage(backend="s3", config=s3_config)
processor = FlextFileProcessor()
processor.add_processor(VirusScanner())
processor.add_processor(ImageOptimizer())

# Add upload middleware
upload_middleware = FileUploadMiddleware(
    max_file_size=10 * 1024 * 1024,  # 10MB
    allowed_types=["image/jpeg", "image/png", "application/pdf"]
)
app.add_middleware(upload_middleware)

@app.post("/upload/file")
async def upload_file(file: UploadFile = File(...)):
    """Upload file with processing and storage."""

    # Process file
    processed_result = await processor.process_upload(file)
    if processed_result.is_failure:
        raise HTTPException(status_code=400, detail=processed_result.error)

    processed_file = processed_result.unwrap()

    # Generate unique filename
    import uuid
    file_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1] if "." in file.filename else ""
    remote_filename = f"{file_id}.{extension}"

    # Upload to storage
    storage_result = storage.upload_file(
        file=processed_file,
        filename=remote_filename,
        content_type=file.content_type,
        metadata={
            "original_filename": file.filename,
            "uploaded_by": "user_123",
            "processed": True
        }
    )

    if storage_result.is_failure:
        raise HTTPException(status_code=500, detail="Upload failed")

    file_url = storage_result.unwrap()

    return {
        "filename": file.filename,
        "url": file_url,
        "id": file_id,
        "size": processed_file.size
    }

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    """Download file by ID."""

    # Find file metadata (implement based on your needs)
    file_info = await file_service.get_file_info(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")

    # Download from storage
    download_result = storage.download_to_bytes(file_info.remote_path)

    if download_result.is_failure:
        raise HTTPException(status_code=500, detail="Download failed")

    file_bytes = download_result.unwrap()

    return Response(
        content=file_bytes,
        media_type=file_info.content_type,
        headers={
            "Content-Disposition": f"attachment; filename={file_info.original_filename}"
        }
    )
```

### Caching with Storage Integration

```python
from flext_api.storage import FlextApiStorage, FlextApiCache

# Initialize storage and cache
storage = FlextApiStorage(backend="s3", config=s3_config)
cache = FlextApiCache(backend="redis", config=redis_config)

@app.get("/users/{user_id}/avatar")
@cache.cached(ttl=3600, key_func=lambda r: f"avatar_{r.path_params['user_id']}")
async def get_user_avatar(user_id: str):
    """Get user avatar with caching."""

    # Check cache first
    cache_key = f"avatar_{user_id}"
    cached_avatar = cache.get(cache_key)

    if cached_avatar:
        return Response(content=cached_avatar, media_type="image/jpeg")

    # Fetch from storage if not cached
    avatar_path = f"avatars/{user_id}.jpg"
    download_result = storage.download_to_bytes(avatar_path)

    if download_result.is_success:
        avatar_bytes = download_result.unwrap()

        # Cache for future requests
        cache.set(cache_key, avatar_bytes, ttl=3600)

        return Response(content=avatar_bytes, media_type="image/jpeg")
    else:
        # Return default avatar
        default_avatar = get_default_avatar()
        return Response(content=default_avatar, media_type="image/jpeg")
```

This storage system provides a comprehensive foundation for file management, caching, and distributed storage operations in HTTP applications.
