<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Resources\OrganizationContextResource;
use App\Models\Organization;
use App\Support\OrganizationContext;
use Illuminate\Http\Request;

class OrganizationContextController extends Controller
{
    public function show(Request $request, Organization $organization): OrganizationContextResource
    {
        $context = $request->attributes->get('organizationContext');

        if (! $context instanceof OrganizationContext) {
            abort(400, 'Invalid organization context.');
        }

        return new OrganizationContextResource($context);
    }
}
