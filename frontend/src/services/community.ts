import { api } from '@/services/api';
import { organizationPath } from '@/services/organizations';
import { unwrapData } from '@/services/unwrap';
import type {
  AdminDashboard,
  Announcement,
  CommunityEvent,
  CommunityShieldOverview,
  CommunityShieldStatus,
  Course,
  Incident,
  MemberDashboard,
  ResourceItem,
} from '@/types';

function scoped<T>(organizationId: number | string, suffix: string) {
  return api.get<T | { data: T }>(organizationPath(organizationId, suffix)).then(({ data }) => unwrapData(data));
}

export const communityApi = {
  dashboard(organizationId: number | string): Promise<MemberDashboard> {
    return scoped(organizationId, '/dashboard');
  },

  adminDashboard(organizationId: number | string): Promise<AdminDashboard> {
    return scoped(organizationId, '/admin/dashboard');
  },

  announcements(organizationId: number | string): Promise<Announcement[]> {
    return scoped(organizationId, '/announcements');
  },

  announcement(organizationId: number | string, id: number | string): Promise<Announcement> {
    return scoped(organizationId, `/announcements/${id}`);
  },

  async createAnnouncement(
    organizationId: number | string,
    payload: Partial<Announcement> & { published?: boolean },
  ): Promise<Announcement> {
    const { data } = await api.post<Announcement | { data: Announcement }>(
      organizationPath(organizationId, '/announcements'),
      payload,
    );
    return unwrapData(data);
  },

  async updateAnnouncement(
    organizationId: number | string,
    id: number | string,
    payload: Partial<Announcement> & { published?: boolean },
  ): Promise<Announcement> {
    const { data } = await api.patch<Announcement | { data: Announcement }>(
      organizationPath(organizationId, `/announcements/${id}`),
      payload,
    );
    return unwrapData(data);
  },

  async deleteAnnouncement(organizationId: number | string, id: number | string): Promise<void> {
    await api.delete(organizationPath(organizationId, `/announcements/${id}`));
  },

  resources(organizationId: number | string): Promise<ResourceItem[]> {
    return scoped(organizationId, '/resources');
  },

  resource(organizationId: number | string, id: number | string): Promise<ResourceItem> {
    return scoped(organizationId, `/resources/${id}`);
  },

  async createResource(
    organizationId: number | string,
    payload: Partial<ResourceItem>,
  ): Promise<ResourceItem> {
    const { data } = await api.post<ResourceItem | { data: ResourceItem }>(
      organizationPath(organizationId, '/resources'),
      payload,
    );
    return unwrapData(data);
  },

  async updateResource(
    organizationId: number | string,
    id: number | string,
    payload: Partial<ResourceItem>,
  ): Promise<ResourceItem> {
    const { data } = await api.patch<ResourceItem | { data: ResourceItem }>(
      organizationPath(organizationId, `/resources/${id}`),
      payload,
    );
    return unwrapData(data);
  },

  async deleteResource(organizationId: number | string, id: number | string): Promise<void> {
    await api.delete(organizationPath(organizationId, `/resources/${id}`));
  },

  events(organizationId: number | string): Promise<CommunityEvent[]> {
    return scoped(organizationId, '/events');
  },

  event(organizationId: number | string, id: number | string): Promise<CommunityEvent> {
    return scoped(organizationId, `/events/${id}`);
  },

  async createEvent(
    organizationId: number | string,
    payload: Partial<CommunityEvent>,
  ): Promise<CommunityEvent> {
    const { data } = await api.post<CommunityEvent | { data: CommunityEvent }>(
      organizationPath(organizationId, '/events'),
      payload,
    );
    return unwrapData(data);
  },

  async updateEvent(
    organizationId: number | string,
    id: number | string,
    payload: Partial<CommunityEvent>,
  ): Promise<CommunityEvent> {
    const { data } = await api.patch<CommunityEvent | { data: CommunityEvent }>(
      organizationPath(organizationId, `/events/${id}`),
      payload,
    );
    return unwrapData(data);
  },

  async deleteEvent(organizationId: number | string, id: number | string): Promise<void> {
    await api.delete(organizationPath(organizationId, `/events/${id}`));
  },

  courses(organizationId: number | string): Promise<Course[]> {
    return scoped(organizationId, '/courses');
  },

  course(organizationId: number | string, id: number | string): Promise<Course> {
    return scoped(organizationId, `/courses/${id}`);
  },

  async createCourse(organizationId: number | string, payload: Partial<Course>): Promise<Course> {
    const { data } = await api.post<Course | { data: Course }>(
      organizationPath(organizationId, '/courses'),
      payload,
    );
    return unwrapData(data);
  },

  async updateCourse(
    organizationId: number | string,
    id: number | string,
    payload: Partial<Course>,
  ): Promise<Course> {
    const { data } = await api.patch<Course | { data: Course }>(
      organizationPath(organizationId, `/courses/${id}`),
      payload,
    );
    return unwrapData(data);
  },

  async deleteCourse(organizationId: number | string, id: number | string): Promise<void> {
    await api.delete(organizationPath(organizationId, `/courses/${id}`));
  },

  incidents(organizationId: number | string, status?: CommunityShieldStatus | ''): Promise<Incident[]> {
    const query = status ? `?status=${encodeURIComponent(status)}` : '';
    return scoped(organizationId, `/incidents${query}`);
  },

  communityShieldOverview(organizationId: number | string): Promise<CommunityShieldOverview> {
    return scoped(organizationId, '/community-shield');
  },

  incident(organizationId: number | string, id: number | string): Promise<Incident> {
    return scoped(organizationId, `/incidents/${id}`);
  },

  async reportIncident(
    organizationId: number | string,
    payload: Pick<Incident, 'platform' | 'content_type' | 'visibility' | 'description'> & {
      source_url?: string | null;
    },
  ): Promise<{ incident: Incident; message: string }> {
    const { data } = await api.post<{ data: Incident; message?: string } | Incident>(
      organizationPath(organizationId, '/incidents'),
      payload,
    );

    if (data && typeof data === 'object' && 'data' in data) {
      return {
        incident: data.data,
        message: data.message ?? 'Your report was received.',
      };
    }

    return {
      incident: data as Incident,
      message: 'Your report was received.',
    };
  },

  async updateIncident(
    organizationId: number | string,
    id: number | string,
    payload: Pick<Incident, 'status'>,
  ): Promise<Incident> {
    const { data } = await api.patch<Incident | { data: Incident }>(
      organizationPath(organizationId, `/incidents/${id}`),
      payload,
    );
    return unwrapData(data);
  },
};
