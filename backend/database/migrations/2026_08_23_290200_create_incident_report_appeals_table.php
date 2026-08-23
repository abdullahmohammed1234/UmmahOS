<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('incident_report_appeals', function (Blueprint $table) {
            $table->id();
            $table->foreignId('incident_external_report_id')
                ->constrained('incident_external_reports')
                ->cascadeOnDelete();
            $table->timestamp('submitted_at');
            $table->foreignId('submitted_by')->constrained('users');
            $table->text('reason');
            $table->text('additional_evidence')->nullable();
            $table->string('reference', 255)->nullable();
            $table->text('notes')->nullable();
            $table->string('status', 32)->default('submitted');
            $table->text('response')->nullable();
            $table->timestamp('responded_at')->nullable();
            $table->foreignId('responded_by')->nullable()->constrained('users');
            $table->timestamps();

            $table->index(['incident_external_report_id', 'status']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('incident_report_appeals');
    }
};
