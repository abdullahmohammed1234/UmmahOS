<?php

namespace App\Providers;

use App\Contracts\AI\AIAnalysisProvider;
use App\Services\AI\Providers\FakeAnalysisProvider;
use App\Services\AI\Providers\GeminiAnalysisProvider;
use App\Services\AI\Providers\UnavailableAnalysisProvider;
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->singleton(FakeAnalysisProvider::class);
        $this->app->singleton(\App\Services\Adapt\FakeAdaptClient::class);

        $this->app->bind(\App\Contracts\Adapt\AdaptClient::class, function ($app) {
            $configured = (string) config('adapt.client', 'http');

            if ($configured === 'fake' || $app->environment('testing')) {
                return $app->make(\App\Services\Adapt\FakeAdaptClient::class);
            }

            return $app->make(\App\Services\Adapt\HttpAdaptClient::class);
        });

        $this->app->bind(AIAnalysisProvider::class, function ($app) {
            $configured = (string) config('ai.provider', 'gemini');

            if ($configured === 'fake' || $app->environment('testing')) {
                return $app->make(FakeAnalysisProvider::class);
            }

            if ($configured === 'unavailable') {
                return $app->make(UnavailableAnalysisProvider::class);
            }

            $gemini = $app->make(GeminiAnalysisProvider::class);

            if (! $gemini->isAvailable()) {
                return $app->make(UnavailableAnalysisProvider::class);
            }

            return $gemini;
        });
    }

    public function boot(): void
    {
        RateLimiter::for('auth', function (Request $request) {
            return Limit::perMinute(5)->by($request->ip());
        });
    }
}
