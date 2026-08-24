<?php

namespace Database\Seeders;

use App\Models\AcademyLesson;
use App\Models\AcademyScenario;
use App\Models\Announcement;
use App\Models\Course;
use App\Models\Event;
use App\Models\Incident;
use App\Models\IncidentAiAnalysis;
use App\Models\IncidentContextRequest;
use App\Models\IncidentExternalReport;
use App\Models\IncidentExternalReportStatusHistory;
use App\Models\IncidentReportAppeal;
use App\Models\IncidentReview;
use App\Models\IncidentReviewAction;
use App\Models\LearningPattern;
use App\Models\LearningRecommendation;
use App\Models\Organization;
use App\Models\Resource;
use App\Models\User;
use App\Prompts\CommunityShieldContextAnalysisV1;
use Illuminate\Database\Seeder;

class DemoCommunitySeeder extends Seeder
{
    public function run(): void
    {
        $alpha = Organization::query()->where('slug', 'demo-msa-alpha')->firstOrFail();
        $beta = Organization::query()->where('slug', 'demo-msa-beta')->firstOrFail();

        $alphaAdmin = User::query()->where('email', 'alpha.admin@example.com')->firstOrFail();
        $alphaMember = User::query()->where('email', 'alpha.member@example.com')->firstOrFail();
        $alphaReviewer = User::query()->where('email', 'alpha.reviewer@example.com')->firstOrFail();
        $betaAdmin = User::query()->where('email', 'beta.admin@example.com')->firstOrFail();
        $multiUser = User::query()->where('email', 'multi.user@example.com')->firstOrFail();

        $this->seedAlpha($alpha, $alphaAdmin, $alphaMember, $alphaReviewer, $multiUser);
        $this->seedBeta($beta, $betaAdmin, $multiUser);
    }

    private function seedAlpha(
        Organization $alpha,
        User $admin,
        User $member,
        User $reviewer,
        User $multiUser
    ): void {
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

        $alphaFlagship = Incident::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'reported_by' => $member->id,
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
            ],
            [
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'source_url' => 'https://x.com/example/status/alpha-demo-1',
                'description' => 'Alpha member reported a concerning public post targeting students after jumuah. This report belongs only to Demo MSA Alpha.',
                'original_item_title' => 'Campus students after jumuah',
                'original_item_content' => "These people don't belong here. Someone should remind them after Friday prayer.",
                'original_item_author' => '@campusvoice_demo',
                'original_item_posted_at' => now()->subDays(2)->setTime(14, 20),
                'observed_at' => now()->subDay()->setTime(9, 15),
                'surrounding_context' => 'The post appeared in a public timeline thread about campus facilities. Several replies amplified the hostility before the original account deleted one reply.',
                'language' => 'en',
                'reporter_notes' => 'I saw a similar tone from this account earlier today in another public thread.',
                'safety_classification' => Incident::CLASSIFICATION_UNCLASSIFIED,
                'classified_by' => null,
                'classified_at' => null,
                'status' => Incident::STATUS_OPEN,
                'review_outcome' => null,
                'escalated' => false,
                'review_lock_version' => 1,
            ]
        );

        if ($alphaFlagship->replies()->count() === 0) {
            $alphaFlagship->replies()->createMany([
                [
                    'author' => '@ally_demo',
                    'content' => 'This is wrong. Leave students alone.',
                    'posted_at' => now()->subDays(2)->setTime(14, 35),
                    'position' => 0,
                ],
                [
                    'author' => '@campusvoice_demo',
                    'content' => 'Keep pushing it. They heard us.',
                    'posted_at' => now()->subDays(2)->setTime(14, 48),
                    'position' => 1,
                ],
            ]);
        }

        if ($alphaFlagship->relatedItems()->count() === 0) {
            $alphaFlagship->relatedItems()->create([
                'platform' => Incident::PLATFORM_REDDIT,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'reference_url' => 'https://reddit.com/r/example/comments/alpha-related-copy',
                'description' => 'Nearly identical wording reposted in a campus subreddit the same evening.',
                'observed_at' => now()->subDay()->setTime(21, 0),
            ]);
        }

        $this->seedCompletedAnalysis($alphaFlagship, $admin, [
            'signals' => [
                [
                    'name' => 'religious_identity_targeting',
                    'description' => 'Language targets students associated with Friday prayer.',
                    'evidence' => ['after Friday prayer', "don't belong here"],
                    'confidence' => 'moderate',
                ],
            ],
            'classification' => [
                'label' => 'potential_hate',
                'confidence' => 'moderate',
            ],
            'uncertainty' => [
                'level' => 'moderate',
                'explanation' => 'Tone is hostile, but intent could also be interpreted as political grievance without further context.',
            ],
            'alternative_interpretation' => 'Could be hyperbolic political speech rather than actionable hate.',
            'recommended_action' => [
                'type' => 'human_review',
                'reason' => 'Human review recommended before any determination.',
            ],
        ]);

        $discordOpen = Incident::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'reported_by' => $member->id,
                'platform' => Incident::PLATFORM_DISCORD,
                'content_type' => Incident::CONTENT_TYPE_MESSAGE,
            ],
            [
                'visibility' => Incident::VISIBILITY_GROUP,
                'source_url' => null,
                'description' => 'Concerning messages appeared in an Alpha Discord community channel. No public URL is available.',
                'original_item_content' => 'Anyone know which dorm the MSA officers live in?',
                'original_item_author' => 'guest_user_demo',
                'observed_at' => now()->subHours(18),
                'surrounding_context' => 'Posted in a general campus Discord server after a heated politics channel discussion. Preceding replies are incomplete.',
                'language' => 'en',
                'reporter_notes' => 'Channel moderators later deleted the message, but members still saw it.',
                'safety_classification' => Incident::CLASSIFICATION_UNCLASSIFIED,
                'status' => Incident::STATUS_REVIEWING,
                'review_outcome' => Incident::OUTCOME_UNCERTAIN,
                'current_reviewer_id' => $reviewer->id,
                'review_started_at' => now()->subHours(2),
                'review_notes' => 'The original post is concerning, but the surrounding conversation is incomplete.',
                'escalated' => false,
                'review_lock_version' => 2,
            ]
        );

        $this->seedCompletedAnalysis($discordOpen, $admin, [
            'signals' => [
                [
                    'name' => 'location_seeking',
                    'description' => 'Asks for dorm location of MSA officers.',
                    'evidence' => ['which dorm the MSA officers live in'],
                    'confidence' => 'moderate',
                ],
            ],
            'classification' => [
                'label' => 'unclear',
                'confidence' => 'low',
            ],
            'uncertainty' => [
                'level' => 'high',
                'explanation' => 'Could be curiosity, doxxing preparation, or unrelated housing talk without preceding replies.',
            ],
            'alternative_interpretation' => 'May be a clumsy housing question with no harmful intent.',
            'recommended_action' => [
                'type' => 'request_more_context',
                'reason' => 'Need preceding replies before making a determination.',
            ],
        ]);

        if ($discordOpen->reviews()->count() === 0) {
            $discordOpen->reviews()->create([
                'reviewer_id' => $reviewer->id,
                'outcome' => IncidentReview::OUTCOME_UNCERTAIN,
                'notes' => 'Need preceding replies before classification.',
                'is_current' => true,
            ]);
        }

        if ($discordOpen->reviewActions()->count() === 0) {
            $discordOpen->reviewActions()->createMany([
                [
                    'actor_id' => $reviewer->id,
                    'action' => IncidentReviewAction::ACTION_STARTED,
                    'notes' => 'Started review',
                    'created_at' => now()->subHours(2),
                ],
                [
                    'actor_id' => $reviewer->id,
                    'action' => IncidentReviewAction::ACTION_MARKED_UNCERTAIN,
                    'notes' => 'Need preceding replies before classification.',
                    'created_at' => now()->subHour(),
                ],
                [
                    'actor_id' => $reviewer->id,
                    'action' => IncidentReviewAction::ACTION_CONTEXT_REQUESTED,
                    'notes' => 'Need the two replies immediately preceding the reported comment.',
                    'created_at' => now()->subMinutes(50),
                ],
            ]);
        }

        if ($discordOpen->contextRequests()->count() === 0) {
            $discordOpen->contextRequests()->create([
                'requested_by' => $reviewer->id,
                'reason' => 'Need the two replies immediately preceding the reported comment.',
                'status' => IncidentContextRequest::STATUS_OPEN,
                'requested_at' => now()->subMinutes(50),
            ]);
        }

        $escalatedReport = Incident::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'reported_by' => $multiUser->id,
                'platform' => Incident::PLATFORM_TELEGRAM,
                'content_type' => Incident::CONTENT_TYPE_MESSAGE,
            ],
            [
                'visibility' => Incident::VISIBILITY_PRIVATE,
                'description' => 'Escalated Alpha demo report requiring specialized human review.',
                'original_item_content' => 'We know who your leaders are. This will not stay online forever.',
                'original_item_author' => 'telegram_guest_demo',
                'observed_at' => now()->subHours(8),
                'surrounding_context' => 'Received in a private Telegram chat after a public flyer was shared.',
                'language' => 'en',
                'reporter_notes' => 'Feels more serious than the usual harassment reports.',
                'safety_classification' => Incident::CLASSIFICATION_THREAT,
                'classified_by' => $reviewer->id,
                'classified_at' => now()->subHours(3),
                'status' => Incident::STATUS_REVIEWING,
                'review_outcome' => null,
                'escalated' => true,
                'escalation_reason' => 'Possible targeted threat language requiring higher-level human review.',
                'escalated_by' => $reviewer->id,
                'escalated_at' => now()->subHours(3),
                'current_reviewer_id' => $reviewer->id,
                'review_started_at' => now()->subHours(4),
                'review_lock_version' => 3,
            ]
        );

        if ($escalatedReport->reviewActions()->count() === 0) {
            $escalatedReport->reviewActions()->createMany([
                [
                    'actor_id' => $reviewer->id,
                    'action' => IncidentReviewAction::ACTION_STARTED,
                    'notes' => 'Started review',
                    'created_at' => now()->subHours(4),
                ],
                [
                    'actor_id' => $reviewer->id,
                    'action' => IncidentReviewAction::ACTION_ESCALATED,
                    'notes' => 'Possible targeted threat language requiring higher-level human review.',
                    'created_at' => now()->subHours(3),
                ],
            ]);
        }

        $confirmedPackage = Incident::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'reported_by' => $admin->id,
                'platform' => Incident::PLATFORM_REDDIT,
                'content_type' => Incident::CONTENT_TYPE_THREAD,
            ],
            [
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'source_url' => 'https://reddit.com/r/example/comments/alpha-demo',
                'description' => 'Resolved Alpha demo thread confirmed by a Community Safety Reviewer. Used as the Phase 7 complete evidence package demo.',
                'original_item_title' => 'Campus thread about Friday prayers',
                'original_item_content' => 'They keep showing up after jumuah like they own the place. Someone needs to push back harder.',
                'original_item_author' => 'u/campus_noise_demo',
                'original_item_posted_at' => now()->subDays(5)->setTime(16, 10),
                'observed_at' => now()->subDays(4)->setTime(11, 0),
                'surrounding_context' => "Before: A thread about campus room bookings.\nReported item: Hostile post targeting students associated with Friday prayer.\nAfter: Several replies agreed and one related cross-post appeared on X.",
                'language' => 'en',
                'reporter_notes' => 'I preserved the original wording. A nearly identical post appeared on X later that night.',
                'safety_classification' => Incident::CLASSIFICATION_HATE,
                'classified_by' => $reviewer->id,
                'classified_at' => now()->subDays(4),
                'status' => Incident::STATUS_RESOLVED,
                'review_outcome' => Incident::OUTCOME_CONFIRMED,
                'review_notes' => 'The original content and surrounding replies support the classification despite moderate AI uncertainty.',
                'current_reviewer_id' => $reviewer->id,
                'review_started_at' => now()->subDays(4)->subHour(),
                'escalated' => false,
                'review_lock_version' => 4,
            ]
        );

        if ($confirmedPackage->replies()->count() === 0) {
            $confirmedPackage->replies()->createMany([
                [
                    'author' => 'u/ally_demo',
                    'content' => 'This is targeting students for their faith. Report it.',
                    'posted_at' => now()->subDays(5)->setTime(16, 25),
                    'position' => 0,
                ],
                [
                    'author' => 'u/campus_noise_demo',
                    'content' => 'Keep the pressure on. They heard us.',
                    'posted_at' => now()->subDays(5)->setTime(16, 40),
                    'position' => 1,
                ],
            ]);
        }

        if ($confirmedPackage->relatedItems()->count() === 0) {
            $confirmedPackage->relatedItems()->create([
                'platform' => Incident::PLATFORM_X,
                'content_type' => Incident::CONTENT_TYPE_POST,
                'reference_url' => 'https://x.com/example/status/alpha-related-confirmed',
                'description' => 'Nearly identical wording posted publicly on X the same evening.',
                'observed_at' => now()->subDays(4)->setTime(22, 15),
            ]);
        }

        $this->seedCompletedAnalysis($confirmedPackage, $admin, [
            'signals' => [
                [
                    'name' => 'religious_identity_targeting',
                    'description' => 'Targets students associated with Friday prayer attendance.',
                    'evidence' => ['after jumuah', 'push back harder'],
                    'confidence' => 'moderate',
                ],
                [
                    'name' => 'related_content_detected',
                    'description' => 'Related cross-platform copy appears on X.',
                    'evidence' => ['related X post'],
                    'confidence' => 'moderate',
                ],
            ],
            'classification' => [
                'label' => 'potential_hate',
                'confidence' => 'moderate',
            ],
            'uncertainty' => [
                'level' => 'moderate',
                'explanation' => 'Context may change interpretation if the surrounding thread was primarily political debate.',
            ],
            'alternative_interpretation' => 'Could be hyperbolic political speech rather than actionable hate.',
            'recommended_action' => [
                'type' => 'human_review',
                'reason' => 'Human review recommended before any determination.',
            ],
        ]);

        if ($confirmedPackage->reviews()->count() === 0) {
            $confirmedPackage->reviews()->create([
                'reviewer_id' => $reviewer->id,
                'outcome' => IncidentReview::OUTCOME_CONFIRMED,
                'notes' => 'The original content and surrounding replies support the classification despite moderate AI uncertainty.',
                'safety_classification' => Incident::CLASSIFICATION_HATE,
                'is_current' => true,
            ]);
        }

        if ($confirmedPackage->reviewActions()->count() === 0) {
            $confirmedPackage->reviewActions()->createMany([
                [
                    'actor_id' => $reviewer->id,
                    'action' => IncidentReviewAction::ACTION_STARTED,
                    'notes' => 'Started review',
                    'created_at' => now()->subDays(4)->subHour(),
                ],
                [
                    'actor_id' => $reviewer->id,
                    'action' => IncidentReviewAction::ACTION_CONTEXT_REQUESTED,
                    'notes' => 'Requested the related X post reference.',
                    'created_at' => now()->subDays(4)->subMinutes(40),
                ],
                [
                    'actor_id' => $reviewer->id,
                    'action' => IncidentReviewAction::ACTION_CONTEXT_FULFILLED,
                    'notes' => 'Related X reference added.',
                    'created_at' => now()->subDays(4)->subMinutes(20),
                ],
                [
                    'actor_id' => $reviewer->id,
                    'action' => IncidentReviewAction::ACTION_CONFIRMED,
                    'notes' => 'The original content and surrounding replies support the classification despite moderate AI uncertainty.',
                    'created_at' => now()->subDays(4),
                ],
            ]);
        }

        if ($confirmedPackage->contextRequests()->count() === 0) {
            $confirmedPackage->contextRequests()->create([
                'requested_by' => $reviewer->id,
                'reason' => 'Requested the related X post reference.',
                'status' => IncidentContextRequest::STATUS_FULFILLED,
                'requested_at' => now()->subDays(4)->subMinutes(40),
                'resolved_by' => $reviewer->id,
                'resolved_at' => now()->subDays(4)->subMinutes(20),
            ]);
        }

        $this->seedOutcomeTracking($alpha, $admin, $member, $reviewer, $confirmedPackage, $discordOpen);
        $this->seedPhase9Education($alpha, $admin, $reviewer, $confirmedPackage);
    }

    /**
     * Phase 9 — sanitized Community Safety Academy path (not raw incident content).
     */
    private function seedPhase9Education(
        Organization $alpha,
        User $admin,
        User $reviewer,
        Incident $confirmedPackage
    ): void {
        $course = Course::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'title' => 'Community Safety',
            ],
            [
                'description' => 'Organization-scoped lessons that turn validated community patterns into privacy-preserving education.',
                'status' => Course::STATUS_PUBLISHED,
                'created_by' => $admin->id,
            ]
        );

        $xAppealIncident = Incident::query()->where('organization_id', $alpha->id)
            ->where('platform', Incident::PLATFORM_X)
            ->where('review_outcome', Incident::OUTCOME_CONFIRMED)
            ->whereKeyNot($confirmedPackage->id)
            ->first();

        $harassmentIncident = $this->seedEducationDemoIncident(
            $alpha,
            $admin,
            $reviewer,
            Incident::PLATFORM_DISCORD,
            Incident::CONTENT_TYPE_MESSAGE,
            'education-demo-harassment-thread',
            'Repeated Discord messages targeting a member\'s name and faith across several days.',
            'repeated_harassment',
        );

        $reportingIncident = $this->seedEducationDemoIncident(
            $alpha,
            $admin,
            $reviewer,
            Incident::PLATFORM_WHATSAPP,
            Incident::CONTENT_TYPE_MESSAGE,
            'education-demo-reporting-channel',
            'Member seeks guidance on reporting harmful content through the correct organization channel.',
            'reporting_safety',
        );

        $privacyIncident = $this->seedEducationDemoIncident(
            $alpha,
            $admin,
            $reviewer,
            Incident::PLATFORM_TELEGRAM,
            Incident::CONTENT_TYPE_MESSAGE,
            'education-demo-reporter-privacy',
            'Community members ask publicly who filed a safety report, creating pressure to disclose reporter identity.',
            'reporting_safety',
        );

        $lessons = [
            [
                'title' => 'Understanding Context Before Responding',
                'learning_objective' => 'Recognize how surrounding context can change interpretation before responding or reporting.',
                'sections' => [
                    ['heading' => 'Why context matters', 'body' => 'A message that looks harmful in isolation may read differently with surrounding conversation. Context does not excuse harm, but it changes what evidence is useful.'],
                    ['heading' => 'Recognizing repeated patterns', 'body' => 'Repeated targeting across messages is often more informative than a single cropped screenshot.'],
                    ['heading' => 'Avoiding premature conclusions', 'body' => 'Rushing to label a person can escalate conflict. Document carefully and seek appropriate guidance.'],
                    ['heading' => 'When to document', 'body' => 'Preserve surrounding messages, timing, and where the content appeared through approved channels.'],
                    ['heading' => 'When to seek help', 'body' => 'If you feel unsafe or unsure, contact your MSA Community Safety Reviewer or another trusted support channel.'],
                    ['heading' => 'Safe reporting practices', 'body' => 'Use approved reporting pathways. Avoid spreading harmful material more widely than necessary.'],
                ],
                'adapt_topic_id' => 'csafety-context',
                'pattern' => [
                    'source_incident' => $confirmedPackage,
                    'pattern_type' => 'contextual_hate',
                    'title' => 'Contextual Religious Targeting',
                    'summary' => 'A community member encounters language that appears more discriminatory when viewed alongside surrounding conversation and repeated replies.',
                    'learning_objective' => 'Identify when context changes the interpretation of seemingly isolated language and what evidence to preserve.',
                    'recommendation_reason' => 'This lesson teaches learners how surrounding context can change meaning and what to preserve before responding or reporting.',
                ],
                'scenarios' => [
                    [
                        'title' => 'Context preservation',
                        'prompt' => 'Demo / educational scenario: A message appears insulting, but the surrounding conversation changes its meaning. What should you do first?',
                        'context' => 'Sanitized educational scenario. Not based on exposing a real incident transcript.',
                        'options' => [
                            'Preserve the surrounding conversation context before deciding how to respond or report',
                            'Reply immediately to call out the author',
                            'Delete your own account so you do not see it again',
                            'Assume the isolated message proves intent and share it widely',
                        ],
                        'expected_reasoning_signals' => ['context', 'surrounding', 'preserve'],
                        'misconception_tags' => ['CSAFE-M001'],
                        'difficulty' => 2,
                        'adapt_challenge_id' => 'CSAFE-CTX-001',
                        'adapt_concept_id' => 'csafety_context_preservation',
                        'sort_order' => 1,
                    ],
                    [
                        'title' => 'Pattern recognition',
                        'prompt' => 'Demo / educational scenario: You encounter repeated comments targeting a religious identity. Which information is most useful to preserve?',
                        'context' => 'Demo / educational scenario focused on transferable evidence skills.',
                        'options' => [
                            'A sequence of related messages that shows the repeated pattern over time',
                            'Only the funniest reply in the thread',
                            'Your private opinion about the author\'s character',
                            'Unrelated posts from other groups',
                        ],
                        'expected_reasoning_signals' => ['repeated', 'pattern', 'sequence'],
                        'misconception_tags' => ['CSAFE-M002'],
                        'difficulty' => 2,
                        'adapt_challenge_id' => 'CSAFE-CTX-002',
                        'adapt_concept_id' => 'csafety_pattern_recognition',
                        'sort_order' => 2,
                    ],
                    [
                        'title' => 'Evidence quality',
                        'prompt' => 'Demo / educational scenario: A report contains an isolated screenshot but lacks context. What additional information would make the report more useful?',
                        'context' => 'Demo / educational scenario about evidence quality.',
                        'options' => [
                            'Surrounding messages, timing, and where the content appeared',
                            'A guess about the author\'s private beliefs',
                            'A demand that the platform ban everyone involved immediately',
                            'A rewritten version of the message in stronger language',
                        ],
                        'expected_reasoning_signals' => ['surrounding', 'timing', 'context'],
                        'misconception_tags' => ['CSAFE-M002'],
                        'difficulty' => 3,
                        'adapt_challenge_id' => 'CSAFE-CTX-003',
                        'adapt_concept_id' => 'csafety_evidence_quality',
                        'sort_order' => 3,
                    ],
                    [
                        'title' => 'Uncertainty',
                        'prompt' => 'Demo / educational scenario: You are unsure whether a comment is coded targeting or ordinary disagreement. What is the most careful next step?',
                        'context' => 'Demo / educational scenario about uncertainty.',
                        'options' => [
                            'Document what you see carefully and seek guidance without publicly escalating',
                            'Publicly accuse the person of hate based on one comment',
                            'Ignore everything and tell no one',
                            'Invent missing details so the report looks stronger',
                        ],
                        'expected_reasoning_signals' => ['uncertain', 'document', 'guidance'],
                        'misconception_tags' => ['CSAFE-M003'],
                        'difficulty' => 3,
                        'adapt_challenge_id' => 'CSAFE-CTX-004',
                        'adapt_concept_id' => 'csafety_uncertainty',
                        'sort_order' => 4,
                    ],
                    [
                        'title' => 'Safe reporting',
                        'prompt' => 'Demo / educational scenario: You want to report potentially harmful content. Which practice best supports safe reporting?',
                        'context' => 'Demo / educational scenario about safe reporting.',
                        'options' => [
                            'Preserve relevant context privately and use approved reporting channels',
                            'Repost the harmful content publicly so more people can see it',
                            'Confront the author with personal accusations in the same thread',
                            'Share reporter contact details in the group chat',
                        ],
                        'expected_reasoning_signals' => ['preserve', 'private', 'approved'],
                        'misconception_tags' => ['CSAFE-M001'],
                        'difficulty' => 3,
                        'adapt_challenge_id' => 'CSAFE-CTX-005',
                        'adapt_concept_id' => 'csafety_safe_reporting',
                        'sort_order' => 5,
                    ],
                ],
            ],
            [
                'title' => 'Recognizing Coded Language',
                'learning_objective' => 'Identify when ordinary-seeming language may carry targeted meaning in community contexts.',
                'sections' => [
                    ['heading' => 'What coded language is', 'body' => 'Some harmful messages use indirect references that look neutral to outsiders but signal hostility to insiders.'],
                    ['heading' => 'Dog whistles and inside jokes', 'body' => 'Memes and shared references can function as dog whistles when they repeatedly target a protected group.'],
                    ['heading' => 'Tone is not enough', 'body' => 'Polite or joking tone does not by itself prove a message is harmless. Look at content, pattern, and who is targeted.'],
                    ['heading' => 'Assessing coded comments', 'body' => 'Use community context, surrounding messages, and repetition—not the isolated line alone.'],
                ],
                'adapt_topic_id' => 'csafety-coded',
                'pattern' => [
                    'source_incident' => $xAppealIncident ?? $confirmedPackage,
                    'pattern_type' => 'coded_language',
                    'title' => 'Coded Language in Public Posts',
                    'summary' => 'A post uses phrasing that appears neutral on the surface but community members recognize as targeting a religious or ethnic group.',
                    'learning_objective' => 'Recognize when indirect language may carry coded meaning and what context helps reviewers assess it.',
                    'recommendation_reason' => 'This lesson helps learners spot coded targeting and avoid dismissing harmful language because it looks polite or humorous.',
                ],
                'scenarios' => [
                    [
                        'title' => 'Coded language recognition',
                        'prompt' => 'Demo / educational scenario: A comment uses an ordinary phrase that members of your community recognize as targeting a religious group. What is the best initial read?',
                        'context' => 'Sanitized educational scenario about indirect targeting.',
                        'options' => [
                            'The phrase may carry coded meaning even if it looks neutral to outsiders',
                            'If you do not understand it, it cannot be harmful',
                            'Any confusing message should be treated as a joke',
                            'Only explicit slurs count as harmful content',
                        ],
                        'expected_reasoning_signals' => ['coded', 'indirect', 'community'],
                        'misconception_tags' => ['CSAFE-M004'],
                        'difficulty' => 2,
                        'adapt_challenge_id' => 'CSAFE-COD-001',
                        'adapt_concept_id' => 'csafety_coded_recognition',
                        'sort_order' => 1,
                    ],
                    [
                        'title' => 'Dog whistles',
                        'prompt' => 'Demo / educational scenario: Someone posts a meme reference that insiders treat as an inside joke about a minority group. What should you prioritize?',
                        'context' => 'Demo / educational scenario about dog whistles.',
                        'options' => [
                            'How the reference is used in context and whether it signals hostility to a protected group',
                            'Whether the image made you laugh',
                            'Whether the author apologized after being asked',
                            'Whether the post got many likes',
                        ],
                        'expected_reasoning_signals' => ['dog whistle', 'inside joke', 'context'],
                        'misconception_tags' => ['CSAFE-M004'],
                        'difficulty' => 3,
                        'adapt_challenge_id' => 'CSAFE-COD-002',
                        'adapt_concept_id' => 'csafety_dog_whistles',
                        'sort_order' => 2,
                    ],
                    [
                        'title' => 'Neutral tone masking',
                        'prompt' => 'Demo / educational scenario: A student says, "They were just being polite, so it cannot be harassment." What is wrong with that reasoning?',
                        'context' => 'Demo / educational scenario about tone and impact.',
                        'options' => [
                            'Polite or joking tone does not rule out harmful intent or impact',
                            'Politeness always means respect',
                            'Jokes cannot target protected groups',
                            'Only angry messages can be reported',
                        ],
                        'expected_reasoning_signals' => ['tone', 'polite', 'impact'],
                        'misconception_tags' => ['CSAFE-M004'],
                        'difficulty' => 2,
                        'adapt_challenge_id' => 'CSAFE-COD-003',
                        'adapt_concept_id' => 'csafety_neutral_tone',
                        'sort_order' => 3,
                    ],
                    [
                        'title' => 'Assessing coded comments',
                        'prompt' => 'When reviewing a potentially coded comment, which combination of factors is most useful?',
                        'context' => 'Demo / educational scenario about assessment habits.',
                        'options' => [
                            'Community context, surrounding messages, and whether the same phrasing targets a group repeatedly',
                            'Only the dictionary definition of each word',
                            'Whether you personally find the comment offensive',
                            'How many followers the author has',
                        ],
                        'expected_reasoning_signals' => ['context', 'surrounding', 'repeated'],
                        'misconception_tags' => ['CSAFE-M002'],
                        'difficulty' => 3,
                        'adapt_challenge_id' => 'CSAFE-COD-004',
                        'adapt_concept_id' => 'csafety_coded_recognition',
                        'sort_order' => 4,
                    ],
                ],
            ],
            [
                'title' => 'Repeated Harassment Patterns',
                'learning_objective' => 'Distinguish isolated disagreement from sustained targeting across messages or spaces.',
                'sections' => [
                    ['heading' => 'Repeated targeting', 'body' => 'A series of comments aimed at the same identity or person is a stronger signal than one ambiguous post.'],
                    ['heading' => 'Escalation signs', 'body' => 'Harassment often intensifies from teasing to slurs to pile-on behavior across time.'],
                    ['heading' => 'Bystander responsibility', 'body' => 'Witnesses can document and report without publicly amplifying harm or demanding the target respond.'],
                    ['heading' => 'Evidence for reviewers', 'body' => 'Reviewers need ordered messages with authors and timing—not a single out-of-context line.'],
                ],
                'adapt_topic_id' => 'csafety-harassment',
                'pattern' => [
                    'source_incident' => $harassmentIncident,
                    'pattern_type' => 'repeated_harassment',
                    'title' => 'Repeated Identity-Based Targeting',
                    'summary' => 'Comments mocking a member\'s name and faith recur across several days in the same group, suggesting a pattern rather than a one-off disagreement.',
                    'learning_objective' => 'Recognize repeated targeting over time and preserve evidence that shows escalation.',
                    'recommendation_reason' => 'This lesson helps learners distinguish a single heated reply from a sustained harassment pattern.',
                ],
                'scenarios' => [
                    [
                        'title' => 'Repeated targeting',
                        'prompt' => 'Demo / educational scenario: One person receives several comments mocking their name and faith across two days in the same group. What pattern is most relevant?',
                        'context' => 'Sanitized educational scenario about repeated harassment.',
                        'options' => [
                            'Repeated comments aimed at the same person and identity over time',
                            'Whether the group usually has lively debates',
                            'Whether the target replied sarcastically once',
                            'How long the group chat has existed',
                        ],
                        'expected_reasoning_signals' => ['repeated', 'same person', 'over time'],
                        'misconception_tags' => ['CSAFE-M002'],
                        'difficulty' => 2,
                        'adapt_challenge_id' => 'CSAFE-HAR-001',
                        'adapt_concept_id' => 'csafety_repeated_targeting',
                        'sort_order' => 1,
                    ],
                    [
                        'title' => 'Escalation signs',
                        'prompt' => 'Demo / educational scenario: Comments begin as mild teasing, then move to slurs, then encourage others to pile on. What does this suggest?',
                        'context' => 'Demo / educational scenario about escalation.',
                        'options' => [
                            'The behavior may be escalating and warrants documentation and review',
                            'Escalation always means the target provoked it',
                            'Once teasing starts, no review is needed',
                            'Only the final slur matters; earlier messages can be ignored',
                        ],
                        'expected_reasoning_signals' => ['escalat', 'slur', 'pile on'],
                        'misconception_tags' => ['CSAFE-M001'],
                        'difficulty' => 3,
                        'adapt_challenge_id' => 'CSAFE-HAR-002',
                        'adapt_concept_id' => 'csafety_escalation_signs',
                        'sort_order' => 2,
                    ],
                    [
                        'title' => 'Bystander role',
                        'prompt' => 'Demo / educational scenario: You witness repeated targeting but are not the direct target. What is a constructive bystander action?',
                        'context' => 'Demo / educational scenario about bystander responsibility.',
                        'options' => [
                            'Document the pattern privately and use approved reporting channels',
                            'Join the thread to argue with the harasser for entertainment',
                            'Share screenshots in a public story to shame everyone involved',
                            'Message the target demanding they respond publicly',
                        ],
                        'expected_reasoning_signals' => ['bystander', 'document', 'report'],
                        'misconception_tags' => ['CSAFE-M001'],
                        'difficulty' => 2,
                        'adapt_challenge_id' => 'CSAFE-HAR-003',
                        'adapt_concept_id' => 'csafety_bystander_role',
                        'sort_order' => 3,
                    ],
                    [
                        'title' => 'Evidence package for review',
                        'prompt' => 'Demo / educational scenario: A moderator asks what to preserve from a harassment thread. Which package is most useful for human review?',
                        'context' => 'Demo / educational scenario about documentation for reviewers.',
                        'options' => [
                            'Ordered messages showing who said what, when, and how the tone changed',
                            'Only the target\'s emotional reaction',
                            'A summary written from memory a week later',
                            'Screenshots with usernames cropped out',
                        ],
                        'expected_reasoning_signals' => ['ordered', 'who', 'when'],
                        'misconception_tags' => ['CSAFE-M002'],
                        'difficulty' => 3,
                        'adapt_challenge_id' => 'CSAFE-HAR-004',
                        'adapt_concept_id' => 'csafety_repeated_targeting',
                        'sort_order' => 4,
                    ],
                ],
            ],
            [
                'title' => 'Safe Reporting & Escalation',
                'learning_objective' => 'Use approved channels and preserve useful context without spreading harm further.',
                'sections' => [
                    ['heading' => 'Approved channels', 'body' => 'Organizations provide designated safety or incident reporting paths. Use them instead of public call-outs.'],
                    ['heading' => 'Useful documentation', 'body' => 'Include links or screenshots with timestamps, location in the app, and surrounding context.'],
                    ['heading' => 'Urgent threats', 'body' => 'Immediate safety threats warrant urgent reporting while preserving what you safely can.'],
                    ['heading' => 'Avoid amplifying harm', 'body' => 'Reposting harmful content to raise awareness often spreads it further and can retraumatize targets.'],
                ],
                'adapt_topic_id' => 'csafety-reporting',
                'pattern' => [
                    'source_incident' => $reportingIncident,
                    'pattern_type' => 'reporting_safety',
                    'title' => 'Safe Reporting After Witnessing Harm',
                    'summary' => 'Members want to help after seeing harmful content but need guidance on using approved channels without spreading the material more widely.',
                    'learning_objective' => 'Choose appropriate reporting channels and include actionable documentation.',
                    'recommendation_reason' => 'This lesson teaches practical reporting habits that help reviewers act without amplifying harm.',
                ],
                'scenarios' => [
                    [
                        'title' => 'Approved reporting channels',
                        'prompt' => 'Demo / educational scenario: You notice harmful content in your organization\'s community space. Where should you report it first?',
                        'context' => 'Sanitized educational scenario about reporting pathways.',
                        'options' => [
                            'The organization\'s approved safety or incident reporting channel',
                            'A public post tagging every admin at once',
                            'A unrelated social media platform with no connection to the organization',
                            'A private group chat of friends to gossip about it',
                        ],
                        'expected_reasoning_signals' => ['approved', 'incident', 'channel'],
                        'misconception_tags' => ['CSAFE-M001'],
                        'difficulty' => 2,
                        'adapt_challenge_id' => 'CSAFE-REP-001',
                        'adapt_concept_id' => 'csafety_report_channels',
                        'sort_order' => 1,
                    ],
                    [
                        'title' => 'Documentation habits',
                        'prompt' => 'Demo / educational scenario: You are preparing a safety report. Which details help reviewers most?',
                        'context' => 'Demo / educational scenario about report quality.',
                        'options' => [
                            'Links or screenshots with timestamps, location in the app, and surrounding context',
                            'Your guess about what punishment the author deserves',
                            'A list of everyone you dislike in the community',
                            'A meme summarizing your frustration',
                        ],
                        'expected_reasoning_signals' => ['timestamp', 'location', 'context'],
                        'misconception_tags' => ['CSAFE-M002'],
                        'difficulty' => 2,
                        'adapt_challenge_id' => 'CSAFE-REP-002',
                        'adapt_concept_id' => 'csafety_documentation',
                        'sort_order' => 2,
                    ],
                    [
                        'title' => 'When to escalate urgently',
                        'prompt' => 'Demo / educational scenario: Content includes an immediate safety threat. What is the priority compared with ordinary harmful speech?',
                        'context' => 'Demo / educational scenario about urgent escalation.',
                        'options' => [
                            'Report immediately through urgent channels and preserve what you safely can',
                            'Wait until you collect ten similar examples',
                            'Debate the theology of the insult first',
                            'Only report if the target asks you to',
                        ],
                        'expected_reasoning_signals' => ['immediate', 'urgent', 'threat'],
                        'misconception_tags' => ['CSAFE-M001'],
                        'difficulty' => 3,
                        'adapt_challenge_id' => 'CSAFE-REP-003',
                        'adapt_concept_id' => 'csafety_escalation_timing',
                        'sort_order' => 3,
                    ],
                    [
                        'title' => 'Avoid amplifying harm',
                        'prompt' => 'Demo / educational scenario: Someone reposts harmful content to "raise awareness" in a large public channel. What is the main problem?',
                        'context' => 'Demo / educational scenario about public reposting.',
                        'options' => [
                            'It can spread the harmful content further and retraumatize targets',
                            'Public awareness always reduces harm',
                            'If the content is already online, sharing it again does not matter',
                            'Only the original author is responsible for copies',
                        ],
                        'expected_reasoning_signals' => ['spread', 'amplify', 'retraumat'],
                        'misconception_tags' => ['CSAFE-M005'],
                        'difficulty' => 3,
                        'adapt_challenge_id' => 'CSAFE-REP-004',
                        'adapt_concept_id' => 'csafety_safe_reporting',
                        'sort_order' => 4,
                    ],
                ],
            ],
            [
                'title' => 'Privacy & Boundaries in Safety Work',
                'learning_objective' => 'Protect reporter identity and avoid turning safety work into public spectacle.',
                'sections' => [
                    ['heading' => 'Reporter privacy', 'body' => 'Sharing who reported an incident can put people at risk and discourage future reports.'],
                    ['heading' => 'Need-to-know sharing', 'body' => 'Detailed evidence should reach designated reviewers and trusted staff—not the whole community chat.'],
                    ['heading' => 'Supporting friends privately', 'body' => 'Check in with someone who reported harassment without discussing their report in group spaces.'],
                ],
                'adapt_topic_id' => 'csafety-privacy',
                'pattern' => [
                    'source_incident' => $privacyIncident,
                    'pattern_type' => 'reporting_safety',
                    'title' => 'Protecting Reporter Privacy',
                    'summary' => 'After a safety report is filed, community curiosity can pressure members to disclose reporter identity in public channels.',
                    'learning_objective' => 'Protect reporter privacy and share incident details only with people who need to know.',
                    'recommendation_reason' => 'This lesson helps learners support safety work without exposing reporters to retaliation.',
                ],
                'scenarios' => [
                    [
                        'title' => 'Reporter privacy',
                        'prompt' => 'Demo / educational scenario: After a report is filed, a member asks who reported the incident in the public chat. What is the best response?',
                        'context' => 'Sanitized educational scenario about reporter confidentiality.',
                        'options' => [
                            'Do not share reporter identity; refer questions to designated staff through private channels',
                            'Name the reporter so the community can thank them',
                            'Hint strongly so people can guess who reported',
                            'Post the report text with the reporter\'s phone number',
                        ],
                        'expected_reasoning_signals' => ['reporter', 'privacy', 'private'],
                        'misconception_tags' => ['CSAFE-M005'],
                        'difficulty' => 2,
                        'adapt_challenge_id' => 'CSAFE-PRV-001',
                        'adapt_concept_id' => 'csafety_reporter_privacy',
                        'sort_order' => 1,
                    ],
                    [
                        'title' => 'Need-to-know sharing',
                        'prompt' => 'Who should typically receive detailed incident evidence during an active review?',
                        'context' => 'Demo / educational scenario about evidence boundaries.',
                        'options' => [
                            'Designated reviewers and staff with a need to know',
                            'Every member of the organization immediately',
                            'Anyone who asks in a public forum',
                            'External accounts with no role in the organization',
                        ],
                        'expected_reasoning_signals' => ['reviewer', 'need to know', 'staff'],
                        'misconception_tags' => ['CSAFE-M005'],
                        'difficulty' => 2,
                        'adapt_challenge_id' => 'CSAFE-PRV-002',
                        'adapt_concept_id' => 'csafety_need_to_know',
                        'sort_order' => 2,
                    ],
                    [
                        'title' => 'Supporting a friend privately',
                        'prompt' => 'Demo / educational scenario: You want to support a friend who reported harassment. What respects their privacy?',
                        'context' => 'Demo / educational scenario about private support.',
                        'options' => [
                            'Check in privately and avoid discussing their report in group chats',
                            'Announce in the group that they did the right thing by reporting',
                            'Forward their report to unrelated contacts for opinions',
                            'Ask them to repost the harmful content so others understand',
                        ],
                        'expected_reasoning_signals' => ['private', 'support', 'avoid'],
                        'misconception_tags' => ['CSAFE-M005'],
                        'difficulty' => 3,
                        'adapt_challenge_id' => 'CSAFE-PRV-003',
                        'adapt_concept_id' => 'csafety_reporter_privacy',
                        'sort_order' => 3,
                    ],
                ],
            ],
        ];

        foreach ($lessons as $lessonDefinition) {
            $this->seedAcademyLessonBundle(
                $alpha,
                $course,
                $admin,
                $reviewer,
                $lessonDefinition
            );
        }
    }

    /**
     * @param  array<string, mixed>  $definition
     */
    private function seedAcademyLessonBundle(
        Organization $alpha,
        Course $course,
        User $admin,
        User $reviewer,
        array $definition
    ): void {
        $lesson = AcademyLesson::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'course_id' => $course->id,
                'title' => $definition['title'],
            ],
            [
                'learning_objective' => $definition['learning_objective'],
                'category' => AcademyLesson::CATEGORY_COMMUNITY_SAFETY,
                'status' => AcademyLesson::STATUS_PUBLISHED,
                'is_demo' => true,
                'created_by' => $admin->id,
                'sections' => $definition['sections'],
            ]
        );

        foreach ($definition['scenarios'] as $scenario) {
            AcademyScenario::query()->firstOrCreate(
                [
                    'organization_id' => $alpha->id,
                    'academy_lesson_id' => $lesson->id,
                    'adapt_challenge_id' => $scenario['adapt_challenge_id'],
                ],
                array_merge($scenario, [
                    'adapt_topic_id' => $definition['adapt_topic_id'],
                    'adapt_domain' => 'community-safety',
                    'is_demo' => true,
                ])
            );
        }

        $patternDefinition = $definition['pattern'];
        /** @var Incident $sourceIncident */
        $sourceIncident = $patternDefinition['source_incident'];

        $pattern = LearningPattern::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'source_incident_id' => $sourceIncident->id,
            ],
            [
                'pattern_type' => $patternDefinition['pattern_type'],
                'title' => $patternDefinition['title'],
                'summary' => $patternDefinition['summary'],
                'learning_objective' => $patternDefinition['learning_objective'],
                'domain' => 'community-safety',
                'severity_context' => 'moderate',
                'status' => LearningPattern::STATUS_APPROVED,
                'created_by' => $reviewer->id,
                'approved_by' => $admin->id,
                'approved_at' => now()->subDay(),
            ]
        );

        LearningRecommendation::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'learning_pattern_id' => $pattern->id,
                'academy_lesson_id' => $lesson->id,
            ],
            [
                'academy_course_id' => $course->id,
                'reason' => $patternDefinition['recommendation_reason'],
                'status' => LearningRecommendation::STATUS_PUBLISHED,
                'created_by' => $admin->id,
            ]
        );
    }

    private function seedEducationDemoIncident(
        Organization $alpha,
        User $admin,
        User $reviewer,
        string $platform,
        string $contentType,
        string $descriptionKey,
        string $description,
        string $patternType,
    ): Incident {
        return Incident::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'reported_by' => $admin->id,
                'platform' => $platform,
                'description' => $descriptionKey,
            ],
            [
                'content_type' => $contentType,
                'visibility' => Incident::VISIBILITY_GROUP,
                'source_url' => null,
                'original_item_content' => 'Demo / educational scenario seed content. Not a live incident transcript.',
                'observed_at' => now()->subDays(2),
                'surrounding_context' => 'Sanitized educational abstraction for Academy demo content.',
                'language' => 'en',
                'reporter_notes' => 'Seeded for Community Safety Academy lesson: '.$patternType,
                'safety_classification' => Incident::CLASSIFICATION_HARASSMENT,
                'classified_by' => $reviewer->id,
                'classified_at' => now()->subDays(2),
                'status' => Incident::STATUS_RESOLVED,
                'review_outcome' => Incident::OUTCOME_CONFIRMED,
                'review_notes' => $description,
                'current_reviewer_id' => $reviewer->id,
                'review_started_at' => now()->subDays(2)->subHour(),
                'escalated' => false,
                'review_lock_version' => 1,
            ]
        );
    }

    /**
     * Phase 8 demo outcome tracking records — not real external platform reports.
     */
    private function seedOutcomeTracking(
        Organization $alpha,
        User $admin,
        User $member,
        User $reviewer,
        Incident $confirmedPackage,
        Incident $discordOpen
    ): void {
        // Demo A — Completed outcome (Reddit)
        if ($confirmedPackage->externalReports()->count() === 0) {
            $demoA = IncidentExternalReport::query()->create([
                'incident_id' => $confirmedPackage->id,
                'organization_id' => $alpha->id,
                'platform' => Incident::PLATFORM_REDDIT,
                'reporting_channel' => 'In-app report',
                'external_reference' => 'RDT-4821',
                'reported_at' => now()->subDays(3),
                'status' => IncidentExternalReport::STATUS_OUTCOME,
                'decision' => IncidentExternalReport::DECISION_ACTION_TAKEN,
                'decision_note' => 'Platform response indicated action on the reported content.',
                'outcome' => IncidentExternalReport::OUTCOME_CONTENT_REMOVED,
                'outcome_source' => IncidentExternalReport::SOURCE_PLATFORM_RESPONSE,
                'outcome_summary' => 'Reported content was removed according to information received from the platform.',
                'reporter_visible_summary' => 'The reported content was removed.',
                'verification_status' => IncidentExternalReport::VERIFICATION_VERIFIED_BY_REVIEWER,
                'internal_notes' => 'Demo seed — reviewer recorded platform response.',
                'created_by' => $reviewer->id,
                'updated_by' => $reviewer->id,
            ]);

            $demoA->statusHistory()->createMany([
                [
                    'previous_status' => null,
                    'new_status' => IncidentExternalReport::STATUS_REPORTED,
                    'changed_by' => $reviewer->id,
                    'note' => 'External report recorded.',
                    'changed_at' => now()->subDays(3),
                ],
                [
                    'previous_status' => IncidentExternalReport::STATUS_REPORTED,
                    'new_status' => IncidentExternalReport::STATUS_UNDER_REVIEW,
                    'changed_by' => $reviewer->id,
                    'note' => 'Platform acknowledged receipt.',
                    'changed_at' => now()->subDays(2),
                ],
                [
                    'previous_status' => IncidentExternalReport::STATUS_UNDER_REVIEW,
                    'new_status' => IncidentExternalReport::STATUS_DECISION,
                    'decision' => IncidentExternalReport::DECISION_ACTION_TAKEN,
                    'changed_by' => $reviewer->id,
                    'note' => 'Decision recorded: action taken.',
                    'changed_at' => now()->subDays(1)->subHours(12),
                ],
                [
                    'previous_status' => IncidentExternalReport::STATUS_DECISION,
                    'new_status' => IncidentExternalReport::STATUS_OUTCOME,
                    'decision' => IncidentExternalReport::DECISION_ACTION_TAKEN,
                    'outcome' => IncidentExternalReport::OUTCOME_CONTENT_REMOVED,
                    'changed_by' => $reviewer->id,
                    'note' => 'Outcome recorded: content removed.',
                    'changed_at' => now()->subDays(1),
                ],
            ]);
        }

        // Demo B — Under review (Discord)
        if ($discordOpen->externalReports()->count() === 0) {
            $demoB = IncidentExternalReport::query()->create([
                'incident_id' => $discordOpen->id,
                'organization_id' => $alpha->id,
                'platform' => Incident::PLATFORM_DISCORD,
                'reporting_channel' => 'Trust & Safety report',
                'external_reference' => 'DSC-9912',
                'reported_at' => now()->subDays(2),
                'status' => IncidentExternalReport::STATUS_UNDER_REVIEW,
                'verification_status' => IncidentExternalReport::VERIFICATION_UNVERIFIED,
                'reporter_visible_summary' => 'Your report was recorded and is being reviewed.',
                'created_by' => $reviewer->id,
                'updated_by' => $reviewer->id,
            ]);

            $demoB->statusHistory()->createMany([
                [
                    'previous_status' => null,
                    'new_status' => IncidentExternalReport::STATUS_REPORTED,
                    'changed_by' => $reviewer->id,
                    'note' => 'External report recorded.',
                    'changed_at' => now()->subDays(2),
                ],
                [
                    'previous_status' => IncidentExternalReport::STATUS_REPORTED,
                    'new_status' => IncidentExternalReport::STATUS_UNDER_REVIEW,
                    'changed_by' => $reviewer->id,
                    'note' => 'External destination acknowledged the report.',
                    'changed_at' => now()->subDay(),
                ],
            ]);
        }

        // Demo C — No action + appeal (X) — member-reported
        $xAppealIncident = Incident::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'reported_by' => $member->id,
                'platform' => Incident::PLATFORM_X,
                'source_url' => 'https://x.com/example/status/alpha-appeal-demo',
            ],
            [
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Phase 8 demo — X post with no action outcome and appeal submitted.',
                'original_item_content' => 'Demo hostile post for outcome tracking appeal workflow.',
                'status' => Incident::STATUS_RESOLVED,
                'review_outcome' => Incident::OUTCOME_CONFIRMED,
                'safety_classification' => Incident::CLASSIFICATION_HARASSMENT,
                'review_notes' => 'Demo seed for Phase 8 appeal workflow.',
            ]
        );

        if ($xAppealIncident->externalReports()->count() === 0) {
            $demoC = IncidentExternalReport::query()->create([
                'incident_id' => $xAppealIncident->id,
                'organization_id' => $alpha->id,
                'platform' => Incident::PLATFORM_X,
                'reporting_channel' => 'In-app report',
                'external_reference' => 'X-7731',
                'reported_at' => now()->subDays(4),
                'status' => IncidentExternalReport::STATUS_OUTCOME,
                'decision' => IncidentExternalReport::DECISION_NO_ACTION,
                'decision_note' => 'Platform indicated no action would be taken.',
                'outcome' => IncidentExternalReport::OUTCOME_NO_ACTION,
                'outcome_source' => IncidentExternalReport::SOURCE_PLATFORM_RESPONSE,
                'outcome_summary' => 'No action recorded per platform response.',
                'reporter_visible_summary' => 'No action was recorded for this report.',
                'verification_status' => IncidentExternalReport::VERIFICATION_UNVERIFIED,
                'created_by' => $reviewer->id,
                'updated_by' => $reviewer->id,
            ]);

            $demoC->statusHistory()->createMany([
                [
                    'previous_status' => null,
                    'new_status' => IncidentExternalReport::STATUS_REPORTED,
                    'changed_by' => $reviewer->id,
                    'note' => 'External report recorded.',
                    'changed_at' => now()->subDays(4),
                ],
                [
                    'previous_status' => IncidentExternalReport::STATUS_REPORTED,
                    'new_status' => IncidentExternalReport::STATUS_DECISION,
                    'decision' => IncidentExternalReport::DECISION_NO_ACTION,
                    'changed_by' => $reviewer->id,
                    'note' => 'Decision recorded: no action.',
                    'changed_at' => now()->subDays(3),
                ],
                [
                    'previous_status' => IncidentExternalReport::STATUS_DECISION,
                    'new_status' => IncidentExternalReport::STATUS_OUTCOME,
                    'decision' => IncidentExternalReport::DECISION_NO_ACTION,
                    'outcome' => IncidentExternalReport::OUTCOME_NO_ACTION,
                    'changed_by' => $reviewer->id,
                    'note' => 'Outcome recorded: no action.',
                    'changed_at' => now()->subDays(2),
                ],
            ]);

            IncidentReportAppeal::query()->create([
                'incident_external_report_id' => $demoC->id,
                'submitted_at' => now()->subDay(),
                'submitted_by' => $member->id,
                'reason' => 'Additional contextual evidence was not considered.',
                'status' => IncidentReportAppeal::STATUS_UNDER_REVIEW,
            ]);
        }

        // Demo D — Unverified reporter observation (Other)
        $otherObservationIncident = Incident::query()->firstOrCreate(
            [
                'organization_id' => $alpha->id,
                'reported_by' => $member->id,
                'platform' => Incident::PLATFORM_OTHER,
                'source_url' => 'https://example.org/campus-board/demo-post',
            ],
            [
                'content_type' => Incident::CONTENT_TYPE_POST,
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'description' => 'Phase 8 demo — unverified reporter observation outcome.',
                'original_item_content' => 'Demo post that appears unavailable to the reporter.',
                'status' => Incident::STATUS_RESOLVED,
                'review_outcome' => Incident::OUTCOME_CONFIRMED,
            ]
        );

        if ($otherObservationIncident->externalReports()->count() === 0) {
            $demoD = IncidentExternalReport::query()->create([
                'incident_id' => $otherObservationIncident->id,
                'organization_id' => $alpha->id,
                'platform' => Incident::PLATFORM_OTHER,
                'reporting_channel' => 'Organization safety office',
                'reported_at' => now()->subDays(5),
                'status' => IncidentExternalReport::STATUS_OUTCOME,
                'decision' => IncidentExternalReport::DECISION_ACTION_TAKEN,
                'outcome' => IncidentExternalReport::OUTCOME_OTHER,
                'outcome_source' => IncidentExternalReport::SOURCE_REPORTER_OBSERVATION,
                'outcome_summary' => 'Content appears unavailable — reporter observation, not independently verified.',
                'reporter_visible_summary' => 'Content appears unavailable when you check the link.',
                'verification_status' => IncidentExternalReport::VERIFICATION_UNVERIFIED,
                'created_by' => $reviewer->id,
                'updated_by' => $reviewer->id,
            ]);

            IncidentExternalReportStatusHistory::query()->create([
                'incident_external_report_id' => $demoD->id,
                'previous_status' => null,
                'new_status' => IncidentExternalReport::STATUS_OUTCOME,
                'decision' => IncidentExternalReport::DECISION_ACTION_TAKEN,
                'outcome' => IncidentExternalReport::OUTCOME_OTHER,
                'changed_by' => $reviewer->id,
                'note' => 'Outcome recorded from reporter observation.',
                'changed_at' => now()->subDays(3),
            ]);
        }
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

        $betaSafetyCourse = Course::query()->firstOrCreate(
            [
                'organization_id' => $beta->id,
                'title' => 'Beta Community Safety',
            ],
            [
                'description' => 'Beta-only community safety education. Alpha members must never see this.',
                'status' => Course::STATUS_PUBLISHED,
                'created_by' => $admin->id,
            ]
        );

        AcademyLesson::query()->firstOrCreate(
            [
                'organization_id' => $beta->id,
                'course_id' => $betaSafetyCourse->id,
                'title' => 'Beta Safe Documentation Basics',
            ],
            [
                'learning_objective' => 'Practice documenting potentially harmful content without escalating publicly.',
                'category' => AcademyLesson::CATEGORY_COMMUNITY_SAFETY,
                'status' => AcademyLesson::STATUS_PUBLISHED,
                'is_demo' => true,
                'created_by' => $admin->id,
                'sections' => [
                    ['heading' => 'Document carefully', 'body' => 'Demo / educational scenario guidance for Beta members only.'],
                ],
            ]
        );

        $betaFlagship = Incident::query()->firstOrCreate(
            [
                'organization_id' => $beta->id,
                'reported_by' => $multiUser->id,
                'platform' => Incident::PLATFORM_DISCORD,
                'content_type' => Incident::CONTENT_TYPE_MESSAGE,
            ],
            [
                'visibility' => Incident::VISIBILITY_GROUP,
                'source_url' => null,
                'description' => 'Beta Community Shield report about hostile messages in a community Discord server, submitted by the multi-organization user while operating inside Beta.',
                'original_item_title' => 'Server #general exchange',
                'original_item_content' => 'لا أحد يريدكم هنا. اخرجوا من الحرم الجامعي.',
                'original_item_author' => 'beta_guest_demo',
                'original_item_posted_at' => now()->subDays(1)->setTime(19, 40),
                'observed_at' => now()->subHours(10),
                'surrounding_context' => 'The message followed a longer argument about student clubs. Several members replied before moderators muted the channel.',
                'language' => 'ar',
                'reporter_notes' => 'I can translate if needed. The account is new and has no public profile link.',
                'safety_classification' => Incident::CLASSIFICATION_UNCLASSIFIED,
                'status' => Incident::STATUS_OPEN,
            ]
        );

        if ($betaFlagship->replies()->count() === 0) {
            $betaFlagship->replies()->create([
                'author' => 'mod_helper_demo',
                'content' => 'Please stop. This is not allowed in this server.',
                'posted_at' => now()->subDays(1)->setTime(19, 55),
                'position' => 0,
            ]);
        }

        if ($betaFlagship->relatedItems()->count() === 0) {
            $betaFlagship->relatedItems()->createMany([
                [
                    'platform' => Incident::PLATFORM_TELEGRAM,
                    'content_type' => Incident::CONTENT_TYPE_MESSAGE,
                    'reference_url' => null,
                    'description' => 'Similar Arabic phrasing appeared in a Telegram campus chat the next morning.',
                    'observed_at' => now()->subHours(8),
                ],
                [
                    'platform' => Incident::PLATFORM_TIKTOK,
                    'content_type' => Incident::CONTENT_TYPE_VIDEO,
                    'reference_url' => 'https://tiktok.com/@example/video/beta-related-copy',
                    'description' => 'Short video repeating the same talking points with overlay text.',
                    'observed_at' => now()->subHours(5),
                ],
            ]);
        }

        Incident::query()->firstOrCreate(
            [
                'organization_id' => $beta->id,
                'reported_by' => $admin->id,
                'platform' => Incident::PLATFORM_WHATSAPP,
                'content_type' => Incident::CONTENT_TYPE_MESSAGE,
            ],
            [
                'visibility' => Incident::VISIBILITY_PRIVATE,
                'source_url' => null,
                'description' => 'Private WhatsApp message reported to Demo MSA Beta. Only necessary context was included.',
                'original_item_content' => 'I know where your meetings are. Watch yourself.',
                'original_item_author' => 'Unknown contact',
                'observed_at' => now()->subHours(4),
                'surrounding_context' => 'Received as a direct message after a public campus event flyer was shared in another chat.',
                'language' => 'en',
                'reporter_notes' => 'No phone number or contact details included beyond what is needed for review.',
                'safety_classification' => Incident::CLASSIFICATION_THREAT,
                'classified_by' => $admin->id,
                'classified_at' => now()->subHour(),
                'status' => Incident::STATUS_REVIEWING,
            ]
        );

        Incident::query()->firstOrCreate(
            [
                'organization_id' => $beta->id,
                'reported_by' => $multiUser->id,
                'platform' => Incident::PLATFORM_YOUTUBE,
                'content_type' => Incident::CONTENT_TYPE_COMMENT,
            ],
            [
                'visibility' => Incident::VISIBILITY_PUBLIC,
                'source_url' => 'https://youtube.com/watch?v=beta-demo-comment',
                'description' => 'Resolved Beta demo YouTube comment that was reviewed by organization admins.',
                'language' => 'en',
                'safety_classification' => Incident::CLASSIFICATION_HARASSMENT,
                'classified_by' => $admin->id,
                'classified_at' => now()->subDays(3),
                'status' => Incident::STATUS_RESOLVED,
            ]
        );
    }

    /**
     * @param  array<string, mixed>  $analysis
     */
    private function seedCompletedAnalysis(Incident $incident, User $requester, array $analysis): void
    {
        if ($incident->aiAnalyses()->exists()) {
            return;
        }

        $incident->aiAnalyses()->create([
            'provider' => 'fake',
            'model' => 'fake-model',
            'prompt_version' => CommunityShieldContextAnalysisV1::VERSION,
            'status' => IncidentAiAnalysis::STATUS_COMPLETED,
            'analysis' => $analysis,
            'error_message' => null,
            'requested_by' => $requester->id,
        ]);
    }
}
