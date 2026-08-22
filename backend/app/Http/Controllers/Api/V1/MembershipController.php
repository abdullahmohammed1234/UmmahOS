<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Requests\Membership\StoreMembershipRequest;
use App\Http\Requests\Membership\UpdateMembershipRequest;
use App\Http\Resources\MembershipResource;
use App\Models\Organization;
use App\Models\Role;
use App\Models\User;
use App\Services\MembershipService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class MembershipController extends Controller
{
    public function __construct(private readonly MembershipService $memberships) {}

    public function index(Organization $organization): AnonymousResourceCollection
    {
        $memberships = $organization->memberships()
            ->with(['user', 'role', 'organization'])
            ->orderBy('id')
            ->get();

        return MembershipResource::collection($memberships);
    }

    public function store(
        StoreMembershipRequest $request,
        Organization $organization
    ): JsonResponse {
        $membership = $this->memberships->add(
            $organization,
            User::query()->findOrFail($request->validated('user_id')),
            Role::query()->where('slug', $request->validated('role'))->firstOrFail()
        );

        return (new MembershipResource($membership))
            ->response()
            ->setStatusCode(201);
    }

    public function update(
        UpdateMembershipRequest $request,
        Organization $organization,
        int $membership
    ): MembershipResource {
        $model = $this->memberships->findInOrganization($organization, $membership);

        $model = $this->memberships->updateRole(
            $model,
            Role::query()->where('slug', $request->validated('role'))->firstOrFail()
        );

        return new MembershipResource($model);
    }

    public function destroy(Organization $organization, int $membership): JsonResponse
    {
        $model = $this->memberships->findInOrganization($organization, $membership);
        $this->memberships->remove($model);

        return response()->json([
            'message' => 'Membership removed.',
        ]);
    }
}
