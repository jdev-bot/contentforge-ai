-- Enable RLS (Row Level Security)
alter table if exists public.users enable row level security;

-- Subscription status constraint values: 'inactive', 'active', 'past_due', 'canceled'

-- Subscription tier enum
create type subscription_tier_enum as enum ('free', 'starter', 'pro', 'enterprise');

-- Users table (extends Supabase Auth)
create table if not exists public.profiles (
    id uuid references auth.users on delete cascade primary key,
    full_name text,
    avatar_url text,
    subscription_tier subscription_tier_enum default 'free',
    subscription_status text default 'inactive',
    stripe_customer_id text,
    stripe_subscription_id text,
    monthly_usage_count integer default 0,
    
    -- Subscription status check constraint
    constraint chk_subscription_status check (subscription_status in ('inactive', 'active', 'past_due', 'canceled')),
    monthly_usage_limit integer default 50, -- free tier limit
    subscription_period_end timestamptz, -- when current period ends
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Enable RLS on profiles
alter table public.profiles enable row level security;

-- Profiles policies
create policy "Users can view own profile"
    on public.profiles for select
    using (auth.uid() = id);

create policy "Users can update own profile"
    on public.profiles for update
    using (auth.uid() = id);

-- Projects table
create table if not exists public.projects (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references auth.users on delete cascade not null,
    name text not null,
    description text,
    brand_voice jsonb default '{}', -- tone, style guidelines
    target_platforms text[] default '{}',
    is_active boolean default true,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Enable RLS on projects
alter table public.projects enable row level security;

-- Projects policies
create policy "Users can CRUD own projects"
    on public.projects for all
    using (auth.uid() = user_id);

-- Content table
create table if not exists public.content (
    id uuid default gen_random_uuid() primary key,
    project_id uuid references public.projects on delete cascade not null,
    user_id uuid references auth.users on delete cascade not null,
    title text not null,
    source_type text not null, -- 'url', 'youtube', 'upload', 'text'
    source_url text,
    original_text text,
    word_count integer,
    status text default 'pending', -- 'pending', 'processing', 'completed', 'failed'
    error_message text,
    metadata jsonb default '{}',
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Enable RLS on content
alter table public.content enable row level security;

-- Content policies
create policy "Users can CRUD own content"
    on public.content for all
    using (auth.uid() = user_id);

-- Generated Assets table
create table if not exists public.generated_assets (
    id uuid default gen_random_uuid() primary key,
    content_id uuid references public.content on delete cascade not null,
    user_id uuid references auth.users on delete cascade not null,
    type text not null, -- 'social_post', 'thread', 'newsletter', 'blog_post', 'video_script'
    platform text, -- 'twitter', 'linkedin', 'instagram', etc.
    content text not null,
    tokens_used integer,
    status text default 'pending', -- 'pending', 'generated', 'approved', 'rejected'
    engagement_prediction jsonb default '{}',
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Enable RLS on generated_assets
alter table public.generated_assets enable row level security;

-- Generated assets policies
create policy "Users can CRUD own assets"
    on public.generated_assets for all
    using (auth.uid() = user_id);

-- Distributions table
create table if not exists public.distributions (
    id uuid default gen_random_uuid() primary key,
    asset_id uuid references public.generated_assets on delete cascade not null,
    user_id uuid references auth.users on delete cascade not null,
    platform text not null,
    status text default 'pending', -- 'pending', 'scheduled', 'publishing', 'published', 'failed', 'cancelled'
    scheduled_at timestamptz,
    published_at timestamptz,
    published_url text,
    external_id text, -- platform-specific ID
    error_message text,
    retry_count integer default 0,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Enable RLS on distributions
alter table public.distributions enable row level security;

-- Distributions policies
create policy "Users can CRUD own distributions"
    on public.distributions for all
    using (auth.uid() = user_id);

-- Usage tracking table
create table if not exists public.usage_logs (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references auth.users on delete cascade not null,
    action text not null, -- 'content_create', 'asset_generate', 'distribution_publish'
    tokens_used integer default 0,
    metadata jsonb default '{}',
    created_at timestamptz default now()
);

-- Enable RLS on usage_logs
alter table public.usage_logs enable row level security;

-- Usage logs policies
create policy "Users can view own usage logs"
    on public.usage_logs for select
    using (auth.uid() = user_id);

-- ============================================================================-- ORGANIZATIONS TABLE (for multi-tenant team support)-- ============================================================================create type organization_role_enum as enum ('admin', 'member');
create table if not exists public.organizations (    id uuid default gen_random_uuid() primary key,    name text not null,    owner_id uuid references auth.users on delete cascade not null,
    created_at timestamptz default now());

-- Enable RLS on organizations
alter table public.organizations enable row level security;

-- Organizations RLS policies
create policy "Users can view own organizations"
    on public.organizations for select
    using (auth.uid() = owner_id);

create policy "Organization members can view their organizations"
    on public.organizations for select
    using (
        exists (
            select 1 from public.organization_members
            where organization_members.org_id = organizations.id
            and organization_members.user_id = auth.uid()
        )
    );

create policy "Owners can update their organizations"
    on public.organizations for update
    using (auth.uid() = owner_id);

create policy "Owners can delete their organizations"
    on public.organizations for delete
    using (auth.uid() = owner_id);

create policy "Authenticated users can create organizations"
    on public.organizations for insert
    with check (auth.uid() = owner_id);

-- Organization members table
create table if not exists public.organization_members (
    id uuid default gen_random_uuid() primary key,
    org_id uuid references public.organizations on delete cascade not null,
    user_id uuid references auth.users on delete cascade not null,
    role organization_role_enum default 'member',
    created_at timestamptz default now(),
    unique(org_id, user_id));

-- Enable RLS on organization_members
alter table public.organization_members enable row level security;

-- Organization members RLS policies
create policy "Users can view organization members of their orgs"
    on public.organization_members for select
    using (
        auth.uid() = user_id
        or exists (
            select 1 from public.organizations
            where organizations.id = organization_members.org_id
            and organizations.owner_id = auth.uid()
        )
        or exists (
            select 1 from public.organization_members om
            where om.org_id = organization_members.org_id
            and om.user_id = auth.uid()
        )
    );

create policy "Owners can manage organization members"
    on public.organization_members for all
    using (
        exists (
            select 1 from public.organizations
            where organizations.id = organization_members.org_id
            and organizations.owner_id = auth.uid()
        )
    );

create policy "Admins can invite members"
    on public.organization_members for insert
    with check (
        exists (
            select 1 from public.organization_members om
            where om.org_id = organization_members.org_id
            and om.user_id = auth.uid()
            and om.role = 'admin'
        )
        or exists (
            select 1 from public.organizations
            where organizations.id = organization_members.org_id
            and organizations.owner_id = auth.uid()
        )
    );

-- Create indexes for organizations
create index if not exists idx_organizations_owner_id on public.organizations(owner_id);
create index if not exists idx_organization_members_org_id on public.organization_members(org_id);
create index if not exists idx_organization_members_user_id on public.organization_members(user_id);

-- Create indexes for performance
create index if not exists idx_projects_user_id on public.projects(user_id);
create index if not exists idx_content_project_id on public.content(project_id);
create index if not exists idx_content_user_id on public.content(user_id);
create index if not exists idx_content_status on public.content(status);
create index if not exists idx_assets_content_id on public.generated_assets(content_id);
create index if not exists idx_assets_user_id on public.generated_assets(user_id);
create index if not exists idx_distributions_user_id on public.distributions(user_id);
create index if not exists idx_distributions_status on public.distributions(status);
create index if not exists idx_usage_logs_user_id on public.usage_logs(user_id);
create index if not exists idx_usage_logs_created_at on public.usage_logs(created_at);

-- Functions for updated_at timestamps
create or replace function public.handle_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

-- Triggers for updated_at
create trigger handle_profiles_updated_at
    before update on public.profiles
    for each row execute function public.handle_updated_at();

create trigger handle_projects_updated_at
    before update on public.projects
    for each row execute function public.handle_updated_at();

create trigger handle_content_updated_at
    before update on public.content
    for each row execute function public.handle_updated_at();

create trigger handle_assets_updated_at
    before update on public.generated_assets
    for each row execute function public.handle_updated_at();

create trigger handle_distributions_updated_at
    before update on public.distributions
    for each row execute function public.handle_updated_at();

-- Function to automatically create profile after signup
create or replace function public.handle_new_user()
returns trigger as $$
begin
    insert into public.profiles (id, full_name, avatar_url)
    values (new.id, new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'avatar_url');
    return new;
end;
$$ language plpgsql security definer;

-- Trigger to create profile on signup
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_user();

-- Function to automatically reset monthly usage at the start of each month
create or replace function public.reset_monthly_usage()
returns trigger as $$
begin
    -- Check if the last update was in a different month
    if extract(month from old.updated_at) != extract(month from current_date) or
       extract(year from old.updated_at) != extract(year from current_date) then
        -- Reset monthly usage count
        new.monthly_usage_count := 0;
    end if;
    return new;
end;
$$ language plpgsql;

-- Trigger to reset usage on profile updates when month changes
create trigger reset_monthly_usage_on_update
    before update on public.profiles
    for each row execute function public.reset_monthly_usage();

-- ============================================================================
-- MONTHLY USAGE RESET FUNCTION (can be called via cron or edge function)
-- ============================================================================
create or replace function public.reset_all_monthly_usage()
returns void as $$
begin
    update public.profiles
    set monthly_usage_count = 0,
        updated_at = now()
    where extract(month from updated_at) != extract(month from current_date)
       or extract(year from updated_at) != extract(year from current_date);
end;
$$ language plpgsql security definer;

-- ============================================================================
-- ERROR LOGS TABLE (for application error tracking)
-- ============================================================================
create table if not exists public.error_logs (
    id uuid default gen_random_uuid() primary key,
    timestamp timestamptz default now(),
    status_code integer not null,
    error_type text not null, -- 'client_error', 'server_error', 'unhandled_exception'
    message text not null,
    detail text,
    path text not null,
    method text not null,
    user_id uuid references auth.users on delete set null,
    ip_address text,
    user_agent text,
    request_body text,
    traceback text,
    metadata jsonb default '{}'
);

-- Enable RLS on error_logs
alter table public.error_logs enable row level security;

-- Error logs policies
-- Only admins can view all error logs
-- Users can view their own error logs (though typically not used)
create policy "Users can view own error logs"
    on public.error_logs for select
    using (auth.uid() = user_id);

-- Create index for error_logs queries
create index if not exists idx_error_logs_timestamp on public.error_logs(timestamp desc);
create index if not exists idx_error_logs_status_code on public.error_logs(status_code);
create index if not exists idx_error_logs_user_id on public.error_logs(user_id);
create index if not exists idx_error_logs_error_type on public.error_logs(error_type);

-- ============================================================================
-- USAGE_TRACKING TABLE (renamed from usage_logs for clarity)
-- ============================================================================

-- Create new usage_tracking table with better name
-- Note: If usage_logs already exists with data, we create a view instead
DO $$
BEGIN
    -- Check if usage_logs table exists
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'usage_logs'
    ) THEN
        -- Rename the table to usage_tracking
        ALTER TABLE public.usage_logs RENAME TO usage_tracking;
        
        -- Rename the index
        IF EXISTS (
            SELECT 1 FROM pg_indexes 
            WHERE indexname = 'idx_usage_logs_user_id'
        ) THEN
            ALTER INDEX idx_usage_logs_user_id RENAME TO idx_usage_tracking_user_id;
        END IF;
        
        IF EXISTS (
            SELECT 1 FROM pg_indexes 
            WHERE indexname = 'idx_usage_logs_created_at'
        ) THEN
            ALTER INDEX idx_usage_logs_created_at RENAME TO idx_usage_tracking_created_at;
        END IF;
    ELSE
        -- Create the table fresh
        CREATE TABLE public.usage_tracking (
            id uuid default gen_random_uuid() primary key,
            user_id uuid references auth.users on delete cascade not null,
            action text not null, -- 'content_create', 'asset_generate', 'distribution_publish'
            tokens_used integer default 0,
            metadata jsonb default '{}',
            created_at timestamptz default now()
        );
        
        -- Enable RLS on usage_tracking
        ALTER TABLE public.usage_tracking ENABLE ROW LEVEL SECURITY;
        
        -- Usage tracking policies
        CREATE POLICY "Users can view own usage tracking"
            ON public.usage_tracking FOR SELECT
            USING (auth.uid() = user_id);
        
        -- Create indexes
        CREATE INDEX idx_usage_tracking_user_id ON public.usage_tracking(user_id);
        CREATE INDEX idx_usage_tracking_created_at ON public.usage_tracking(created_at);
    END IF;
END $$;
