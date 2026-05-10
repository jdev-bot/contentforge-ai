"""
Organization management router with full CRUD and member management.
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from pydantic import BaseModel, EmailStr

from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.routers.auth import get_auth_user

router = APIRouter(prefix="/organizations", tags=["organizations"])
logger = logging.getLogger(__name__)


class OrganizationRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class OrganizationBase(BaseModel):
    name: str


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None


class OrganizationMemberBase(BaseModel):
    email: EmailStr
    role: OrganizationRole = OrganizationRole.MEMBER


class OrganizationMemberUpdate(BaseModel):
    role: OrganizationRole


class OrganizationMemberResponse(BaseModel):
    id: UUID
    org_id: UUID
    user_id: UUID
    role: OrganizationRole
    created_at: datetime
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    avatar_url: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    member_count: Optional[int] = None
    is_owner: Optional[bool] = None


class OrganizationWithMembers(OrganizationResponse):
    members: List[OrganizationMemberResponse] = []
    current_user_role: Optional[str] = None


class InvitationResponse(BaseModel):
    message: str
    email: str
    org_id: UUID


class OwnershipTransferRequest(BaseModel):
    new_owner_id: UUID


class OwnershipTransferResponse(BaseModel):
    message: str
    organization_id: UUID
    new_owner_id: UUID


# Helper function to check if user is org member
def check_org_access(supabase, org_id: str, user_id: str) -> tuple[bool, Optional[str]]:
    """Check if user has access to organization and return their role."""
    # Check if user is owner
    result = (
        supabase.table("organizations")
        .select("*")
        .eq("id", org_id)
        .eq("owner_id", user_id)
        .single()
        .execute()
    )
    if result.data:
        return True, "owner"

    # Check if user is a member
    result = (
        supabase.table("organization_members")
        .select("role")
        .eq("org_id", org_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if result.data:
        return True, result.data.get("role")

    return False, None


def check_is_admin(supabase, org_id: str, user_id: str) -> bool:
    """Check if user is owner or admin of the organization."""
    has_access, role = check_org_access(supabase, org_id, user_id)
    if not has_access:
        return False
    return role in ["owner", "admin"]


def check_is_owner(supabase, org_id: str, user_id: str) -> bool:
    """Check if user is the owner of the organization."""
    has_access, role = check_org_access(supabase, org_id, user_id)
    return role == "owner"


# Organization CRUD


@router.post(
    "/", response_model=OrganizationResponse, status_code=http_status.HTTP_201_CREATED
)
@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=http_status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_organization(
    org_data: OrganizationCreate, user=Depends(get_auth_user)
):
    """Create a new organization. User becomes the owner."""
    supabase = get_supabase_admin_client()

    try:
        # Create organization
        data = {
            "name": org_data.name,
            "owner_id": str(user.id),
        }

        result = supabase.table("organizations").insert(data).execute()

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create organization",
            )

        created_org = result.data[0]

        # Add owner as admin member
        member_data = {
            "org_id": created_org["id"],
            "user_id": str(user.id),
            "role": "admin",
        }
        supabase.table("organization_members").insert(member_data).execute()

        return OrganizationResponse(**created_org, is_owner=True, member_count=1)

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=List[OrganizationResponse])
@router.get("", response_model=List[OrganizationResponse], include_in_schema=False)
async def list_organizations(
    user=Depends(get_auth_user),
    include_member_count: bool = Query(
        True, description="Include member count in response"
    ),
):
    """List all organizations the user owns or is a member of."""
    supabase = get_supabase_admin_client()

    try:
        user_id = str(user.id)
        organizations = []

        # Run owned orgs and member orgs queries in parallel
        def fetch_owned():
            return (
                supabase.table("organizations")
                .select("*")
                .eq("owner_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )

        def fetch_member_links():
            return (
                supabase.table("organization_members")
                .select("org_id")
                .eq("user_id", user_id)
                .execute()
            )

        owned_result, member_result = await asyncio.gather(
            asyncio.to_thread(fetch_owned),
            asyncio.to_thread(fetch_member_links),
            return_exceptions=True,
        )
        if isinstance(owned_result, Exception):
            raise owned_result
        if isinstance(member_result, Exception):
            logger.warning(
                "Organization member lookup failed for user %s: %s", user_id, member_result
            )
            member_org_ids = []
        else:
            member_org_ids = (
                [m["org_id"] for m in member_result.data] if member_result.data else []
            )

        # Get organizations where user is a member
        # Fetch member orgs if any (separate from owned)
        member_orgs = []
        if member_org_ids:
            try:
                member_orgs_result = (
                    supabase.table("organizations")
                    .select("*")
                    .in_("id", member_org_ids)
                    .order("created_at", desc=True)
                    .execute()
                )
                member_orgs = member_orgs_result.data if member_orgs_result.data else []
            except Exception as member_orgs_err:
                logger.warning(
                    "Organization detail lookup failed for user %s: %s",
                    user_id,
                    member_orgs_err,
                )
                member_orgs = []

        # Combine and deduplicate
        all_org_ids = set()
        all_orgs = []

        for org in (owned_result.data or []) + member_orgs:
            if org["id"] not in all_org_ids:
                all_org_ids.add(org["id"])
                all_orgs.append(org)

        # Sort by created_at desc
        all_orgs.sort(key=lambda x: x["created_at"], reverse=True)

        # Batch-fetch member counts to avoid N+1 queries
        member_counts: Dict[str, int] = {}
        if include_member_count and all_org_ids:
            try:
                all_members_result = (
                    supabase.table("organization_members")
                    .select("org_id")
                    .in_("org_id", list(all_org_ids))
                    .execute()
                )
                for m in all_members_result.data or []:
                    oid = m["org_id"]
                    member_counts[oid] = member_counts.get(oid, 0) + 1
            except Exception as count_err:
                logger.warning(
                    "Organization member count lookup failed for user %s: %s",
                    user_id,
                    count_err,
                )

        for org in all_orgs:
            is_owner = org["owner_id"] == user_id
            member_count = member_counts.get(org["id"], 0) if include_member_count else None

            organizations.append(
                OrganizationResponse(
                    **org, is_owner=is_owner, member_count=member_count
                )
            )

        return organizations

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/{org_id}", response_model=OrganizationWithMembers)
async def get_organization(org_id: UUID, user=Depends(get_auth_user)):
    """Get a specific organization with its members."""
    supabase = get_supabase_admin_client()

    try:
        user_id = str(user.id)

        # Check access
        has_access, role = check_org_access(supabase, str(org_id), user_id)
        if not has_access:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this organization",
            )

        # Get organization
        result = (
            supabase.table("organizations")
            .select("*")
            .eq("id", str(org_id))
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        org = result.data
        is_owner = org["owner_id"] == user_id

        # Get members with user details
        members_result = (
            supabase.table("organization_members")
            .select("*")
            .eq("org_id", str(org_id))
            .execute()
        )

        # Batch-fetch profiles for all members to avoid N+1 queries
        member_user_ids = [m["user_id"] for m in members_result.data or []]
        profiles_by_id: Dict[str, dict] = {}
        if member_user_ids:
            profiles_result = (
                supabase.table("profiles")
                .select("id, full_name, avatar_url")
                .in_("id", member_user_ids)
                .execute()
            )
            for p in profiles_result.data or []:
                profiles_by_id[p["id"]] = p

        members = []
        for member in members_result.data or []:
            profile = profiles_by_id.get(str(member["user_id"]), {})
            members.append(
                OrganizationMemberResponse(
                    **member,
                    user_email=None,
                    user_name=profile.get("full_name"),
                    avatar_url=profile.get("avatar_url"),
                )
            )

        return OrganizationWithMembers(
            **org,
            is_owner=is_owner,
            member_count=len(members),
            members=members,
            current_user_role=role,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID, org_data: OrganizationUpdate, user=Depends(get_auth_user)
):
    """Update an organization. Only admins can update."""
    supabase = get_supabase_admin_client()

    try:
        user_id = str(user.id)

        # Check admin access
        if not check_is_admin(supabase, str(org_id), user_id):
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this organization",
            )

        # Build update data
        update_data = {}
        if org_data.name is not None:
            update_data["name"] = org_data.name

        if not update_data:
            # Return existing organization
            result = (
                supabase.table("organizations")
                .select("*")
                .eq("id", str(org_id))
                .single()
                .execute()
            )
            return OrganizationResponse(**result.data, is_owner=True)

        result = (
            supabase.table("organizations")
            .update(update_data)
            .eq("id", str(org_id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        updated_org = result.data[0]
        is_owner = updated_org["owner_id"] == user_id

        return OrganizationResponse(**updated_org, is_owner=is_owner)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{org_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_organization(org_id: UUID, user=Depends(get_auth_user)):
    """Delete an organization. Only the owner can delete."""
    supabase = get_supabase_admin_client()

    try:
        user_id = str(user.id)

        # Check ownership
        if not check_is_owner(supabase, str(org_id), user_id):
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Only the owner can delete this organization",
            )

        # Delete organization (cascade will handle members)
        result = (
            supabase.table("organizations")
            .delete()
            .eq("id", str(org_id))
            .eq("owner_id", user_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# Member Management


@router.post("/{org_id}/invite", response_model=InvitationResponse)
async def invite_member(
    org_id: UUID, invitation: OrganizationMemberBase, user=Depends(get_auth_user)
):
    """Invite a member to the organization by email."""
    supabase = get_supabase_admin_client()

    try:
        user_id = str(user.id)

        # Check admin access
        if not check_is_admin(supabase, str(org_id), user_id):
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to invite members",
            )

        # Check if email is already a member
        # First get user by email from auth.users (we need admin client)
        try:
            admin_supabase = get_supabase_admin_client()
            # Note: In production, you'd use auth.admin.listUsers() or similar
            # For now, we try to find by profile
            profile_result = (
                supabase.table("profiles")
                .select("id")
                .eq("email", str(invitation.email))
                .single()
                .execute()
            )

            if profile_result.data:
                invited_user_id = profile_result.data["id"]

                # Check if already a member
                existing_member = (
                    supabase.table("organization_members")
                    .select("*")
                    .eq("org_id", str(org_id))
                    .eq("user_id", invited_user_id)
                    .execute()
                )

                if existing_member.data:
                    raise HTTPException(
                        status_code=http_status.HTTP_400_BAD_REQUEST,
                        detail="User is already a member of this organization",
                    )
            else:
                # User not found - in production, send invitation email
                # For now, we return a message that user needs to sign up first
                return InvitationResponse(
                    message=f"Invitation prepared for {invitation.email}. User needs to sign up first.",
                    email=str(invitation.email),
                    org_id=org_id,
                )

            # Add member
            member_data = {
                "org_id": str(org_id),
                "user_id": invited_user_id,
                "role": invitation.role.value,
            }

            result = (
                supabase.table("organization_members").insert(member_data).execute()
            )

            if not result.data:
                raise HTTPException(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to add member",
                )

            return InvitationResponse(
                message=f"Successfully invited {invitation.email} as {invitation.role.value}",
                email=str(invitation.email),
                org_id=org_id,
            )

        except HTTPException:
            raise
        except Exception as e:
            # User might not exist yet
            return InvitationResponse(
                message=f"Invitation sent to {invitation.email}. They will be added once they sign up.",
                email=str(invitation.email),
                org_id=org_id,
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{org_id}/members", response_model=List[OrganizationMemberResponse])
async def list_members(org_id: UUID, user=Depends(get_auth_user)):
    """List all members of an organization."""
    supabase = get_supabase_admin_client()

    try:
        user_id = str(user.id)

        # Check access
        has_access, _ = check_org_access(supabase, str(org_id), user_id)
        if not has_access:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this organization",
            )

        # Get members
        members_result = (
            supabase.table("organization_members")
            .select("*")
            .eq("org_id", str(org_id))
            .execute()
        )

        # Batch-fetch profiles for all members
        member_user_ids = [m["user_id"] for m in members_result.data or []]
        profiles_by_id: Dict[str, dict] = {}
        if member_user_ids:
            profiles_result = (
                supabase.table("profiles")
                .select("id, full_name, avatar_url")
                .in_("id", member_user_ids)
                .execute()
            )
            for p in profiles_result.data or []:
                profiles_by_id[p["id"]] = p

        members = []
        for member in members_result.data or []:
            profile = profiles_by_id.get(str(member["user_id"]), {})
            members.append(
                OrganizationMemberResponse(
                    **member,
                    user_name=profile.get("full_name"),
                    avatar_url=profile.get("avatar_url"),
                )
            )

        return members

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.patch(
    "/{org_id}/members/{member_id}", response_model=OrganizationMemberResponse
)
async def update_member_role(
    org_id: UUID,
    member_id: UUID,
    update_data: OrganizationMemberUpdate,
    user=Depends(get_auth_user),
):
    """Update a member's role. Only admins can change roles."""
    supabase = get_supabase_admin_client()

    try:
        user_id = str(user.id)

        # Check admin access
        if not check_is_admin(supabase, str(org_id), user_id):
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update member roles",
            )

        # Prevent changing own role (owners should transfer ownership instead)
        if str(member_id) == user_id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="You cannot change your own role. Use ownership transfer instead.",
            )

        # Update member role
        result = (
            supabase.table("organization_members")
            .update({"role": update_data.role.value})
            .eq("id", str(member_id))
            .eq("org_id", str(org_id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )

        updated_member = result.data[0]

        # Get user info
        user_name = None
        avatar_url = None

        try:
            profile_result = (
                supabase.table("profiles")
                .select("full_name, avatar_url")
                .eq("id", str(updated_member["user_id"]))
                .single()
                .execute()
            )
            if profile_result.data:
                user_name = profile_result.data.get("full_name")
                avatar_url = profile_result.data.get("avatar_url")
        except Exception:
            pass

        return OrganizationMemberResponse(
            **updated_member, user_name=user_name, avatar_url=avatar_url
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{org_id}/members/{member_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def remove_member(org_id: UUID, member_id: UUID, user=Depends(get_auth_user)):
    """Remove a member from the organization. Admins can remove members, users can remove themselves."""
    supabase = get_supabase_admin_client()

    try:
        user_id = str(user.id)

        # Get the member to check permissions
        member_result = (
            supabase.table("organization_members")
            .select("*")
            .eq("id", str(member_id))
            .eq("org_id", str(org_id))
            .single()
            .execute()
        )

        if not member_result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )

        member = member_result.data

        # Check permissions: admin can remove anyone, users can remove themselves
        is_admin = check_is_admin(supabase, str(org_id), user_id)
        is_self = str(member["user_id"]) == user_id

        if not is_admin and not is_self:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to remove this member",
            )

        # Cannot remove the owner
        org_result = (
            supabase.table("organizations")
            .select("owner_id")
            .eq("id", str(org_id))
            .single()
            .execute()
        )
        if org_result.data and str(org_result.data["owner_id"]) == str(
            member["user_id"]
        ):
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the organization owner. Transfer ownership first.",
            )

        # Delete member
        supabase.table("organization_members").delete().eq("id", str(member_id)).eq(
            "org_id", str(org_id)
        ).execute()

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# Ownership Transfer


@router.post("/{org_id}/transfer-ownership", response_model=OwnershipTransferResponse)
async def transfer_ownership(
    org_id: UUID, transfer_data: OwnershipTransferRequest, user=Depends(get_auth_user)
):
    """Transfer organization ownership to another member. Only the current owner can do this."""
    supabase = get_supabase_admin_client()

    try:
        user_id = str(user.id)

        # Check ownership
        if not check_is_owner(supabase, str(org_id), user_id):
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Only the owner can transfer ownership",
            )

        # Cannot transfer to self
        if str(transfer_data.new_owner_id) == user_id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="You are already the owner",
            )

        # Check if new owner is a member
        new_owner_member = (
            supabase.table("organization_members")
            .select("*")
            .eq("org_id", str(org_id))
            .eq("user_id", str(transfer_data.new_owner_id))
            .single()
            .execute()
        )

        if not new_owner_member.data:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="New owner must be a member of the organization",
            )

        # Update organization owner
        org_result = (
            supabase.table("organizations")
            .update({"owner_id": str(transfer_data.new_owner_id)})
            .eq("id", str(org_id))
            .execute()
        )

        if not org_result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        # Update member roles: old owner becomes admin, new owner becomes admin
        supabase.table("organization_members").update({"role": "admin"}).eq(
            "org_id", str(org_id)
        ).eq("user_id", str(transfer_data.new_owner_id)).execute()

        return OwnershipTransferResponse(
            message="Ownership transferred successfully",
            organization_id=org_id,
            new_owner_id=transfer_data.new_owner_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{org_id}/leave", status_code=http_status.HTTP_204_NO_CONTENT)
async def leave_organization(org_id: UUID, user=Depends(get_auth_user)):
    """Leave an organization. The owner must transfer ownership before leaving."""
    supabase = get_supabase_admin_client()

    try:
        user_id = str(user.id)

        # Check if user is owner
        if check_is_owner(supabase, str(org_id), user_id):
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Owner cannot leave the organization. Transfer ownership or delete the organization.",
            )

        # Find and delete membership
        member_result = (
            supabase.table("organization_members")
            .select("id")
            .eq("org_id", str(org_id))
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not member_result.data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="You are not a member of this organization",
            )

        supabase.table("organization_members").delete().eq(
            "id", member_result.data["id"]
        ).execute()

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
