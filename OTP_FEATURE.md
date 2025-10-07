# OTP Verification Feature Documentation

## Overview
This document explains the OTP (One-Time Password) verification feature added to the Alpha-Auth project.

## Features Added

### 1. OTP Generation and Validation Utility (`utils/otp_service.py`)
- `generate_otp(length: int = 6)` - Generates a random numeric OTP code
- `is_otp_valid(otp_code: str, expiration_time: datetime, valid_duration: int = 10)` - Validates OTP against expiration time

### 2. Data Model (`models.py`)
- Added `OTP` model with fields:
  - `id`: Primary key
  - `email`: Email associated with the OTP
  - `otp_code`: The OTP code
  - `created_at`: When the OTP was created
  - `expires_at`: When the OTP expires

### 3. CRUD Operations (`app/crud/crud_otp.py`)
- `create_otp(db, email, otp_code, valid_duration)` - Creates a new OTP record
- `get_otp_by_email_and_code(db, email, otp_code)` - Retrieves OTP record if valid
- `delete_otp(db, email)` - Deletes OTP record for an email

### 4. API Endpoints (`auth/routes.py`)

#### Request OTP: `POST /auth/request-otp`
**Description**: Generates and sends an OTP to the user's email

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (Success - 200):
```json
{
  "message": "OTP sent to your email",
  "email": "user@example.com"
}
```

**Response** (Error - 404):
```json
{
  "detail": "User not found"
}
```

#### Verify OTP: `POST /auth/verify-otp`
**Description**: Verifies the OTP code entered by the user

**Request Body**:
```json
{
  "email": "user@example.com",
  "otp_code": "123456"
}
```

**Response** (Success - 200):
```json
{
  "message": "OTP verified successfully",
  "email": "user@example.com"
}
```

**Response** (Error - 400):
```json
{
  "detail": "Invalid or expired OTP"
}
```

## Email Template
The system uses the existing `app/templates/email/otp_verfication.html` template to send OTP emails.

## Security Features
- OTP codes are stored temporarily with an expiration time (default 10 minutes)
- Old OTP codes for the same email are automatically replaced
- OTP records are deleted after successful verification
- OTP validation happens both by code and expiration time

## Usage Example

### 1. Request OTP
```bash
curl -X POST http://localhost:8000/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

### 2. Verify OTP
```bash
curl -X POST http://localhost:8000/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp_code": "123456"
  }'
```

## Integration with Existing System
- The OTP system integrates with the existing user database
- Uses the same email service configuration as other features
- Respects existing user authentication patterns

## Error Handling
- Invalid email addresses return a 404 error
- Expired or incorrect OTP codes return a 400 error
- Server email sending failures return a 500 error

## Time-to-Live (TTL)
- OTP codes are valid for 10 minutes by default
- This can be customized by changing the `valid_duration` parameter
- After the TTL, the code becomes invalid and cannot be used