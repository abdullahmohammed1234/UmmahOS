<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Requests\Resource\StoreResourceRequest;
use App\Http\Requests\Resource\UpdateResourceRequest;
use App\Http\Resources\ResourceItemResource;
use App\Models\Organization;
use App\Services\ResourceService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class ResourceController extends Controller
{
    public function __construct(private readonly ResourceService $resources) {}

    public function index(Organization $organization): AnonymousResourceCollection
    {
        return ResourceItemResource::collection(
            $this->resources->list($organization)
        );
    }

    public function store(
        StoreResourceRequest $request,
        Organization $organization
    ): JsonResponse {
        $resource = $this->resources->create(
            $organization,
            $request->user(),
            $request->validated()
        );

        return (new ResourceItemResource($resource))
            ->response()
            ->setStatusCode(201);
    }

    public function show(Organization $organization, int $resource): ResourceItemResource
    {
        return new ResourceItemResource(
            $this->resources->findInOrganization($organization, $resource)
        );
    }

    public function update(
        UpdateResourceRequest $request,
        Organization $organization,
        int $resource
    ): ResourceItemResource {
        $model = $this->resources->findInOrganization($organization, $resource);

        return new ResourceItemResource(
            $this->resources->update($model, $request->validated())
        );
    }

    public function destroy(Organization $organization, int $resource): JsonResponse
    {
        $model = $this->resources->findInOrganization($organization, $resource);
        $this->resources->delete($model);

        return response()->json([
            'message' => 'Resource deleted.',
        ]);
    }
}
