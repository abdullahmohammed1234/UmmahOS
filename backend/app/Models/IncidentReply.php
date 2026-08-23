<?php

namespace App\Models;

use Database\Factories\IncidentReplyFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class IncidentReply extends Model
{
    /** @use HasFactory<IncidentReplyFactory> */
    use HasFactory;

    public const CONTENT_MAX_LENGTH = 8000;

    public const AUTHOR_MAX_LENGTH = 255;

    protected $fillable = [
        'incident_id',
        'author',
        'content',
        'posted_at',
        'position',
    ];

    /**
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'posted_at' => 'datetime',
            'position' => 'integer',
        ];
    }

    public function incident(): BelongsTo
    {
        return $this->belongsTo(Incident::class);
    }
}
