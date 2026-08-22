<?php

namespace App\Http\Middleware;

use App\Models\Organization;
use App\Support\OrganizationContext;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class EnsureOrganizationMembership
{
    public function handle(Request $request, Closure $next): Response
    {
        $user = $request->user();

        if ($user === null) {
            return response()->json([
                'message' => 'Unauthenticated.',
            ], 401);
        }

        $organization = $request->route('organization');

        if (! $organization instanceof Organization) {
            return response()->json([
                'message' => 'Invalid organization context.',
            ], 400);
        }

        $membership = $user->membershipFor($organization);

        if ($membership === null) {
            return response()->json([
                'message' => 'You are not a member of this organization.',
            ], 403);
        }

        $membership->loadMissing('role.permissions');

        $context = new OrganizationContext($organization, $membership, $user);
        app()->instance(OrganizationContext::class, $context);
        $request->attributes->set('organizationContext', $context);

        return $next($request);
    }
}
