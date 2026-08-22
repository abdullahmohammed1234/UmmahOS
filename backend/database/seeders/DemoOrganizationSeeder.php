<?php

namespace Database\Seeders;

use App\Models\Membership;
use App\Models\Organization;
use App\Models\Role;
use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DemoOrganizationSeeder extends Seeder
{
    public function run(): void
    {
        $adminRole = Role::admin();
        $memberRole = Role::member();

        $alpha = Organization::query()->firstOrCreate(
            ['slug' => 'demo-msa-alpha'],
            [
                'name' => 'Demo MSA Alpha',
                'status' => Organization::STATUS_ACTIVE,
            ]
        );

        $beta = Organization::query()->firstOrCreate(
            ['slug' => 'demo-msa-beta'],
            [
                'name' => 'Demo MSA Beta',
                'status' => Organization::STATUS_ACTIVE,
            ]
        );

        $users = [
            [
                'name' => 'Alpha Admin',
                'email' => 'alpha.admin@example.com',
                'memberships' => [
                    ['organization' => $alpha, 'role' => $adminRole],
                ],
            ],
            [
                'name' => 'Alpha Member',
                'email' => 'alpha.member@example.com',
                'memberships' => [
                    ['organization' => $alpha, 'role' => $memberRole],
                ],
            ],
            [
                'name' => 'Beta Admin',
                'email' => 'beta.admin@example.com',
                'memberships' => [
                    ['organization' => $beta, 'role' => $adminRole],
                ],
            ],
            [
                'name' => 'Multi Org User',
                'email' => 'multi.user@example.com',
                'memberships' => [
                    ['organization' => $alpha, 'role' => $memberRole],
                    ['organization' => $beta, 'role' => $adminRole],
                ],
            ],
            [
                'name' => 'Unaffiliated User',
                'email' => 'outsider@example.com',
                'memberships' => [],
            ],
        ];

        foreach ($users as $definition) {
            $user = User::query()->firstOrCreate(
                ['email' => $definition['email']],
                [
                    'name' => $definition['name'],
                    'password' => Hash::make('password'),
                    'email_verified_at' => now(),
                ]
            );

            foreach ($definition['memberships'] as $membership) {
                Membership::query()->firstOrCreate(
                    [
                        'user_id' => $user->id,
                        'organization_id' => $membership['organization']->id,
                    ],
                    [
                        'role_id' => $membership['role']->id,
                    ]
                );
            }
        }
    }
}
