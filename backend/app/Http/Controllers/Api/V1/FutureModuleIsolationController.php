<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Models\Organization;
use Illuminate\Http\JsonResponse;

/**
 * Phase 1 isolation lock for future organization-scoped modules.
 *
 * Events, courses, content, incidents, and reports are not implemented yet.
 * These endpoints only prove that non-members cannot reach another
 * organization's resource namespace, including direct-ID (IDOR) URLs.
 */
class FutureModuleIsolationController extends Controller
{
    public function show(Organization $organization, string $module, int $record): JsonResponse
    {
        return $this->notImplemented($organization, $module, $record);
    }

    public function update(Organization $organization, string $module, int $record): JsonResponse
    {
        return $this->notImplemented($organization, $module, $record);
    }

    public function destroy(Organization $organization, string $module, int $record): JsonResponse
    {
        return $this->notImplemented($organization, $module, $record);
    }

    private function notImplemented(Organization $organization, string $module, int $record): JsonResponse
    {
        return response()->json([
            'message' => 'Resource not found in this organization.',
            'organization_id' => $organization->id,
            'module' => $module,
            'record_id' => $record,
        ], 404);
    }
}
