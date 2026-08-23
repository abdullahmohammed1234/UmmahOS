<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Requests\Course\StoreCourseRequest;
use App\Http\Requests\Course\UpdateCourseRequest;
use App\Http\Resources\CourseResource;
use App\Models\Organization;
use App\Services\CourseService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class CourseController extends Controller
{
    public function __construct(private readonly CourseService $courses) {}

    public function index(Organization $organization): AnonymousResourceCollection
    {
        return CourseResource::collection(
            $this->courses->listForCurrentViewer($organization)
        );
    }

    public function store(
        StoreCourseRequest $request,
        Organization $organization
    ): JsonResponse {
        $course = $this->courses->create(
            $organization,
            $request->user(),
            $request->validated()
        );

        return (new CourseResource($course))
            ->response()
            ->setStatusCode(201);
    }

    public function show(Organization $organization, int $course): CourseResource
    {
        return new CourseResource(
            $this->courses->findVisible($organization, $course)
        );
    }

    public function update(
        UpdateCourseRequest $request,
        Organization $organization,
        int $course
    ): CourseResource {
        $model = $this->courses->findVisible($organization, $course);

        return new CourseResource(
            $this->courses->update($model, $request->validated())
        );
    }

    public function destroy(Organization $organization, int $course): JsonResponse
    {
        $model = $this->courses->findVisible($organization, $course);
        $this->courses->delete($model);

        return response()->json([
            'message' => 'Course deleted.',
        ]);
    }
}
