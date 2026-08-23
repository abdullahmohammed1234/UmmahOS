<?php

namespace App\Models;

use App\Models\Concerns\BelongsToOrganization;
use Database\Factories\IncidentFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Incident extends Model
{
    /** @use HasFactory<IncidentFactory> */
    use BelongsToOrganization, HasFactory;

    public const STATUS_OPEN = 'open';
    public const STATUS_REVIEWING = 'reviewing';
    public const STATUS_RESOLVED = 'resolved';

    public const CATEGORY_SAFETY = 'safety';
    public const CATEGORY_HARASSMENT = 'harassment';
    public const CATEGORY_HATE = 'hate';
    public const CATEGORY_COMMUNITY_CONCERN = 'community_concern';
    public const CATEGORY_OTHER = 'other';

    protected $fillable = [
        'organization_id',
        'reported_by',
        'category',
        'description',
        'status',
    ];

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
    public static function categories(): array
    {
        return [
            self::CATEGORY_SAFETY,
            self::CATEGORY_HARASSMENT,
            self::CATEGORY_HATE,
            self::CATEGORY_COMMUNITY_CONCERN,
            self::CATEGORY_OTHER,
        ];
    }

    public function reporter(): BelongsTo
    {
        return $this->belongsTo(User::class, 'reported_by');
    }
}
