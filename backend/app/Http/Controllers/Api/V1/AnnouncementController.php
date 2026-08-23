<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Requests\Announcement\StoreAnnouncementRequest;
use App\Http\Requests\Announcement\UpdateAnnouncementRequest;
use App\Http\Resources\AnnouncementResource;
use App\Models\Organization;
use App\Services\AnnouncementService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class AnnouncementController extends Controller
{
    public function __construct(private readonly AnnouncementService $announcements) {}

    public function index(Organization $organization): AnonymousResourceCollection
    {
        return AnnouncementResource::collection(
            $this->announcements->listForCurrentViewer($organization)
        );
    }

    public function store(
        StoreAnnouncementRequest $request,
        Organization $organization
    ): JsonResponse {
        $announcement = $this->announcements->create(
            $organization,
            $request->user(),
            $request->validated()
        );

        return (new AnnouncementResource($announcement))
            ->response()
            ->setStatusCode(201);
    }

    public function show(Organization $organization, int $announcement): AnnouncementResource
    {
        return new AnnouncementResource(
            $this->announcements->findVisible($organization, $announcement)
        );
    }

    public function update(
        UpdateAnnouncementRequest $request,
        Organization $organization,
        int $announcement
    ): AnnouncementResource {
        $model = $this->announcements->findVisible($organization, $announcement);

        return new AnnouncementResource(
            $this->announcements->update($model, $request->validated())
        );
    }

    public function destroy(Organization $organization, int $announcement): JsonResponse
    {
        $model = $this->announcements->findVisible($organization, $announcement);
        $this->announcements->delete($model);

        return response()->json([
            'message' => 'Announcement deleted.',
        ]);
    }
}
