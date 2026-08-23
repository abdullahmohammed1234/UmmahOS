<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Requests\Event\StoreEventRequest;
use App\Http\Requests\Event\UpdateEventRequest;
use App\Http\Resources\EventResource;
use App\Models\Organization;
use App\Services\EventService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class EventController extends Controller
{
    public function __construct(private readonly EventService $events) {}

    public function index(Organization $organization): AnonymousResourceCollection
    {
        return EventResource::collection(
            $this->events->list($organization)
        );
    }

    public function store(
        StoreEventRequest $request,
        Organization $organization
    ): JsonResponse {
        $event = $this->events->create(
            $organization,
            $request->user(),
            $request->validated()
        );

        return (new EventResource($event))
            ->response()
            ->setStatusCode(201);
    }

    public function show(Organization $organization, int $event): EventResource
    {
        return new EventResource(
            $this->events->findInOrganization($organization, $event)
        );
    }

    public function update(
        UpdateEventRequest $request,
        Organization $organization,
        int $event
    ): EventResource {
        $model = $this->events->findInOrganization($organization, $event);

        return new EventResource(
            $this->events->update($model, $request->validated())
        );
    }

    public function destroy(Organization $organization, int $event): JsonResponse
    {
        $model = $this->events->findInOrganization($organization, $event);
        $this->events->delete($model);

        return response()->json([
            'message' => 'Event deleted.',
        ]);
    }
}
