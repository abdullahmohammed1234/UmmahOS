<?php

namespace Tests;

use Illuminate\Foundation\Testing\TestCase as BaseTestCase;
use Tests\Concerns\InteractsWithOrganizations;

abstract class TestCase extends BaseTestCase
{
    use InteractsWithOrganizations;
}
