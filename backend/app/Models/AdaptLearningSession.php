<?php

namespace App\Models;

use App\Models\Concerns\BelongsToOrganization;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class AdaptLearningSession extends Model
{
    use BelongsToOrganization, HasFactory;

    public const STATUS_ACTIVE = 'active';

    public const STATUS_COMPLETED = 'completed';

    public const STATUS_UNAVAILABLE = 'unavailable';

    protected $fillable = [
        'organization_id',
        'user_id',
        'academy_lesson_id',
        'academy_scenario_id',
        'adapt_session_id',
        'adapt_topic_id',
        'adapt_subject_id',
        'status',
        'started_at',
        'completed_at',
        'last_result',
    ];

    protected function casts(): array
    {
        return [
            'started_at' => 'datetime',
            'completed_at' => 'datetime',
            'last_result' => 'array',
        ];
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function lesson(): BelongsTo
    {
        return $this->belongsTo(AcademyLesson::class, 'academy_lesson_id');
    }

    public function scenario(): BelongsTo
    {
        return $this->belongsTo(AcademyScenario::class, 'academy_scenario_id');
    }
}
