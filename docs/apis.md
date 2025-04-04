# API Documentation

## Index
1. [Base URL](#base-url)
2. [Endpoints](#endpoints)
   - [Check Connection](#1-check-connection)
   - [Get Connection Stats](#2-get-connection-stats)
   - [Chat with AI](#3-chat-with-ai)
3. [Notes](#notes)

---

## Base URL
```
http://localhost:5000
```

---

## Endpoints

### 1. Check Connection
**Endpoint:** `GET /api/connection`

**Description:** Checks the connection to the local Ollama server.

**Response:**
- **200 OK** - Server is reachable.
- **404 ERROR** - Server is unreachable.

**Example Response:**
```json
{
  "host": "localhost",
  "port": 11434,
  "status": "OK"
}
```

---

### 2. Get Connection Stats
**Endpoint:** `GET /api/connection/stats`

**Description:** Returns available and active AI models.

**Response:**
- **200 OK** - Returns list of models.
- **404 ERROR** - No models found.

**Example Response:**
```json
{
  "available": ["model1", "model2"],
  "active": ["model1"]
}
```

---

### 3. Chat with AI
**Endpoint:** `POST /api/chat`

**Description:** Sends a chat request to the AI model and returns a response. Ensure that the selected model is available before making a request.

**Request Body:**
```json
{
  "model": "model_name",
  "prompt": "Hello AI!"
}
```

**Response:**
- **200 OK** - Successful response from AI.
- **400 ERROR** - Invalid request data.

**Example Response:**
```json
{
  "response": "Hello, how can I assist you today?"
}
```

---

## Notes
- The Ollama server is expected to be running on `http://localhost:11434`.
- Requests to `/api/chat` are processed asynchronously using a queue.

