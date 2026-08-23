import { api } from '@/services/api';
import { organizationPath } from '@/services/organizations';
import { unwrapData } from '@/services/unwrap';
import type {
  AdminDashboard,
  Announcement,
  AcademyLesson,
  AcademyLessonProgress,
  AcademyScenario,
  AdaptSessionShowResponse,
  AdaptStartResponse,
  AdaptSubmitResponse,
  CommunityEvent,
  CommunityShieldOverview,
  CommunityShieldSafetyClassification,
  CommunityShieldStatus,
  Course,
  Incident,
  IncidentAiAnalysis,
  IncidentContextRequest,
  IncidentEvidencePackage,
  IncidentExternalReportRecord,
  IncidentRelatedItem,
  IncidentReply,
  IncidentReviewPackage,
  LearningPattern,
  LearningRecommendation,
  MemberReportSummary,
  MemberDashboard,
  ResourceItem,
  ReviewQueueItem,
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
      original_item_title?: string | null;
      original_item_content?: string | null;
      original_item_author?: string | null;
      original_item_posted_at?: string | null;
      observed_at?: string | null;
      surrounding_context?: string | null;
      language?: string | null;
      reporter_notes?: string | null;
      replies?: Array<Pick<IncidentReply, 'author' | 'content' | 'posted_at' | 'position'>>;
      related_items?: Array<
        Pick<
          IncidentRelatedItem,
          'platform' | 'content_type' | 'reference_url' | 'description' | 'observed_at'
        >
      >;
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
    payload: {
      status?: CommunityShieldStatus;
      safety_classification?: CommunityShieldSafetyClassification;
    },
  ): Promise<Incident> {
    const { data } = await api.patch<Incident | { data: Incident }>(
      organizationPath(organizationId, `/incidents/${id}`),
      payload,
    );
    return unwrapData(data);
  },

  async addIncidentReply(
    organizationId: number | string,
    incidentId: number | string,
    payload: Pick<IncidentReply, 'author' | 'content' | 'posted_at' | 'position'>,
  ): Promise<IncidentReply> {
    const { data } = await api.post<IncidentReply | { data: IncidentReply }>(
      organizationPath(organizationId, `/incidents/${incidentId}/replies`),
      payload,
    );
    return unwrapData(data);
  },

  async deleteIncidentReply(
    organizationId: number | string,
    incidentId: number | string,
    replyId: number | string,
  ): Promise<void> {
    await api.delete(organizationPath(organizationId, `/incidents/${incidentId}/replies/${replyId}`));
  },

  async addIncidentRelatedItem(
    organizationId: number | string,
    incidentId: number | string,
    payload: Pick<
      IncidentRelatedItem,
      'platform' | 'content_type' | 'reference_url' | 'description' | 'observed_at'
    >,
  ): Promise<IncidentRelatedItem> {
    const { data } = await api.post<IncidentRelatedItem | { data: IncidentRelatedItem }>(
      organizationPath(organizationId, `/incidents/${incidentId}/related-items`),
      payload,
    );
    return unwrapData(data);
  },

  async deleteIncidentRelatedItem(
    organizationId: number | string,
    incidentId: number | string,
    itemId: number | string,
  ): Promise<void> {
    await api.delete(
      organizationPath(organizationId, `/incidents/${incidentId}/related-items/${itemId}`),
    );
  },

  aiAnalyses(
    organizationId: number | string,
    incidentId: number | string,
  ): Promise<IncidentAiAnalysis[]> {
    return scoped(organizationId, `/incidents/${incidentId}/ai-analyses`);
  },

  aiAnalysis(
    organizationId: number | string,
    incidentId: number | string,
    analysisId: number | string,
  ): Promise<IncidentAiAnalysis> {
    return scoped(organizationId, `/incidents/${incidentId}/ai-analyses/${analysisId}`);
  },

  async requestAiAnalysis(
    organizationId: number | string,
    incidentId: number | string,
  ): Promise<IncidentAiAnalysis> {
    const { data } = await api.post<IncidentAiAnalysis | { data: IncidentAiAnalysis }>(
      organizationPath(organizationId, `/incidents/${incidentId}/ai-analysis`),
    );
    return unwrapData(data);
  },

  reviewQueue(
    organizationId: number | string,
    filters: {
      status?: CommunityShieldStatus | '';
      platform?: string;
      confidence?: string;
      uncertainty?: string;
      classification?: string;
      escalated?: boolean | '';
    } = {},
  ): Promise<ReviewQueueItem[]> {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.set(key, String(value));
      }
    });
    const query = params.toString() ? `?${params.toString()}` : '';
    return scoped(organizationId, `/community-shield/review-queue${query}`);
  },

  reviewPackage(
    organizationId: number | string,
    reportId: number | string,
  ): Promise<IncidentReviewPackage> {
    return scoped(organizationId, `/community-shield/reports/${reportId}/review`);
  },

  async startReview(
    organizationId: number | string,
    reportId: number | string,
    payload: { review_lock_version?: number } = {},
  ): Promise<IncidentReviewPackage> {
    const { data } = await api.post(
      organizationPath(organizationId, `/community-shield/reports/${reportId}/review/start`),
      payload,
    );
    return unwrapData(data);
  },

  async confirmReview(
    organizationId: number | string,
    reportId: number | string,
    payload: {
      notes: string;
      safety_classification: CommunityShieldSafetyClassification;
      review_lock_version?: number;
    },
  ): Promise<IncidentReviewPackage> {
    const { data } = await api.post(
      organizationPath(organizationId, `/community-shield/reports/${reportId}/review/confirm`),
      payload,
    );
    return unwrapData(data);
  },

  async markUncertain(
    organizationId: number | string,
    reportId: number | string,
    payload: { notes: string; review_lock_version?: number },
  ): Promise<IncidentReviewPackage> {
    const { data } = await api.post(
      organizationPath(organizationId, `/community-shield/reports/${reportId}/review/uncertain`),
      payload,
    );
    return unwrapData(data);
  },

  async closeReview(
    organizationId: number | string,
    reportId: number | string,
    payload: { notes?: string; review_lock_version?: number } = {},
  ): Promise<IncidentReviewPackage> {
    const { data } = await api.post(
      organizationPath(organizationId, `/community-shield/reports/${reportId}/review/close`),
      payload,
    );
    return unwrapData(data);
  },

  async escalateReview(
    organizationId: number | string,
    reportId: number | string,
    payload: { reason: string; review_lock_version?: number },
  ): Promise<IncidentReviewPackage> {
    const { data } = await api.post(
      organizationPath(organizationId, `/community-shield/reports/${reportId}/review/escalate`),
      payload,
    );
    return unwrapData(data);
  },

  async requestContext(
    organizationId: number | string,
    reportId: number | string,
    payload: { reason: string; review_lock_version?: number },
  ): Promise<IncidentContextRequest> {
    const { data } = await api.post(
      organizationPath(organizationId, `/community-shield/reports/${reportId}/context-requests`),
      payload,
    );
    return unwrapData(data);
  },

  async updateContextRequest(
    organizationId: number | string,
    reportId: number | string,
    contextRequestId: number | string,
    payload: { status: 'fulfilled' | 'cancelled'; review_lock_version?: number },
  ): Promise<IncidentContextRequest> {
    const { data } = await api.patch(
      organizationPath(
        organizationId,
        `/community-shield/reports/${reportId}/context-requests/${contextRequestId}`,
      ),
      payload,
    );
    return unwrapData(data);
  },

  evidencePackage(
    organizationId: number | string,
    reportId: number | string,
  ): Promise<IncidentEvidencePackage> {
    return scoped(organizationId, `/community-shield/reports/${reportId}/evidence-package`);
  },

  async exportEvidenceJson(
    organizationId: number | string,
    reportId: number | string,
  ): Promise<Blob> {
    const { data } = await api.get(
      organizationPath(organizationId, `/community-shield/reports/${reportId}/evidence-package.json`),
      { responseType: 'blob' },
    );
    return data as Blob;
  },

  async exportEvidencePdf(
    organizationId: number | string,
    reportId: number | string,
  ): Promise<Blob> {
    const { data } = await api.get(
      organizationPath(organizationId, `/community-shield/reports/${reportId}/evidence-package.pdf`),
      { responseType: 'blob', timeout: 60000 },
    );
    return data as Blob;
  },

  externalReports(
    organizationId: number | string,
    reportId: number | string,
  ): Promise<IncidentExternalReportRecord[]> {
    return scoped(organizationId, `/community-shield/reports/${reportId}/external-reports`);
  },

  async createExternalReport(
    organizationId: number | string,
    reportId: number | string,
    payload: {
      platform: string;
      reporting_channel: string;
      external_reference?: string;
      reported_at: string;
      note?: string;
      internal_notes?: string;
      reporter_visible_summary?: string;
    },
  ): Promise<IncidentExternalReportRecord> {
    const { data } = await api.post(
      organizationPath(organizationId, `/community-shield/reports/${reportId}/external-reports`),
      payload,
    );
    return unwrapData(data);
  },

  async updateExternalReport(
    organizationId: number | string,
    reportId: number | string,
    externalReportId: number | string,
    payload: Record<string, unknown>,
  ): Promise<IncidentExternalReportRecord> {
    const { data } = await api.patch(
      organizationPath(
        organizationId,
        `/community-shield/reports/${reportId}/external-reports/${externalReportId}`,
      ),
      payload,
    );
    return unwrapData(data);
  },

  async submitExternalReportAppeal(
    organizationId: number | string,
    reportId: number | string,
    externalReportId: number | string,
    payload: { reason: string; additional_evidence?: string; reference?: string; notes?: string },
    memberRoute = false,
  ): Promise<unknown> {
    const suffix = memberRoute
      ? `/community-shield/my-reports/${reportId}/external-reports/${externalReportId}/appeals`
      : `/community-shield/reports/${reportId}/external-reports/${externalReportId}/appeals`;
    const { data } = await api.post(organizationPath(organizationId, suffix), payload);
    return unwrapData(data);
  },

  myReports(organizationId: number | string): Promise<MemberReportSummary[]> {
    return scoped(organizationId, '/community-shield/my-reports');
  },

  myReport(organizationId: number | string, reportId: number | string): Promise<MemberReportSummary> {
    return scoped(organizationId, `/community-shield/my-reports/${reportId}`);
  },

  communitySafetyLessons(organizationId: number | string): Promise<AcademyLesson[]> {
    return scoped(organizationId, '/academy/community-safety');
  },

  academyLesson(organizationId: number | string, lessonId: number | string): Promise<AcademyLesson> {
    return scoped(organizationId, `/academy/lessons/${lessonId}`);
  },

  academyScenario(
    organizationId: number | string,
    scenarioId: number | string,
  ): Promise<AcademyScenario> {
    return scoped(organizationId, `/academy/scenarios/${scenarioId}`);
  },

  academyProgress(organizationId: number | string): Promise<AcademyLessonProgress[]> {
    return scoped(organizationId, '/academy/progress');
  },

  async completeAcademyLesson(
    organizationId: number | string,
    lessonId: number | string,
  ): Promise<AcademyLessonProgress> {
    const { data } = await api.post<AcademyLessonProgress | { data: AcademyLessonProgress }>(
      organizationPath(organizationId, `/academy/lessons/${lessonId}/complete`),
    );
    return unwrapData(data);
  },

  async startAdaptSession(
    organizationId: number | string,
    lessonId: number | string,
  ): Promise<AdaptStartResponse> {
    const { data } = await api.post<AdaptStartResponse | { data: AdaptStartResponse }>(
      organizationPath(organizationId, `/academy/lessons/${lessonId}/adapt-sessions`),
    );
    return unwrapData(data);
  },

  async adaptSession(
    organizationId: number | string,
    sessionId: number | string,
  ): Promise<AdaptSessionShowResponse> {
    const { data } = await api.get<AdaptSessionShowResponse | { data: AdaptSessionShowResponse }>(
      organizationPath(organizationId, `/academy/adapt-sessions/${sessionId}`),
    );
    return unwrapData(data);
  },

  async submitAdaptResponse(
    organizationId: number | string,
    sessionId: number | string,
    payload: {
      answer: string;
      confidence: number;
      reasoning?: string;
      challenge_id?: string;
    },
  ): Promise<AdaptSubmitResponse> {
    const { data } = await api.post<AdaptSubmitResponse | { data: AdaptSubmitResponse }>(
      organizationPath(organizationId, `/academy/adapt-sessions/${sessionId}/responses`),
      payload,
    );
    return unwrapData(data);
  },

  learningPatterns(organizationId: number | string): Promise<LearningPattern[]> {
    return scoped(organizationId, '/learning-patterns');
  },

  learningPattern(
    organizationId: number | string,
    patternId: number | string,
  ): Promise<LearningPattern> {
    return scoped(organizationId, `/learning-patterns/${patternId}`);
  },

  async reportLearningPattern(
    organizationId: number | string,
    reportId: number | string,
  ): Promise<LearningPattern | null> {
    const { data } = await api.get<LearningPattern | { data: LearningPattern | null }>(
      organizationPath(organizationId, `/community-shield/reports/${reportId}/learning-pattern`),
    );
    if (data && typeof data === 'object' && 'data' in data) {
      return data.data;
    }
    return data as LearningPattern;
  },

  async createReportLearningPattern(
    organizationId: number | string,
    reportId: number | string,
    payload: {
      pattern_type: string;
      title: string;
      summary: string;
      learning_objective: string;
      domain?: string | null;
      audience_context?: string | null;
    },
  ): Promise<LearningPattern> {
    const { data } = await api.post<LearningPattern | { data: LearningPattern }>(
      organizationPath(organizationId, `/community-shield/reports/${reportId}/learning-pattern`),
      payload,
    );
    return unwrapData(data);
  },

  async updateLearningPattern(
    organizationId: number | string,
    patternId: number | string,
    payload: Partial<{
      pattern_type: string;
      title: string;
      summary: string;
      learning_objective: string;
      domain: string | null;
      audience_context: string | null;
      status: string;
    }>,
  ): Promise<LearningPattern> {
    const { data } = await api.patch<LearningPattern | { data: LearningPattern }>(
      organizationPath(organizationId, `/learning-patterns/${patternId}`),
      payload,
    );
    return unwrapData(data);
  },

  async approveLearningPattern(
    organizationId: number | string,
    patternId: number | string,
  ): Promise<LearningPattern> {
    const { data } = await api.post<LearningPattern | { data: LearningPattern }>(
      organizationPath(organizationId, `/learning-patterns/${patternId}/approve`),
    );
    return unwrapData(data);
  },

  async archiveLearningPattern(
    organizationId: number | string,
    patternId: number | string,
  ): Promise<LearningPattern> {
    const { data } = await api.post<LearningPattern | { data: LearningPattern }>(
      organizationPath(organizationId, `/learning-patterns/${patternId}/archive`),
    );
    return unwrapData(data);
  },

  learningRecommendations(organizationId: number | string): Promise<LearningRecommendation[]> {
    return scoped(organizationId, '/learning-recommendations');
  },

  async createLearningRecommendation(
    organizationId: number | string,
    payload: {
      learning_pattern_id: number;
      academy_course_id?: number | null;
      academy_lesson_id?: number | null;
      reason: string;
      status?: string;
    },
  ): Promise<LearningRecommendation> {
    const { data } = await api.post<LearningRecommendation | { data: LearningRecommendation }>(
      organizationPath(organizationId, '/learning-recommendations'),
      payload,
    );
    return unwrapData(data);
  },

  async updateLearningRecommendation(
    organizationId: number | string,
    recommendationId: number | string,
    payload: Partial<{
      academy_course_id: number | null;
      academy_lesson_id: number | null;
      reason: string;
      status: string;
    }>,
  ): Promise<LearningRecommendation> {
    const { data } = await api.patch<LearningRecommendation | { data: LearningRecommendation }>(
      organizationPath(organizationId, `/learning-recommendations/${recommendationId}`),
      payload,
    );
    return unwrapData(data);
  },
};
