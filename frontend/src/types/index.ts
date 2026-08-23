export type CommunityShieldPlatform =
  | 'x'
  | 'youtube'
  | 'tiktok'
  | 'reddit'
  | 'discord'
  | 'telegram'
  | 'whatsapp'
  | 'other';

export type CommunityShieldContentType =
  | 'post'
  | 'comment'
  | 'video'
  | 'image'
  | 'message'
  | 'profile'
  | 'thread';

export type CommunityShieldVisibility = 'public' | 'group' | 'private' | 'unknown';

export type CommunityShieldStatus = 'open' | 'reviewing' | 'resolved';

export type CommunityShieldReviewOutcome = 'confirmed' | 'uncertain' | 'closed';

export type CommunityShieldReviewActionType =
  | 'started'
  | 'confirmed'
  | 'marked_uncertain'
  | 'closed'
  | 'escalated'
  | 'context_requested'
  | 'context_fulfilled'
  | 'context_cancelled'
  | 'notes_updated';

export type ContextRequestStatus = 'open' | 'fulfilled' | 'cancelled';

export type ReviewAllowedAction =
  | 'start'
  | 'confirm'
  | 'uncertain'
  | 'close'
  | 'escalate'
  | 'request_context';

export type CommunityShieldLanguage =
  | 'en'
  | 'ar'
  | 'fr'
  | 'ur'
  | 'tr'
  | 'es'
  | 'bn'
  | 'id'
  | 'ms'
  | 'fa'
  | 'so'
  | 'sw'
  | 'de'
  | 'nl'
  | 'pt'
  | 'zh'
  | 'hi'
  | 'other'
  | 'unknown';

export type CommunityShieldSafetyClassification =
  | 'unclassified'
  | 'harassment'
  | 'hate'
  | 'threat'
  | 'targeted_abuse'
  | 'discrimination'
  | 'incitement'
  | 'other';

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

export interface IncidentReply {
  id?: number;
  incident_id?: number;
  author: string | null;
  content: string;
  posted_at: string | null;
  position: number;
  created_at?: string;
  updated_at?: string;
}

export interface IncidentRelatedItem {
  id?: number;
  incident_id?: number;
  platform: CommunityShieldPlatform;
  content_type: CommunityShieldContentType;
  reference_url: string | null;
  description: string | null;
  observed_at: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface Incident {
  id: number;
  organization_id: number;
  platform: CommunityShieldPlatform;
  content_type: CommunityShieldContentType;
  visibility: CommunityShieldVisibility;
  source_url: string | null;
  description: string;
  original_item_title: string | null;
  original_item_content: string | null;
  original_item_author: string | null;
  original_item_posted_at: string | null;
  observed_at: string | null;
  surrounding_context: string | null;
  language: CommunityShieldLanguage | string | null;
  reporter_notes: string | null;
  safety_classification: CommunityShieldSafetyClassification;
  classified_by?: UserSummary | null;
  classified_at: string | null;
  status: CommunityShieldStatus;
  review_outcome?: CommunityShieldReviewOutcome | null;
  escalated?: boolean;
  escalation_reason?: string | null;
  escalated_by?: UserSummary | null;
  escalated_at?: string | null;
  current_reviewer?: UserSummary | null;
  review_started_at?: string | null;
  review_notes?: string | null;
  review_lock_version?: number;
  replies?: IncidentReply[];
  related_items?: IncidentRelatedItem[];
  reported_by?: UserSummary | null;
  created_at?: string;
  updated_at?: string;
}

export interface ReviewQueueItem {
  id: number;
  platform: CommunityShieldPlatform;
  content_type: CommunityShieldContentType;
  visibility: CommunityShieldVisibility;
  status: CommunityShieldStatus;
  review_outcome: CommunityShieldReviewOutcome | null;
  escalated: boolean;
  safety_classification: CommunityShieldSafetyClassification;
  related_item_count: number;
  open_context_requests: number;
  ai_assisted_triage: {
    classification: string | null;
    confidence: AiConfidenceLevel | null;
    uncertainty: AiConfidenceLevel | null;
    recommended_action: AiRecommendedActionType | null;
  };
  current_reviewer?: UserSummary | null;
  created_at?: string;
  updated_at?: string;
}

export interface IncidentReviewRecord {
  id: number;
  incident_id: number;
  outcome: CommunityShieldReviewOutcome | null;
  notes: string | null;
  safety_classification: CommunityShieldSafetyClassification | null;
  escalation_reason: string | null;
  is_current: boolean;
  reviewer?: UserSummary | null;
  created_at?: string;
  updated_at?: string;
}

export interface IncidentReviewAction {
  id: number;
  incident_id: number;
  action: CommunityShieldReviewActionType;
  notes: string | null;
  payload?: Record<string, unknown> | null;
  actor?: UserSummary | null;
  created_at?: string;
}

export interface IncidentContextRequest {
  id: number;
  incident_id: number;
  reason: string;
  status: ContextRequestStatus;
  requested_at: string;
  resolved_at: string | null;
  requested_by?: UserSummary | null;
  resolved_by?: UserSummary | null;
  created_at?: string;
  updated_at?: string;
}

export interface IncidentReviewPackage {
  incident: Incident;
  ai_assisted_triage: {
    label: string;
    advisory_disclaimer: string;
    latest: IncidentAiAnalysis | null;
    history: IncidentAiAnalysis[];
  };
  human_review: {
    outcome: CommunityShieldReviewOutcome | null;
    notes: string | null;
    escalated: boolean;
    escalation_reason: string | null;
    current_review: IncidentReviewRecord | null;
    reviews: IncidentReviewRecord[];
    context_requests: IncidentContextRequest[];
    history: IncidentReviewAction[];
    allowed_actions: ReviewAllowedAction[];
  };
  queue_summary: {
    related_item_count: number;
    reply_count: number;
    ai_classification: string | null;
    ai_confidence: AiConfidenceLevel | null;
    ai_uncertainty: AiConfidenceLevel | null;
  };
}

export interface IncidentEvidencePackage {
  package: {
    schema_version: number;
    package_version: number;
    generated_at: string;
    generated_by: { name: string; role_label?: string };
    organization: { name: string | null; slug: string | null };
    source_incident_updated_at: string | null;
    hierarchy: Record<string, string>;
  };
  incident: {
    reference: string;
    submitted_at: string | null;
    observed_at: string | null;
    original_item_posted_at: string | null;
    status: string | null;
    review_outcome: CommunityShieldReviewOutcome | null;
    content_type: string | null;
    visibility: string | null;
    platform: string | null;
    language: string | null;
    source_url: string | null;
    description: string | null;
  };
  evidence: {
    label: string;
    original_item: Record<string, unknown>;
    surrounding_context: string | null;
    replies: Array<Record<string, unknown>>;
    related_items: Array<Record<string, unknown>>;
    language: string | null;
    reporter_notes: { label: string; notes: string | null };
    reported_safety_classification: {
      label: string;
      value: string;
      note: string;
    };
  };
  ai_analysis: {
    label: string;
    advisory: boolean;
    disclaimer: string;
    current: Record<string, unknown>;
    previous: Array<Record<string, unknown>>;
    uncertainty: {
      confidence: string;
      uncertainty: string;
      interpretation_note: string;
    };
  };
  human_review: {
    label: string;
    authoritative: boolean;
    disclaimer: string;
    status: 'reviewed' | 'not_yet_reviewed' | string;
    reviewer: string | null;
    review_started_at: string | null;
    review_completed_at: string | null;
    outcome: CommunityShieldReviewOutcome | null;
    human_classification: string | null;
    notes: string | null;
    escalation: {
      escalated: boolean;
      escalated_by: string | null;
      escalated_at: string | null;
      reason: string | null;
      note: string;
    };
    context_requests: Array<Record<string, unknown>>;
    history: Array<Record<string, unknown>>;
    decision: {
      outcome: CommunityShieldReviewOutcome | null;
      classification: string | null;
      reviewer: string | null;
      reviewed_at: string | null;
      rationale: string | null;
      uncertain_prominence: string | null;
    };
  };
  references: Array<{
    type: string;
    label: string;
    url: string | null;
    note: string | null;
  }>;
  reporting_route: {
    label?: string;
    platform: string;
    platform_label: string;
    recommended_route: string;
    general_instructions: string;
    safety_notes: string;
    privacy_notes: string;
    last_reviewed: string | null;
    disclaimer: string;
    automatic_submission: boolean;
  };
  safety_privacy_notes: {
    label: string;
    notes: string[];
    reporting_disclaimer: string;
  };
  disclaimers: {
    ai: string;
    human_review: string;
    reporting: string;
    outcome_tracking?: string;
  };
  outcome_tracking?: {
    label: string;
    disclaimer: string;
    reports: IncidentExternalReportSummary[];
  };
}

export type ExternalReportStatus = 'reported' | 'under_review' | 'decision' | 'outcome';

export type ExternalReportDecision =
  | 'action_taken'
  | 'no_action'
  | 'content_does_not_violate_policy'
  | 'insufficient_information'
  | 'other';

export type ExternalReportOutcome =
  | 'content_removed'
  | 'content_restricted'
  | 'account_action'
  | 'no_action'
  | 'warning'
  | 'resolved'
  | 'unable_to_determine'
  | 'other';

export type ExternalReportOutcomeSource =
  | 'platform_response'
  | 'reporter_observation'
  | 'reviewer_observation'
  | 'other';

export type ExternalReportVerificationStatus =
  | 'unverified'
  | 'reported_by_user'
  | 'verified_by_reviewer';

export type AppealStatus =
  | 'submitted'
  | 'under_review'
  | 'accepted'
  | 'rejected'
  | 'withdrawn'
  | 'resolved';

export interface IncidentExternalReportStatusHistoryEntry {
  id: number;
  previous_status: ExternalReportStatus | null;
  new_status: ExternalReportStatus;
  decision: ExternalReportDecision | null;
  outcome: ExternalReportOutcome | null;
  changed_by: UserSummary | null;
  changed_at: string | null;
  note: string | null;
}

export interface IncidentReportAppealRecord {
  id: number;
  submitted_at: string | null;
  submitted_by: UserSummary | null;
  reason: string;
  additional_evidence: string | null;
  reference: string | null;
  notes: string | null;
  status: AppealStatus;
  response: string | null;
  responded_at: string | null;
  responded_by: UserSummary | null;
  created_at?: string;
  updated_at?: string;
}

export interface IncidentExternalReportRecord {
  id: number;
  incident_id: number;
  platform: string;
  reporting_channel: string;
  external_reference: string | null;
  reported_at: string | null;
  status: ExternalReportStatus;
  decision: ExternalReportDecision | null;
  decision_note: string | null;
  outcome: ExternalReportOutcome | null;
  outcome_source: ExternalReportOutcomeSource | null;
  outcome_summary: string | null;
  reporter_visible_summary: string | null;
  verification_status: ExternalReportVerificationStatus;
  internal_notes: string | null;
  created_by: UserSummary | null;
  updated_by: UserSummary | null;
  created_at?: string;
  updated_at?: string;
  status_history?: IncidentExternalReportStatusHistoryEntry[];
  appeals?: IncidentReportAppealRecord[];
}

export interface IncidentExternalReportSummary {
  id?: number;
  platform: string;
  reporting_channel: string;
  reported_at: string | null;
  status: ExternalReportStatus;
  external_reference: string | null;
  decision: ExternalReportDecision | null;
  outcome: ExternalReportOutcome | null;
  outcome_source: ExternalReportOutcomeSource | null;
  verification_status: ExternalReportVerificationStatus;
  appeals: Array<{ id: number; status: AppealStatus; submitted_at: string | null; reason: string }>;
}

export interface MemberReportSummary {
  id: number;
  reference: string;
  platform: string;
  content_type: string;
  status: CommunityShieldStatus;
  review_outcome: CommunityShieldReviewOutcome | null;
  submitted_at: string | null;
  external_reports: IncidentExternalReportRecord[];
  external_report_count?: number;
}

export type IncidentAiAnalysisStatus = 'queued' | 'running' | 'completed' | 'failed';

export type AiConfidenceLevel = 'low' | 'moderate' | 'high';

export type AiRecommendedActionType = 'human_review' | 'request_more_context' | 'no_immediate_action';

export interface IncidentAiSignal {
  name: string;
  description: string;
  evidence: string[];
  confidence: AiConfidenceLevel;
}

export interface IncidentAiAnalysisPackage {
  signals: IncidentAiSignal[];
  classification: {
    label: string;
    confidence: AiConfidenceLevel;
  };
  uncertainty: {
    level: AiConfidenceLevel;
    explanation: string;
  };
  alternative_interpretation: string | null;
  recommended_action: {
    type: AiRecommendedActionType;
    reason: string;
  };
}

export interface IncidentAiAnalysis {
  id: number;
  incident_id: number;
  provider: string;
  model: string | null;
  prompt_version: string;
  status: IncidentAiAnalysisStatus;
  analysis: IncidentAiAnalysisPackage | null;
  error_message?: string | null;
  requested_by?: UserSummary | null;
  created_at?: string;
  updated_at?: string;
  advisory_disclaimer?: string;
}

export interface CommunityShieldOverview {
  can_report: boolean;
  can_review: boolean;
  counts?: {
    open: number;
    reviewing: number;
    resolved: number;
  };
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
    reviewing_incidents: number;
    resolved_incidents: number;
  };
}

export type AcademyLessonStatus = 'draft' | 'published';

export type AcademyLessonCategory = 'general' | 'community_safety';

export type AcademyLessonProgressStatus = 'started' | 'completed';

export type LearningPatternStatus = 'draft' | 'approved' | 'archived';

export type LearningPatternType =
  | 'religious_targeting'
  | 'coded_language'
  | 'repeated_harassment'
  | 'contextual_hate'
  | 'visual_hate'
  | 'dog_whistle'
  | 'coordinated_behavior'
  | 'misinformation_related_harm'
  | 'reporting_safety'
  | 'other';

export type LearningRecommendationStatus = 'draft' | 'published' | 'archived';

export type AdaptSessionStatus = 'active' | 'completed' | 'unavailable';

export interface AcademyLessonSection {
  heading: string;
  body: string;
}

export interface AcademyScenario {
  id: number;
  organization_id: number;
  academy_lesson_id: number;
  title: string;
  prompt: string;
  context: string | null;
  options: string[] | Record<string, unknown> | null;
  expected_reasoning_signals?: string[] | null;
  misconception_tags?: string[] | null;
  difficulty: number | string | null;
  adapt_challenge_id: string | null;
  adapt_topic_id: string | null;
  adapt_concept_id: string | null;
  adapt_domain: string | null;
  sort_order: number;
  is_demo: boolean;
}

export interface AcademyLesson {
  id: number;
  organization_id: number;
  course_id: number | null;
  title: string;
  learning_objective: string | null;
  sections: AcademyLessonSection[];
  category: AcademyLessonCategory | string;
  status: AcademyLessonStatus;
  is_demo: boolean;
  course?: Pick<Course, 'id' | 'title' | 'status'> | null;
  scenarios?: AcademyScenario[];
  scenario_count?: number;
  created_at?: string;
  updated_at?: string;
}

export interface AcademyLessonProgress {
  id: number;
  organization_id: number;
  user_id: number;
  academy_lesson_id: number;
  status: AcademyLessonProgressStatus | string;
  started_at: string | null;
  completed_at: string | null;
  lesson?: Pick<AcademyLesson, 'id' | 'title' | 'category' | 'status'> | null;
}

export interface LearningPattern {
  id: number;
  organization_id: number;
  pattern_type: LearningPatternType | string;
  title: string;
  summary: string;
  learning_objective: string;
  domain: string | null;
  audience_context: string | null;
  status: LearningPatternStatus | string;
  source_incident_id?: number | null;
  created_by?: UserSummary | null;
  approved_by?: UserSummary | null;
  approved_at?: string | null;
  recommendations?: LearningRecommendation[];
  created_at?: string;
  updated_at?: string;
}

export interface LearningRecommendation {
  id: number;
  organization_id: number;
  learning_pattern_id: number;
  academy_course_id: number | null;
  academy_lesson_id: number | null;
  reason: string;
  status: LearningRecommendationStatus | string;
  pattern?: (Pick<
    LearningPattern,
    'id' | 'title' | 'pattern_type' | 'summary' | 'learning_objective' | 'domain' | 'status'
  > & { source_incident_id?: number | null }) | null;
  course?: Course | null;
  lesson?: AcademyLesson | null;
  created_by?: UserSummary | null;
  created_at?: string;
  updated_at?: string;
}

export interface AdaptChallenge {
  challenge_id: string | null;
  prompt: string | null;
  choices: string[];
  difficulty: number | null;
  difficulty_label: string | null;
  challenge_type: string | null;
  concept_id: string | null;
  domain: string | null;
  topic_id: string | null;
}

export interface AdaptSessionPayload {
  session_id: string;
  learner_id: string | null;
  status: string | null;
  challenge: AdaptChallenge | null;
  evidence_plan: Record<string, unknown>;
  confidence_scale: Array<{ value?: number; label?: string } | number | string>;
  can_submit: boolean;
  complete: boolean;
}

export interface AdaptFeedbackPayload {
  session_id: string;
  status: string | null;
  challenge: AdaptChallenge | null;
  feedback: Record<string, unknown> | null;
  noticed: Record<string, unknown> | null;
  why_this_question: Record<string, unknown> | null;
  next_challenge: AdaptChallenge | null;
  adaptation: Record<string, unknown> | null;
  complete: boolean;
}

export interface AdaptLearningSessionRecord {
  id: number;
  organization_id: number;
  user_id: number;
  academy_lesson_id: number;
  academy_scenario_id: number | null;
  adapt_session_id: string | null;
  adapt_topic_id: string | null;
  adapt_subject_id: string | null;
  status: AdaptSessionStatus | string;
  started_at: string | null;
  completed_at: string | null;
}

export interface AdaptStartResponse {
  available: boolean;
  message?: string;
  session: AdaptLearningSessionRecord;
  adapt?: AdaptSessionPayload;
}

export interface AdaptSessionShowResponse {
  available: boolean;
  message?: string;
  session: AdaptLearningSessionRecord;
  adapt?: AdaptSessionPayload;
  last_result?: AdaptFeedbackPayload | null;
}

export interface AdaptSubmitResponse {
  available: boolean;
  message?: string;
  session: AdaptLearningSessionRecord;
  result?: AdaptFeedbackPayload;
}
