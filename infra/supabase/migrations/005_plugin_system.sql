-- ============================================================================
-- PLUGIN SYSTEM TABLES
-- ============================================================================

-- Plugin registry (marketplace)
create table if not exists public.plugins (
    id uuid default gen_random_uuid() primary key,
    name text not null,
    slug text not null unique,
    description text default '',
    version text default '1.0.0',
    category text default 'utility', -- 'utility', 'analytics', 'distribution', 'editor', 'integration'
    author_id uuid references auth.users on delete cascade not null,
    icon_url text,
    homepage_url text,
    repository_url text,
    permissions jsonb default '[]',  -- list of permission strings
    hooks jsonb default '[]',         -- list of hook strings
    config_schema jsonb default '{}', -- JSON Schema for plugin configuration
    default_config jsonb default '{}',-- default configuration values
    is_official boolean default false,
    status text default 'published',  -- 'draft', 'published', 'deprecated'
    downloads integer default 0,
    rating_avg numeric(3,2) default 0.0,
    rating_count integer default 0,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Enable RLS on plugins
alter table public.plugins enable row level security;

-- Plugins policies
create policy "Anyone can view published plugins"
    on public.plugins for select
    using (status = 'published' or auth.uid() = author_id);

create policy "Authenticated users can create plugins"
    on public.plugins for insert
    with check (auth.uid() = author_id);

create policy "Authors can update own plugins"
    on public.plugins for update
    using (auth.uid() = author_id);

create policy "Authors can delete own plugins"
    on public.plugins for delete
    using (auth.uid() = author_id);

-- Installed plugins (per organization)
create table if not exists public.installed_plugins (
    id uuid default gen_random_uuid() primary key,
    plugin_id uuid references public.plugins on delete cascade not null,
    organization_id uuid references public.organizations on delete cascade not null,
    installed_by uuid references auth.users on delete set null not null,
    config jsonb default '{}',        -- org-specific configuration overrides
    is_enabled boolean default true,
    installed_at timestamptz default now(),
    updated_at timestamptz default now(),
    unique(plugin_id, organization_id)
);

-- Enable RLS on installed_plugins
alter table public.installed_plugins enable row level security;

-- Installed plugins policies
create policy "Org members can view installed plugins"
    on public.installed_plugins for select
    using (
        exists (
            select 1 from public.organizations o
            left join public.organization_members om on om.org_id = o.id
            where o.id = installed_plugins.organization_id
            and (o.owner_id = auth.uid() or om.user_id = auth.uid())
        )
    );

create policy "Org admins can install plugins"
    on public.installed_plugins for insert
    with check (
        exists (
            select 1 from public.organizations o
            left join public.organization_members om on om.org_id = o.id and om.role = 'admin'
            where o.id = installed_plugins.organization_id
            and (o.owner_id = auth.uid() or om.user_id = auth.uid())
        )
    );

create policy "Org admins can update installed plugins"
    on public.installed_plugins for update
    using (
        exists (
            select 1 from public.organizations o
            left join public.organization_members om on om.org_id = o.id and om.role = 'admin'
            where o.id = installed_plugins.organization_id
            and (o.owner_id = auth.uid() or om.user_id = auth.uid())
        )
    );

create policy "Org admins can uninstall plugins"
    on public.installed_plugins for delete
    using (
        exists (
            select 1 from public.organizations o
            left join public.organization_members om on om.org_id = o.id and om.role = 'admin'
            where o.id = installed_plugins.organization_id
            and (o.owner_id = auth.uid() or om.user_id = auth.uid())
        )
    );

-- Plugin hook events (async processing log)
create table if not exists public.plugin_hook_events (
    id uuid default gen_random_uuid() primary key,
    installed_plugin_id uuid references public.installed_plugins on delete cascade not null,
    organization_id uuid references public.organizations on delete cascade not null,
    hook text not null,
    payload jsonb default '{}',
    status text default 'pending',     -- 'pending', 'processing', 'completed', 'failed'
    attempts integer default 0,
    last_attempt_at timestamptz,
    error_message text,
    result jsonb,
    created_at timestamptz default now()
);

-- Enable RLS on plugin_hook_events
alter table public.plugin_hook_events enable row level security;

create policy "Org members can view plugin hook events"
    on public.plugin_hook_events for select
    using (
        exists (
            select 1 from public.organizations o
            left join public.organization_members om on om.org_id = o.id
            where o.id = plugin_hook_events.organization_id
            and (o.owner_id = auth.uid() or om.user_id = auth.uid())
        )
    );

-- Indexes for plugin tables
create index if not exists idx_plugins_slug on public.plugins(slug);
create index if not exists idx_plugins_author_id on public.plugins(author_id);
create index if not exists idx_plugins_category on public.plugins(category);
create index if not exists idx_plugins_status on public.plugins(status);
create index if not exists idx_installed_plugins_org_id on public.installed_plugins(organization_id);
create index if not exists idx_installed_plugins_plugin_id on public.installed_plugins(plugin_id);
create index if not exists idx_plugin_hook_events_org_id on public.plugin_hook_events(organization_id);
create index if not exists idx_plugin_hook_events_status on public.plugin_hook_events(status);
create index if not exists idx_plugin_hook_events_hook on public.plugin_hook_events(hook);
create index if not exists idx_plugin_hook_events_created_at on public.plugin_hook_events(created_at desc);

-- Updated_at trigger for plugins
create trigger handle_plugins_updated_at
    before update on public.plugins
    for each row execute function public.handle_updated_at();

-- Updated_at trigger for installed_plugins
create trigger handle_installed_plugins_updated_at
    before update on public.installed_plugins
    for each row execute function public.handle_updated_at();