<?php

use App\Http\Controllers\Api\V1\AuthController;
use App\Http\Controllers\Api\V1\FutureModuleIsolationController;
use App\Http\Controllers\Api\V1\MembershipController;
use App\Http\Controllers\Api\V1\OrganizationContextController;
use App\Http\Controllers\Api\V1\OrganizationController;
use Illuminate\Support\Facades\Route;

Route::prefix('v1')->group(function () {
    Route::prefix('auth')->group(function () {
        Route::post('/login', [AuthController::class, 'login'])
            ->middleware('throttle:auth')
            ->name('api.auth.login');

        Route::middleware('auth:sanctum')->group(function () {
            Route::post('/logout', [AuthController::class, 'logout'])->name('api.auth.logout');
            Route::get('/me', [AuthController::class, 'me'])->name('api.auth.me');
        });
    });

    Route::middleware('auth:sanctum')->group(function () {
        Route::get('/organizations', [OrganizationController::class, 'index'])
            ->name('api.organizations.index');
        Route::post('/organizations', [OrganizationController::class, 'store'])
            ->name('api.organizations.store');

        Route::prefix('organizations/{organization}')
            ->middleware('organization.member')
            ->group(function () {
                Route::get('/', [OrganizationController::class, 'show'])
                    ->middleware('organization.permission:organization.view')
                    ->name('api.organizations.show');
                Route::patch('/', [OrganizationController::class, 'update'])
                    ->middleware('organization.permission:organization.manage')
                    ->name('api.organizations.update');
                Route::delete('/', [OrganizationController::class, 'destroy'])
                    ->middleware('organization.permission:organization.manage')
                    ->name('api.organizations.destroy');

                Route::get('/context', [OrganizationContextController::class, 'show'])
                    ->name('api.organizations.context');

                Route::get('/members', [MembershipController::class, 'index'])
                    ->middleware('organization.permission:members.view')
                    ->name('api.organizations.members.index');
                Route::post('/members', [MembershipController::class, 'store'])
                    ->middleware('organization.permission:members.manage')
                    ->name('api.organizations.members.store');
                Route::patch('/members/{membership}', [MembershipController::class, 'update'])
                    ->middleware('organization.permission:members.manage')
                    ->name('api.organizations.members.update');
                Route::delete('/members/{membership}', [MembershipController::class, 'destroy'])
                    ->middleware('organization.permission:members.manage')
                    ->name('api.organizations.members.destroy');

                Route::prefix('{module}')
                    ->whereIn('module', ['events', 'courses', 'content', 'incidents', 'reports'])
                    ->group(function () {
                        Route::get('/{record}', [FutureModuleIsolationController::class, 'show'])
                            ->name('api.organizations.modules.show');
                        Route::patch('/{record}', [FutureModuleIsolationController::class, 'update'])
                            ->name('api.organizations.modules.update');
                        Route::delete('/{record}', [FutureModuleIsolationController::class, 'destroy'])
                            ->name('api.organizations.modules.destroy');
                    });
            });
    });
});
