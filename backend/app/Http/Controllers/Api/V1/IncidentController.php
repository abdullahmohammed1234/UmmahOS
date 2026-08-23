<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Requests\Incident\ListIncidentsRequest;
use App\Http\Requests\Incident\StoreIncidentRelatedItemRequest;
use App\Http\Requests\Incident\StoreIncidentReplyRequest;
use App\Http\Requests\Incident\StoreIncidentRequest;
use App\Http\Requests\Incident\UpdateIncidentRequest;
use App\Http\Resources\IncidentRelatedItemResource;
use App\Http\Resources\IncidentReplyResource;
use App\Http\Resources\IncidentResource;
use App\Models\Organization;
use App\Services\IncidentService;
use App\Support\CommunityVisibility;
use App\Support\Permissions;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;
use Illuminate\Http\Response;

class IncidentController extends Controller
{
    public function __construct(private readonly IncidentService $incidents) {}

    public function overview(Organization $organization): JsonResponse
    {
        $canReview = CommunityVisibility::canManage(Permissions::INCIDENTS_MANAGE);

        $payload = [
            'can_report' => true,
            'can_review' => $canReview,
        ];

        if ($canReview) {
            $payload['counts'] = $this->incidents->counts($organization);
        }

        return response()->json([
            'data' => $payload,
        ]);
    }

    public function index(
        ListIncidentsRequest $request,
        Organization $organization
    ): AnonymousResourceCollection {
        $status = $request->validated('status');

        return IncidentResource::collection(
            $this->incidents->list($organization, $status)
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
                'message' => 'Your report has been received by your MSA\'s Community Shield team.',
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
            $this->incidents->updateReview($model, $request->user(), $request->validated())
        );
    }

    public function storeReply(
        StoreIncidentReplyRequest $request,
        Organization $organization,
        int $incident
    ): JsonResponse {
        $model = $this->incidents->findInOrganization($organization, $incident);
        $reply = $this->incidents->addReply($model, $request->validated());

        return (new IncidentReplyResource($reply))
            ->response()
            ->setStatusCode(201);
    }

    public function destroyReply(
        Organization $organization,
        int $incident,
        int $reply
    ): Response {
        $model = $this->incidents->findInOrganization($organization, $incident);
        $this->incidents->deleteReply($model, $reply);

        return response()->noContent();
    }

    public function storeRelatedItem(
        StoreIncidentRelatedItemRequest $request,
        Organization $organization,
        int $incident
    ): JsonResponse {
        $model = $this->incidents->findInOrganization($organization, $incident);
        $item = $this->incidents->addRelatedItem($model, $request->validated());

        return (new IncidentRelatedItemResource($item))
            ->response()
            ->setStatusCode(201);
    }

    public function destroyRelatedItem(
        Organization $organization,
        int $incident,
        int $relatedItem
    ): Response {
        $model = $this->incidents->findInOrganization($organization, $incident);
        $this->incidents->deleteRelatedItem($model, $relatedItem);

        return response()->noContent();
    }
}
