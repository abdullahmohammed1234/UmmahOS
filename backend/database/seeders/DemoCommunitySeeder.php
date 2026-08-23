<?php

namespace Database\Seeders;

use App\Models\Announcement;
use App\Models\Course;
use App\Models\Event;
use App\Models\Incident;
use App\Models\Organization;
use App\Models\Resource;
use App\Models\User;
use Illuminate\Database\Seeder;

class DemoCommunitySeeder extends Seeder
{
    public function run(): void
    {
        $alpha = Organization::query()->where('slug', 'demo-msa-alpha')->firstOrFail();
        $beta = Organization::query()->where('slug', 'demo-msa-beta')->firstOrFail();

        $alphaAdmin = User::query()->where('email', 'alpha.admin@example.com')->firstOrFail();
        $alphaMember = User::query()->where('email', 'alpha.member@example.com')->firstOrFail();
        $betaAdmin = User::query()->where('email', 'beta.admin@example.com')->firstOrFail();
        $multiUser = User::query()->where('email', 'multi.user@example.com')->firstOrFail();

        $this->seedAlpha($alpha, $alphaAdmin, $alphaMember);
        $this->seedBeta($beta, $betaAdmin, $multiUser);
    }

    private function seedAlpha(Organization $alpha, User $admin, User $member): void
    {
        Announcement::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'title' => 'Alpha Friday gathering moved to Room 210',
            ],
            [
                'body' => 'Demo MSA Alpha will meet in Room 210 this week. Brothers and sisters wings remain the same.',
                'published_at' => now()->subDay(),
                'created_by' => $admin->id,
            ]
        );

        Announcement::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'title' => 'Welcome to Demo MSA Alpha',
            ],
            [
                'body' => 'This is Alpha-only community news. Beta members should never see this announcement.',
                'published_at' => now()->subHours(3),
                'created_by' => $admin->id,
            ]
        );

        Announcement::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'title' => 'Alpha unpublished officer memo',
            ],
            [
                'body' => 'Draft for Alpha officers only. Members must not see this until it is published.',
                'published_at' => null,
                'created_by' => $admin->id,
            ]
        );

        Resource::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'title' => 'Alpha prayer timetable',
            ],
            [
                'description' => 'Campus prayer spaces used by Demo MSA Alpha.',
                'url' => 'https://example.com/alpha/prayer-times',
                'category' => 'worship',
                'created_by' => $admin->id,
            ]
        );

        Resource::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'title' => 'Alpha new-student guide',
            ],
            [
                'description' => 'Housing, dining, and first-week tips for Alpha members.',
                'url' => 'https://example.com/alpha/new-students',
                'category' => 'community',
                'created_by' => $admin->id,
            ]
        );

        Event::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'title' => 'Alpha community iftar',
            ],
            [
                'description' => 'Open to Demo MSA Alpha members and their families.',
                'location' => 'Alpha Student Union Ballroom',
                'starts_at' => now()->addDays(5)->setTime(18, 30),
                'ends_at' => now()->addDays(5)->setTime(20, 30),
                'registration_url' => 'https://example.com/alpha/iftar',
                'created_by' => $admin->id,
            ]
        );

        Event::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'title' => 'Alpha brothers hike',
            ],
            [
                'description' => 'Day hike organized by Demo MSA Alpha.',
                'location' => 'Alpha Trailhead',
                'starts_at' => now()->addDays(12)->setTime(9, 0),
                'ends_at' => now()->addDays(12)->setTime(14, 0),
                'created_by' => $admin->id,
            ]
        );

        Course::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'title' => 'Alpha Qur\'an foundations',
            ],
            [
                'description' => 'Introductory recitation circle for Demo MSA Alpha.',
                'status' => Course::STATUS_PUBLISHED,
                'created_by' => $admin->id,
            ]
        );

        Course::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'title' => 'Alpha leadership draft',
            ],
            [
                'description' => 'Unpublished Alpha officer training. Members must not see this course.',
                'status' => Course::STATUS_DRAFT,
                'created_by' => $admin->id,
            ]
        );

        Incident::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'reported_by' => $member->id,
                'category' => Incident::CATEGORY_COMMUNITY_CONCERN,
            ],
            [
                'description' => 'Alpha member reported a hallway confrontation after jumuah. This report belongs only to Demo MSA Alpha.',
                'status' => Incident::STATUS_OPEN,
            ]
        );
    }

    private function seedBeta(Organization $beta, User $admin, User $multiUser): void
    {
        Announcement::query()->firstOrCreate(
            [
                'organization_id' => $beta->id,
                'title' => 'Beta elections open this week',
            ],
            [
                'body' => 'Demo MSA Beta executive nominations are open. This notice is not visible inside Alpha.',
                'published_at' => now()->subHours(2),
                'created_by' => $admin->id,
            ]
        );

        Announcement::query()->firstOrCreate(
            [
                'organization_id' => $beta->id,
                'title' => 'Beta sisters study circle',
            ],
            [
                'body' => 'Weekly Beta-only halaqah in the east lounge.',
                'published_at' => now()->subDays(2),
                'created_by' => $admin->id,
            ]
        );

        Resource::query()->firstOrCreate(
            [
                'organization_id' => $beta->id,
                'title' => 'Beta housing list',
            ],
            [
                'description' => 'Off-campus rooms shared inside Demo MSA Beta.',
                'url' => 'https://example.com/beta/housing',
                'category' => 'housing',
                'created_by' => $admin->id,
            ]
        );

        Resource::query()->firstOrCreate(
            [
                'organization_id' => $beta->id,
                'title' => 'Beta local masjid map',
            ],
            [
                'description' => 'Masajid near campus used by Demo MSA Beta.',
                'url' => 'https://example.com/beta/masajid',
                'category' => 'worship',
                'created_by' => $admin->id,
            ]
        );

        Event::query()->firstOrCreate(
            [
                'organization_id' => $beta->id,
                'title' => 'Beta sports day',
            ],
            [
                'description' => 'Basketball and soccer for Demo MSA Beta members.',
                'location' => 'Beta Recreation Centre',
                'starts_at' => now()->addDays(8)->setTime(16, 0),
                'ends_at' => now()->addDays(8)->setTime(19, 0),
                'created_by' => $admin->id,
            ]
        );

        Course::query()->firstOrCreate(
            [
                'organization_id' => $beta->id,
                'title' => 'Beta seerah circle',
            ],
            [
                'description' => 'Published seerah series for Demo MSA Beta.',
                'status' => Course::STATUS_PUBLISHED,
                'created_by' => $admin->id,
            ]
        );

        Course::query()->firstOrCreate(
            [
                'organization_id' => $beta->id,
                'title' => 'Beta fiqh workshop draft',
            ],
            [
                'description' => 'Unpublished Beta workshop outline.',
                'status' => Course::STATUS_DRAFT,
                'created_by' => $admin->id,
            ]
        );

        Incident::query()->firstOrCreate(
            [
                'organization_id' => $beta->id,
                'reported_by' => $multiUser->id,
                'category' => Incident::CATEGORY_HARASSMENT,
            ],
            [
                'description' => 'Beta-only Community Shield report submitted by the multi-organization user while operating inside Beta.',
                'status' => Incident::STATUS_REVIEWING,
            ]
        );
    }
}
