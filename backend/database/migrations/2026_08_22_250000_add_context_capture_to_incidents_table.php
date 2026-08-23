<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('incidents', function (Blueprint $table) {
            $table->string('original_item_title')->nullable()->after('description');
            $table->text('original_item_content')->nullable()->after('original_item_title');
            $table->string('original_item_author')->nullable()->after('original_item_content');
            $table->timestampTz('original_item_posted_at')->nullable()->after('original_item_author');
            $table->timestampTz('observed_at')->nullable()->after('original_item_posted_at');
            $table->text('surrounding_context')->nullable()->after('observed_at');
            $table->string('language', 32)->nullable()->after('surrounding_context');
            $table->text('reporter_notes')->nullable()->after('language');
            $table->string('safety_classification')->default('unclassified')->after('reporter_notes');
            $table->foreignId('classified_by')->nullable()->after('safety_classification')->constrained('users')->nullOnDelete();
            $table->timestampTz('classified_at')->nullable()->after('classified_by');
        });
    }

    public function down(): void
    {
        Schema::table('incidents', function (Blueprint $table) {
            $table->dropConstrainedForeignId('classified_by');
            $table->dropColumn([
                'original_item_title',
                'original_item_content',
                'original_item_author',
                'original_item_posted_at',
                'observed_at',
                'surrounding_context',
                'language',
                'reporter_notes',
                'safety_classification',
                'classified_at',
            ]);
        });
    }
};
