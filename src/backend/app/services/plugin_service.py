"""
Plugin service for the ContentForge AI plugin system.
Handles plugin registry CRUD, lifecycle hooks, configuration, and permissions.
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

from app.core.supabase import get_supabase_admin_client, get_supabase_client

# ============================================================================
# Plugin Lifecycle Hooks
# ============================================================================

class PluginHook(str, Enum):
    """Lifecycle hooks that plugins can subscribe to."""
    ON_CONTENT_CREATED = "on_content_created"
    ON_CONTENT_UPDATED = "on_content_updated"
    ON_CONTENT_DELETED = "on_content_deleted"
    ON_CONTENT_PUBLISHED = "on_content_published"
    ON_CONTENT_ANALYZED = "on_content_analyzed"
    ON_ASSET_GENERATED = "on_asset_generated"
    ON_DISTRIBUTION_PUBLISHED = "on_distribution_published"
    ON_PROJECT_CREATED = "on_project_created"


AVAILABLE_HOOKS = [h.value for h in PluginHook]


# ============================================================================
# Plugin Permissions
# ============================================================================

class PluginPermission(str, Enum):
    """Permissions that plugins can request."""
    READ_CONTENT = "read_content"
    WRITE_CONTENT = "write_content"
    DELETE_CONTENT = "delete_content"
    READ_PROJECTS = "read_projects"
    WRITE_PROJECTS = "write_projects"
    READ_ASSETS = "read_assets"
    WRITE_ASSETS = "write_assets"
    READ_DISTRIBUTIONS = "read_distributions"
    WRITE_DISTRIBUTIONS = "write_distributions"
    READ_ANALYTICS = "read_analytics"
    READ_ORGANIZATIONS = "read_organizations"
    MANAGE_WEBHOOKS = "manage_webhooks"
    ACCESS_AI_SERVICES = "access_ai_services"


AVAILABLE_PERMISSIONS = [p.value for p in PluginPermission]

# Permissions required per hook
HOOK_REQUIRED_PERMISSIONS: Dict[str, List[str]] = {
    PluginHook.ON_CONTENT_CREATED: [PluginPermission.READ_CONTENT],
    PluginHook.ON_CONTENT_UPDATED: [PluginPermission.READ_CONTENT],
    PluginHook.ON_CONTENT_DELETED: [PluginPermission.READ_CONTENT],
    PluginHook.ON_CONTENT_PUBLISHED: [PluginPermission.READ_CONTENT, PluginPermission.READ_DISTRIBUTIONS],
    PluginHook.ON_CONTENT_ANALYZED: [PluginPermission.READ_CONTENT, PluginPermission.READ_ANALYTICS],
    PluginHook.ON_ASSET_GENERATED: [PluginPermission.READ_ASSETS],
    PluginHook.ON_DISTRIBUTION_PUBLISHED: [PluginPermission.READ_DISTRIBUTIONS],
    PluginHook.ON_PROJECT_CREATED: [PluginPermission.READ_PROJECTS],
}


# ============================================================================
# Plugin Service
# ============================================================================

class PluginService:
    """
    Service class for managing the plugin lifecycle.

    Handles:
    - Plugin registry CRUD
    - Plugin installation/uninstallation per organization
    - Plugin configuration per organization
    - Plugin permissions model
    - Lifecycle hook dispatching
    """

    def __init__(self):
        self._supabase = None
        self._admin_supabase = None
        self._hook_handlers: Dict[str, List[Callable]] = {}

    @property
    def supabase(self):
        """Lazy Supabase client init."""
        if self._supabase is None:
            self._supabase = get_supabase_client()
        return self._supabase

    @property
    def admin_supabase(self):
        """Lazy admin Supabase client init."""
        if self._admin_supabase is None:
            self._admin_supabase = get_supabase_admin_client()
        return self._admin_supabase

    # ------------------------------------------------------------------
    # Plugin Registry CRUD
    # ------------------------------------------------------------------

    async def list_plugins(
        self,
        *,
        category: Optional[str] = None,
        is_official: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """List all plugins in the registry (marketplace)."""
        query = self.supabase.table("plugins").select("*", count="exact")

        if category:
            query = query.eq("category", category)
        if is_official is not None:
            query = query.eq("is_official", is_official)
        if search:
            query = query.ilike("name", f"%{search}%")

        query = query.eq("status", "published").order("downloads", desc=True)
        query = query.range(offset, offset + limit - 1)

        result = query.execute()
        return {"plugins": result.data or [], "total": result.count or 0}

    async def get_plugin(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get a single plugin from the registry."""
        result = self.supabase.table("plugins").select("*").eq("id", plugin_id).single().execute()
        return result.data

    async def create_plugin(self, data: Dict[str, Any], author_id: str) -> Dict[str, Any]:
        """Register a new plugin in the marketplace."""
        now = datetime.now(timezone.utc).isoformat()
        plugin = {
            "id": str(uuid.uuid4()),
            "name": data["name"],
            "slug": data.get("slug") or data["name"].lower().replace(" ", "-"),
            "description": data.get("description", ""),
            "version": data.get("version", "1.0.0"),
            "category": data.get("category", "utility"),
            "author_id": author_id,
            "icon_url": data.get("icon_url"),
            "homepage_url": data.get("homepage_url"),
            "repository_url": data.get("repository_url"),
            "permissions": json.dumps(data.get("permissions", [])),
            "hooks": json.dumps(data.get("hooks", [])),
            "config_schema": json.dumps(data.get("config_schema", {})),
            "default_config": json.dumps(data.get("default_config", {})),
            "is_official": data.get("is_official", False),
            "status": data.get("status", "published"),
            "downloads": 0,
            "rating_avg": 0.0,
            "rating_count": 0,
            "created_at": now,
            "updated_at": now,
        }

        result = self.supabase.table("plugins").insert(plugin).execute()
        if not result.data:
            raise RuntimeError("Failed to create plugin")
        return result.data[0]

    async def update_plugin(self, plugin_id: str, author_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a plugin's metadata (only the author can update)."""
        existing = await self.get_plugin(plugin_id)
        if not existing:
            raise ValueError("Plugin not found")
        if existing["author_id"] != author_id:
            raise PermissionError("Only the plugin author can update it")

        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
        for field in ("name", "slug", "description", "version", "category",
                       "icon_url", "homepage_url", "repository_url", "status"):
            if field in data:
                update_data[field] = data[field]

        if "permissions" in data:
            update_data["permissions"] = json.dumps(data["permissions"])
        if "hooks" in data:
            update_data["hooks"] = json.dumps(data["hooks"])
        if "config_schema" in data:
            update_data["config_schema"] = json.dumps(data["config_schema"])
        if "default_config" in data:
            update_data["default_config"] = json.dumps(data["default_config"])

        result = self.supabase.table("plugins").update(update_data).eq("id", plugin_id).execute()
        if not result.data:
            raise RuntimeError("Failed to update plugin")
        return result.data[0]

    async def delete_plugin(self, plugin_id: str, author_id: str) -> bool:
        """Remove a plugin from the registry (only the author can delete)."""
        existing = await self.get_plugin(plugin_id)
        if not existing:
            raise ValueError("Plugin not found")
        if existing["author_id"] != author_id:
            raise PermissionError("Only the plugin author can delete it")

        self.supabase.table("plugins").delete().eq("id", plugin_id).execute()
        return True

    # ------------------------------------------------------------------
    # Plugin Installation / Uninstallation
    # ------------------------------------------------------------------

    async def install_plugin(
        self,
        plugin_id: str,
        organization_id: str,
        user_id: str,
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Install a plugin for an organization."""
        # Verify plugin exists and is published
        plugin = await self.get_plugin(plugin_id)
        if not plugin:
            raise ValueError("Plugin not found")
        if plugin.get("status") != "published":
            raise ValueError("Plugin is not available for installation")

        # Check if already installed
        existing = (
            self.supabase.table("installed_plugins")
            .select("id")
            .eq("plugin_id", plugin_id)
            .eq("organization_id", organization_id)
            .execute()
        )
        if existing.data:
            raise ValueError("Plugin is already installed for this organization")

        # Merge default config with custom config
        default_config = plugin.get("default_config")
        if isinstance(default_config, str):
            default_config = json.loads(default_config)
        final_config = {**(default_config or {}), **(custom_config or {})}

        now = datetime.now(timezone.utc).isoformat()
        install = {
            "id": str(uuid.uuid4()),
            "plugin_id": plugin_id,
            "organization_id": organization_id,
            "installed_by": user_id,
            "config": json.dumps(final_config),
            "is_enabled": True,
            "installed_at": now,
            "updated_at": now,
        }

        result = self.supabase.table("installed_plugins").insert(install).execute()
        if not result.data:
            raise RuntimeError("Failed to install plugin")

        # Increment download count
        self.admin_supabase.table("plugins").update({
            "downloads": (plugin.get("downloads") or 0) + 1,
            "updated_at": now,
        }).eq("id", plugin_id).execute()

        return result.data[0]

    async def uninstall_plugin(self, install_id: str, organization_id: str, user_id: str) -> bool:
        """Uninstall a plugin from an organization."""
        # Verify the installed plugin belongs to this org
        existing = (
            self.supabase.table("installed_plugins")
            .select("id")
            .eq("id", install_id)
            .eq("organization_id", organization_id)
            .execute()
        )
        if not existing.data:
            raise ValueError("Installed plugin not found for this organization")

        self.supabase.table("installed_plugins").delete().eq("id", install_id).execute()
        return True

    async def list_installed_plugins(
        self,
        organization_id: str,
        is_enabled: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """List all plugins installed for an organization."""
        query = (
            self.supabase.table("installed_plugins")
            .select("*, plugins(*)")
            .eq("organization_id", organization_id)
            .order("installed_at", desc=True)
        )
        if is_enabled is not None:
            query = query.eq("is_enabled", is_enabled)

        result = query.execute()
        return result.data or []

    async def get_installed_plugin(self, install_id: str, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific installed plugin instance."""
        result = (
            self.supabase.table("installed_plugins")
            .select("*, plugins(*)")
            .eq("id", install_id)
            .eq("organization_id", organization_id)
            .single()
            .execute()
        )
        return result.data

    # ------------------------------------------------------------------
    # Plugin Configuration
    # ------------------------------------------------------------------

    async def get_plugin_config(self, install_id: str, organization_id: str) -> Dict[str, Any]:
        """Get the configuration for an installed plugin."""
        installed = await self.get_installed_plugin(install_id, organization_id)
        if not installed:
            raise ValueError("Installed plugin not found")
        config = installed.get("config", {})
        if isinstance(config, str):
            config = json.loads(config)
        return config

    async def update_plugin_config(
        self,
        install_id: str,
        organization_id: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update the configuration for an installed plugin."""
        installed = await self.get_installed_plugin(install_id, organization_id)
        if not installed:
            raise ValueError("Installed plugin not found")

        update_data = {
            "config": json.dumps(config),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        result = (
            self.supabase.table("installed_plugins")
            .update(update_data)
            .eq("id", install_id)
            .eq("organization_id", organization_id)
            .execute()
        )
        if not result.data:
            raise RuntimeError("Failed to update plugin config")
        return result.data[0]

    async def toggle_plugin(
        self,
        install_id: str,
        organization_id: str,
        is_enabled: bool,
    ) -> Dict[str, Any]:
        """Enable or disable an installed plugin."""
        installed = await self.get_installed_plugin(install_id, organization_id)
        if not installed:
            raise ValueError("Installed plugin not found")

        result = (
            self.supabase.table("installed_plugins")
            .update({
                "is_enabled": is_enabled,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            .eq("id", install_id)
            .eq("organization_id", organization_id)
            .execute()
        )
        if not result.data:
            raise RuntimeError("Failed to toggle plugin")
        return result.data[0]

    # ------------------------------------------------------------------
    # Plugin Permissions
    # ------------------------------------------------------------------

    def validate_permissions(self, plugin_data: Dict[str, Any], requested_hooks: List[str]) -> List[str]:
        """
        Validate that the plugin's declared permissions cover its requested hooks.
        Returns a list of validation errors (empty if valid).
        """
        errors: List[str] = []
        permissions = plugin_data.get("permissions", [])
        if isinstance(permissions, str):
            permissions = json.loads(permissions)

        # Validate requested permissions
        for perm in permissions:
            if perm not in AVAILABLE_PERMISSIONS:
                errors.append(f"Unknown permission: {perm}")

        # Validate hooks
        hooks = plugin_data.get("hooks", [])
        if isinstance(hooks, str):
            hooks = json.loads(hooks)

        for hook in hooks:
            if hook not in AVAILABLE_HOOKS:
                errors.append(f"Unknown hook: {hook}")
                continue

            required = HOOK_REQUIRED_PERMISSIONS.get(hook, [])
            for req_perm in required:
                if req_perm.value not in permissions:
                    errors.append(
                        f"Hook '{hook}' requires permission '{req_perm.value}'"
                    )

        return errors

    def get_plugin_permissions(self, plugin_id: str) -> List[str]:
        """Get the permissions declared by a plugin."""
        result = self.supabase.table("plugins").select("permissions").eq("id", plugin_id).single().execute()
        if not result.data:
            return []
        perms = result.data.get("permissions", [])
        if isinstance(perms, str):
            perms = json.loads(perms)
        return perms

    # ------------------------------------------------------------------
    # Lifecycle Hook Dispatching
    # ------------------------------------------------------------------

    def register_hook_handler(self, hook: str, handler: Callable):
        """Register a handler function for a lifecycle hook (in-process)."""
        if hook not in self._hook_handlers:
            self._hook_handlers[hook] = []
        self._hook_handlers[hook].append(handler)

    async def dispatch_hook(self, hook: str, payload: Dict[str, Any], organization_id: str):
        """
        Dispatch a lifecycle hook event.

        1. Calls any in-process registered handlers.
        2. Records the event in plugin_hook_events for async processing.
        """
        # In-process handlers
        for handler in self._hook_handlers.get(hook, []):
            try:
                await handler(payload)
            except Exception as exc:
                logger.error(f"[PluginService] Hook handler error for {hook}: {exc}")

        # Find all enabled installed plugins for this org that subscribe to this hook
        installed = (
            self.admin_supabase.table("installed_plugins")
            .select("id, plugin_id, config, plugins(hooks)")
            .eq("organization_id", organization_id)
            .eq("is_enabled", True)
            .execute()
        )

        for record in (installed.data or []):
            plugin = record.get("plugins")
            if not plugin:
                continue
            plugin_hooks = plugin.get("hooks", [])
            if isinstance(plugin_hooks, str):
                plugin_hooks = json.loads(plugin_hooks)
            if hook not in plugin_hooks:
                continue

            # Log the hook event for async processing
            event = {
                "id": str(uuid.uuid4()),
                "installed_plugin_id": record["id"],
                "organization_id": organization_id,
                "hook": hook,
                "payload": json.dumps(payload),
                "status": "pending",
                "attempts": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            try:
                self.admin_supabase.table("plugin_hook_events").insert(event).execute()
            except Exception as exc:
                logger.error(f"[PluginService] Failed to log hook event: {exc}")


# Singleton service instance
_plugin_service: Optional[PluginService] = None


def get_plugin_service() -> PluginService:
    """Get or create the singleton PluginService."""
    global _plugin_service
    if _plugin_service is None:
        _plugin_service = PluginService()
    return _plugin_service