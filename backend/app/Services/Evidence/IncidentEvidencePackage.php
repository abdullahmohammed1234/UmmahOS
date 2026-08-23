<?php

namespace App\Services\Evidence;

/**
 * Immutable structured Incident Evidence Package (schema version 1).
 *
 * Explicit DTO — never serialize Eloquent models directly into exports.
 */
final class IncidentEvidencePackage
{
    public const SCHEMA_VERSION = 1;

    /**
     * @param  array<string, mixed>  $payload
     */
    public function __construct(
        private readonly array $payload,
    ) {}

    /**
     * @return array<string, mixed>
     */
    public function toArray(): array
    {
        return $this->payload;
    }

    public function reference(): string
    {
        return (string) data_get($this->payload, 'incident.reference', 'unknown');
    }

    public function jsonFilename(): string
    {
        return 'community-shield-incident-'.$this->safeFilenameReference().'.json';
    }

    public function pdfFilename(): string
    {
        return 'community-shield-incident-'.$this->safeFilenameReference().'.pdf';
    }

    private function safeFilenameReference(): string
    {
        $reference = preg_replace('/[^A-Za-z0-9._-]+/', '-', $this->reference()) ?: 'unknown';

        return trim($reference, '-') ?: 'unknown';
    }
}
