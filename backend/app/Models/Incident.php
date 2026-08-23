<?php

namespace App\Models;

use App\Models\Concerns\BelongsToOrganization;
use Database\Factories\IncidentFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Incident extends Model
{
    /** @use HasFactory<IncidentFactory> */
    use BelongsToOrganization, HasFactory;

    public const STATUS_OPEN = 'open';

    public const STATUS_REVIEWING = 'reviewing';

    public const STATUS_RESOLVED = 'resolved';

    public const PLATFORM_X = 'x';

    public const PLATFORM_YOUTUBE = 'youtube';

    public const PLATFORM_TIKTOK = 'tiktok';

    public const PLATFORM_REDDIT = 'reddit';

    public const PLATFORM_DISCORD = 'discord';

    public const PLATFORM_TELEGRAM = 'telegram';

    public const PLATFORM_WHATSAPP = 'whatsapp';

    public const PLATFORM_OTHER = 'other';

    public const CONTENT_TYPE_POST = 'post';

    public const CONTENT_TYPE_COMMENT = 'comment';

    public const CONTENT_TYPE_VIDEO = 'video';

    public const CONTENT_TYPE_IMAGE = 'image';

    public const CONTENT_TYPE_MESSAGE = 'message';

    public const CONTENT_TYPE_PROFILE = 'profile';

    public const CONTENT_TYPE_THREAD = 'thread';

    public const VISIBILITY_PUBLIC = 'public';

    public const VISIBILITY_GROUP = 'group';

    public const VISIBILITY_PRIVATE = 'private';

    public const VISIBILITY_UNKNOWN = 'unknown';

    public const LANGUAGE_UNKNOWN = 'unknown';

    public const CLASSIFICATION_UNCLASSIFIED = 'unclassified';

    public const CLASSIFICATION_HARASSMENT = 'harassment';

    public const CLASSIFICATION_HATE = 'hate';

    public const CLASSIFICATION_THREAT = 'threat';

    public const CLASSIFICATION_TARGETED_ABUSE = 'targeted_abuse';

    public const CLASSIFICATION_DISCRIMINATION = 'discrimination';

    public const CLASSIFICATION_INCITEMENT = 'incitement';

    public const CLASSIFICATION_OTHER = 'other';

    public const OUTCOME_CONFIRMED = 'confirmed';

    public const OUTCOME_UNCERTAIN = 'uncertain';

    public const OUTCOME_CLOSED = 'closed';

    public const DESCRIPTION_MAX_LENGTH = 8000;

    public const ORIGINAL_ITEM_TITLE_MAX_LENGTH = 255;

    public const ORIGINAL_ITEM_CONTENT_MAX_LENGTH = 16000;

    public const ORIGINAL_ITEM_AUTHOR_MAX_LENGTH = 255;

    public const SURROUNDING_CONTEXT_MAX_LENGTH = 8000;

    public const REPORTER_NOTES_MAX_LENGTH = 4000;

    public const REVIEW_NOTES_MAX_LENGTH = 4000;

    public const ESCALATION_REASON_MAX_LENGTH = 4000;

    public const CONTEXT_REQUEST_REASON_MAX_LENGTH = 4000;

    public const LANGUAGE_MAX_LENGTH = 32;

    protected $fillable = [
        'organization_id',
        'reported_by',
        'platform',
        'content_type',
        'visibility',
        'source_url',
        'description',
        'original_item_title',
        'original_item_content',
        'original_item_author',
        'original_item_posted_at',
        'observed_at',
        'surrounding_context',
        'language',
        'reporter_notes',
        'safety_classification',
        'classified_by',
        'classified_at',
        'status',
        'review_outcome',
        'escalated',
        'escalation_reason',
        'escalated_by',
        'escalated_at',
        'current_reviewer_id',
        'review_started_at',
        'review_notes',
        'review_lock_version',
    ];

    /**
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'original_item_posted_at' => 'datetime',
            'observed_at' => 'datetime',
            'classified_at' => 'datetime',
            'escalated' => 'boolean',
            'escalated_at' => 'datetime',
            'review_started_at' => 'datetime',
            'review_lock_version' => 'integer',
        ];
    }

    /**
     * @return list<string>
     */
    public static function statuses(): array
    {
        return [
            self::STATUS_OPEN,
            self::STATUS_REVIEWING,
            self::STATUS_RESOLVED,
        ];
    }

    /**
     * @return list<string>
     */
    public static function reviewOutcomes(): array
    {
        return [
            self::OUTCOME_CONFIRMED,
            self::OUTCOME_UNCERTAIN,
            self::OUTCOME_CLOSED,
        ];
    }

    /**
     * @return list<string>
     */
    public static function platforms(): array
    {
        return [
            self::PLATFORM_X,
            self::PLATFORM_YOUTUBE,
            self::PLATFORM_TIKTOK,
            self::PLATFORM_REDDIT,
            self::PLATFORM_DISCORD,
            self::PLATFORM_TELEGRAM,
            self::PLATFORM_WHATSAPP,
            self::PLATFORM_OTHER,
        ];
    }

    /**
     * @return list<string>
     */
    public static function contentTypes(): array
    {
        return [
            self::CONTENT_TYPE_POST,
            self::CONTENT_TYPE_COMMENT,
            self::CONTENT_TYPE_VIDEO,
            self::CONTENT_TYPE_IMAGE,
            self::CONTENT_TYPE_MESSAGE,
            self::CONTENT_TYPE_PROFILE,
            self::CONTENT_TYPE_THREAD,
        ];
    }

    /**
     * @return list<string>
     */
    public static function visibilities(): array
    {
        return [
            self::VISIBILITY_PUBLIC,
            self::VISIBILITY_GROUP,
            self::VISIBILITY_PRIVATE,
            self::VISIBILITY_UNKNOWN,
        ];
    }

    /**
     * Stable language codes. Expandable in code without a database migration.
     *
     * @return list<string>
     */
    public static function languages(): array
    {
        return [
            'en',
            'ar',
            'fr',
            'ur',
            'tr',
            'es',
            'bn',
            'id',
            'ms',
            'fa',
            'so',
            'sw',
            'de',
            'nl',
            'pt',
            'zh',
            'hi',
            'other',
            self::LANGUAGE_UNKNOWN,
        ];
    }

    /**
     * Internal safety-review classifications — not legal determinations.
     *
     * @return list<string>
     */
    public static function safetyClassifications(): array
    {
        return [
            self::CLASSIFICATION_UNCLASSIFIED,
            self::CLASSIFICATION_HARASSMENT,
            self::CLASSIFICATION_HATE,
            self::CLASSIFICATION_THREAT,
            self::CLASSIFICATION_TARGETED_ABUSE,
            self::CLASSIFICATION_DISCRIMINATION,
            self::CLASSIFICATION_INCITEMENT,
            self::CLASSIFICATION_OTHER,
        ];
    }

    public function reporter(): BelongsTo
    {
        return $this->belongsTo(User::class, 'reported_by');
    }

    public function classifier(): BelongsTo
    {
        return $this->belongsTo(User::class, 'classified_by');
    }

    public function currentReviewer(): BelongsTo
    {
        return $this->belongsTo(User::class, 'current_reviewer_id');
    }

    public function escalatedByUser(): BelongsTo
    {
        return $this->belongsTo(User::class, 'escalated_by');
    }

    public function replies(): HasMany
    {
        return $this->hasMany(IncidentReply::class)->orderBy('position')->orderBy('id');
    }

    public function relatedItems(): HasMany
    {
        return $this->hasMany(IncidentRelatedItem::class)->orderBy('id');
    }

    public function aiAnalyses(): HasMany
    {
        return $this->hasMany(IncidentAiAnalysis::class)->orderByDesc('id');
    }

    public function reviews(): HasMany
    {
        return $this->hasMany(IncidentReview::class)->orderByDesc('id');
    }

    public function reviewActions(): HasMany
    {
        return $this->hasMany(IncidentReviewAction::class)->orderBy('id');
    }

    public function contextRequests(): HasMany
    {
        return $this->hasMany(IncidentContextRequest::class)->orderByDesc('id');
    }

    public function evidenceExports(): HasMany
    {
        return $this->hasMany(IncidentEvidenceExport::class)->orderByDesc('id');
    }
}
