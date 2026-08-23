<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

/**
 * Append-only audit log for external report status transitions.
 */
class IncidentExternalReportStatusHistory extends Model
{
    public const UPDATED_AT = null;

    protected $table = 'incident_external_report_status_history';

    protected $fillable = [
        'incident_external_report_id',
        'previous_status',
        'new_status',
        'decision',
        'outcome',
        'changed_by',
        'note',
        'changed_at',
    ];

    /**
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'changed_at' => 'datetime',
            'created_at' => 'datetime',
        ];
    }

    public function externalReport(): BelongsTo
    {
        return $this->belongsTo(IncidentExternalReport::class, 'incident_external_report_id');
    }

    public function changedByUser(): BelongsTo
    {
        return $this->belongsTo(User::class, 'changed_by');
    }
}
