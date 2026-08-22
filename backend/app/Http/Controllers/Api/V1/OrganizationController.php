<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Requests\Organization\StoreOrganizationRequest;
use App\Http\Requests\Organization\UpdateOrganizationRequest;
use App\Http\Resources\OrganizationResource;
use App\Models\Organization;
use App\Services\OrganizationService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class OrganizationController extends Controller
{
    public function __construct(private readonly OrganizationService $organizations) {}

    public function index(Request $request): AnonymousResourceCollection
    {
        $organizations = $request->user()
            ->organizations()
            ->orderBy('name')
            ->get();

        return OrganizationResource::collection($organizations);
    }

    public function store(StoreOrganizationRequest $request): JsonResponse
    {
        $organization = $this->organizations->create(
            $request->user(),
            $request->validated()
        );

        return (new OrganizationResource($organization))
            ->response()
            ->setStatusCode(201);
    }

    public function show(Organization $organization): OrganizationResource
    {
        return new OrganizationResource($organization);
    }

    public function update(
        UpdateOrganizationRequest $request,
        Organization $organization
    ): OrganizationResource {
        $organization = $this->organizations->update(
            $organization,
            $request->validated()
        );

        return new OrganizationResource($organization);
    }

    public function destroy(Organization $organization): JsonResponse
    {
        $this->organizations->delete($organization);

        return response()->json([
            'message' => 'Organization deleted.',
        ]);
    }
}
