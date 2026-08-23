<?php

namespace App\Models;

use App\Models\Concerns\BelongsToOrganization;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class AcademyScenario extends Model
{
    use BelongsToOrganization, HasFactory;

    protected $fillable = [
        'organization_id',
        'academy_lesson_id',
        'title',
        'prompt',
        'context',
        'options',
        'expected_reasoning_signals',
        'misconception_tags',
        'difficulty',
        'adapt_challenge_id',
        'adapt_topic_id',
        'adapt_concept_id',
        'adapt_domain',
        'sort_order',
        'is_demo',
    ];

    protected function casts(): array
    {
        return [
            'options' => 'array',
            'expected_reasoning_signals' => 'array',
            'misconception_tags' => 'array',
            'is_demo' => 'boolean',
        ];
    }

    public function lesson(): BelongsTo
    {
        return $this->belongsTo(AcademyLesson::class, 'academy_lesson_id');
    }
}
