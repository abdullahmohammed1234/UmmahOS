<?php

namespace App\Models;

use App\Models\Concerns\BelongsToOrganization;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class AcademyLessonProgress extends Model
{
    use BelongsToOrganization, HasFactory;

    public const STATUS_STARTED = 'started';

    public const STATUS_COMPLETED = 'completed';

    protected $table = 'academy_lesson_progress';

    protected $fillable = [
        'organization_id',
        'user_id',
        'academy_lesson_id',
        'status',
        'started_at',
        'completed_at',
    ];

    protected function casts(): array
    {
        return [
            'started_at' => 'datetime',
            'completed_at' => 'datetime',
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
}
