<?php

namespace App\Exceptions\Adapt;

use RuntimeException;

class AdaptUnavailableException extends RuntimeException
{
    public static function serviceDown(?string $detail = null): self
    {
        $message = 'Adaptive practice is temporarily unavailable. You can continue with the lesson.';

        if ($detail) {
            $message .= ' ('.$detail.')';
        }

        return new self($message);
    }
}
