# Conversational AI Chatbot

This project implements a minimal conversational AI service using a lightweight, instruction-tuned model that can run efficiently on a CPU. The chatbot supports multiple languages (English and French) and is accessible via a RESTful API built with FastAPI. It also maintains conversational context using in-memory sessions.

---

## Table of Contents

1. [Design Decisions](#design-decisions)  
2. [Setup & Installation](#setup--installation)  
   - [Windows (PowerShell)](#windows-powershell)  
   - [macOS/Linux](#macoslinux)  
3. [Running the API Server](#running-the-api-server)  
4. [API Usage](#api-usage)  
   - [Swagger UI](#swagger-ui)  
   - [cURL Examples](#curl-examples)  
   - [Postman Collection](#postman-collection)  
5. [Running Tests](#running-tests)  
6. [Manual QA-Style Test Cases](#manual-qa-style-test-cases)  
7. [Project Structure](#project-structure)  
8. [Additional Notes](#additional-notes)  

---

## Design Decisions

- **Model Selection & Setup**  
  - `google/flan-t5-small` is used for instruction following. This model is small (~60M parameters) and can run on CPU with ~8GB RAM.  
  - A system prompt instructs the model to act as a “helpful Saloon assistant” for booking appointments (haircut/facial from 10AM to 8PM).

- **REST API Development**  
  - Built with **FastAPI**, which automatically generates interactive documentation at `/docs`.  
  - A single endpoint `POST /chat` accepts `conversation_id`, `messages`, and an optional `language` parameter.

- **Generative Response Requirements**  
  1. **Instruction Following:** The system prompt is prepended to each conversation.  
  2. **Multi-Language Output:** If `language` is `"fr"`, a French instruction is added; otherwise, the response is in English.  
  3. **Conversational Context:** In-memory session management stores conversation history by `conversation_id`.

- **Documentation & Testing**  
  - This **README.md** is with complete setup, usage, and examples.  
  - **Unit tests** with pytest to validate endpoint behavior.

---

## Setup & Installation

### Prerequisites

- Python 3.8+  
- [pip](https://pip.pypa.io/en/stable/installation/)

Ensure you have a virtual environment or an isolated environment to avoid dependency conflicts.

### Windows (PowerShell)

1. **Create a Virtual Environment**  
    ```
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
    If you see an execution policy error, run:
    ```
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```

2. **Install Dependencies**  
    ```
    pip install -r requirements.txt
    ```

### macOS/Linux

1. **Create a Virtual Environment**  
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```

2. **Install Dependencies**  
    ```
    pip install -r requirements.txt
    ```

---

## Running the API Server

From the project root (where `app/main.py` is located), run:

uvicorn app.main:app --reload


- This starts the FastAPI server at [http://127.0.0.1:8000](http://127.0.0.1:8000).  
- Swagger documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## API Usage

### Swagger UI

1. Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your web browser.  
2. Expand the `POST /chat` endpoint.  
3. Click **“Try it out”** to send a test request.

### cURL Examples

**English (Windows PowerShell)**:
curl -X POST "http://127.0.0.1:8000/chat" ^ -H "Content-Type: application/json" ^ -d "{ "conversation_id": "conv1", "messages": [{"role": "user", "content": "Hello, I need an appointment."}], "language": "en" }"


**French (Windows PowerShell)**:
curl -X POST "http://127.0.0.1:8000/chat" ^ -H "Content-Type: application/json" ^ -d "{ "conversation_id": "conv2", "messages": [{"role": "user", "content": "Bonjour, je voudrais un rendez-vous."}], "language": "fr" }"

### Postman Collection

You can import the following JSON into Postman to quickly test the `/chat` endpoint:

{ "info": { "_postman_id": "12345678-90ab-cdef-1234-567890abcdef", "name": "Conversational AI Chatbot API", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json" }, "item": [ { "name": "Chat Endpoint", "request": { "method": "POST", "header": [ { "key": "Content-Type", "value": "application/json", "type": "text" } ], "body": { "mode": "raw", "raw": "{\n "conversation_id": "conv1",\n "messages": [\n {"role": "user", "content": "Hello, I need an appointment."}\n ],\n "language": "en"\n}" }, "url": { "raw": "http://127.0.0.1:8000/chat", "protocol": "http", "host": [ "127", "0", "0", "1" ], "port": "8000", "path": [ "chat" ] } }, "response": [] } ] }


Save this JSON to `postman_collection.json` and import it into Postman.

---

## Running Tests

1. **Install Pytest** (if not already):
    ```
    pip install pytest
    ```
2. **Run the Tests**:
    ```
    pytest tests/
    ```

### Example Tests (`tests/test_main.py`)

from fastapi.testclient import TestClient from app.main import app

client = TestClient(app)

def test_chat_endpoint_valid(): payload = { "conversation_id": "test123", "messages": [ {"role": "user", "content": "Hello, I need to book an appointment for a haircut."} ], "language": "en" } response = client.post("/chat", json=payload) assert response.status_code == 200 data = response.json() assert data["conversation_id"] == "test123" assert "response" in data assert isinstance(data["response"], str)

def test_chat_endpoint_empty_messages(): payload = { "conversation_id": "test123", "messages": [], "language": "en" } response = client.post("/chat", json=payload) assert response.status_code == 400 assert response.json()["detail"] == "Messages list is empty."

---

## Manual QA-Style Test Cases

Below are sample test cases in a typical QA format:

### Test Case 1
| Field              | Description                                                     |
|--------------------|-----------------------------------------------------------------|
| **Test Case ID**   | TC-001                                                          |
| **Title**          | Valid `/chat` Request (English)                                |
| **Description**    | Ensures the endpoint handles a valid request in English         |
| **Preconditions**  | Server running at `http://127.0.0.1:8000`                       |
| **Steps**          | 1. POST to `/chat` with:<br><br>  {<br>    "conversation_id": "conv1",<br>    "messages": [<br>      {"role": "user", "content": "Hello, I need a haircut appointment."}<br>    ],<br>    "language": "en"<br>  } |
| **Expected Result**| - Status code `200` <br> - JSON includes `"conversation_id": "conv1"` <br> - `"response"` is a non-empty string |
| **Actual Result**  | (Status code `200` <br> - JSON includes `"conversation_id": "conv1"` <br> - `"response"` is a non-empty string)                                               |
| **Status**         | Pass                                                   |

### Test Case 2
| Field              | Description                                                         |
|--------------------|---------------------------------------------------------------------|
| **Test Case ID**   | TC-002                                                              |
| **Title**          | Empty Messages in Request                                          |
| **Description**    | Checks if the endpoint rejects a request with no messages          |
| **Preconditions**  | Server running at `http://127.0.0.1:8000`                           |
| **Steps**          | 1. POST to `/chat` with:<br><br>  {<br>    "conversation_id": "conv2",<br>    "messages": [],<br>    "language": "en"<br>  } |
| **Expected Result**| - Status code `400` <br> - JSON includes `"detail": "Messages list is empty."` |
| **Actual Result**  | (Status code `400` <br> - JSON includes `"detail": "Messages list is empty."`)                                                    |
| **Status**         | Pass                                                          |

### Test Case 3
| Field              | Description                                                                         |
|--------------------|-------------------------------------------------------------------------------------|
| **Test Case ID**   | TC-003                                                                              |
| **Title**          | Valid `/chat` Request (French)                                                      |
| **Description**    | Ensures the endpoint processes a valid request in French                            |
| **Preconditions**  | Server running at `http://127.0.0.1:8000`                                           |
| **Steps**          | 1. POST to `/chat` with:<br><br>  {<br>    "conversation_id": "conv3",<br>    "messages": [<br>      {"role": "user", "content": "Bonjour, je voudrais un rendez-vous pour une coupe de cheveux."}<br>    ],<br>    "language": "fr"<br>  } |
| **Expected Result**| - Status code `200` <br> - JSON includes `"conversation_id": "conv3"` <br> - `"response"` is in French or partially French |
| **Actual Result**  | (Status code `200` <br> - JSON includes `"conversation_id": "conv3"` <br> - `"response"` is in  partially French)                                                                    |
| **Status**         | Pass                                                                         |

---

## Project Structure

ConversationalAIProject/ ├── app/ │ ├── init.py │ └── main.py ├── tests/ │ └── test_main.py ├── README.md └── requirements.txt


---

## Additional Notes

- **Session Management**  
  A global dictionary keyed by `conversation_id` stores conversation history. Using the same `conversation_id` in multiple calls preserves context.

- **Model Limitations**  
  `flan-t5-small` can produce short or repetitive answers. However, it’s sufficient for demonstrating a CPU-friendly, instruction-tuned chatbot.

- **Future Improvements**  
  - we should use a larger or more specialized model if we have more RAM or a GPU.  
  - Store sessions in a database if you need to preserve them across server restarts.  
  - Adjust generation parameters (e.g., `temperature`, `top_p`) or system prompts for more varied responses.
