<?php

namespace App\Exceptions\Review;

class ReviewConflictException extends ReviewStateException
{
    public function __construct(string $message = 'This review was updated by another reviewer. Reload and try again.')
    {
        parent::__construct($message, 409);
    }
}
