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

    public const DESCRIPTION_MAX_LENGTH = 8000;

    protected $fillable = [
        'organization_id',
        'reported_by',
        'platform',
        'content_type',
        'visibility',
        'source_url',
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

    public function reporter(): BelongsTo
    {
        return $this->belongsTo(User::class, 'reported_by');
    }
}
