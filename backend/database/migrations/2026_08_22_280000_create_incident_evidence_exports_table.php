<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('incident_evidence_exports', function (Blueprint $table) {
            $table->id();
            $table->foreignId('incident_id')->constrained('incidents')->cascadeOnDelete();
            $table->foreignId('exported_by')->constrained('users')->cascadeOnDelete();
            $table->string('format', 16);
            $table->unsignedInteger('package_version');
            $table->string('incident_reference', 128);
            $table->timestamp('created_at')->useCurrent();

            $table->index(['incident_id', 'created_at']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('incident_evidence_exports');
    }
};
