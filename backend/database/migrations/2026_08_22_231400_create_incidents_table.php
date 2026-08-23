<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('incidents', function (Blueprint $table) {
            $table->id();
            $table->foreignId('organization_id')->constrained()->cascadeOnDelete();
            $table->foreignId('reported_by')->constrained('users')->cascadeOnDelete();
            $table->string('platform');
            $table->string('content_type');
            $table->string('visibility');
            $table->string('source_url', 2048)->nullable();
            $table->text('description');
            $table->string('status')->default('open');
            $table->timestamps();

            $table->index(['organization_id', 'status']);
            $table->index(['organization_id', 'reported_by']);
            $table->index(['organization_id', 'platform']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('incidents');
    }
};
