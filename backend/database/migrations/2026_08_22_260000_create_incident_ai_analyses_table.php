<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('incident_ai_analyses', function (Blueprint $table) {
            $table->id();
            $table->foreignId('incident_id')->constrained('incidents')->cascadeOnDelete();
            $table->string('provider', 64);
            $table->string('model', 128)->nullable();
            $table->string('prompt_version', 64);
            $table->string('status', 32);
            $table->json('analysis')->nullable();
            $table->text('error_message')->nullable();
            $table->foreignId('requested_by')->nullable()->constrained('users')->nullOnDelete();
            $table->timestamps();

            $table->index(['incident_id', 'id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('incident_ai_analyses');
    }
};
