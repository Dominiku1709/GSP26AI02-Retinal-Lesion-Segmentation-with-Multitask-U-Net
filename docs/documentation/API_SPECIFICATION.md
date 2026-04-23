# OCT Image Analysis API - OpenAPI Specification

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

None (for prototype). Add JWT in production.

---

## Endpoints

### 1. Analyze OCT Image

**Endpoint:** `POST /analyze`

**Purpose:** Upload and analyze an OCT image for lesion detection.

**Request:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | `File` | Yes | OCT image (PNG, JPG, JPEG, TIFF) |

**Allowed File Types:**
- `image/png` (.png)
- `image/jpeg` (.jpg, .jpeg)
- `image/tiff` (.tiff, .tif)

**File Size Limit:** 50MB (configurable)

**Example:**

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@oct_image.png"
```

**Response (200 OK):**

```json
{
  "label": "Drusen",
  "confidence": 0.92,
  "mask_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
}
```

**Response Schema:**

```typescript
{
  label: string;           // Lesion type: "Normal", "Drusen", "CNV", "Geographic Atrophy"
  confidence: number;      // Confidence score [0.0, 1.0]
  mask_base64: string;     // Base64-encoded PNG segmentation mask
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `Bad Request` | Invalid file type, unsupported extension, or file exceeds size limit |
| 422 | `Unprocessable Entity` | Missing required file field |
| 500 | `Internal Server Error` | Preprocessing, inference, or database error |

**Example Error Response (400):**

```json
{
  "detail": "Invalid file type. Allowed: png, jpg, jpeg, tiff, tif"
}
```

---

### 2. Health Check

**Endpoint:** `GET /health`

**Purpose:** Verify API availability and component health.

**Request:** None

**Example:**

```bash
curl http://localhost:8000/api/v1/health
```

**Response (200 OK):**

```json
{
  "status": "healthy",
  "app_name": "OCT Image Analysis API",
  "version": "1.0.0",
  "database": "connected",
  "model_available": true
}
```

**Response Schema:**

```typescript
{
  status: "healthy" | "unhealthy";
  app_name: string;
  version: string;
  database: "connected" | "disconnected";
  model_available: boolean;
}
```

---

### 3. Get All Scans

**Endpoint:** `GET /scans`

**Purpose:** Retrieve paginated list of analyzed scans.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `integer` | 100 | Max results to return (1-1000) |
| `offset` | `integer` | 0 | Number of results to skip |

**Example:**

```bash
curl "http://localhost:8000/api/v1/scans?limit=10&offset=0"
```

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "filename": "oct_001.png",
    "lesion_type": "Drusen",
    "confidence": 0.92,
    "created_at": "2024-01-15T10:30:45.123456"
  },
  {
    "id": 2,
    "filename": "oct_002.png",
    "lesion_type": "Normal",
    "confidence": 0.87,
    "created_at": "2024-01-15T10:32:12.654321"
  }
]
```

**Response Schema:**

```typescript
Array<{
  id: number;
  filename: string;
  lesion_type: string;
  confidence: number;
  created_at: string;  // ISO 8601 datetime
}>
```

---

### 4. Get Specific Scan by ID

**Endpoint:** `GET /scans/{scan_id}`

**Purpose:** Retrieve a specific scan result by database ID.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `scan_id` | `integer` | Database ID of the scan |

**Example:**

```bash
curl http://localhost:8000/api/v1/scans/1
```

**Response (200 OK):**

```json
{
  "id": 1,
  "filename": "oct_001.png",
  "lesion_type": "Drusen",
  "confidence": 0.92,
  "created_at": "2024-01-15T10:30:45.123456"
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 404 | `Not Found` | Scan with specified ID does not exist |

**Example Error Response (404):**

```json
{
  "detail": "Scan with id 9999 not found"
}
```

---

### 5. Get Scan by Filename

**Endpoint:** `GET /scans/filename/{filename}`

**Purpose:** Retrieve scan result by uploaded filename.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | `string` | Original uploaded filename |

**Example:**

```bash
curl "http://localhost:8000/api/v1/scans/filename/oct_image.png"
```

**Response (200 OK):**

```json
{
  "id": 1,
  "filename": "oct_image.png",
  "lesion_type": "CNV",
  "confidence": 0.88,
  "created_at": "2024-01-15T10:30:45.123456"
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 404 | `Not Found` | Scan with specified filename does not exist |

---

## Data Types

### OCTScan

Database record for a single analyzed image.

```typescript
{
  id: number;              // Auto-incremented primary key
  filename: string;        // Original uploaded filename (unique)
  lesion_type: string;     // Classification label
  confidence: number;      // Confidence score [0.0, 1.0]
  created_at: string;      // ISO 8601 timestamp (UTC)
}
```

### AnalysisResponse

Response from image analysis endpoint.

```typescript
{
  label: string;           // Predicted lesion type
  confidence: number;      // Confidence score [0.0, 1.0]
  mask_base64: string;     // Base64-encoded PNG image
}
```

### HealthCheckResponse

API health status.

```typescript
{
  status: string;          // "healthy" or "unhealthy"
  app_name: string;        // Application name
  version: string;         // API version
  database: string;        // Database connection status
  model_available: boolean; // Is ONNX model loaded?
}
```

---

## Error Handling

All errors follow the same format:

```json
{
  "detail": "Human-readable error message"
}
```

### Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 404 | Not Found (resource doesn't exist) |
| 422 | Validation Error (missing/malformed fields) |
| 500 | Internal Server Error (unexpected error) |

---

## Rate Limiting

**Not implemented for prototype.**

Recommended for production:
- 100 requests per minute per IP
- 1000 requests per day per user

---

## CORS

**Allowed Origins (configurable):**
- `http://localhost:3000`
- `http://localhost:5173`

Add more origins in `.env`:

```
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173", "https://your-domain.com"]
```

---

## Request/Response Examples

### Python (requests)

```python
import requests
import base64

# Analyze image
with open("oct_image.png", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        files={"file": f}
    )

result = response.json()
print(f"Label: {result['label']}")
print(f"Confidence: {result['confidence']:.2%}")

# Save mask
mask_bytes = base64.b64decode(result['mask_base64'])
with open("mask.png", "wb") as f:
    f.write(mask_bytes)

# Get scan history
scans = requests.get("http://localhost:8000/api/v1/scans?limit=5").json()
for scan in scans:
    print(f"{scan['filename']}: {scan['lesion_type']} ({scan['confidence']:.2%})")
```

### JavaScript (fetch)

```javascript
// Analyze image
const formData = new FormData();
formData.append("file", imageFile);

const response = await fetch(
  "http://localhost:8000/api/v1/analyze",
  { method: "POST", body: formData }
);

const result = await response.json();
console.log(`Label: ${result.label}`);
console.log(`Confidence: ${(result.confidence * 100).toFixed(1)}%`);

// Display mask
const img = document.createElement("img");
img.src = `data:image/png;base64,${result.mask_base64}`;
document.body.appendChild(img);

// Get scans
const scans = await fetch("http://localhost:8000/api/v1/scans?limit=5")
  .then(r => r.json());
scans.forEach(scan => {
  console.log(`${scan.filename}: ${scan.lesion_type}`);
});
```

### cURL

```bash
# Analyze
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@image.png" | jq

# Health check
curl http://localhost:8000/api/v1/health | jq

# Get scans
curl "http://localhost:8000/api/v1/scans?limit=5" | jq

# Get specific scan
curl http://localhost:8000/api/v1/scans/1 | jq

# Get by filename
curl "http://localhost:8000/api/v1/scans/filename/image.png" | jq
```

---

## OpenAPI/Swagger

**Interactive API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## Versioning

Current API Version: **v1**

Future versions accessible at `/api/v2/`, etc.

---

## WebSocket Support

Not implemented (prototype uses REST).

For real-time updates, consider:
- Server-Sent Events (SSE)
- WebSocket endpoint for streaming inference

---

## Pagination

Supported on `/scans` endpoint:

```bash
# First page
curl "http://localhost:8000/api/v1/scans?limit=10&offset=0"

# Next page
curl "http://localhost:8000/api/v1/scans?limit=10&offset=10"

# Last page
curl "http://localhost:8000/api/v1/scans?limit=10&offset=1000"
```

---

## Filtering

Not implemented for prototype.

Future enhancement:
- Filter by lesion type: `?lesion_type=Drusen`
- Filter by confidence: `?confidence_min=0.8`
- Filter by date: `?created_after=2024-01-15`

---

## Sorting

Not implemented for prototype.

Current sort: By `created_at` descending (newest first)

---

## Batch Operations

Not implemented for prototype.

**Consider for production:**
- Batch analysis: `POST /analyze/batch` (multiple files)
- Bulk export: `GET /scans/export?format=csv`

---

## Deprecation Policy

API version changes will follow semver:
- **v1.x.y**: Minor changes (backward compatible)
- **v2.x.x**: Major changes (breaking)

Deprecation notice: 3 months before breaking changes

---

## Service Level Agreement (SLA)

**For Production:**
- Uptime: 99.9%
- Response time: <500ms (p95)
- Error rate: <0.1%

---

## Support Channels

- GitHub Issues: [link]
- Email: [support@example.com]
- Slack: [#api-support]

---

**API Specification Version: 1.0**  
**Last Updated: 2024-01-15**
