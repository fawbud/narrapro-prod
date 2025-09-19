# How to Get Supabase Storage Credentials

## Step-by-Step Guide to Finding Your Supabase Credentials

### 1. SUPABASE_URL (Project URL)

**Location**: Supabase Dashboard → Settings → API

1. Go to [supabase.com](https://supabase.com) and log in
2. Select your project (or create one if you haven't)
3. In the left sidebar, click **Settings** (gear icon)
4. Click **API** from the settings menu
5. Look for **Project URL** section
6. Copy the URL that looks like: `https://abcdefghijklmnop.supabase.co`

**Example**:
```
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
```

### 2. SUPABASE_ACCESS_KEY_ID & SUPABASE_SECRET_ACCESS_KEY

**Important**: For Supabase Storage, you have two options for authentication:

#### Option A: Using Service Role Key (Recommended for Production)

**Location**: Supabase Dashboard → Settings → API

1. In the same **API** settings page
2. Look for **Project API keys** section
3. Find the **service_role** key (it's the longer one)
4. Copy this key

**For Supabase Storage, use**:
```bash
SUPABASE_ACCESS_KEY_ID=your_service_role_key_here
SUPABASE_SECRET_ACCESS_KEY=your_service_role_key_here
```

*Note: For Supabase Storage via S3 API, you use the same service role key for both access key and secret key.*

#### Option B: Using Anon Key (For Public Access Only)

**Location**: Supabase Dashboard → Settings → API

1. In the **API** settings page
2. Look for **Project API keys** section  
3. Find the **anon public** key
4. Copy this key

**For public-only access**:
```bash
SUPABASE_ACCESS_KEY_ID=your_anon_key_here
SUPABASE_SECRET_ACCESS_KEY=your_anon_key_here
```

### 3. Complete Example Configuration

Here's what your `.env` file should look like:

```bash
# Database (you already have this)
DATABASE_URL=postgresql://postgres:pt8Jkv4WlSLHJmR2@db.ijabdhhlybsdvkebioce.supabase.co:5432/postgres

# Production toggle
PRODUCTION=false  # Set to true when deploying

# Email Configuration
RESEND_API_KEY=your_resend_api_key_here
DEFAULT_FROM_EMAIL=noreply@narrapro.com

# Supabase Storage Configuration
SUPABASE_URL=https://ijabdhhlybsdvkebioce.supabase.co
SUPABASE_ACCESS_KEY_ID=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlqYWJkaGhseWJzZHZrZWJpb2NlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5NzY2NjYxMCwiZXhwIjoyMDEzMjQyNjEwfQ.example_service_role_key
SUPABASE_SECRET_ACCESS_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlqYWJkaGhseWJzZHZrZWJpb2NlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5NzY2NjYxMCwiZXhwIjoyMDEzMjQyNjEwfQ.example_service_role_key
SUPABASE_BUCKET_NAME=storage
```

### 4. Setting Up Supabase Storage Bucket

Before using the credentials, you need to create a storage bucket:

1. **Go to Storage**:
   - In your Supabase dashboard
   - Click **Storage** in the left sidebar

2. **Create a Bucket**:
   - Click **Create bucket** button
   - Name it `storage` (or whatever you set in SUPABASE_BUCKET_NAME)
   - Make it **Public** (for serving images directly)
   - Click **Create bucket**

3. **Set Bucket Policies** (Important for Security):
   - Click on your bucket
   - Go to **Policies** tab
   - Add policies for proper access control (see SUPABASE_STORAGE_SETUP.md for SQL examples)

### 5. Security Best Practices

#### For Development:
- Use **anon** key for testing
- Keep `PRODUCTION=false`
- Files stored locally

#### For Production:
- Use **service_role** key
- Set `PRODUCTION=true`
- Files stored in Supabase
- Ensure proper RLS policies are set

### 6. Quick Test After Setup

1. **Update your .env file** with the real credentials
2. **Test the connection**:
   ```bash
   python manage.py test_supabase_storage
   ```
3. **If using production mode**:
   ```bash
   # Set PRODUCTION=true in .env first
   python manage.py test_supabase_storage
   ```

### 7. Visual Guide to Finding Credentials

```
Supabase Dashboard Layout:
┌─────────────────────────────────────────────────────────────┐
│ Project: Your Project Name                                  │
├─────────────────────────────────────────────────────────────┤
│ ☰ Table Editor          │                                  │
│ 🔐 Authentication       │                                  │
│ 📊 Database            │   Main Content Area              │
│ 📁 Storage             │                                  │
│ 🌐 Edge Functions      │                                  │
│ ⚙️  Settings           │                                  │
│   └── 🔑 API ←────────  │   ← Click here for credentials  │
│   └── 🗄️  Database      │                                  │
│   └── 👥 Auth          │                                  │
└─────────────────────────────────────────────────────────────┘
```

### 8. Troubleshooting Common Issues

**Issue**: "Access Denied" when uploading files
- **Solution**: Check that your service role key has storage permissions
- **Solution**: Verify bucket is set to public if serving images directly

**Issue**: "Bucket not found"
- **Solution**: Ensure bucket name in .env matches the actual bucket name in Supabase
- **Solution**: Check that the bucket exists in your Storage dashboard

**Issue**: "Invalid credentials"
- **Solution**: Copy the complete service role key (they're very long!)
- **Solution**: Make sure no extra spaces in the .env file

### 9. Expected Credential Formats

**SUPABASE_URL**:
- Format: `https://[project-ref].supabase.co`
- Example: `https://ijabdhhlybsdvkebioce.supabase.co`
- Length: Usually around 40-50 characters

**Service Role Key**:
- Format: JWT token starting with `eyJ...`
- Length: Very long (300+ characters)
- Contains: Encoded project information and permissions

**Anon Key**:
- Format: JWT token starting with `eyJ...`  
- Length: Very long (300+ characters)
- Contains: Public access permissions only

The credentials are now ready to use! Remember to keep `PRODUCTION=false` for development and switch to `true` only when deploying to production.
