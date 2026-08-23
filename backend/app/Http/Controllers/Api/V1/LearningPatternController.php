<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Requests\Education\ApproveLearningPatternRequest;
use App\Http\Requests\Education\StoreLearningPatternRequest;
use App\Http\Requests\Education\UpdateLearningPatternRequest;
use App\Http\Resources\LearningPatternResource;
use App\Models\Organization;
use App\Services\Education\LearningPatternService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class LearningPatternController extends Controller
{
    public function __construct(private readonly LearningPatternService $patterns) {}

    public function index(Organization $organization): AnonymousResourceCollection
    {
        return LearningPatternResource::collection(
            $this->patterns->listForStaff($organization)
        );
    }

    public function show(Organization $organization, int $pattern): LearningPatternResource
    {
        return new LearningPatternResource(
            $this->patterns->findForStaff($organization, $pattern)
        );
    }

    public function forReport(Organization $organization, int $report): JsonResponse
    {
        $pattern = $this->patterns->findForIncident($organization, $report);

        if ($pattern === null) {
            return response()->json(['data' => null]);
        }

        return (new LearningPatternResource($pattern))->response();
    }

    public function storeForReport(
        StoreLearningPatternRequest $request,
        Organization $organization,
        int $report
    ): JsonResponse {
        $incident = $organization->incidents()->whereKey($report)->firstOrFail();

        $pattern = $this->patterns->createFromIncident(
            $organization,
            $incident,
            $request->user(),
            $request->validated()
        );

        return (new LearningPatternResource($pattern))
            ->response()
            ->setStatusCode(201);
    }

    public function update(
        UpdateLearningPatternRequest $request,
        Organization $organization,
        int $pattern
    ): LearningPatternResource {
        $model = $this->patterns->findForStaff($organization, $pattern);

        return new LearningPatternResource(
            $this->patterns->update($model, $request->validated())
        );
    }

    public function approve(
        ApproveLearningPatternRequest $request,
        Organization $organization,
        int $pattern
    ): LearningPatternResource {
        $model = $this->patterns->findForStaff($organization, $pattern);

        return new LearningPatternResource(
            $this->patterns->approve($model, $request->user())
        );
    }

    public function archive(Organization $organization, int $pattern): LearningPatternResource
    {
        $model = $this->patterns->findForStaff($organization, $pattern);

        return new LearningPatternResource(
            $this->patterns->archive($model)
        );
    }
}
