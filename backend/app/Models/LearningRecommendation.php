<?php

namespace App\Models;

use App\Models\Concerns\BelongsToOrganization;
use App\Models\Concerns\HasCreator;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class LearningRecommendation extends Model
{
    use BelongsToOrganization, HasCreator, HasFactory;

    public const STATUS_DRAFT = 'draft';

    public const STATUS_PUBLISHED = 'published';

    public const STATUS_ARCHIVED = 'archived';

    protected $fillable = [
        'organization_id',
        'learning_pattern_id',
        'academy_course_id',
        'academy_lesson_id',
        'reason',
        'status',
        'created_by',
    ];

    public function pattern(): BelongsTo
    {
        return $this->belongsTo(LearningPattern::class, 'learning_pattern_id');
    }

    public function course(): BelongsTo
    {
        return $this->belongsTo(Course::class, 'academy_course_id');
    }

    public function lesson(): BelongsTo
    {
        return $this->belongsTo(AcademyLesson::class, 'academy_lesson_id');
    }

    public function isPublished(): bool
    {
        return $this->status === self::STATUS_PUBLISHED;
    }
}
