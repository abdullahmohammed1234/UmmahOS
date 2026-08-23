<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Requests\Education\CompleteAcademyLessonRequest;
use App\Http\Requests\Education\StartAdaptSessionRequest;
use App\Http\Requests\Education\SubmitAdaptResponseRequest;
use App\Http\Resources\AcademyLessonProgressResource;
use App\Http\Resources\AcademyLessonResource;
use App\Http\Resources\AcademyScenarioResource;
use App\Models\Organization;
use App\Services\Education\AcademyEducationService;
use App\Services\Education\AdaptLearningSessionService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class AcademyEducationController extends Controller
{
    public function __construct(
        private readonly AcademyEducationService $academy,
        private readonly AdaptLearningSessionService $adaptSessions,
    ) {}

    public function communitySafety(Organization $organization): AnonymousResourceCollection
    {
        return AcademyLessonResource::collection(
            $this->academy->communitySafetyLessons($organization)
        );
    }

    public function showLesson(Organization $organization, int $lesson): AcademyLessonResource
    {
        return new AcademyLessonResource(
            $this->academy->findLesson($organization, $lesson)
        );
    }

    public function showScenario(Organization $organization, int $scenario): AcademyScenarioResource
    {
        return new AcademyScenarioResource(
            $this->academy->findScenario($organization, $scenario)
        );
    }

    public function progress(Organization $organization): AnonymousResourceCollection
    {
        return AcademyLessonProgressResource::collection(
            $this->academy->progressForUser($organization, request()->user())
        );
    }

    public function completeLesson(
        CompleteAcademyLessonRequest $request,
        Organization $organization,
        int $lesson
    ): AcademyLessonProgressResource {
        $model = $this->academy->findLesson($organization, $lesson);

        return new AcademyLessonProgressResource(
            $this->academy->markCompleted($organization, $request->user(), $model)
        );
    }

    public function startAdapt(
        StartAdaptSessionRequest $request,
        Organization $organization,
        int $lesson
    ): JsonResponse {
        $model = $this->academy->findLesson($organization, $lesson);
        $payload = $this->adaptSessions->start($organization, $request->user(), $model);

        return response()->json(['data' => $payload], $payload['available'] ? 201 : 200);
    }

    public function showAdaptSession(Organization $organization, int $session): JsonResponse
    {
        $payload = $this->adaptSessions->show($organization, request()->user(), $session);

        return response()->json(['data' => $payload]);
    }

    public function submitAdapt(
        SubmitAdaptResponseRequest $request,
        Organization $organization,
        int $session
    ): JsonResponse {
        $payload = $this->adaptSessions->submit(
            $organization,
            $request->user(),
            $session,
            $request->validated()
        );

        return response()->json(['data' => $payload]);
    }
}
