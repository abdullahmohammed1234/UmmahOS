<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Models\IncidentEvidenceExport;
use App\Models\Organization;
use App\Services\Evidence\EvidencePackagePdfRenderer;
use App\Services\Evidence\IncidentEvidencePackage;
use App\Services\Evidence\IncidentEvidencePackageService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Response;
use Symfony\Component\HttpFoundation\StreamedResponse;

class IncidentEvidencePackageController extends Controller
{
    public function __construct(
        private readonly IncidentEvidencePackageService $packages,
        private readonly EvidencePackagePdfRenderer $pdfRenderer,
    ) {}

    public function show(Organization $organization, int $report): JsonResponse
    {
        $package = $this->packages->build($organization, $report, request()->user());

        return response()->json(['data' => $package->toArray()]);
    }

    public function exportJson(Organization $organization, int $report): StreamedResponse
    {
        $package = $this->packages->build($organization, $report, request()->user());
        $this->recordExport($organization, $report, $package, IncidentEvidenceExport::FORMAT_JSON);

        $filename = $package->jsonFilename();
        $json = json_encode(
            $package->toArray(),
            JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES
        );

        return response()->streamDownload(
            function () use ($json): void {
                echo $json;
            },
            $filename,
            [
                'Content-Type' => 'application/json; charset=UTF-8',
            ]
        );
    }

    public function exportPdf(Organization $organization, int $report): Response
    {
        $package = $this->packages->build($organization, $report, request()->user());
        $binary = $this->pdfRenderer->render($package);
        $this->recordExport($organization, $report, $package, IncidentEvidenceExport::FORMAT_PDF);

        return response($binary, 200, [
            'Content-Type' => 'application/pdf',
            'Content-Disposition' => 'attachment; filename="'.$package->pdfFilename().'"',
            'Content-Length' => (string) strlen($binary),
        ]);
    }

    private function recordExport(
        Organization $organization,
        int $report,
        IncidentEvidencePackage $package,
        string $format
    ): void {
        $incident = $organization->incidents()->findOrFail($report);

        IncidentEvidenceExport::query()->create([
            'incident_id' => $incident->id,
            'exported_by' => request()->user()->id,
            'format' => $format,
            'package_version' => (int) data_get($package->toArray(), 'package.package_version', 1),
            'incident_reference' => $package->reference(),
        ]);
    }
}
