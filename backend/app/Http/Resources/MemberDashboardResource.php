<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class MemberDashboardResource extends JsonResource
{
    /**
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        /** @var array<string, mixed> $payload */
        $payload = $this->resource;

        return [
            'organization' => new OrganizationResource($payload['organization']),
            'welcome' => $payload['welcome'],
            'role' => $payload['role'],
            'upcoming_events' => EventResource::collection($payload['upcoming_events']),
            'recent_announcements' => AnnouncementResource::collection($payload['recent_announcements']),
            'featured_resources' => ResourceItemResource::collection($payload['featured_resources']),
            'academy' => [
                'published_courses_count' => $payload['academy']['published_courses_count'],
                'courses' => CourseResource::collection($payload['academy']['courses']),
            ],
            'community_shield' => $payload['community_shield'],
        ];
    }
}
