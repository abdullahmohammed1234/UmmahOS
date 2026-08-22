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
