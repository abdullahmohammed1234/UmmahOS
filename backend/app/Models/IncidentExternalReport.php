<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class IncidentExternalReport extends Model
{
    public const STATUS_REPORTED = 'reported';

    public const STATUS_UNDER_REVIEW = 'under_review';

    public const STATUS_DECISION = 'decision';

    public const STATUS_OUTCOME = 'outcome';

    public const DECISION_ACTION_TAKEN = 'action_taken';

    public const DECISION_NO_ACTION = 'no_action';

    public const DECISION_CONTENT_DOES_NOT_VIOLATE = 'content_does_not_violate_policy';

    public const DECISION_INSUFFICIENT_INFORMATION = 'insufficient_information';

    public const DECISION_OTHER = 'other';

    public const OUTCOME_CONTENT_REMOVED = 'content_removed';

    public const OUTCOME_CONTENT_RESTRICTED = 'content_restricted';

    public const OUTCOME_ACCOUNT_ACTION = 'account_action';

    public const OUTCOME_NO_ACTION = 'no_action';

    public const OUTCOME_WARNING = 'warning';

    public const OUTCOME_RESOLVED = 'resolved';

    public const OUTCOME_UNABLE_TO_DETERMINE = 'unable_to_determine';

    public const OUTCOME_OTHER = 'other';

    public const SOURCE_PLATFORM_RESPONSE = 'platform_response';

    public const SOURCE_REPORTER_OBSERVATION = 'reporter_observation';

    public const SOURCE_REVIEWER_OBSERVATION = 'reviewer_observation';

    public const SOURCE_OTHER = 'other';

    public const VERIFICATION_UNVERIFIED = 'unverified';

    public const VERIFICATION_REPORTED_BY_USER = 'reported_by_user';

    public const VERIFICATION_VERIFIED_BY_REVIEWER = 'verified_by_reviewer';

    public const REPORTING_CHANNEL_MAX_LENGTH = 255;

    public const EXTERNAL_REFERENCE_MAX_LENGTH = 255;

    public const INTERNAL_NOTES_MAX_LENGTH = 4000;

    public const REPORTER_VISIBLE_SUMMARY_MAX_LENGTH = 4000;

    public const DECISION_NOTE_MAX_LENGTH = 4000;

    public const OUTCOME_SUMMARY_MAX_LENGTH = 4000;

    protected $fillable = [
        'incident_id',
        'organization_id',
        'platform',
        'reporting_channel',
        'external_reference',
        'reported_at',
        'status',
        'decision',
        'outcome',
        'outcome_source',
        'verification_status',
        'internal_notes',
        'reporter_visible_summary',
        'decision_note',
        'outcome_summary',
        'created_by',
        'updated_by',
    ];

    /**
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'reported_at' => 'datetime',
        ];
    }

    /**
     * @return list<string>
     */
    public static function statuses(): array
    {
        return [
            self::STATUS_REPORTED,
            self::STATUS_UNDER_REVIEW,
            self::STATUS_DECISION,
            self::STATUS_OUTCOME,
        ];
    }

    /**
     * @return list<string>
     */
    public static function decisions(): array
    {
        return [
            self::DECISION_ACTION_TAKEN,
            self::DECISION_NO_ACTION,
            self::DECISION_CONTENT_DOES_NOT_VIOLATE,
            self::DECISION_INSUFFICIENT_INFORMATION,
            self::DECISION_OTHER,
        ];
    }

    /**
     * @return list<string>
     */
    public static function outcomes(): array
    {
        return [
            self::OUTCOME_CONTENT_REMOVED,
            self::OUTCOME_CONTENT_RESTRICTED,
            self::OUTCOME_ACCOUNT_ACTION,
            self::OUTCOME_NO_ACTION,
            self::OUTCOME_WARNING,
            self::OUTCOME_RESOLVED,
            self::OUTCOME_UNABLE_TO_DETERMINE,
            self::OUTCOME_OTHER,
        ];
    }

    /**
     * @return list<string>
     */
    public static function outcomeSources(): array
    {
        return [
            self::SOURCE_PLATFORM_RESPONSE,
            self::SOURCE_REPORTER_OBSERVATION,
            self::SOURCE_REVIEWER_OBSERVATION,
            self::SOURCE_OTHER,
        ];
    }

    /**
     * @return list<string>
     */
    public static function verificationStatuses(): array
    {
        return [
            self::VERIFICATION_UNVERIFIED,
            self::VERIFICATION_REPORTED_BY_USER,
            self::VERIFICATION_VERIFIED_BY_REVIEWER,
        ];
    }

    /**
     * Reporting destination platforms — incident platforms plus non-platform destinations.
     *
     * @return list<string>
     */
    public static function destinationPlatforms(): array
    {
        return array_merge(Incident::platforms(), [
            'campus_administration',
            'university_office',
            'community_organization',
        ]);
    }

    public function incident(): BelongsTo
    {
        return $this->belongsTo(Incident::class);
    }

    public function organization(): BelongsTo
    {
        return $this->belongsTo(Organization::class);
    }

    public function creator(): BelongsTo
    {
        return $this->belongsTo(User::class, 'created_by');
    }

    public function updater(): BelongsTo
    {
        return $this->belongsTo(User::class, 'updated_by');
    }

    public function statusHistory(): HasMany
    {
        return $this->hasMany(IncidentExternalReportStatusHistory::class)
            ->orderBy('changed_at')
            ->orderBy('id');
    }

    public function appeals(): HasMany
    {
        return $this->hasMany(IncidentReportAppeal::class)
            ->orderBy('submitted_at')
            ->orderBy('id');
    }
}
