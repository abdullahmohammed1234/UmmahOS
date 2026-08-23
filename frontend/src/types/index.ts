export interface Organization {
  id: number;
  name: string;
  slug: string;
  status: string;
  created_at?: string;
  updated_at?: string;
}

export interface RoleSummary {
  id: number;
  name: string;
  slug: string;
}

export interface UserSummary {
  id: number;
  name: string;
  email: string;
}

export interface Membership {
  id: number;
  user: UserSummary;
  organization: Organization;
  role: RoleSummary;
  created_at?: string;
  updated_at?: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
  memberships: Membership[];
}

export interface OrganizationContext {
  organization: Organization;
  membership: Membership;
  role: string | null;
  permissions: string[];
}

export interface AuthResponse {
  message: string;
  user: User;
  token: string;
}

export interface Announcement {
  id: number;
  organization_id: number;
  title: string;
  body: string;
  published_at: string | null;
  is_published: boolean;
  created_by?: UserSummary | null;
  created_at?: string;
  updated_at?: string;
}

export interface ResourceItem {
  id: number;
  organization_id: number;
  title: string;
  description: string | null;
  url: string;
  category: string | null;
  created_by?: UserSummary | null;
  created_at?: string;
  updated_at?: string;
}

export interface CommunityEvent {
  id: number;
  organization_id: number;
  title: string;
  description: string | null;
  location: string | null;
  starts_at: string;
  ends_at: string | null;
  registration_url: string | null;
  created_by?: UserSummary | null;
  created_at?: string;
  updated_at?: string;
}

export interface Course {
  id: number;
  organization_id: number;
  title: string;
  description: string | null;
  status: 'draft' | 'published';
  created_by?: UserSummary | null;
  created_at?: string;
  updated_at?: string;
}

export interface Incident {
  id: number;
  organization_id: number;
  category: string;
  description: string;
  status: 'open' | 'reviewing' | 'resolved';
  reported_by?: UserSummary | null;
  created_at?: string;
  updated_at?: string;
}

export interface MemberDashboard {
  organization: Organization;
  welcome: string;
  role: string | null;
  upcoming_events: CommunityEvent[];
  recent_announcements: Announcement[];
  featured_resources: ResourceItem[];
  academy: {
    published_courses_count: number;
    courses: Course[];
  };
  community_shield: {
    can_report: boolean;
  };
}

export interface AdminDashboard {
  organization: Organization;
  role: string | null;
  counts: {
    members: number;
    upcoming_events: number;
    published_announcements: number;
    published_courses: number;
    open_incidents: number;
  };
}
