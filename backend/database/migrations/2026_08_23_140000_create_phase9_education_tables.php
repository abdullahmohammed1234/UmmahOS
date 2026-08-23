<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('academy_lessons', function (Blueprint $table) {
            $table->id();
            $table->foreignId('organization_id')->constrained()->cascadeOnDelete();
            $table->foreignId('course_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->text('learning_objective')->nullable();
            $table->json('sections')->nullable();
            $table->string('category')->default('general');
            $table->string('status')->default('draft');
            $table->boolean('is_demo')->default(false);
            $table->foreignId('created_by')->nullable()->constrained('users')->nullOnDelete();
            $table->timestamps();

            $table->index(['organization_id', 'status']);
            $table->index(['organization_id', 'category']);
        });

        Schema::create('academy_scenarios', function (Blueprint $table) {
            $table->id();
            $table->foreignId('organization_id')->constrained()->cascadeOnDelete();
            $table->foreignId('academy_lesson_id')->constrained('academy_lessons')->cascadeOnDelete();
            $table->string('title');
            $table->text('prompt');
            $table->text('context')->nullable();
            $table->json('options')->nullable();
            $table->json('expected_reasoning_signals')->nullable();
            $table->json('misconception_tags')->nullable();
            $table->unsignedTinyInteger('difficulty')->default(2);
            $table->string('adapt_challenge_id')->nullable();
            $table->string('adapt_topic_id')->nullable();
            $table->string('adapt_concept_id')->nullable();
            $table->string('adapt_domain')->default('community-safety');
            $table->unsignedInteger('sort_order')->default(0);
            $table->boolean('is_demo')->default(false);
            $table->timestamps();

            $table->index(['organization_id', 'academy_lesson_id']);
        });

        Schema::create('academy_lesson_progress', function (Blueprint $table) {
            $table->id();
            $table->foreignId('organization_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('academy_lesson_id')->constrained('academy_lessons')->cascadeOnDelete();
            $table->string('status')->default('started');
            $table->timestamp('started_at')->nullable();
            $table->timestamp('completed_at')->nullable();
            $table->timestamps();

            $table->unique(['user_id', 'academy_lesson_id']);
            $table->index(['organization_id', 'user_id']);
        });

        Schema::create('learning_patterns', function (Blueprint $table) {
            $table->id();
            $table->foreignId('organization_id')->constrained()->cascadeOnDelete();
            $table->foreignId('source_incident_id')->constrained('incidents')->cascadeOnDelete();
            $table->string('pattern_type');
            $table->string('title');
            $table->text('summary');
            $table->text('learning_objective');
            $table->string('domain')->default('community-safety');
            $table->string('severity_context')->nullable();
            $table->string('status')->default('draft');
            $table->foreignId('created_by')->constrained('users')->cascadeOnDelete();
            $table->foreignId('approved_by')->nullable()->constrained('users')->nullOnDelete();
            $table->timestamp('approved_at')->nullable();
            $table->timestamps();

            $table->index(['organization_id', 'status']);
            $table->unique(['organization_id', 'source_incident_id']);
        });

        Schema::create('learning_recommendations', function (Blueprint $table) {
            $table->id();
            $table->foreignId('organization_id')->constrained()->cascadeOnDelete();
            $table->foreignId('learning_pattern_id')->constrained('learning_patterns')->cascadeOnDelete();
            $table->foreignId('academy_course_id')->nullable()->constrained('courses')->nullOnDelete();
            $table->foreignId('academy_lesson_id')->nullable()->constrained('academy_lessons')->nullOnDelete();
            $table->text('reason');
            $table->string('status')->default('draft');
            $table->foreignId('created_by')->constrained('users')->cascadeOnDelete();
            $table->timestamps();

            $table->index(['organization_id', 'status']);
        });

        Schema::create('adapt_learning_sessions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('organization_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('academy_lesson_id')->nullable()->constrained('academy_lessons')->nullOnDelete();
            $table->foreignId('academy_scenario_id')->nullable()->constrained('academy_scenarios')->nullOnDelete();
            $table->string('adapt_session_id')->nullable();
            $table->string('adapt_topic_id')->nullable();
            $table->string('adapt_subject_id')->default('community-safety');
            $table->string('status')->default('active');
            $table->timestamp('started_at')->nullable();
            $table->timestamp('completed_at')->nullable();
            $table->json('last_result')->nullable();
            $table->timestamps();

            $table->index(['organization_id', 'user_id']);
            $table->index(['user_id', 'adapt_session_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('adapt_learning_sessions');
        Schema::dropIfExists('learning_recommendations');
        Schema::dropIfExists('learning_patterns');
        Schema::dropIfExists('academy_lesson_progress');
        Schema::dropIfExists('academy_scenarios');
        Schema::dropIfExists('academy_lessons');
    }
};
