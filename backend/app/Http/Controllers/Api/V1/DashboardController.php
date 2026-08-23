<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Resources\AdminDashboardResource;
use App\Http\Resources\MemberDashboardResource;
use App\Models\Organization;
use App\Services\DashboardService;
use App\Support\CommunityVisibility;

class DashboardController extends Controller
{
    public function __construct(private readonly DashboardService $dashboards) {}

    public function member(Organization $organization): MemberDashboardResource
    {
        $context = CommunityVisibility::context();

        abort_unless($context->organization->is($organization), 400, 'Invalid organization context.');

        return new MemberDashboardResource(
            $this->dashboards->memberDashboard($context)
        );
    }

    public function admin(Organization $organization): AdminDashboardResource
    {
        $context = CommunityVisibility::context();

        abort_unless($context->organization->is($organization), 400, 'Invalid organization context.');

        return new AdminDashboardResource(
            $this->dashboards->adminDashboard($context)
        );
    }
}
