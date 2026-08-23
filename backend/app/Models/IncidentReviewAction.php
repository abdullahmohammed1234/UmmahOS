<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class IncidentReviewAction extends Model
{
    public const UPDATED_AT = null;

    public const ACTION_STARTED = 'started';

    public const ACTION_CONFIRMED = 'confirmed';

    public const ACTION_MARKED_UNCERTAIN = 'marked_uncertain';

    public const ACTION_CLOSED = 'closed';

    public const ACTION_ESCALATED = 'escalated';

    public const ACTION_CONTEXT_REQUESTED = 'context_requested';

    public const ACTION_CONTEXT_FULFILLED = 'context_fulfilled';

    public const ACTION_CONTEXT_CANCELLED = 'context_cancelled';

    public const ACTION_NOTES_UPDATED = 'notes_updated';

    protected $fillable = [
        'incident_id',
        'actor_id',
        'action',
        'notes',
        'payload',
    ];

    /**
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'payload' => 'array',
            'created_at' => 'datetime',
        ];
    }

    public function incident(): BelongsTo
    {
        return $this->belongsTo(Incident::class);
    }

    public function actor(): BelongsTo
    {
        return $this->belongsTo(User::class, 'actor_id');
    }
}
