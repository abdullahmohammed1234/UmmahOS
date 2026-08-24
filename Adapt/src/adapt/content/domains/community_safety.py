"""Community Safety catalog for UmmahOS Academy + ADAPT integration.

Educational scenarios are sanitized abstractions aligned with Community Shield
learning patterns. They do not reproduce raw incident content.
"""

from __future__ import annotations

from adapt.content.models import CatalogChallenge, ConceptSpec, TopicSpec, ch

SUBJECT_ID = "community-safety"

TOPICS = (
    TopicSpec(
        "csafety-context",
        SUBJECT_ID,
        "Understanding Context Before Responding",
        "Recognize how surrounding context changes interpretation and when to preserve evidence safely.",
        (
            "csafety_context_preservation",
            "csafety_pattern_recognition",
            "csafety_safe_reporting",
            "csafety_evidence_quality",
            "csafety_uncertainty",
        ),
        "CSAFE-CTX-001",
    ),
    TopicSpec(
        "csafety-coded",
        SUBJECT_ID,
        "Recognizing Coded Language",
        "Identify when ordinary-seeming language may carry targeted meaning in community contexts.",
        (
            "csafety_coded_recognition",
            "csafety_dog_whistles",
            "csafety_neutral_tone",
        ),
        "CSAFE-COD-001",
    ),
    TopicSpec(
        "csafety-harassment",
        SUBJECT_ID,
        "Repeated Harassment Patterns",
        "Distinguish isolated disagreement from sustained targeting across messages or spaces.",
        (
            "csafety_repeated_targeting",
            "csafety_escalation_signs",
            "csafety_bystander_role",
        ),
        "CSAFE-HAR-001",
    ),
    TopicSpec(
        "csafety-reporting",
        SUBJECT_ID,
        "Safe Reporting & Escalation",
        "Use approved channels and preserve useful context without spreading harm further.",
        (
            "csafety_report_channels",
            "csafety_escalation_timing",
            "csafety_documentation",
        ),
        "CSAFE-REP-001",
    ),
    TopicSpec(
        "csafety-privacy",
        SUBJECT_ID,
        "Privacy & Boundaries in Safety Work",
        "Protect reporter identity and avoid turning safety work into public spectacle.",
        (
            "csafety_reporter_privacy",
            "csafety_need_to_know",
        ),
        "CSAFE-PRV-001",
    ),
)

CONCEPTS = (
    ConceptSpec(
        "csafety_context_preservation",
        "csafety-context",
        SUBJECT_ID,
        "Context preservation",
        "Surrounding conversation can change how a message should be interpreted.",
        "BEGINNER",
    ),
    ConceptSpec(
        "csafety_pattern_recognition",
        "csafety-context",
        SUBJECT_ID,
        "Pattern recognition",
        "Repeated targeting across messages can be more informative than a single screenshot.",
        "BEGINNER",
    ),
    ConceptSpec(
        "csafety_safe_reporting",
        "csafety-context",
        SUBJECT_ID,
        "Safe reporting",
        "Preserve useful context and avoid escalating harm while seeking help.",
        "INTERMEDIATE",
    ),
    ConceptSpec(
        "csafety_evidence_quality",
        "csafety-context",
        SUBJECT_ID,
        "Evidence quality",
        "Useful reports include surrounding context, not only an isolated clip.",
        "INTERMEDIATE",
    ),
    ConceptSpec(
        "csafety_uncertainty",
        "csafety-context",
        SUBJECT_ID,
        "Uncertainty",
        "It is often better to document carefully than to rush to a conclusion.",
        "BEGINNER",
    ),
    ConceptSpec(
        "csafety_coded_recognition",
        "csafety-coded",
        SUBJECT_ID,
        "Coded language recognition",
        "Some harmful messages use indirect references that look neutral on their own.",
        "INTERMEDIATE",
    ),
    ConceptSpec(
        "csafety_dog_whistles",
        "csafety-coded",
        SUBJECT_ID,
        "Dog whistles",
        "Phrases may signal hostility to some audiences while appearing innocuous to others.",
        "INTERMEDIATE",
    ),
    ConceptSpec(
        "csafety_neutral_tone",
        "csafety-coded",
        SUBJECT_ID,
        "Neutral tone masking",
        "Polite or joking tone does not by itself prove a message is harmless.",
        "BEGINNER",
    ),
    ConceptSpec(
        "csafety_repeated_targeting",
        "csafety-harassment",
        SUBJECT_ID,
        "Repeated targeting",
        "A series of comments aimed at the same identity or person is a stronger signal than one post.",
        "BEGINNER",
    ),
    ConceptSpec(
        "csafety_escalation_signs",
        "csafety-harassment",
        SUBJECT_ID,
        "Escalation signs",
        "Harassment often intensifies across messages, spaces, or time.",
        "INTERMEDIATE",
    ),
    ConceptSpec(
        "csafety_bystander_role",
        "csafety-harassment",
        SUBJECT_ID,
        "Bystander responsibility",
        "Witnesses can document and report without publicly amplifying harm.",
        "INTERMEDIATE",
    ),
    ConceptSpec(
        "csafety_report_channels",
        "csafety-reporting",
        SUBJECT_ID,
        "Approved reporting channels",
        "Organizations provide specific paths for safety concerns; use them instead of public call-outs.",
        "BEGINNER",
    ),
    ConceptSpec(
        "csafety_escalation_timing",
        "csafety-reporting",
        SUBJECT_ID,
        "When to escalate",
        "Some situations need immediate review; others benefit from careful documentation first.",
        "INTERMEDIATE",
    ),
    ConceptSpec(
        "csafety_documentation",
        "csafety-reporting",
        SUBJECT_ID,
        "Documentation habits",
        "Timestamps, links, and surrounding messages make reports actionable for reviewers.",
        "BEGINNER",
    ),
    ConceptSpec(
        "csafety_reporter_privacy",
        "csafety-privacy",
        SUBJECT_ID,
        "Reporter privacy",
        "Sharing who reported an incident can put people at risk and discourage future reports.",
        "BEGINNER",
    ),
    ConceptSpec(
        "csafety_need_to_know",
        "csafety-privacy",
        SUBJECT_ID,
        "Need-to-know sharing",
        "Safety details should reach reviewers and trusted staff—not the whole community chat.",
        "INTERMEDIATE",
    ),
)

PREMATURE = (("CSAFE-M001", ("react immediately", "reply angrily", "call them out publicly", "ignore context")),)
ISOLATED = (("CSAFE-M002", ("one screenshot is enough", "ignore surrounding posts", "no need for context")),)
LABEL = (("CSAFE-M003", ("they are hateful", "label the person", "decide intent alone")),)
CODED = (("CSAFE-M004", ("looks fine to me", "just a joke", "no hidden meaning")),)
PUBLIC = (("CSAFE-M005", ("post it everywhere", "name the reporter", "share in group chat")),)

CHALLENGES: tuple[CatalogChallenge, ...] = (
    ch(
        "CSAFE-CTX-001",
        SUBJECT_ID,
        "csafety-context",
        "csafety_context_preservation",
        2,
        "SCENARIO",
        (
            "Demo / educational scenario: A message appears insulting on its own, but the surrounding "
            "conversation changes its meaning. What should you do first?"
        ),
        "Preserve the surrounding conversation context before deciding how to respond or report",
        (
            "Context can change interpretation. Preserve surrounding messages before concluding "
            "or responding publicly."
        ),
        choices=(
            "Preserve the surrounding conversation context before deciding how to respond or report",
            "Reply immediately to call out the author",
            "Delete your own account so you do not see it again",
            "Assume the isolated message proves intent and share it widely",
        ),
        cues=("context", "surrounding", "preserve", "before"),
        misconceptions=PREMATURE,
        target="CSAFE-M001",
        family="CSAFE-CTX",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "MAINTAIN", "DIAGNOSE"),
    ),
    ch(
        "CSAFE-CTX-002",
        SUBJECT_ID,
        "csafety-context",
        "csafety_pattern_recognition",
        2,
        "SCENARIO",
        (
            "Demo / educational scenario: You encounter repeated comments targeting a religious identity "
            "across a thread. Which information is most useful to preserve?"
        ),
        "A sequence of related messages that shows the repeated pattern over time",
        (
            "A repeated pattern is often clearer than one isolated comment. Preserve a sequence that "
            "shows how the targeting continues."
        ),
        choices=(
            "A sequence of related messages that shows the repeated pattern over time",
            "Only the funniest reply in the thread",
            "Your private opinion about the author's character",
            "Unrelated posts from other groups",
        ),
        cues=("repeated", "pattern", "sequence", "preserve"),
        misconceptions=ISOLATED,
        target="CSAFE-M002",
        family="CSAFE-CTX",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "MAINTAIN", "DIAGNOSE"),
    ),
    ch(
        "CSAFE-CTX-003",
        SUBJECT_ID,
        "csafety-context",
        "csafety_evidence_quality",
        3,
        "SCENARIO",
        (
            "Demo / educational scenario: A report contains an isolated screenshot but lacks context. "
            "What additional information would make the report more useful?"
        ),
        "Surrounding messages, timing, and where the content appeared",
        (
            "Useful reports include surrounding messages, approximate timing, and the place the "
            "content appeared—not only one cropped screenshot."
        ),
        choices=(
            "Surrounding messages, timing, and where the content appeared",
            "A guess about the author's private beliefs",
            "A demand that the platform ban everyone involved immediately",
            "A rewritten version of the message in stronger language",
        ),
        cues=("surrounding", "timing", "location", "context"),
        misconceptions=ISOLATED,
        target="CSAFE-M002",
        family="CSAFE-CTX",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "MAINTAIN", "REMEDIATE"),
    ),
    ch(
        "CSAFE-CTX-004",
        SUBJECT_ID,
        "csafety-context",
        "csafety_uncertainty",
        3,
        "SCENARIO",
        (
            "Demo / educational scenario: You are unsure whether a comment is coded targeting or "
            "ordinary disagreement. What is the most careful next step?"
        ),
        "Document what you see carefully and seek guidance without publicly escalating",
        (
            "Uncertainty is common. Document carefully and seek appropriate guidance rather than "
            "rushing to label someone or escalate publicly."
        ),
        choices=(
            "Document what you see carefully and seek guidance without publicly escalating",
            "Publicly accuse the person of hate based on one comment",
            "Ignore everything and tell no one",
            "Invent missing details so the report looks stronger",
        ),
        cues=("uncertain", "document", "guidance", "careful"),
        misconceptions=LABEL,
        target="CSAFE-M003",
        family="CSAFE-CTX",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("DIAGNOSE", "REMEDIATE", "MAINTAIN"),
    ),
    ch(
        "CSAFE-CTX-005",
        SUBJECT_ID,
        "csafety-context",
        "csafety_safe_reporting",
        3,
        "SCENARIO",
        (
            "Demo / educational scenario: You want to report potentially harmful content. Which "
            "practice best supports safe reporting?"
        ),
        "Preserve relevant context privately and use approved reporting channels",
        (
            "Safe reporting preserves relevant context through approved channels without spreading "
            "harmful material more widely than necessary."
        ),
        choices=(
            "Preserve relevant context privately and use approved reporting channels",
            "Repost the harmful content publicly so more people can see it",
            "Confront the author with personal accusations in the same thread",
            "Share reporter contact details in the group chat",
        ),
        cues=("preserve", "private", "approved", "channels"),
        misconceptions=PREMATURE,
        target="CSAFE-M001",
        family="CSAFE-CTX",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "MAINTAIN"),
    ),
    ch(
        "CSAFE-COD-001",
        SUBJECT_ID,
        "csafety-coded",
        "csafety_coded_recognition",
        2,
        "SCENARIO",
        (
            "Demo / educational scenario: A comment uses an ordinary phrase that members of your "
            "community recognize as targeting a religious group. What is the best initial read?"
        ),
        "The phrase may carry coded meaning even if it looks neutral to outsiders",
        (
            "Coded language can appear harmless on the surface. Community context matters when "
            "interpreting indirect targeting."
        ),
        choices=(
            "The phrase may carry coded meaning even if it looks neutral to outsiders",
            "If you do not understand it, it cannot be harmful",
            "Any confusing message should be treated as a joke",
            "Only explicit slurs count as harmful content",
        ),
        cues=("coded", "indirect", "community", "context"),
        misconceptions=CODED,
        target="CSAFE-M004",
        family="CSAFE-COD",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "DIAGNOSE", "MAINTAIN"),
    ),
    ch(
        "CSAFE-COD-002",
        SUBJECT_ID,
        "csafety-coded",
        "csafety_dog_whistles",
        3,
        "SCENARIO",
        (
            "Demo / educational scenario: Someone posts a meme reference that insiders treat as an "
            "inside joke about a minority group. What should you prioritize?"
        ),
        "How the reference is used in context and whether it signals hostility to a protected group",
        (
            "Dog whistles rely on shared knowledge. Review context and pattern rather than assuming "
            "a harmless meme."
        ),
        choices=(
            "How the reference is used in context and whether it signals hostility to a protected group",
            "Whether the image made you laugh",
            "Whether the author apologized after being asked",
            "Whether the post got many likes",
        ),
        cues=("dog whistle", "inside joke", "context", "pattern"),
        misconceptions=CODED,
        target="CSAFE-M004",
        family="CSAFE-COD",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("DIAGNOSE", "INCREASE", "MAINTAIN"),
    ),
    ch(
        "CSAFE-COD-003",
        SUBJECT_ID,
        "csafety-coded",
        "csafety_neutral_tone",
        2,
        "ERROR_ANALYSIS",
        (
            "Demo / educational scenario: A student says, 'They were just being polite, so it cannot "
            "be harassment.' What is wrong with that reasoning?"
        ),
        "Polite or joking tone does not rule out harmful intent or impact",
        (
            "Tone alone is not proof of harmlessness. Look at content, pattern, and who is targeted."
        ),
        choices=(
            "Polite or joking tone does not rule out harmful intent or impact",
            "Politeness always means respect",
            "Jokes cannot target protected groups",
            "Only angry messages can be reported",
        ),
        cues=("tone", "polite", "joke", "impact"),
        misconceptions=CODED,
        target="CSAFE-M004",
        family="CSAFE-COD",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("REMEDIATE", "DIAGNOSE"),
    ),
    ch(
        "CSAFE-COD-004",
        SUBJECT_ID,
        "csafety-coded",
        "csafety_coded_recognition",
        3,
        "CONCEPT_CHECK",
        (
            "When reviewing a potentially coded comment, which combination of factors is most useful?"
        ),
        "Community context, surrounding messages, and whether the same phrasing targets a group repeatedly",
        (
            "Coded language is best assessed with context, surrounding messages, and repetition—not "
            "the isolated line alone."
        ),
        choices=(
            "Community context, surrounding messages, and whether the same phrasing targets a group repeatedly",
            "Only the dictionary definition of each word",
            "Whether you personally find the comment offensive",
            "How many followers the author has",
        ),
        cues=("context", "surrounding", "repeated", "assess"),
        misconceptions=ISOLATED,
        target="CSAFE-M002",
        family="CSAFE-COD",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "MAINTAIN"),
    ),
    ch(
        "CSAFE-HAR-001",
        SUBJECT_ID,
        "csafety-harassment",
        "csafety_repeated_targeting",
        2,
        "SCENARIO",
        (
            "Demo / educational scenario: One person receives several comments mocking their name and "
            "faith across two days in the same group. What pattern is most relevant?"
        ),
        "Repeated comments aimed at the same person and identity over time",
        (
            "Repeated targeting across time is a stronger harassment signal than a single ambiguous reply."
        ),
        choices=(
            "Repeated comments aimed at the same person and identity over time",
            "Whether the group usually has lively debates",
            "Whether the target replied sarcastically once",
            "How long the group chat has existed",
        ),
        cues=("repeated", "same person", "over time", "pattern"),
        misconceptions=ISOLATED,
        target="CSAFE-M002",
        family="CSAFE-HAR",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "DIAGNOSE", "MAINTAIN"),
    ),
    ch(
        "CSAFE-HAR-002",
        SUBJECT_ID,
        "csafety-harassment",
        "csafety_escalation_signs",
        3,
        "SCENARIO",
        (
            "Demo / educational scenario: Comments begin as mild teasing, then move to slurs, then "
            "encourage others to pile on. What does this suggest?"
        ),
        "The behavior may be escalating and warrants documentation and review",
        (
            "Escalation from teasing to slurs and pile-on behavior is a warning sign that should be "
            "documented and reviewed."
        ),
        choices=(
            "The behavior may be escalating and warrants documentation and review",
            "Escalation always means the target provoked it",
            "Once teasing starts, no review is needed",
            "Only the final slur matters; earlier messages can be ignored",
        ),
        cues=("escalat", "slur", "pile on", "document"),
        misconceptions=PREMATURE,
        target="CSAFE-M001",
        family="CSAFE-HAR",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "REMEDIATE", "DIAGNOSE"),
    ),
    ch(
        "CSAFE-HAR-003",
        SUBJECT_ID,
        "csafety-harassment",
        "csafety_bystander_role",
        2,
        "SCENARIO",
        (
            "Demo / educational scenario: You witness repeated targeting but are not the direct target. "
            "What is a constructive bystander action?"
        ),
        "Document the pattern privately and use approved reporting channels",
        (
            "Bystanders can help by preserving evidence and reporting through proper channels without "
            "publicly amplifying the harm."
        ),
        choices=(
            "Document the pattern privately and use approved reporting channels",
            "Join the thread to argue with the harasser for entertainment",
            "Share screenshots in a public story to shame everyone involved",
            "Message the target demanding they respond publicly",
        ),
        cues=("bystander", "document", "report", "private"),
        misconceptions=PREMATURE,
        target="CSAFE-M001",
        family="CSAFE-HAR",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "MAINTAIN"),
    ),
    ch(
        "CSAFE-HAR-004",
        SUBJECT_ID,
        "csafety-harassment",
        "csafety_repeated_targeting",
        3,
        "APPLICATION",
        (
            "Demo / educational scenario: A moderator asks what to preserve from a harassment thread. "
            "Which package is most useful for human review?"
        ),
        "Ordered messages showing who said what, when, and how the tone changed",
        (
            "Reviewers need an ordered sequence with authors and timing—not a single out-of-context line."
        ),
        choices=(
            "Ordered messages showing who said what, when, and how the tone changed",
            "Only the target's emotional reaction",
            "A summary written from memory a week later",
            "Screenshots with usernames cropped out",
        ),
        cues=("ordered", "who", "when", "sequence"),
        misconceptions=ISOLATED,
        target="CSAFE-M002",
        family="CSAFE-HAR",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "MAINTAIN", "REMEDIATE"),
    ),
    ch(
        "CSAFE-REP-001",
        SUBJECT_ID,
        "csafety-reporting",
        "csafety_report_channels",
        2,
        "SCENARIO",
        (
            "Demo / educational scenario: You notice harmful content in your organization's community "
            "space. Where should you report it first?"
        ),
        "The organization's approved safety or incident reporting channel",
        (
            "Use the organization's designated reporting path so reviewers receive structured, "
            "actionable information."
        ),
        choices=(
            "The organization's approved safety or incident reporting channel",
            "A public post tagging every admin at once",
            "A unrelated social media platform with no connection to the organization",
            "A private group chat of friends to gossip about it",
        ),
        cues=("approved", "incident", "organization", "channel"),
        misconceptions=PREMATURE,
        target="CSAFE-M001",
        family="CSAFE-REP",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "MAINTAIN"),
    ),
    ch(
        "CSAFE-REP-002",
        SUBJECT_ID,
        "csafety-reporting",
        "csafety_documentation",
        2,
        "SCENARIO",
        (
            "Demo / educational scenario: You are preparing a safety report. Which details help "
            "reviewers most?"
        ),
        "Links or screenshots with timestamps, location in the app, and surrounding context",
        (
            "Actionable reports include where content appeared, when, and surrounding context—not "
            "only a paraphrase."
        ),
        choices=(
            "Links or screenshots with timestamps, location in the app, and surrounding context",
            "Your guess about what punishment the author deserves",
            "A list of everyone you dislike in the community",
            "A meme summarizing your frustration",
        ),
        cues=("timestamp", "location", "context", "link"),
        misconceptions=ISOLATED,
        target="CSAFE-M002",
        family="CSAFE-REP",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "MAINTAIN", "REMEDIATE"),
    ),
    ch(
        "CSAFE-REP-003",
        SUBJECT_ID,
        "csafety-reporting",
        "csafety_escalation_timing",
        3,
        "SCENARIO",
        (
            "Demo / educational scenario: Content includes an immediate safety threat. What is the "
            "priority compared with ordinary harmful speech?"
        ),
        "Report immediately through urgent channels and preserve what you safely can",
        (
            "Immediate safety threats warrant urgent reporting while preserving available evidence "
            "without delay."
        ),
        choices=(
            "Report immediately through urgent channels and preserve what you safely can",
            "Wait until you collect ten similar examples",
            "Debate the theology of the insult first",
            "Only report if the target asks you to",
        ),
        cues=("immediate", "urgent", "threat", "report"),
        misconceptions=PREMATURE,
        target="CSAFE-M001",
        family="CSAFE-REP",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "DIAGNOSE"),
    ),
    ch(
        "CSAFE-REP-004",
        SUBJECT_ID,
        "csafety-reporting",
        "csafety_safe_reporting",
        3,
        "ERROR_ANALYSIS",
        (
            "Demo / educational scenario: Someone reposts harmful content to 'raise awareness' in "
            "a large public channel. What is the main problem?"
        ),
        "It can spread the harmful content further and retraumatize targets",
        (
            "Public reposting often amplifies harm. Report through private, approved channels instead."
        ),
        choices=(
            "It can spread the harmful content further and retraumatize targets",
            "Public awareness always reduces harm",
            "If the content is already online, sharing it again does not matter",
            "Only the original author is responsible for copies",
        ),
        cues=("spread", "amplify", "retraumat", "private"),
        misconceptions=PUBLIC,
        target="CSAFE-M005",
        family="CSAFE-REP",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("REMEDIATE", "DIAGNOSE", "MAINTAIN"),
    ),
    ch(
        "CSAFE-PRV-001",
        SUBJECT_ID,
        "csafety-privacy",
        "csafety_reporter_privacy",
        2,
        "SCENARIO",
        (
            "Demo / educational scenario: After a report is filed, a member asks who reported the "
            "incident in the public chat. What is the best response?"
        ),
        "Do not share reporter identity; refer questions to designated staff through private channels",
        (
            "Reporter privacy protects safety and encourages future reporting. Do not disclose identity "
            "in public spaces."
        ),
        choices=(
            "Do not share reporter identity; refer questions to designated staff through private channels",
            "Name the reporter so the community can thank them",
            "Hint strongly so people can guess who reported",
            "Post the report text with the reporter's phone number",
        ),
        cues=("reporter", "privacy", "do not share", "private"),
        misconceptions=PUBLIC,
        target="CSAFE-M005",
        family="CSAFE-PRV",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "MAINTAIN", "REMEDIATE"),
    ),
    ch(
        "CSAFE-PRV-002",
        SUBJECT_ID,
        "csafety-privacy",
        "csafety_need_to_know",
        2,
        "CONCEPT_CHECK",
        (
            "Who should typically receive detailed incident evidence during an active review?"
        ),
        "Designated reviewers and staff with a need to know",
        (
            "Detailed evidence belongs with reviewers and trusted staff—not broad community channels."
        ),
        choices=(
            "Designated reviewers and staff with a need to know",
            "Every member of the organization immediately",
            "Anyone who asks in a public forum",
            "External accounts with no role in the organization",
        ),
        cues=("reviewer", "need to know", "staff", "designated"),
        misconceptions=PUBLIC,
        target="CSAFE-M005",
        family="CSAFE-PRV",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "MAINTAIN"),
    ),
    ch(
        "CSAFE-PRV-003",
        SUBJECT_ID,
        "csafety-privacy",
        "csafety_reporter_privacy",
        3,
        "SCENARIO",
        (
            "Demo / educational scenario: You want to support a friend who reported harassment. "
            "What respects their privacy?"
        ),
        "Check in privately and avoid discussing their report in group chats",
        (
            "Support friends privately. Public discussion of their report can expose them to retaliation."
        ),
        choices=(
            "Check in privately and avoid discussing their report in group chats",
            "Announce in the group that they did the right thing by reporting",
            "Forward their report to unrelated contacts for opinions",
            "Ask them to repost the harmful content so others understand",
        ),
        cues=("private", "support", "avoid", "group chat"),
        misconceptions=PUBLIC,
        target="CSAFE-M005",
        family="CSAFE-PRV",
        evidence=("answer", "confidence", "reasoning"),
        strategies=("INCREASE", "REMEDIATE", "MAINTAIN"),
    ),
)
