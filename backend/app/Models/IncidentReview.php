<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class IncidentReview extends Model
{
    public const OUTCOME_CONFIRMED = 'confirmed';

    public const OUTCOME_UNCERTAIN = 'uncertain';

    public const OUTCOME_CLOSED = 'closed';

    protected $fillable = [
        'incident_id',
        'reviewer_id',
        'outcome',
        'notes',
        'safety_classification',
        'escalation_reason',
        'is_current',
    ];

    /**
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'is_current' => 'boolean',
        ];
    }

    /**
     * @return list<string>
     */
    public static function outcomes(): array
    {
        return [
            self::OUTCOME_CONFIRMED,
            self::OUTCOME_UNCERTAIN,
            self::OUTCOME_CLOSED,
        ];
    }

    public function incident(): BelongsTo
    {
        return $this->belongsTo(Incident::class);
    }

    public function reviewer(): BelongsTo
    {
        return $this->belongsTo(User::class, 'reviewer_id');
    }
}
