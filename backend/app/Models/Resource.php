<?php

namespace App\Models;

use App\Models\Concerns\BelongsToOrganization;
use App\Models\Concerns\HasCreator;
use Database\Factories\ResourceFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Resource extends Model
{
    /** @use HasFactory<ResourceFactory> */
    use BelongsToOrganization, HasCreator, HasFactory;

    protected $fillable = [
        'organization_id',
        'title',
        'description',
        'url',
        'category',
        'created_by',
    ];
}
