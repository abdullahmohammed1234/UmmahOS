<?php

namespace App\Models;

use App\Models\Concerns\BelongsToOrganization;
use App\Models\Concerns\HasCreator;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class AcademyLesson extends Model
{
    use BelongsToOrganization, HasCreator, HasFactory;

    public const STATUS_DRAFT = 'draft';

    public const STATUS_PUBLISHED = 'published';

    public const CATEGORY_GENERAL = 'general';

    public const CATEGORY_COMMUNITY_SAFETY = 'community_safety';

    protected $fillable = [
        'organization_id',
        'course_id',
        'title',
        'learning_objective',
        'sections',
        'category',
        'status',
        'is_demo',
        'created_by',
    ];

    protected function casts(): array
    {
        return [
            'sections' => 'array',
            'is_demo' => 'boolean',
        ];
    }

    public function course(): BelongsTo
    {
        return $this->belongsTo(Course::class);
    }

    public function scenarios(): HasMany
    {
        return $this->hasMany(AcademyScenario::class)->orderBy('sort_order');
    }

    public function progressRecords(): HasMany
    {
        return $this->hasMany(AcademyLessonProgress::class);
    }

    public function recommendations(): HasMany
    {
        return $this->hasMany(LearningRecommendation::class);
    }

    public function isPublished(): bool
    {
        return $this->status === self::STATUS_PUBLISHED;
    }
}
