# Enhanced Email Verification System Documentation

## Overview
This document explains the enhanced email verification system in the Alpha-Auth project that includes temporary user storage and email verification status tracking.

## Key Improvements

### 1. Dual Database Structure
- **Main User Table (`users`)**: Stores verified users with `is_verified` status field
- **Temporary User Table (`temp_users`)**: Stores unverified users with expiration time

### 2. Enhanced User Model
- Added `is_verified` Boolean field to track email verification status
- Added `created_at` and `updated_at` timestamps
- Temporary users have `expires_at` field for automatic cleanup

### 3. Registration Flow
1. New users register and are stored in `temp_users` table (not in main `users` table)
2. OTP is sent to verify their email address
3. Upon successful OTP verification, user is moved from `temp_users` to `users` table
4. User account becomes active with `is_verified = True`

### 4. Duplicate Registration Handling
- If a user attempts to register again with the same email before verification:
  - The old temporary record is deleted
  - A new temporary record is created
  - A new OTP is sent
  - This effectively resets the verification process

### 5. Login Security
- Users in the temporary table cannot log in
- Unverified users in the main table cannot log in
- Only verified users can successfully log in

## Database Schema Changes

### Main User Table (`users`)
```
- id: Integer (Primary Key)
- name: String(100)
- email: String(100) (Unique, Indexed)
- hashed_password: String(255)
- is_verified: Boolean (Default: False)
- created_at: DateTime (Default: UTC Now)
- updated_at: DateTime (Default: UTC Now, On Update: Now)
```

### Temporary User Table (`temp_users`)
```
- id: Integer (Primary Key)
- name: String(100)
- email: String(100) (Unique, Indexed)
- hashed_password: String(255)
- created_at: DateTime (Default: UTC Now)
- expires_at: DateTime (Not Null)
```

## API Endpoints

### 1. User Registration: `POST /auth/register`
**Before**: Created user directly in main table and sent welcome email
**After**: Creates user in temp table and sends OTP verification email

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Response** (Success - 200):
```json
{
  "message": "Please verify your email using the OTP sent to your email",
  "email": "john@example.com"
}
```

### 2. OTP Verification: `POST /auth/verify-otp`
**Before**: Just verified the OTP
**After**: Verifies OTP and moves user from temp to main table

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
  "message": "Email verified successfully! Registration completed.",
  "email": "user@example.com",
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

### 3. Complete Registration: `POST /auth/complete-registration`
Alternative endpoint for completing registration after OTP verification

### 4. User Login: `POST /auth/login`
**Enhanced**: Now checks if user is verified before allowing login

## Security Features

### 1. Temp User Expiration
- Temporary user records expire after 60 minutes by default
- A cleanup function can be called periodically to remove expired records

### 2. Verification Requirement
- Users must verify their email before logging in
- Unverified users in main table cannot log in
- Temp users cannot log in at all

### 3. Process Reset
- If user registers again with same email, previous temp record is removed
- New registration process starts fresh

## Data Integrity

### 1. Email Uniqueness
- Email must be unique across both main and temporary user tables
- Prevents duplicate registrations

### 2. Automatic Cleanup
- Expired temporary user records are automatically removed
- Prevents database bloat

## Integration Notes

### 1. Existing Features
- Password reset functionality remains unchanged
- All other authentication features continue to work as before

### 2. Email Templates
- Uses existing `otp_verfication.html` template
- Updated registration flow sends OTP verification email instead of welcome email

## Error Handling

### Registration with Existing Email
- If email exists in main users: Returns 400 "User already exists"
- If email exists in temp users: Deletes old temp user, creates new one

### Login with Unverified Account
- If user exists in main table but is not verified: Returns 401 "Please verify your email address before logging in"
- If user exists only in temp table: Returns 401 "Please verify your email address before logging in"

## Example Flow

1. User registers with email `test@example.com`
2. User record created in `temp_users` table
3. OTP is sent to `test@example.com`
4. User enters OTP via `/auth/verify-otp`
5. If OTP is valid, user is moved from `temp_users` to `users` table with `is_verified = True`
6. User receives JWT token and can now log in successfully

## Benefits

1. **Enhanced Security**: Ensures valid email addresses before full account access
2. **Resource Management**: Temporary records are automatically cleaned up
3. **User Experience**: Clear verification process with proper error messages
4. **Data Integrity**: Prevents duplicate emails and maintains clean user database