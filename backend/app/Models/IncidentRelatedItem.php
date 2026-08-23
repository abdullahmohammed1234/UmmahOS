<?php

namespace App\Models;

use Database\Factories\IncidentRelatedItemFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class IncidentRelatedItem extends Model
{
    /** @use HasFactory<IncidentRelatedItemFactory> */
    use HasFactory;

    public const DESCRIPTION_MAX_LENGTH = 4000;

    public const REFERENCE_URL_MAX_LENGTH = 2048;

    protected $fillable = [
        'incident_id',
        'platform',
        'content_type',
        'reference_url',
        'description',
        'observed_at',
    ];

    /**
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'observed_at' => 'datetime',
        ];
    }

    public function incident(): BelongsTo
    {
        return $this->belongsTo(Incident::class);
    }
}
