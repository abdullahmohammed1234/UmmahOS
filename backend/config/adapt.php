<?php

return [
    /*
    |--------------------------------------------------------------------------
    | ADAPT adaptive learning service (Phase 9)
    |--------------------------------------------------------------------------
    |
    | UmmahOS Academy talks to ADAPT over HTTP. ADAPT remains authoritative for
    | learner state, strategy, and next-challenge selection. Set ADAPT_CLIENT=fake
    | only for automated tests.
    |
    */
    'base_url' => env('ADAPT_BASE_URL', 'http://127.0.0.1:8765'),
    'timeout' => (int) env('ADAPT_TIMEOUT', 10),
    'client' => env('ADAPT_CLIENT', 'http'),
];
