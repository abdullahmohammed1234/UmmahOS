<?php

namespace App\Http\Controllers\Api\V1;

use App\Exceptions\Outcome\OutcomeStateException;
use App\Http\Controllers\Controller;
use App\Http\Requests\Outcome\StoreAppealRequest;
use App\Http\Requests\Outcome\StoreExternalReportRequest;
use App\Http\Requests\Outcome\UpdateAppealRequest;
use App\Http\Requests\Outcome\UpdateExternalReportRequest;
use App\Http\Resources\IncidentExternalReportResource;
use App\Http\Resources\IncidentExternalReportStatusHistoryResource;
use App\Http\Resources\IncidentReportAppealResource;
use App\Http\Resources\MemberReportResource;
use App\Models\Organization;
use App\Services\Outcome\IncidentOutcomeService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class IncidentOutcomeController extends Controller
{
    public function __construct(private readonly IncidentOutcomeService $outcomes) {}

    public function index(Organization $organization, int $report): AnonymousResourceCollection
    {
        return IncidentExternalReportResource::collection(
            $this->outcomes->listForIncident($organization, $report)
        );
    }

    public function store(
        StoreExternalReportRequest $request,
        Organization $organization,
        int $report
    ): JsonResponse {
        return $this->respond(function () use ($request, $organization, $report) {
            $reportModel = $this->outcomes->recordExternalReport(
                $organization,
                $report,
                $request->user(),
                $request->validated()
            );

            return (new IncidentExternalReportResource($reportModel))
                ->response()
                ->setStatusCode(201);
        });
    }

    public function show(Organization $organization, int $report, int $externalReport): IncidentExternalReportResource
    {
        return new IncidentExternalReportResource(
            $this->outcomes->findReport($organization, $report, $externalReport)
        );
    }

    public function update(
        UpdateExternalReportRequest $request,
        Organization $organization,
        int $report,
        int $externalReport
    ): JsonResponse|IncidentExternalReportResource {
        return $this->respond(function () use ($request, $organization, $report, $externalReport) {
            return new IncidentExternalReportResource(
                $this->outcomes->updateReport(
                    $organization,
                    $report,
                    $externalReport,
                    $request->user(),
                    $request->validated()
                )
            );
        });
    }

    public function history(
        Organization $organization,
        int $report,
        int $externalReport
    ): AnonymousResourceCollection {
        $reportModel = $this->outcomes->findReport($organization, $report, $externalReport);

        return IncidentExternalReportStatusHistoryResource::collection(
            $reportModel->statusHistory
        );
    }

    public function storeAppeal(
        StoreAppealRequest $request,
        Organization $organization,
        int $report,
        int $externalReport
    ): JsonResponse {
        return $this->respond(function () use ($request, $organization, $report, $externalReport) {
            $appeal = $this->outcomes->submitAppeal(
                $organization,
                $report,
                $externalReport,
                $request->user(),
                $request->validated(),
                false
            );

            return (new IncidentReportAppealResource($appeal))
                ->response()
                ->setStatusCode(201);
        });
    }

    public function updateAppeal(
        UpdateAppealRequest $request,
        Organization $organization,
        int $report,
        int $externalReport,
        int $appeal
    ): IncidentReportAppealResource {
        return new IncidentReportAppealResource(
            $this->outcomes->updateAppeal(
                $organization,
                $report,
                $externalReport,
                $appeal,
                $request->user(),
                $request->validated()
            )
        );
    }

    public function memberIndex(Request $request, Organization $organization): AnonymousResourceCollection
    {
        $request->attributes->set('member_outcome_view', true);

        return MemberReportResource::collection(
            $this->outcomes->listMemberReports($organization, $request->user())
        )->additional(['member_outcome_view' => true]);
    }

    public function memberShow(Request $request, Organization $organization, int $report): MemberReportResource
    {
        $request->attributes->set('member_outcome_view', true);

        $incident = $this->outcomes->memberReportDetail($organization, $request->user(), $report);

        return (new MemberReportResource($incident))->additional(['member_outcome_view' => true]);
    }

    public function memberStoreAppeal(
        StoreAppealRequest $request,
        Organization $organization,
        int $report,
        int $externalReport
    ): JsonResponse {
        return $this->respond(function () use ($request, $organization, $report, $externalReport) {
            $appeal = $this->outcomes->submitAppeal(
                $organization,
                $report,
                $externalReport,
                $request->user(),
                $request->validated(),
                true
            );

            return (new IncidentReportAppealResource($appeal))
                ->response()
                ->setStatusCode(201);
        });
    }

    private function respond(callable $callback): JsonResponse|IncidentExternalReportResource|IncidentReportAppealResource
    {
        try {
            return $callback();
        } catch (OutcomeStateException $exception) {
            return response()->json([
                'message' => $exception->getMessage(),
            ], 422);
        }
    }
}
