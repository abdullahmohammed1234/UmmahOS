<?php

namespace App\Http\Middleware;

use App\Support\OrganizationContext;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class EnsureOrganizationPermission
{
    public function handle(Request $request, Closure $next, string $permissions): Response
    {
        if ($request->user() === null) {
            return response()->json([
                'message' => 'Unauthenticated.',
            ], 401);
        }

        $context = $request->attributes->get('organizationContext');

        if (! $context instanceof OrganizationContext) {
            return response()->json([
                'message' => 'Invalid organization context.',
            ], 400);
        }

        foreach (explode('|', $permissions) as $permission) {
            if ($context->hasPermission(trim($permission))) {
                return $next($request);
            }
        }

        return response()->json([
            'message' => 'Unauthorized.',
        ], 403);
    }
}
