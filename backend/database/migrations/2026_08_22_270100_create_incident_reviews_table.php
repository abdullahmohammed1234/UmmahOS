<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('incident_reviews', function (Blueprint $table) {
            $table->id();
            $table->foreignId('incident_id')->constrained('incidents')->cascadeOnDelete();
            $table->foreignId('reviewer_id')->constrained('users')->cascadeOnDelete();
            $table->string('outcome')->nullable();
            $table->text('notes')->nullable();
            $table->string('safety_classification')->nullable();
            $table->text('escalation_reason')->nullable();
            $table->boolean('is_current')->default(true);
            $table->timestamps();

            $table->index(['incident_id', 'is_current']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('incident_reviews');
    }
};
