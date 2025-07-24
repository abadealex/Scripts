# 📘 API Reference (v1)

**Base URL:** `/api/v1`

---

## 🔐 Authentication

### POST `/auth/login`
Authenticate a user and return a JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "jwt.token.here"
}
```

---

### POST `/auth/register`
Register a new user account.

**Request:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "securePassword"
}
```

**Response:**
```json
{
  "message": "Registration successful"
}
```

---

## 📄 Submissions

### GET `/submissions`
List all submissions for the authenticated user.

**Response:**
```json
[
  {
    "id": "sub_123",
    "created_at": "2025-07-10T10:15:00Z",
    "status": "graded"
  }
]
```

---

### POST `/submissions`
Upload a new submission for grading.

**Request (multipart/form-data):**
- `file`: PDF or image of submission
- `assignment_id`: string

**Response:**
```json
{
  "submission_id": "sub_456",
  "status": "queued"
}
```

---

### GET `/submissions/<id>`
Get a specific submission’s details.

**Response:**
```json
{
  "id": "sub_456",
  "status": "graded",
  "score": 89,
  "feedback_id": "fb_789"
}
```

---

## 🤖 Grading

### POST `/grading/score`
Submit answers to be graded by the AI.

**Request:**
```json
{
  "submission_id": "sub_456"
}
```

**Response:**
```json
{
  "score": 87,
  "feedback": "Great job! Minor arithmetic mistakes on question 3."
}
```

---

## 💬 Feedback

### GET `/feedback/<submission_id>`
Fetch feedback for a given submission.

**Response:**
```json
{
  "feedback_id": "fb_789",
  "comments": [
    "Question 1: Excellent explanation.",
    "Question 3: Incorrect unit conversion."
  ]
}
```

---

## 💳 Billing

### GET `/billing/status`
Returns the user's subscription status and plan.

**Response:**
```json
{
  "plan": "pro",
  "renewal_date": "2025-08-01",
  "is_active": true
}
```

---

### POST `/billing/webhook`
Stripe webhook handler (internal use only).

**Note:** Verifies Stripe signature and updates subscription status.

---

## 🧪 Health Check

### GET `/healthz`
Returns API health status.

**Response:**
```json
{
  "status": "ok",
  "uptime": "104h 22m"
}
```
