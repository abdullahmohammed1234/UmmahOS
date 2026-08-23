<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('incidents', function (Blueprint $table) {
            if (! Schema::hasColumn('incidents', 'review_outcome')) {
                $table->string('review_outcome')->nullable()->after('status');
            }

            if (! Schema::hasColumn('incidents', 'escalated')) {
                $table->boolean('escalated')->default(false)->after('review_outcome');
            }

            if (! Schema::hasColumn('incidents', 'escalation_reason')) {
                $table->text('escalation_reason')->nullable()->after('escalated');
            }

            if (! Schema::hasColumn('incidents', 'escalated_by')) {
                $table->foreignId('escalated_by')->nullable()->after('escalation_reason')
                    ->constrained('users')->nullOnDelete();
            }

            if (! Schema::hasColumn('incidents', 'escalated_at')) {
                $table->timestamp('escalated_at')->nullable()->after('escalated_by');
            }

            if (! Schema::hasColumn('incidents', 'current_reviewer_id')) {
                $table->foreignId('current_reviewer_id')->nullable()->after('escalated_at')
                    ->constrained('users')->nullOnDelete();
            }

            if (! Schema::hasColumn('incidents', 'review_started_at')) {
                $table->timestamp('review_started_at')->nullable()->after('current_reviewer_id');
            }

            if (! Schema::hasColumn('incidents', 'review_notes')) {
                $table->text('review_notes')->nullable()->after('review_started_at');
            }

            if (! Schema::hasColumn('incidents', 'review_lock_version')) {
                $table->unsignedInteger('review_lock_version')->default(1)->after('review_notes');
            }
        });
    }

    public function down(): void
    {
        Schema::table('incidents', function (Blueprint $table) {
            $columns = [
                'review_outcome',
                'escalated',
                'escalation_reason',
                'escalated_by',
                'escalated_at',
                'current_reviewer_id',
                'review_started_at',
                'review_notes',
                'review_lock_version',
            ];

            foreach ($columns as $column) {
                if (! Schema::hasColumn('incidents', $column)) {
                    continue;
                }

                if (in_array($column, ['escalated_by', 'current_reviewer_id'], true)) {
                    $table->dropConstrainedForeignId($column);
                } else {
                    $table->dropColumn($column);
                }
            }
        });
    }
};
