<?php

namespace App\Http\Controllers\Api\V1;

use App\Exceptions\Review\ReviewStateException;
use App\Http\Controllers\Controller;
use App\Http\Requests\Review\CloseReviewRequest;
use App\Http\Requests\Review\ConfirmReviewRequest;
use App\Http\Requests\Review\EscalateReviewRequest;
use App\Http\Requests\Review\ListReviewQueueRequest;
use App\Http\Requests\Review\StartReviewRequest;
use App\Http\Requests\Review\StoreContextRequestRequest;
use App\Http\Requests\Review\UncertainReviewRequest;
use App\Http\Requests\Review\UpdateContextRequestRequest;
use App\Http\Resources\IncidentContextRequestResource;
use App\Http\Resources\IncidentReviewPackageResource;
use App\Http\Resources\ReviewQueueItemResource;
use App\Models\IncidentContextRequest;
use App\Models\Organization;
use App\Services\Review\IncidentReviewService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class IncidentReviewController extends Controller
{
    public function __construct(private readonly IncidentReviewService $reviews) {}

    public function queue(
        ListReviewQueueRequest $request,
        Organization $organization
    ): AnonymousResourceCollection {
        return ReviewQueueItemResource::collection(
            $this->reviews->queue($organization, $request->validated())
        );
    }

    public function show(Organization $organization, int $report): IncidentReviewPackageResource
    {
        return new IncidentReviewPackageResource(
            $this->reviews->reviewPackage($organization, $report)
        );
    }

    public function start(
        StartReviewRequest $request,
        Organization $organization,
        int $report
    ): JsonResponse {
        return $this->respond($organization, $report, function ($incident) use ($request) {
            return $this->reviews->start($incident, $request->user(), $request->validated());
        });
    }

    public function confirm(
        ConfirmReviewRequest $request,
        Organization $organization,
        int $report
    ): JsonResponse {
        return $this->respond($organization, $report, function ($incident) use ($request) {
            return $this->reviews->confirm($incident, $request->user(), $request->validated());
        });
    }

    public function uncertain(
        UncertainReviewRequest $request,
        Organization $organization,
        int $report
    ): JsonResponse {
        return $this->respond($organization, $report, function ($incident) use ($request) {
            return $this->reviews->markUncertain($incident, $request->user(), $request->validated());
        });
    }

    public function close(
        CloseReviewRequest $request,
        Organization $organization,
        int $report
    ): JsonResponse {
        return $this->respond($organization, $report, function ($incident) use ($request) {
            return $this->reviews->close($incident, $request->user(), $request->validated());
        });
    }

    public function escalate(
        EscalateReviewRequest $request,
        Organization $organization,
        int $report
    ): JsonResponse {
        return $this->respond($organization, $report, function ($incident) use ($request) {
            return $this->reviews->escalate($incident, $request->user(), $request->validated());
        });
    }

    public function storeContextRequest(
        StoreContextRequestRequest $request,
        Organization $organization,
        int $report
    ): JsonResponse {
        try {
            $incident = $this->reviews->reviewPackage($organization, $report);
            $contextRequest = $this->reviews->requestContext(
                $incident,
                $request->user(),
                $request->validated()
            );

            return (new IncidentContextRequestResource($contextRequest))
                ->additional([
                    'review' => new IncidentReviewPackageResource(
                        $this->reviews->reviewPackage($organization, $report)
                    ),
                ])
                ->response()
                ->setStatusCode(201);
        } catch (ReviewStateException $exception) {
            return response()->json([
                'message' => $exception->getMessage(),
            ], $exception->status);
        }
    }

    public function updateContextRequest(
        UpdateContextRequestRequest $request,
        Organization $organization,
        int $report,
        int $contextRequest
    ): JsonResponse {
        try {
            $incident = $this->reviews->reviewPackage($organization, $report);
            $model = IncidentContextRequest::query()
                ->where('incident_id', $incident->id)
                ->whereKey($contextRequest)
                ->firstOrFail();

            $updated = $this->reviews->resolveContextRequest(
                $incident,
                $model,
                $request->user(),
                $request->validated()
            );

            return (new IncidentContextRequestResource($updated))
                ->additional([
                    'review' => new IncidentReviewPackageResource(
                        $this->reviews->reviewPackage($organization, $report)
                    ),
                ])
                ->response();
        } catch (ReviewStateException $exception) {
            return response()->json([
                'message' => $exception->getMessage(),
            ], $exception->status);
        }
    }

    /**
     * @param  callable(\App\Models\Incident): \App\Models\Incident  $callback
     */
    private function respond(Organization $organization, int $report, callable $callback): JsonResponse
    {
        try {
            $incident = $this->reviews->reviewPackage($organization, $report);
            $updated = $callback($incident);

            return (new IncidentReviewPackageResource($updated))->response();
        } catch (ReviewStateException $exception) {
            return response()->json([
                'message' => $exception->getMessage(),
            ], $exception->status);
        }
    }
}
