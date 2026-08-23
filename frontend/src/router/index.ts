import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useOrganizationStore } from '@/stores/organization';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/LoginPage.vue'),
      meta: { guest: true },
    },
    {
      path: '/',
      component: () => import('@/components/AppShell.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/pages/DashboardPage.vue'),
        },
        {
          path: 'announcements',
          name: 'announcements',
          component: () => import('@/pages/AnnouncementsPage.vue'),
        },
        {
          path: 'announcements/:id',
          name: 'announcement-detail',
          component: () => import('@/pages/AnnouncementDetailPage.vue'),
        },
        {
          path: 'resources',
          name: 'resources',
          component: () => import('@/pages/ResourcesPage.vue'),
        },
        {
          path: 'resources/:id',
          name: 'resource-detail',
          component: () => import('@/pages/ResourceDetailPage.vue'),
        },
        {
          path: 'events',
          name: 'events',
          component: () => import('@/pages/EventsPage.vue'),
        },
        {
          path: 'events/:id',
          name: 'event-detail',
          component: () => import('@/pages/EventDetailPage.vue'),
        },
        {
          path: 'academy',
          name: 'academy',
          component: () => import('@/pages/AcademyPage.vue'),
        },
        {
          path: 'academy/:id',
          name: 'course-detail',
          component: () => import('@/pages/CourseDetailPage.vue'),
        },
        {
          path: 'community-shield',
          name: 'community-shield',
          component: () => import('@/pages/CommunityShieldPage.vue'),
        },
        {
          path: 'members',
          name: 'members',
          component: () => import('@/pages/MembersPage.vue'),
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('@/pages/SettingsPage.vue'),
        },
        {
          path: 'admin',
          name: 'admin-dashboard',
          component: () => import('@/pages/admin/AdminDashboardPage.vue'),
        },
        {
          path: 'admin/announcements',
          name: 'admin-announcements',
          component: () => import('@/pages/admin/AdminAnnouncementsPage.vue'),
        },
        {
          path: 'admin/announcements/new',
          name: 'admin-announcement-create',
          component: () => import('@/pages/admin/AdminAnnouncementFormPage.vue'),
        },
        {
          path: 'admin/announcements/:id/edit',
          name: 'admin-announcement-edit',
          component: () => import('@/pages/admin/AdminAnnouncementFormPage.vue'),
        },
        {
          path: 'admin/resources',
          name: 'admin-resources',
          component: () => import('@/pages/admin/AdminResourcesPage.vue'),
        },
        {
          path: 'admin/resources/new',
          name: 'admin-resource-create',
          component: () => import('@/pages/admin/AdminResourceFormPage.vue'),
        },
        {
          path: 'admin/resources/:id/edit',
          name: 'admin-resource-edit',
          component: () => import('@/pages/admin/AdminResourceFormPage.vue'),
        },
        {
          path: 'admin/events',
          name: 'admin-events',
          component: () => import('@/pages/admin/AdminEventsPage.vue'),
        },
        {
          path: 'admin/events/new',
          name: 'admin-event-create',
          component: () => import('@/pages/admin/AdminEventFormPage.vue'),
        },
        {
          path: 'admin/events/:id/edit',
          name: 'admin-event-edit',
          component: () => import('@/pages/admin/AdminEventFormPage.vue'),
        },
        {
          path: 'admin/academy',
          name: 'admin-academy',
          component: () => import('@/pages/admin/AdminAcademyPage.vue'),
        },
        {
          path: 'admin/academy/new',
          name: 'admin-course-create',
          component: () => import('@/pages/admin/AdminCourseFormPage.vue'),
        },
        {
          path: 'admin/academy/:id/edit',
          name: 'admin-course-edit',
          component: () => import('@/pages/admin/AdminCourseFormPage.vue'),
        },
        {
          path: 'admin/community-shield',
          name: 'admin-incidents',
          component: () => import('@/pages/admin/AdminIncidentsPage.vue'),
        },
        {
          path: 'admin/community-shield/:id',
          name: 'admin-incident-detail',
          component: () => import('@/pages/admin/AdminIncidentDetailPage.vue'),
        },
      ],
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' };
  }

  if (to.meta.guest && auth.isAuthenticated) {
    return { name: 'dashboard' };
  }

  if (to.meta.requiresAuth && auth.isAuthenticated) {
    const organization = useOrganizationStore();
    if (!organization.context) {
      await organization.loadContext();
    }
  }

  return true;
});

export default router;
