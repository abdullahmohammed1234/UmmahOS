<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('incident_external_report_status_history', function (Blueprint $table) {
            $table->id();
            $table->foreignId('incident_external_report_id')
                ->constrained('incident_external_reports')
                ->cascadeOnDelete();
            $table->string('previous_status', 32)->nullable();
            $table->string('new_status', 32);
            $table->string('decision', 64)->nullable();
            $table->string('outcome', 64)->nullable();
            $table->foreignId('changed_by')->constrained('users');
            $table->text('note')->nullable();
            $table->timestamp('changed_at');
            $table->timestamp('created_at')->useCurrent();

            $table->index(['incident_external_report_id', 'changed_at']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('incident_external_report_status_history');
    }
};
