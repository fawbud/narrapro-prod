# Quick Supabase Credentials Guide for Your Project

## Your Project Information

From your existing database URL, I can see:
- **Project Reference**: `ijabdhhlybsdvkebioce`
- **Supabase URL**: `https://ijabdhhlybsdvkebioce.supabase.co`

## Step 1: Get Your Credentials

### 1. Go to Your Supabase Dashboard
Visit: https://supabase.com/dashboard/project/ijabdhhlybsdvkebioce

### 2. Navigate to API Settings
- Click **Settings** (gear icon) in the left sidebar
- Click **API** from the settings menu

### 3. Copy the Required Values

You'll see a page with **Project API keys**. Copy these:

#### Project URL (You already know this!)
```
SUPABASE_URL=https://ijabdhhlybsdvkebioce.supabase.co
```

#### Service Role Key (The long JWT token)
Look for **service_role** key - it's a very long string starting with `eyJ...`

```
SUPABASE_ACCESS_KEY_ID=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9....(very long)
SUPABASE_SECRET_ACCESS_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9....(same as above)
```

**Important**: For Supabase Storage, use the **same service_role key** for both ACCESS_KEY_ID and SECRET_ACCESS_KEY.

## Step 2: Update Your .env File

Replace the placeholder values in your `.env` file:

```bash
DATABASE_URL=postgresql://postgres:pt8Jkv4WlSLHJmR2@db.ijabdhhlybsdvkebioce.supabase.co:5432/postgres
PRODUCTION=false

# Email Configuration
RESEND_API_KEY=your_resend_api_key_here
DEFAULT_FROM_EMAIL=noreply@narrapro.com

# Supabase Storage Configuration
SUPABASE_URL=https://ijabdhhlybsdvkebioce.supabase.co
SUPABASE_ACCESS_KEY_ID=paste_your_service_role_key_here
SUPABASE_SECRET_ACCESS_KEY=paste_your_service_role_key_here
SUPABASE_BUCKET_NAME=storage
```

## Step 3: Create Storage Bucket

1. Go to **Storage** in your Supabase dashboard
2. Click **Create bucket**
3. Name it `storage`
4. Make it **Public**
5. Click **Create bucket**

## Step 4: Test Your Configuration

```bash
python manage.py test_supabase_storage
```

## What the Keys Look Like

- **service_role key**: Starts with `eyJ...` and is about 300+ characters long
- **anon key**: Also starts with `eyJ...` but has different permissions

## Quick Access Link

Direct link to your API settings:
https://supabase.com/dashboard/project/ijabdhhlybsdvkebioce/settings/api

That's it! Just copy the service_role key from that page and use it for both ACCESS_KEY_ID and SECRET_ACCESS_KEY.
