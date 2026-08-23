<?php

namespace App\Models;

use App\Models\Concerns\BelongsToOrganization;
use App\Models\Concerns\HasCreator;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class LearningPattern extends Model
{
    use BelongsToOrganization, HasCreator, HasFactory;

    public const STATUS_DRAFT = 'draft';

    public const STATUS_APPROVED = 'approved';

    public const STATUS_ARCHIVED = 'archived';

    public const PATTERN_TYPES = [
        'religious_targeting',
        'coded_language',
        'repeated_harassment',
        'contextual_hate',
        'visual_hate',
        'dog_whistle',
        'coordinated_behavior',
        'misinformation_related_harm',
        'reporting_safety',
        'other',
    ];

    protected $fillable = [
        'organization_id',
        'source_incident_id',
        'pattern_type',
        'title',
        'summary',
        'learning_objective',
        'domain',
        'severity_context',
        'status',
        'created_by',
        'approved_by',
        'approved_at',
    ];

    protected function casts(): array
    {
        return [
            'approved_at' => 'datetime',
        ];
    }

    public function sourceIncident(): BelongsTo
    {
        return $this->belongsTo(Incident::class, 'source_incident_id');
    }

    public function approver(): BelongsTo
    {
        return $this->belongsTo(User::class, 'approved_by');
    }

    public function recommendations(): HasMany
    {
        return $this->hasMany(LearningRecommendation::class);
    }

    public function isApproved(): bool
    {
        return $this->status === self::STATUS_APPROVED;
    }

    public function isDraft(): bool
    {
        return $this->status === self::STATUS_DRAFT;
    }
}
