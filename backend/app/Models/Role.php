<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Role extends Model
{
    public const ADMIN = 'admin';
    public const MEMBER = 'member';

    protected $fillable = [
        'name',
        'slug',
        'description',
    ];

    public function permissions(): BelongsToMany
    {
        return $this->belongsToMany(Permission::class);
    }

    public function memberships(): HasMany
    {
        return $this->hasMany(Membership::class);
    }

    public function isAdmin(): bool
    {
        return $this->slug === self::ADMIN;
    }

    public static function admin(): self
    {
        return static::query()->where('slug', self::ADMIN)->firstOrFail();
    }

    public static function member(): self
    {
        return static::query()->where('slug', self::MEMBER)->firstOrFail();
    }
}
