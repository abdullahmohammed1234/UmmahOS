<?php

namespace App\Services;

use App\Support\OrganizationContext;

class DashboardService
{
    public function __construct(private readonly IncidentService $incidents) {}

    /**
     * @return array<string, mixed>
     */
    public function memberDashboard(OrganizationContext $context): array
    {
        $organization = $context->organization;

        return [
            'organization' => $organization,
            'welcome' => 'Welcome to '.$organization->name.'.',
            'role' => $context->role()?->slug,
            'upcoming_events' => $organization->events()
                ->upcoming()
                ->with('creator')
                ->limit(5)
                ->get(),
            'recent_announcements' => $organization->announcements()
                ->published()
                ->with('creator')
                ->orderByDesc('published_at')
                ->limit(5)
                ->get(),
            'featured_resources' => $organization->resources()
                ->with('creator')
                ->orderByDesc('id')
                ->limit(4)
                ->get(),
            'academy' => [
                'published_courses_count' => $organization->courses()->published()->count(),
                'courses' => $organization->courses()
                    ->published()
                    ->with('creator')
                    ->orderBy('title')
                    ->limit(4)
                    ->get(),
            ],
            'community_shield' => [
                'can_report' => true,
            ],
        ];
    }

    /**
     * @return array<string, mixed>
     */
    public function adminDashboard(OrganizationContext $context): array
    {
        $organization = $context->organization;
        $incidentCounts = $this->incidents->counts($organization);

        return [
            'organization' => $organization,
            'role' => $context->role()?->slug,
            'counts' => [
                'members' => $organization->memberships()->count(),
                'upcoming_events' => $organization->events()->upcoming()->count(),
                'published_announcements' => $organization->announcements()->published()->count(),
                'published_courses' => $organization->courses()->published()->count(),
                'open_incidents' => $incidentCounts['open'],
                'reviewing_incidents' => $incidentCounts['reviewing'],
                'resolved_incidents' => $incidentCounts['resolved'],
            ],
        ];
    }
}
