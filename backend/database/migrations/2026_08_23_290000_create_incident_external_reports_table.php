<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('incident_external_reports', function (Blueprint $table) {
            $table->id();
            $table->foreignId('incident_id')->constrained()->cascadeOnDelete();
            $table->foreignId('organization_id')->constrained()->cascadeOnDelete();
            $table->string('platform', 64);
            $table->string('reporting_channel', 255);
            $table->string('external_reference', 255)->nullable();
            $table->timestamp('reported_at');
            $table->string('status', 32)->default('reported');
            $table->string('decision', 64)->nullable();
            $table->string('outcome', 64)->nullable();
            $table->string('outcome_source', 64)->nullable();
            $table->string('verification_status', 32)->default('unverified');
            $table->text('internal_notes')->nullable();
            $table->text('reporter_visible_summary')->nullable();
            $table->text('decision_note')->nullable();
            $table->text('outcome_summary')->nullable();
            $table->foreignId('created_by')->constrained('users');
            $table->foreignId('updated_by')->nullable()->constrained('users');
            $table->timestamps();

            $table->index(['organization_id', 'incident_id']);
            $table->index(['incident_id', 'status']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('incident_external_reports');
    }
};
