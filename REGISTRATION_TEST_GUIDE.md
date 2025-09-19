# NarraPro Registration System Test Guide

## Overview
The registration system has been successfully implemented with the following features:
- Dynamic role-based registration forms
- User authentication (login/logout)
- Guest and authenticated home pages
- Admin approval workflow

## Components Created

### 1. Forms (`main/forms.py`)
- `BaseUserRegistrationForm`: Common user fields (username, email, password, etc.)
- `NarasumberRegistrationForm`: Narasumber-specific fields
- `EventRegistrationForm`: Event organizer-specific fields
- `CombinedRegistrationForm`: Utility class to handle both forms

### 2. Views (`main/views.py`)
- `home`: Shows different content for guest vs authenticated users
- `register_view`: Dynamic registration with AJAX field loading
- `login_view`: User authentication
- `logout_view`: User logout
- `get_role_form_fields`: AJAX endpoint for dynamic form fields

### 3. Templates
- `templates/base.html`: Enhanced base template with navigation
- `main/home_guest.html`: Guest home page with register/login buttons
- `main/home_authenticated.html`: User dashboard showing profile status
- `main/login.html`: Login form
- `main/register.html`: Dynamic registration form with JavaScript
- `main/partials/narasumber_fields.html`: Narasumber-specific fields
- `main/partials/event_fields.html`: Event organizer-specific fields

### 4. URLs (`main/urls.py`)
- `/` - Home page
- `/register/` - Registration
- `/login/` - Login
- `/logout/` - Logout
- `/api/get-role-form-fields/` - AJAX endpoint

## Testing Instructions

### 1. Start the Server
```bash
cd "C:\Coding_Projects\narrapro"
.\env\Scripts\python.exe manage.py runserver
```

### 2. Create Test Data (First Time Only)
```bash
.\env\Scripts\python.exe manage.py setup_test_data
```

### 3. Access the Application
Open your browser and navigate to: http://127.0.0.1:8000/

### 4. Test Scenarios

#### A. Guest Home Page
- ✅ Should show welcome message and features
- ✅ Should display "Register Now" and "Login" buttons
- ✅ Navigation should show "Login" and "Register" links

#### B. Registration Process

**Test Narasumber Registration:**
1. Click "Register Now" or navigate to `/register/`
2. Fill in base user fields:
   - First Name: `John`
   - Last Name: `Doe`
   - Username: `john_narasumber`
   - Email: `john@example.com`
   - Password: `testpass123`
   - Confirm Password: `testpass123`
3. Select "Narasumber" from role dropdown
4. ✅ Additional fields should appear without page refresh
5. Fill in narasumber fields:
   - Full Name: `John Doe`
   - Bio: `Experienced software developer...`
   - Expertise Area: `Technology`
   - Experience Level: `Expert`
   - Years of Experience: `5`
   - Location: `DKI Jakarta`
   - Contact Email: `john@example.com`
   - Phone: `+62123456789`
   - Portfolio: `https://johndoe.dev`
6. Submit form
7. ✅ Should show success message about pending approval
8. ✅ Should redirect to login page

**Test Event Organizer Registration:**
1. Navigate to `/register/`
2. Fill in base user fields:
   - First Name: `Jane`
   - Last Name: `Smith`
   - Username: `jane_event`
   - Email: `jane@example.com`
   - Password: `testpass123`
   - Confirm Password: `testpass123`
3. Select "Event" from role dropdown
4. ✅ Different fields should appear
5. Fill in event fields:
   - Name: `Tech Conference Jakarta`
   - Description: `Annual technology conference...`
   - Location: `DKI Jakarta`
   - Contact: `jane@example.com / +62987654321`
   - Website: `https://techconf.id`
   - Cover Image: Upload any image file
   - Start Date: Select future date
   - End Date: Select future date (after start)
6. Submit form
7. ✅ Should show success message and redirect to login

#### C. Login Process
1. Navigate to `/login/`
2. Try logging in with unregistered user:
   - ✅ Should show "Invalid username or password" error
3. Try logging in with registered but unapproved user:
   - Username: `john_narasumber`
   - Password: `testpass123`
   - ✅ Should show "Account pending approval" message
4. Create approved user via admin and test login:
   - ✅ Should show welcome message and redirect to dashboard

#### D. Authenticated Home Page
1. After successful login:
   - ✅ Should show user dashboard
   - ✅ Should display user's name and role
   - ✅ Should show approval status
   - ✅ Should show profile completion status
   - ✅ Navigation should show user name and "Logout" link

#### E. Logout Process
1. Click "Logout" from navigation or dashboard
2. ✅ Should show goodbye message
3. ✅ Should redirect to guest home page
4. ✅ Navigation should show "Login" and "Register" again

### 5. Admin Integration Test
1. Navigate to `/admin/`
2. Login with superuser account
3. Check that new users appear in Users section
4. Check that profiles appear in their respective apps
5. Test approving a user and sending approval email

## Features Implemented

### ✅ Dynamic Form Fields
- Form fields change without page refresh based on role selection
- AJAX endpoint provides role-specific form HTML
- JavaScript handles the dynamic switching

### ✅ User Authentication
- Complete login/logout functionality
- Session management
- Redirect handling

### ✅ Approval Workflow
- Users start with `is_approved=False`
- Approval message displayed during login attempt
- Admin can approve users from admin panel

### ✅ Profile Creation
- Automatic profile creation during registration
- One-to-one relationship with User model
- Role-specific fields and validation

### ✅ Responsive UI
- Bootstrap 5 styling
- Font Awesome icons
- Mobile-friendly design
- Message system for feedback

### ✅ File Upload
- Event cover image uploads
- Supabase storage integration (when configured)
- Proper file handling and validation

## Files Created/Modified

### New Files:
- `main/forms.py`
- `main/urls.py`
- `main/templates/main/home_guest.html`
- `main/templates/main/home_authenticated.html`
- `main/templates/main/login.html`
- `main/templates/main/register.html`
- `main/templates/main/partials/narasumber_fields.html`
- `main/templates/main/partials/event_fields.html`
- `main/management/commands/setup_test_data.py`

### Modified Files:
- `main/views.py`
- `narrapro/urls.py`
- `templates/base.html`

## Next Steps

1. **Admin Integration**: The user approval workflow is ready
2. **Email Notifications**: Approval emails are configured
3. **Profile Management**: Users can view their profile status
4. **File Storage**: Supabase integration is ready for production

The registration system is fully functional and ready for testing!
