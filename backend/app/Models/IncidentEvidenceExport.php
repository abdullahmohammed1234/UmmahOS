<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

/**
 * Immutable audit record for evidence package exports.
 * Does not mutate the underlying incident.
 */
class IncidentEvidenceExport extends Model
{
    public const UPDATED_AT = null;

    public const FORMAT_JSON = 'json';

    public const FORMAT_PDF = 'pdf';

    protected $fillable = [
        'incident_id',
        'exported_by',
        'format',
        'package_version',
        'incident_reference',
    ];

    /**
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'package_version' => 'integer',
            'created_at' => 'datetime',
        ];
    }

    public function incident(): BelongsTo
    {
        return $this->belongsTo(Incident::class);
    }

    public function exporter(): BelongsTo
    {
        return $this->belongsTo(User::class, 'exported_by');
    }
}
