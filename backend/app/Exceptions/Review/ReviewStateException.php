<?php

namespace App\Exceptions\Review;

use RuntimeException;

class ReviewStateException extends RuntimeException
{
    public function __construct(
        string $message,
        public readonly int $status = 422,
    ) {
        parent::__construct($message);
    }
}
