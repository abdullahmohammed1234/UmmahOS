<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Requests\Education\StoreLearningRecommendationRequest;
use App\Http\Requests\Education\UpdateLearningRecommendationRequest;
use App\Http\Resources\LearningRecommendationResource;
use App\Models\Organization;
use App\Services\Education\LearningRecommendationService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class LearningRecommendationController extends Controller
{
    public function __construct(private readonly LearningRecommendationService $recommendations) {}

    public function index(Organization $organization): AnonymousResourceCollection
    {
        return LearningRecommendationResource::collection(
            $this->recommendations->listForViewer($organization)
        );
    }

    public function store(
        StoreLearningRecommendationRequest $request,
        Organization $organization
    ): JsonResponse {
        $recommendation = $this->recommendations->create(
            $organization,
            $request->user(),
            $request->validated()
        );

        return (new LearningRecommendationResource($recommendation))
            ->response()
            ->setStatusCode(201);
    }

    public function show(Organization $organization, int $recommendation): LearningRecommendationResource
    {
        return new LearningRecommendationResource(
            $this->recommendations->findVisible($organization, $recommendation)
        );
    }

    public function update(
        UpdateLearningRecommendationRequest $request,
        Organization $organization,
        int $recommendation
    ): LearningRecommendationResource {
        $model = $this->recommendations->findVisible($organization, $recommendation);

        return new LearningRecommendationResource(
            $this->recommendations->update($model, $request->validated())
        );
    }
}
