<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Default AI analysis provider
    |--------------------------------------------------------------------------
    |
    | Supported: "gemini", "fake", "unavailable"
    |
    | "fake" is intended for automated tests. Production/demo environments
    | should use "gemini" when credentials are present.
    |
    */

    'provider' => env('AI_ANALYSIS_PROVIDER', 'gemini'),

    'gemini' => [
        'api_key' => env('GEMINI_API_KEY'),
        'model' => env('GEMINI_MODEL', 'gemini-2.0-flash'),
        'endpoint' => env(
            'GEMINI_API_ENDPOINT',
            'https://generativelanguage.googleapis.com/v1beta'
        ),
        'timeout' => (int) env('GEMINI_TIMEOUT', 45),
    ],

];
