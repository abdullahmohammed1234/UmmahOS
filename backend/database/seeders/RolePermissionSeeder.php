<?php

namespace Database\Seeders;

use App\Models\Permission;
use App\Models\Role;
use App\Support\Permissions;
use Illuminate\Database\Seeder;

class RolePermissionSeeder extends Seeder
{
    public function run(): void
    {
        foreach (Permissions::catalog() as $permission) {
            Permission::query()->firstOrCreate(
                ['slug' => $permission['slug']],
                ['name' => $permission['name']]
            );
        }

        $admin = Role::query()->firstOrCreate(
            ['slug' => Role::ADMIN],
            [
                'name' => 'Admin',
                'description' => 'Organization administrator. All permissions apply only inside the assigned organization.',
            ]
        );

        $member = Role::query()->firstOrCreate(
            ['slug' => Role::MEMBER],
            [
                'name' => 'Member',
                'description' => 'Organization member with view access inside the assigned organization.',
            ]
        );

        $reviewer = Role::query()->firstOrCreate(
            ['slug' => Role::COMMUNITY_SAFETY_REVIEWER],
            [
                'name' => 'Community Safety Reviewer',
                'description' => 'Organization-scoped Community Shield reviewer. Permissions apply only inside the assigned organization.',
            ]
        );

        $admin->permissions()->sync(Permission::query()->pluck('id'));
        $member->permissions()->sync(
            Permission::query()->whereIn('slug', Permissions::viewSlugs())->pluck('id')
        );
        $reviewer->permissions()->sync(
            Permission::query()->whereIn('slug', Permissions::communitySafetyReviewerSlugs())->pluck('id')
        );
    }
}
