<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('incidents', function (Blueprint $table) {
            if (! Schema::hasColumn('incidents', 'platform')) {
                $table->string('platform')->default('other');
            }
            if (! Schema::hasColumn('incidents', 'content_type')) {
                $table->string('content_type')->default('post');
            }
            if (! Schema::hasColumn('incidents', 'visibility')) {
                $table->string('visibility')->default('unknown');
            }
            if (! Schema::hasColumn('incidents', 'source_url')) {
                $table->string('source_url', 2048)->nullable();
            }
        });

        if (Schema::hasColumn('incidents', 'category')) {
            Schema::table('incidents', function (Blueprint $table) {
                $table->dropColumn('category');
            });
        }
    }

    public function down(): void
    {
        if (! Schema::hasColumn('incidents', 'category')) {
            Schema::table('incidents', function (Blueprint $table) {
                $table->string('category')->default('other');
            });
        }

        Schema::table('incidents', function (Blueprint $table) {
            $columns = array_values(array_filter(
                ['platform', 'content_type', 'visibility', 'source_url'],
                fn (string $column) => Schema::hasColumn('incidents', $column)
            ));

            if ($columns !== []) {
                $table->dropColumn($columns);
            }
        });
    }
};
