# API Endpoints Report

## LostAndFound API
Version: v1

### `GET` /api/Admin/reports

**Tags**: Admin

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| ForPublicView | query | `boolean` | No | - |
| Type | query | `string` | No | - |
| Status | query | `string` | No | - |
| Search | query | `string` | No | - |
| CategoryId | query | `integer` | No | - |
| SubCategoryId | query | `integer` | No | - |
| DateFrom | query | `string` | No | - |
| DateTo | query | `string` | No | - |
| Page | query | `integer` | No | - |
| PageSize | query | `integer` | No | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `PUT` /api/Admin/reports/{id}/approve

**Tags**: Admin

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `PUT` /api/Admin/reports/{id}/reject

**Tags**: Admin

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `PUT` /api/Admin/reports/{id}/flag

**Tags**: Admin

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `PUT` /api/Admin/reports/{id}/archive

**Tags**: Admin

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `DELETE` /api/Admin/reports/{id}

**Tags**: Admin

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `PUT` /api/Admin/users/{id}/verify

**Tags**: Admin

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/auth/signup

**Summary**: Create a new user account

**Description**: Registers a new user with email, password, and personal information. A verification code will be sent to the provided email address.

**Tags**: Auth

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `SignupDto`
- **Content-Type**: `text/json`
  - Schema: `SignupDto`
- **Content-Type**: `application/*+json`
  - Schema: `SignupDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/auth/login

**Summary**: Authenticate user and get access token

**Description**: Logs in a user with email and password. Returns a JWT access token for authenticated requests.

**Tags**: Auth

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `LoginDto`
- **Content-Type**: `text/json`
  - Schema: `LoginDto`
- **Content-Type**: `application/*+json`
  - Schema: `LoginDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/auth/google

**Summary**: Sign in with Google

**Description**: Authenticates using a Google ID token (from Google Sign-In on mobile or web). Creates a new user if none exists for this Google account, or links to an existing account by email. Returns the same JWT access token and refresh token as login.

**Tags**: Auth

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `GoogleSignInDto`
- **Content-Type**: `text/json`
  - Schema: `GoogleSignInDto`
- **Content-Type**: `application/*+json`
  - Schema: `GoogleSignInDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/auth/verify-account

**Summary**: Verify user account with verification code

**Description**: Verifies a user's email address using the verification code sent to their email. This endpoint does not require authentication.

**Tags**: Auth

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| code | query | `string` | No | - |
| email | query | `string` | No | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/auth/refresh-token

**Summary**: Refresh access token using a valid refresh token

**Description**: Validates the provided refresh token and issues a new access token and refresh token pair. This allows users to maintain their session without re-authenticating.

**Tags**: Auth

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `RefreshTokenDto`
- **Content-Type**: `text/json`
  - Schema: `RefreshTokenDto`
- **Content-Type**: `application/*+json`
  - Schema: `RefreshTokenDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/auth/forgot-password

**Summary**: Request a password reset email

**Description**: Sends a password reset email with a secure token to the provided email address. The token is valid for 1 hour.

**Tags**: Auth

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `ForgotPasswordDto`
- **Content-Type**: `text/json`
  - Schema: `ForgotPasswordDto`
- **Content-Type**: `application/*+json`
  - Schema: `ForgotPasswordDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/auth/reset-password

**Summary**: Reset password using the token received via email

**Description**: Validates the reset token and updates the user's password. All active refresh tokens are invalidated for security.

**Tags**: Auth

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `ResetPasswordDto`
- **Content-Type**: `text/json`
  - Schema: `ResetPasswordDto`
- **Content-Type**: `application/*+json`
  - Schema: `ResetPasswordDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/auth/change-password

**Summary**: Change password for authenticated user

**Description**: Allows an authenticated user to change their password by providing the current password and a new password. All active refresh tokens are invalidated for security.

**Tags**: Auth

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `ChangePasswordDto`
- **Content-Type**: `text/json`
  - Schema: `ChangePasswordDto`
- **Content-Type**: `application/*+json`
  - Schema: `ChangePasswordDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/auth/resend-verification

**Summary**: Resend account verification code

**Description**: Generates a new verification code and sends it to the user's email address. The code is valid for 24 hours.

**Tags**: Auth

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `ResendVerificationDto`
- **Content-Type**: `text/json`
  - Schema: `ResendVerificationDto`
- **Content-Type**: `application/*+json`
  - Schema: `ResendVerificationDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/auth/logout

**Summary**: Logout user and invalidate refresh token

**Description**: Invalidates the user's refresh token to end the session. Requires authentication.

**Tags**: Auth

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `LogoutDto`
- **Content-Type**: `text/json`
  - Schema: `LogoutDto`
- **Content-Type**: `application/*+json`
  - Schema: `LogoutDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/auth/me

**Summary**: Get current authenticated user

**Description**: Returns the profile information of the currently authenticated user. Requires authentication.

**Tags**: Auth

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/auth/change-email-request

**Summary**: Request email change

**Description**: Initiates an email change request. A verification code will be sent to the new email address. Requires authentication.

**Tags**: Auth

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `ChangeEmailRequestDto`
- **Content-Type**: `text/json`
  - Schema: `ChangeEmailRequestDto`
- **Content-Type**: `application/*+json`
  - Schema: `ChangeEmailRequestDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/auth/change-email-confirm

**Summary**: Confirm email change

**Description**: Confirms the email change using the verification code sent to the new email. All active sessions will be invalidated. Requires authentication.

**Tags**: Auth

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `ChangeEmailConfirmDto`
- **Content-Type**: `text/json`
  - Schema: `ChangeEmailConfirmDto`
- **Content-Type**: `application/*+json`
  - Schema: `ChangeEmailConfirmDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `DELETE` /api/auth/delete-account

**Summary**: Delete user account

**Description**: Permanently deletes the user's account (soft delete). Requires password confirmation for security. Requires authentication.

**Tags**: Auth

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `DeleteAccountDto`
- **Content-Type**: `text/json`
  - Schema: `DeleteAccountDto`
- **Content-Type**: `application/*+json`
  - Schema: `DeleteAccountDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Categories

**Summary**: Get all categories

**Description**: Retrieves a flat list of all categories without nested SubCategories. Returns only basic category information (Id, Name, Description, SubCategoryCount) for lightweight responses. Requires authentication.

**Tags**: Categories

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/Categories

**Summary**: Create a new category

**Description**: Creates a new category in the system. This endpoint is restricted to Admin users only. Requires Admin role.

**Tags**: Categories

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `CreateCategoryDto`
- **Content-Type**: `text/json`
  - Schema: `CreateCategoryDto`
- **Content-Type**: `application/*+json`
  - Schema: `CreateCategoryDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Categories/tree

**Summary**: Get all categories along with their subcategories

**Description**: Retrieves the full hierarchical category tree with nested SubCategories. Returns complete parent-child relationships for building tree structures. Requires authentication.

**Tags**: Categories

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Categories/mapping

**Summary**: Get category-subcategory mapping for mobile

**Description**: Returns a flat list of all category-subcategory-id mappings for mobile app dropdowns. Public endpoint - no authentication required.

**Tags**: Categories

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Categories/{id}

**Summary**: Get category by ID

**Description**: Retrieves a single category by its ID with basic information. Requires authentication.

**Tags**: Categories

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `PUT` /api/Categories/{id}

**Summary**: Update category

**Description**: Updates an existing category's information. This endpoint is restricted to Admin users only. Requires Admin role.

**Tags**: Categories

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `UpdateCategoryDto`
- **Content-Type**: `text/json`
  - Schema: `UpdateCategoryDto`
- **Content-Type**: `application/*+json`
  - Schema: `UpdateCategoryDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `DELETE` /api/Categories/{id}

**Summary**: Delete category

**Description**: Deletes a category from the system. Categories with existing subcategories cannot be deleted. This endpoint is restricted to Admin users only. Requires Admin role.

**Tags**: Categories

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Categories/{id}/reports

**Summary**: Get reports by category

**Description**: Retrieves all reports that belong to subcategories under the specified category. Requires authentication.

**Tags**: Categories

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/chat/sessions

**Summary**: Get chat sessions

**Description**: Retrieves all chat sessions for the authenticated user. Returns a list of chat sessions with other users. Requires authentication.

**Tags**: Chat

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/chat/sessions/{otherUserId}

**Summary**: Open or create chat session

**Description**: Opens an existing chat session or creates a new one with another user. Returns the chat session details. Requires authentication.

**Tags**: Chat

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| otherUserId | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/chat/sessions/{sessionId}

**Summary**: Get chat session details

**Description**: Retrieves detailed information about a specific chat session including participants. Only participants can access the session. Requires authentication.

**Tags**: Chat

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| sessionId | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/chat/sessions/{sessionId}/messages

**Summary**: Get chat messages

**Description**: Retrieves all messages in a specific chat session. Only participants can access messages. Requires authentication.

**Tags**: Chat

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| sessionId | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/chat/sessions/{sessionId}/messages

**Summary**: Send chat message

**Description**: Sends a new message in a chat session. Only participants can send messages. The message is delivered via SignalR in real-time. Requires authentication.

**Tags**: Chat

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| sessionId | path | `integer` | Yes | - |

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `SendChatMessageDto`
- **Content-Type**: `text/json`
  - Schema: `SendChatMessageDto`
- **Content-Type**: `application/*+json`
  - Schema: `SendChatMessageDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `PUT` /api/chat/messages/{messageId}/read

**Summary**: Mark message as read

**Description**: Marks a chat message as read. Only the message recipient can mark messages as read. Requires authentication.

**Tags**: Chat

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| messageId | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Home/dashboard

**Tags**: Home

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/Matching/run/{reportId}

**Tags**: Matching

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| reportId | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Matching/{reportId}

**Tags**: Matching

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| reportId | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Notifications/vapid-public-key

**Summary**: Get VAPID public key

**Description**: Returns the VAPID public key for web push subscription. Use this in the frontend when registering for push. No auth required.

**Tags**: Notifications

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Notifications

**Summary**: Get notifications

**Description**: Retrieves notifications for the authenticated user with optional filters. Type filter: all/unread/read. Category filter: all/general/matches. Requires authentication.

**Tags**: Notifications

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| page | query | `integer` | No | - |
| pageSize | query | `integer` | No | - |
| type | query | `string` | No | - |
| category | query | `string` | No | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Notifications/unread

**Summary**: Get unread count

**Description**: Retrieves the count of unread notifications. Requires authentication.

**Tags**: Notifications

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `PUT` /api/Notifications/{id}/read

**Summary**: Mark as read

**Description**: Marks a notification as read. Requires authentication.

**Tags**: Notifications

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/Notifications/mark-all-read

**Summary**: Mark all as read

**Description**: Marks all notifications as read for the authenticated user. Requires authentication.

**Tags**: Notifications

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `DELETE` /api/Notifications/{id}

**Summary**: Delete notification

**Description**: Deletes a notification. Requires authentication.

**Tags**: Notifications

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/Notifications/register-device

**Summary**: Register device token

**Description**: Registers or updates the device token for push notifications. Requires authentication.

**Tags**: Notifications

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `RegisterDeviceTokenDto`
- **Content-Type**: `text/json`
  - Schema: `RegisterDeviceTokenDto`
- **Content-Type**: `application/*+json`
  - Schema: `RegisterDeviceTokenDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/Reports

**Tags**: Reports

#### Request Body:
Required: No

- **Content-Type**: `multipart/form-data`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Reports

**Tags**: Reports

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| ForPublicView | query | `boolean` | No | - |
| Type | query | `string` | No | - |
| Status | query | `string` | No | - |
| Search | query | `string` | No | - |
| CategoryId | query | `integer` | No | - |
| SubCategoryId | query | `integer` | No | - |
| DateFrom | query | `string` | No | - |
| DateTo | query | `string` | No | - |
| Page | query | `integer` | No | - |
| PageSize | query | `integer` | No | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Reports/{id}

**Tags**: Reports

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `PUT` /api/Reports/{id}

**Tags**: Reports

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Request Body:
Required: No

- **Content-Type**: `multipart/form-data`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `DELETE` /api/Reports/{id}

**Tags**: Reports

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/Reports/{id}/interested

**Tags**: Reports

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Reports/my-reports

**Tags**: Reports

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| page | query | `integer` | No | - |
| pageSize | query | `integer` | No | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Reports/nearby

**Tags**: Reports

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| lat | query | `number` | No | - |
| lng | query | `number` | No | - |
| radius | query | `number` | No | - |
| type | query | `string` | No | - |
| page | query | `integer` | No | - |
| pageSize | query | `integer` | No | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `PUT` /api/Reports/{id}/status

**Tags**: Reports

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `UpdateReportStatusDto`
- **Content-Type**: `text/json`
  - Schema: `UpdateReportStatusDto`
- **Content-Type**: `application/*+json`
  - Schema: `UpdateReportStatusDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/Reports/{id}/report

**Tags**: Reports

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `ReportAbuseDto`
- **Content-Type**: `text/json`
  - Schema: `ReportAbuseDto`
- **Content-Type**: `application/*+json`
  - Schema: `ReportAbuseDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/Reports/{id}/save

**Tags**: Reports

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `DELETE` /api/Reports/{id}/save

**Tags**: Reports

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/SubCategories

**Summary**: Get all subcategories

**Description**: Retrieves a list of all subcategories with their associated category information. Requires authentication.

**Tags**: SubCategories

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `POST` /api/SubCategories

**Summary**: Create a new subcategory

**Description**: Creates a new subcategory under a specified category. This endpoint is restricted to Admin users only. Requires Admin role.

**Tags**: SubCategories

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `CreateSubCategoryDto`
- **Content-Type**: `text/json`
  - Schema: `CreateSubCategoryDto`
- **Content-Type**: `application/*+json`
  - Schema: `CreateSubCategoryDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/SubCategories/category/{categoryId}

**Summary**: Get subcategories by category

**Description**: Retrieves all subcategories that belong to a specific category. Requires authentication.

**Tags**: SubCategories

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| categoryId | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/SubCategories/{id}

**Summary**: Get subcategory by ID

**Description**: Retrieves a single subcategory by its ID with associated category information. Requires authentication.

**Tags**: SubCategories

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `PUT` /api/SubCategories/{id}

**Summary**: Update subcategory

**Description**: Updates an existing subcategory's information. This endpoint is restricted to Admin users only. Requires Admin role.

**Tags**: SubCategories

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `UpdateSubCategoryDto`
- **Content-Type**: `text/json`
  - Schema: `UpdateSubCategoryDto`
- **Content-Type**: `application/*+json`
  - Schema: `UpdateSubCategoryDto`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `DELETE` /api/SubCategories/{id}

**Summary**: Delete subcategory

**Description**: Deletes a subcategory from the system. Subcategories with existing posts cannot be deleted. This endpoint is restricted to Admin users only. Requires Admin role.

**Tags**: SubCategories

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/SubCategories/{id}/reports

**Summary**: Get reports by subcategory

**Description**: Retrieves all reports that belong to the specified subcategory. Requires authentication.

**Tags**: SubCategories

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | - |

---

### `GET` /api/Users

**Summary**: Get all users

**Description**: Retrieves a paginated list of all users in the system. Requires Admin role. Supports search filtering by name or email.

**Tags**: Users

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| pageNumber | query | `integer` | No | - |
| pageSize | query | `integer` | No | - |
| searchTerm | query | `string` | No | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | `SafeUserDtoPaginatedResponseBaseResponse` |
| 401 | Unauthorized | `ProblemDetails` |
| 403 | Forbidden | `ProblemDetails` |

---

### `GET` /api/Users/{id}

**Summary**: Get user by ID

**Description**: Retrieves user details by ID. Users can only view their own profile unless they are an Admin. Requires authentication.

**Tags**: Users

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | `SafeUserDtoBaseResponse` |
| 401 | Unauthorized | `ProblemDetails` |
| 403 | Forbidden | `ProblemDetails` |
| 404 | Not Found | `ProblemDetails` |

---

### `GET` /api/Users/me

**Summary**: Get my data

**Description**: Returns the authenticated user's profile information including name, email, phone, and verification status. Requires authentication.

**Tags**: Users

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | `SafeUserDtoBaseResponse` |
| 401 | Unauthorized | `ProblemDetails` |

---

### `PUT` /api/Users/me

**Summary**: Update my data

**Description**: Updates the authenticated user's profile information including name, phone, date of birth, gender, and profile picture. Accepts multipart/form-data. Requires authentication.

**Tags**: Users

#### Request Body:
Required: No

- **Content-Type**: `multipart/form-data`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | `SafeUserDtoBaseResponse` |
| 400 | Bad Request | `ProblemDetails` |
| 401 | Unauthorized | `ProblemDetails` |
| 404 | Not Found | `ProblemDetails` |

---

### `POST` /api/Users/admin

**Summary**: Create a new user

**Description**: Creates a new admin user account. This endpoint is restricted to existing Admin users only. Requires Admin role.

**Tags**: Users

#### Request Body:
Required: No

- **Content-Type**: `application/json`
  - Schema: `CreateAdminCommand`
- **Content-Type**: `text/json`
  - Schema: `CreateAdminCommand`
- **Content-Type**: `application/*+json`
  - Schema: `CreateAdminCommand`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 201 | Created | `UserDtoBaseResponse` |
| 400 | Bad Request | `ProblemDetails` |
| 401 | Unauthorized | `ProblemDetails` |
| 403 | Forbidden | `ProblemDetails` |

---

### `PUT` /api/Users/{id}/verify

**Summary**: Verify a user account

**Description**: Allows an Admin to manually verify a user's account. Sets the user's verification status to true. Requires Admin role.

**Tags**: Users

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | `ObjectBaseResponse` |
| 401 | Unauthorized | `ProblemDetails` |
| 403 | Forbidden | `ProblemDetails` |
| 404 | Not Found | `ProblemDetails` |

---

### `POST` /api/Users/me/profile-picture

**Summary**: Upload profile picture

**Description**: Uploads a profile picture for the authenticated user. Accepts image files (jpg, jpeg, png, gif, webp) up to 5MB. Requires authentication.

**Tags**: Users

#### Request Body:
Required: No

- **Content-Type**: `multipart/form-data`

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | `ObjectBaseResponse` |
| 400 | Bad Request | `ProblemDetails` |
| 401 | Unauthorized | `ProblemDetails` |

---

### `GET` /api/Users/{id}/reports

**Summary**: Get user's reports

**Description**: Retrieves all reports created by a specific user with pagination support. Requires authentication.

**Tags**: Users

#### Parameters:
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| id | path | `integer` | Yes | - |
| page | query | `integer` | No | - |
| pageSize | query | `integer` | No | - |

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | `ObjectBaseResponse` |
| 401 | Unauthorized | `ProblemDetails` |
| 404 | Not Found | `ProblemDetails` |

---

### `GET` /api/Users/me/saved-reports

**Summary**: Get my saved reports

**Description**: Retrieves all reports the authenticated user has saved.

**Tags**: Users

#### Responses:
| Status | Description | Schema |
|---|---|---|
| 200 | OK | `ObjectBaseResponse` |
| 401 | Unauthorized | `ProblemDetails` |

---

## Models (Schemas)

### ChangeEmailConfirmDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| verificationCode | `string` | No | - |

### ChangeEmailRequestDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| newEmail | `string` | No | - |

### ChangePasswordDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| currentPassword | `string` | No | - |
| newPassword | `string` | No | - |

### CreateAdminCommand

| Property | Type | Nullable | Description |
|---|---|---|---|
| fullName | `string` | Yes | - |
| email | `string` | Yes | - |
| phone | `string` | Yes | - |
| password | `string` | Yes | - |

### CreateCategoryDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| name | `string` | Yes | - |

### CreateSubCategoryDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| name | `string` | Yes | - |
| categoryId | `integer` | No | - |

### DeleteAccountDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| password | `string` | No | - |

### ForgotPasswordDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| email | `string` | No | - |

### GoogleSignInDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| idToken | `string` | No | - |

### LoginDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| email | `string` | No | - |
| password | `string` | No | - |

### LogoutDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| refreshToken | `string` | No | - |

### ObjectBaseResponse

| Property | Type | Nullable | Description |
|---|---|---|---|
| success | `boolean` | No | - |
| message | `string` | Yes | - |
| data | `any` | Yes | - |
| errors | `Array<string>` | Yes | - |

### ProblemDetails

| Property | Type | Nullable | Description |
|---|---|---|---|
| type | `string` | Yes | - |
| title | `string` | Yes | - |
| status | `integer` | Yes | - |
| detail | `string` | Yes | - |
| instance | `string` | Yes | - |

### RefreshTokenDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| refreshToken | `string` | No | - |

### RegisterDeviceTokenDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| token | `string` | No | - |
| platform | `string` | No | - |

### ReportAbuseDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| reason | `string` | Yes | - |
| details | `string` | Yes | - |

### ResendVerificationDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| email | `string` | No | - |

### ResetPasswordDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| email | `string` | No | - |
| resetToken | `string` | No | - |
| newPassword | `string` | No | - |

### SafeUserDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| id | `integer` | No | - |
| fullName | `string` | Yes | - |
| email | `string` | Yes | - |
| phone | `string` | Yes | - |
| isVerified | `boolean` | No | - |
| dateOfBirth | `string` | Yes | - |
| gender | `string` | Yes | - |
| profilePictureUrl | `string` | Yes | - |
| createdAt | `string` | No | - |
| updatedAt | `string` | Yes | - |

### SafeUserDtoBaseResponse

| Property | Type | Nullable | Description |
|---|---|---|---|
| success | `boolean` | No | - |
| message | `string` | Yes | - |
| data | `SafeUserDto` | No | - |
| errors | `Array<string>` | Yes | - |

### SafeUserDtoPaginatedResponse

| Property | Type | Nullable | Description |
|---|---|---|---|
| data | `Array<SafeUserDto>` | Yes | - |
| totalCount | `integer` | No | - |
| pageNumber | `integer` | No | - |
| pageSize | `integer` | No | - |
| totalPages | `integer` | No | - |
| hasPreviousPage | `boolean` | No | - |
| hasNextPage | `boolean` | No | - |

### SafeUserDtoPaginatedResponseBaseResponse

| Property | Type | Nullable | Description |
|---|---|---|---|
| success | `boolean` | No | - |
| message | `string` | Yes | - |
| data | `SafeUserDtoPaginatedResponse` | No | - |
| errors | `Array<string>` | Yes | - |

### SendChatMessageDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| text | `string` | Yes | - |

### SignupDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| firstName | `string` | No | - |
| lastName | `string` | No | - |
| dateOfBirth | `string` | Yes | - |
| gender | `string` | Yes | - |
| email | `string` | No | - |
| phone | `string` | No | - |
| password | `string` | No | - |

### UpdateCategoryDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| id | `integer` | No | - |
| name | `string` | Yes | - |
| description | `string` | Yes | - |

### UpdateReportStatusDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| status | `string` | No | - |

### UpdateSubCategoryDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| id | `integer` | No | - |
| name | `string` | Yes | - |
| description | `string` | Yes | - |
| categoryId | `integer` | No | - |

### UserDto

| Property | Type | Nullable | Description |
|---|---|---|---|
| id | `integer` | No | - |
| fullName | `string` | Yes | - |
| email | `string` | Yes | - |
| phone | `string` | Yes | - |
| isVerified | `boolean` | No | - |
| roles | `Array<string>` | Yes | - |
| dateOfBirth | `string` | Yes | - |
| gender | `string` | Yes | - |
| profilePictureUrl | `string` | Yes | - |
| createdAt | `string` | No | - |
| updatedAt | `string` | Yes | - |

### UserDtoBaseResponse

| Property | Type | Nullable | Description |
|---|---|---|---|
| success | `boolean` | No | - |
| message | `string` | Yes | - |
| data | `UserDto` | No | - |
| errors | `Array<string>` | Yes | - |

