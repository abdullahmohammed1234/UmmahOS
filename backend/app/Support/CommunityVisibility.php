<?php

namespace App\Support;

/**
 * Phase 2 visibility helper.
 *
 * Members see published/public records in the current organization.
 * Admins (via *.manage) see and manage all records in that organization only.
 */
final class CommunityVisibility
{
    public static function context(): OrganizationContext
    {
        $context = request()->attributes->get('organizationContext');

        if (! $context instanceof OrganizationContext && app()->bound(OrganizationContext::class)) {
            $context = app(OrganizationContext::class);
        }

        if (! $context instanceof OrganizationContext) {
            throw new \RuntimeException('Organization context is not available.');
        }

        return $context;
    }

    public static function canManage(string $permission): bool
    {
        return self::context()->hasPermission($permission);
    }
}
