<?php

namespace App\Support;

final class Permissions
{
    public const ORGANIZATION_VIEW = 'organization.view';
    public const ORGANIZATION_MANAGE = 'organization.manage';

    public const MEMBERS_VIEW = 'members.view';
    public const MEMBERS_MANAGE = 'members.manage';

    public const EVENTS_VIEW = 'events.view';
    public const EVENTS_MANAGE = 'events.manage';

    public const COURSES_VIEW = 'courses.view';
    public const COURSES_MANAGE = 'courses.manage';

    public const CONTENT_VIEW = 'content.view';
    public const CONTENT_MANAGE = 'content.manage';

    public const INCIDENTS_VIEW = 'incidents.view';
    public const INCIDENTS_MANAGE = 'incidents.manage';

    public const REPORTS_VIEW = 'reports.view';
    public const REPORTS_MANAGE = 'reports.manage';

    /**
     * @return list<array{name: string, slug: string}>
     */
    public static function catalog(): array
    {
        return [
            ['name' => 'View organization', 'slug' => self::ORGANIZATION_VIEW],
            ['name' => 'Manage organization', 'slug' => self::ORGANIZATION_MANAGE],
            ['name' => 'View members', 'slug' => self::MEMBERS_VIEW],
            ['name' => 'Manage members', 'slug' => self::MEMBERS_MANAGE],
            ['name' => 'View events', 'slug' => self::EVENTS_VIEW],
            ['name' => 'Manage events', 'slug' => self::EVENTS_MANAGE],
            ['name' => 'View courses', 'slug' => self::COURSES_VIEW],
            ['name' => 'Manage courses', 'slug' => self::COURSES_MANAGE],
            ['name' => 'View content', 'slug' => self::CONTENT_VIEW],
            ['name' => 'Manage content', 'slug' => self::CONTENT_MANAGE],
            ['name' => 'View incidents', 'slug' => self::INCIDENTS_VIEW],
            ['name' => 'Manage incidents', 'slug' => self::INCIDENTS_MANAGE],
            ['name' => 'View reports', 'slug' => self::REPORTS_VIEW],
            ['name' => 'Manage reports', 'slug' => self::REPORTS_MANAGE],
        ];
    }

    /**
     * @return list<string>
     */
    public static function slugs(): array
    {
        return array_column(self::catalog(), 'slug');
    }

    /**
     * @return list<string>
     */
    public static function viewSlugs(): array
    {
        return array_values(array_filter(
            self::slugs(),
            fn (string $slug) => str_ends_with($slug, '.view')
        ));
    }
}
