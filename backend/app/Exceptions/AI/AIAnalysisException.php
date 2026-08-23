<?php

namespace App\Exceptions\AI;

use Exception;

class AIAnalysisException extends Exception
{
    public static function unavailable(string $reason = 'AI analysis is currently unavailable.'): self
    {
        return new self($reason);
    }

    public static function providerFailed(string $reason = 'AI analysis unavailable.'): self
    {
        return new self($reason);
    }

    public static function malformedResponse(string $reason = 'The AI provider returned an invalid analysis.'): self
    {
        return new self($reason);
    }
}
