<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class IncidentReportAppeal extends Model
{
    public const STATUS_SUBMITTED = 'submitted';

    public const STATUS_UNDER_REVIEW = 'under_review';

    public const STATUS_ACCEPTED = 'accepted';

    public const STATUS_REJECTED = 'rejected';

    public const STATUS_WITHDRAWN = 'withdrawn';

    public const STATUS_RESOLVED = 'resolved';

    public const REASON_MAX_LENGTH = 4000;

    public const ADDITIONAL_EVIDENCE_MAX_LENGTH = 4000;

    public const REFERENCE_MAX_LENGTH = 255;

    public const NOTES_MAX_LENGTH = 4000;

    public const RESPONSE_MAX_LENGTH = 4000;

    protected $fillable = [
        'incident_external_report_id',
        'submitted_at',
        'submitted_by',
        'reason',
        'additional_evidence',
        'reference',
        'notes',
        'status',
        'response',
        'responded_at',
        'responded_by',
    ];

    /**
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'submitted_at' => 'datetime',
            'responded_at' => 'datetime',
        ];
    }

    /**
     * @return list<string>
     */
    public static function statuses(): array
    {
        return [
            self::STATUS_SUBMITTED,
            self::STATUS_UNDER_REVIEW,
            self::STATUS_ACCEPTED,
            self::STATUS_REJECTED,
            self::STATUS_WITHDRAWN,
            self::STATUS_RESOLVED,
        ];
    }

    public function externalReport(): BelongsTo
    {
        return $this->belongsTo(IncidentExternalReport::class, 'incident_external_report_id');
    }

    public function submitter(): BelongsTo
    {
        return $this->belongsTo(User::class, 'submitted_by');
    }

    public function responder(): BelongsTo
    {
        return $this->belongsTo(User::class, 'responded_by');
    }
}
