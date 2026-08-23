<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Resources\IncidentAiAnalysisResource;
use App\Models\Organization;
use App\Services\AI\IncidentAiAnalysisService;
use App\Services\IncidentService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class IncidentAiAnalysisController extends Controller
{
    public function __construct(
        private readonly IncidentService $incidents,
        private readonly IncidentAiAnalysisService $analyses,
    ) {}

    public function index(Organization $organization, int $incident): AnonymousResourceCollection
    {
        $model = $this->incidents->findInOrganization($organization, $incident);

        return IncidentAiAnalysisResource::collection(
            $this->analyses->listForIncident($model)
        );
    }

    public function show(Organization $organization, int $incident, int $analysis): IncidentAiAnalysisResource
    {
        $model = $this->incidents->findInOrganization($organization, $incident);

        return new IncidentAiAnalysisResource(
            $this->analyses->findForIncident($model, $analysis)
        );
    }

    public function store(Organization $organization, int $incident): JsonResponse
    {
        $model = $this->incidents->findInOrganization($organization, $incident);
        $analysis = $this->analyses->requestAnalysis($model, request()->user());

        return (new IncidentAiAnalysisResource($analysis))
            ->additional([
                'message' => $analysis->isFailed()
                    ? ($analysis->error_message ?? 'AI analysis unavailable.')
                    : 'AI context analysis completed. Human review is still required.',
                'provider_available' => $this->analyses->providerAvailable(),
            ])
            ->response()
            ->setStatusCode(201);
    }
}
