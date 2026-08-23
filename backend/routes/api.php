<?php

use App\Http\Controllers\Api\V1\AnnouncementController;
use App\Http\Controllers\Api\V1\AuthController;
use App\Http\Controllers\Api\V1\CourseController;
use App\Http\Controllers\Api\V1\DashboardController;
use App\Http\Controllers\Api\V1\EventController;
use App\Http\Controllers\Api\V1\FutureModuleIsolationController;
use App\Http\Controllers\Api\V1\IncidentAiAnalysisController;
use App\Http\Controllers\Api\V1\IncidentController;
use App\Http\Controllers\Api\V1\MembershipController;
use App\Http\Controllers\Api\V1\OrganizationContextController;
use App\Http\Controllers\Api\V1\OrganizationController;
use App\Http\Controllers\Api\V1\ResourceController;
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

                Route::get('/dashboard', [DashboardController::class, 'member'])
                    ->middleware('organization.permission:organization.view')
                    ->name('api.organizations.dashboard');
                Route::get('/admin/dashboard', [DashboardController::class, 'admin'])
                    ->middleware('organization.permission:organization.manage')
                    ->name('api.organizations.admin.dashboard');

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

                Route::get('/announcements', [AnnouncementController::class, 'index'])
                    ->middleware('organization.permission:content.view')
                    ->name('api.organizations.announcements.index');
                Route::post('/announcements', [AnnouncementController::class, 'store'])
                    ->middleware('organization.permission:content.manage')
                    ->name('api.organizations.announcements.store');
                Route::get('/announcements/{announcement}', [AnnouncementController::class, 'show'])
                    ->middleware('organization.permission:content.view')
                    ->name('api.organizations.announcements.show');
                Route::patch('/announcements/{announcement}', [AnnouncementController::class, 'update'])
                    ->middleware('organization.permission:content.manage')
                    ->name('api.organizations.announcements.update');
                Route::delete('/announcements/{announcement}', [AnnouncementController::class, 'destroy'])
                    ->middleware('organization.permission:content.manage')
                    ->name('api.organizations.announcements.destroy');

                Route::get('/resources', [ResourceController::class, 'index'])
                    ->middleware('organization.permission:content.view')
                    ->name('api.organizations.resources.index');
                Route::post('/resources', [ResourceController::class, 'store'])
                    ->middleware('organization.permission:content.manage')
                    ->name('api.organizations.resources.store');
                Route::get('/resources/{resource}', [ResourceController::class, 'show'])
                    ->middleware('organization.permission:content.view')
                    ->name('api.organizations.resources.show');
                Route::patch('/resources/{resource}', [ResourceController::class, 'update'])
                    ->middleware('organization.permission:content.manage')
                    ->name('api.organizations.resources.update');
                Route::delete('/resources/{resource}', [ResourceController::class, 'destroy'])
                    ->middleware('organization.permission:content.manage')
                    ->name('api.organizations.resources.destroy');

                Route::get('/events', [EventController::class, 'index'])
                    ->middleware('organization.permission:events.view')
                    ->name('api.organizations.events.index');
                Route::post('/events', [EventController::class, 'store'])
                    ->middleware('organization.permission:events.manage')
                    ->name('api.organizations.events.store');
                Route::get('/events/{event}', [EventController::class, 'show'])
                    ->middleware('organization.permission:events.view')
                    ->name('api.organizations.events.show');
                Route::patch('/events/{event}', [EventController::class, 'update'])
                    ->middleware('organization.permission:events.manage')
                    ->name('api.organizations.events.update');
                Route::delete('/events/{event}', [EventController::class, 'destroy'])
                    ->middleware('organization.permission:events.manage')
                    ->name('api.organizations.events.destroy');

                Route::get('/courses', [CourseController::class, 'index'])
                    ->middleware('organization.permission:courses.view')
                    ->name('api.organizations.courses.index');
                Route::post('/courses', [CourseController::class, 'store'])
                    ->middleware('organization.permission:courses.manage')
                    ->name('api.organizations.courses.store');
                Route::get('/courses/{course}', [CourseController::class, 'show'])
                    ->middleware('organization.permission:courses.view')
                    ->name('api.organizations.courses.show');
                Route::patch('/courses/{course}', [CourseController::class, 'update'])
                    ->middleware('organization.permission:courses.manage')
                    ->name('api.organizations.courses.update');
                Route::delete('/courses/{course}', [CourseController::class, 'destroy'])
                    ->middleware('organization.permission:courses.manage')
                    ->name('api.organizations.courses.destroy');

                Route::get('/community-shield', [IncidentController::class, 'overview'])
                    ->name('api.organizations.community-shield.overview');
                Route::post('/incidents', [IncidentController::class, 'store'])
                    ->name('api.organizations.incidents.store');
                Route::get('/incidents', [IncidentController::class, 'index'])
                    ->middleware('organization.permission:incidents.manage')
                    ->name('api.organizations.incidents.index');
                Route::get('/incidents/{incident}', [IncidentController::class, 'show'])
                    ->middleware('organization.permission:incidents.manage')
                    ->name('api.organizations.incidents.show');
                Route::patch('/incidents/{incident}', [IncidentController::class, 'update'])
                    ->middleware('organization.permission:incidents.manage')
                    ->name('api.organizations.incidents.update');
                Route::post('/incidents/{incident}/replies', [IncidentController::class, 'storeReply'])
                    ->middleware('organization.permission:incidents.manage')
                    ->name('api.organizations.incidents.replies.store');
                Route::delete('/incidents/{incident}/replies/{reply}', [IncidentController::class, 'destroyReply'])
                    ->middleware('organization.permission:incidents.manage')
                    ->name('api.organizations.incidents.replies.destroy');
                Route::post('/incidents/{incident}/related-items', [IncidentController::class, 'storeRelatedItem'])
                    ->middleware('organization.permission:incidents.manage')
                    ->name('api.organizations.incidents.related-items.store');
                Route::delete('/incidents/{incident}/related-items/{relatedItem}', [IncidentController::class, 'destroyRelatedItem'])
                    ->middleware('organization.permission:incidents.manage')
                    ->name('api.organizations.incidents.related-items.destroy');

                Route::post('/incidents/{incident}/ai-analysis', [IncidentAiAnalysisController::class, 'store'])
                    ->middleware('organization.permission:incidents.manage')
                    ->name('api.organizations.incidents.ai-analysis.store');
                Route::get('/incidents/{incident}/ai-analyses', [IncidentAiAnalysisController::class, 'index'])
                    ->middleware('organization.permission:incidents.manage')
                    ->name('api.organizations.incidents.ai-analyses.index');
                Route::get('/incidents/{incident}/ai-analyses/{analysis}', [IncidentAiAnalysisController::class, 'show'])
                    ->middleware('organization.permission:incidents.manage')
                    ->name('api.organizations.incidents.ai-analyses.show');

                Route::prefix('{module}')
                    ->whereIn('module', ['content', 'reports'])
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
