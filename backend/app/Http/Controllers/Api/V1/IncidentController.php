<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Requests\Incident\StoreIncidentRequest;
use App\Http\Requests\Incident\UpdateIncidentRequest;
use App\Http\Resources\IncidentResource;
use App\Models\Organization;
use App\Services\IncidentService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class IncidentController extends Controller
{
    public function __construct(private readonly IncidentService $incidents) {}

    public function index(Organization $organization): AnonymousResourceCollection
    {
        return IncidentResource::collection(
            $this->incidents->list($organization)
        );
    }

    public function store(
        StoreIncidentRequest $request,
        Organization $organization
    ): JsonResponse {
        $incident = $this->incidents->report(
            $organization,
            $request->user(),
            $request->validated()
        );

        return (new IncidentResource($incident))
            ->additional([
                'message' => 'Your report was received. An organization administrator can review it.',
            ])
            ->response()
            ->setStatusCode(201);
    }

    public function show(Organization $organization, int $incident): IncidentResource
    {
        return new IncidentResource(
            $this->incidents->findInOrganization($organization, $incident)
        );
    }

    public function update(
        UpdateIncidentRequest $request,
        Organization $organization,
        int $incident
    ): IncidentResource {
        $model = $this->incidents->findInOrganization($organization, $incident);

        return new IncidentResource(
            $this->incidents->updateStatus($model, $request->validated())
        );
    }
}
