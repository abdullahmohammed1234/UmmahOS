<template>
  <div class="landing" data-testid="landing-page">
    <a class="skip-link" href="#landing-main">Skip to content</a>
    <header class="landing-nav">
      <div class="landing-nav-inner landing-wide">
        <RouterLink to="/" class="brand" aria-label="UmmahOS home">
          <BrandMark aria-hidden="true" />
          <span class="brand-name">UmmahOS</span>
        </RouterLink>
        <nav class="nav-links" aria-label="Landing navigation">
          <a href="#ummahos-loop">How it works</a>
          <a href="#community-shield">Community Shield</a>
          <a href="#ethics">Ethics</a>
          <a href="#multi-msa">Multi-MSA</a>
        </nav>
        <div class="nav-actions">
          <RouterLink class="button secondary" to="/login">Sign in</RouterLink>
          <RouterLink class="button" to="/login" data-testid="landing-explore-cta">
            Explore the Demo
          </RouterLink>
        </div>
        <button
          class="mobile-menu-btn"
          type="button"
          aria-label="Toggle menu"
          aria-controls="landing-mobile-nav"
          :aria-expanded="mobileOpen"
          data-testid="landing-mobile-menu"
          @click="mobileOpen = !mobileOpen"
        >
          <span class="menu-icon" aria-hidden="true" />
        </button>
      </div>
      <nav v-if="mobileOpen" id="landing-mobile-nav" class="mobile-nav" aria-label="Mobile navigation">
        <a href="#ummahos-loop" @click="mobileOpen = false">How it works</a>
        <a href="#community-shield" @click="mobileOpen = false">Community Shield</a>
        <a href="#ethics" @click="mobileOpen = false">Ethics</a>
        <a href="#multi-msa" @click="mobileOpen = false">Multi-MSA</a>
        <RouterLink to="/login" @click="mobileOpen = false">Sign in</RouterLink>
        <RouterLink to="/login" @click="mobileOpen = false">Explore the Demo</RouterLink>
      </nav>
    </header>

    <main id="landing-main" tabindex="-1">
      <section class="hero">
        <div class="hero-inner landing-wide">
          <div class="hero-copy">
            <p class="eyebrow">UmmahOS</p>
            <h1 class="display-title">Community infrastructure for Muslim student organizations.</h1>
            <p class="lede">
              Preserve context. Protect people. Track outcomes. Turn community learning into action.
            </p>
            <div class="actions">
              <RouterLink class="button large" to="/login" data-testid="hero-explore-cta">
                Explore the Demo
              </RouterLink>
              <a class="button secondary large" href="#ummahos-loop">See How It Works</a>
            </div>
            <p class="hero-tagline">
              <strong>AI assists. Humans decide.</strong>
            </p>
          </div>
          <HeroVisual />
        </div>
      </section>

      <section class="section">
        <div class="landing-wide">
          <div class="section-header centered">
            <p class="eyebrow">The problem</p>
            <h2>Fragmented workflows lose the story.</h2>
            <p>
              Forms → screenshots → spreadsheets → messaging apps → disconnected reports.
              When something concerning happens online, context disappears before a trained reviewer
              ever sees it.
            </p>
          </div>
          <ProblemComparison />
          <p class="section-footnote muted">
            UmmahOS replaces that scatter with <strong>one organization-aware system</strong>.
          </p>
        </div>
      </section>

      <section id="ummahos-loop" class="section section-alt">
        <div class="landing-wide">
          <div class="section-header centered">
            <p class="eyebrow">The UmmahOS loop</p>
            <h2>From concern to adaptive learning.</h2>
            <p>One coherent story — not a pile of disconnected tools.</p>
          </div>
          <UmmahOSLoop />
        </div>
      </section>

      <section id="community-shield" class="section">
        <div class="landing-wide">
          <div class="section-header centered">
            <p class="eyebrow">Community Shield</p>
            <h2>Why a screenshot is not enough.</h2>
            <p>
              Preserve context. Protect people. Respond responsibly. Community Shield captures the
              surrounding story so reviewers can decide carefully.
            </p>
          </div>
          <ContextEvidenceCompare />
          <CommunityShieldLoop />
        </div>
      </section>

      <CommunityShieldShowcase />

      <section id="ethics" class="section section-alt">
        <div class="landing-wide">
          <div class="section-header centered">
            <p class="eyebrow">AI + human oversight</p>
            <h2>AI analyzes. Humans decide.</h2>
            <p>
              Potential signals, classification, confidence, uncertainty, and recommended action —
              then a reviewer confirms, marks uncertain, requests context, escalates, or closes.
            </p>
          </div>
          <AiHumanComparison />
          <p class="section-footnote centered">
            <strong>Uncertainty is a valid outcome.</strong>
          </p>
          <UncertaintySection />
        </div>
      </section>

      <section class="section">
        <div class="landing-wide">
          <OutcomeTimeline />
          <p class="section-footnote muted centered">
            UmmahOS does not stop when the report is submitted. Members can follow
            <strong>What happened next?</strong>
          </p>
        </div>
      </section>

      <section class="section academy-section">
        <div class="landing-wide">
          <div class="section-header centered">
            <p class="eyebrow">Safety → education</p>
            <h2>Confirmed patterns become practice.</h2>
            <p>
              Community Shield → Academy lesson → scenario → learner response → ADAPT → next challenge.
            </p>
          </div>
          <AcademyAdaptFlow />
        </div>
      </section>

      <section id="multi-msa" class="section">
        <div class="landing-wide two-col">
          <div class="section-header">
            <p class="eyebrow">Multi-MSA</p>
            <h2>One platform. Isolated organizations.</h2>
            <p>
              Each MSA keeps its own members, events, reports, evidence, reviews, Academy, and
              outcomes. Switching organizations changes both content and permissions.
            </p>
          </div>
          <MultiMsaNetwork />
        </div>
      </section>

      <section class="section section-alt">
        <div class="landing-wide">
          <div class="section-header centered">
            <p class="eyebrow">Ethics</p>
            <h2>Principles that stay visible in the product.</h2>
          </div>
          <div class="principles-row">
            <article v-for="p in principles" :key="p.title" class="principle panel content">
              <h3>{{ p.title }}</h3>
              <p>{{ p.body }}</p>
            </article>
          </div>
        </div>
      </section>

      <section class="section cta-section">
        <div class="landing-wide cta-inner">
          <h2>Explore the UmmahOS demo</h2>
          <div class="actions">
            <RouterLink class="button large" to="/login" data-testid="landing-final-cta">
              Explore the Demo
            </RouterLink>
            <RouterLink class="button secondary large" to="/login">Sign in</RouterLink>
          </div>
          <p class="muted demo-credentials">
            Demo accounts and seeded data are labeled in the repository documentation — not presented
            as production analytics.
          </p>
        </div>
      </section>
    </main>

    <footer class="landing-footer">
      <div class="landing-wide footer-inner">
        <p>
          <strong>UmmahOS</strong> — Community infrastructure for Muslim student organizations.
        </p>
        <p class="muted">AI assists. Humans decide.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import BrandMark from '@/components/BrandMark.vue';
import HeroVisual from '@/components/landing/HeroVisual.vue';
import ProblemComparison from '@/components/landing/ProblemComparison.vue';
import UmmahOSLoop from '@/components/landing/UmmahOSLoop.vue';
import ContextEvidenceCompare from '@/components/landing/ContextEvidenceCompare.vue';
import CommunityShieldLoop from '@/components/landing/CommunityShieldLoop.vue';
import CommunityShieldShowcase from '@/components/landing/CommunityShieldShowcase.vue';
import AiHumanComparison from '@/components/landing/AiHumanComparison.vue';
import UncertaintySection from '@/components/landing/UncertaintySection.vue';
import OutcomeTimeline from '@/components/landing/OutcomeTimeline.vue';
import AcademyAdaptFlow from '@/components/landing/AcademyAdaptFlow.vue';
import MultiMsaNetwork from '@/components/landing/MultiMsaNetwork.vue';

const mobileOpen = ref(false);

const principles = [
  {
    title: 'AI is advisory',
    body: 'AI analysis surfaces signals and uncertainty. It never issues an automatic verdict.',
  },
  {
    title: 'Human review is authoritative',
    body: 'Trained reviewers confirm, mark uncertain, request context, escalate, or close.',
  },
  {
    title: 'Uncertainty is explicit',
    body: 'Uncertainty is a valid outcome — not something the product hides behind false confidence.',
  },
  {
    title: 'Private information stays protected',
    body: 'Reporter-visible summaries and internal notes are separated by design and permissions.',
  },
  {
    title: 'No automatic enforcement',
    body: 'Exporting an evidence package creates a report. It does not automatically submit it anywhere.',
  },
  {
    title: 'Synthetic data powers safety evaluation',
    body: 'Safety evaluation uses synthetic scenarios so judges can inspect behavior without live harm claims.',
  },
];
</script>

<style scoped>
.landing {
  min-height: 100vh;
  overflow-x: hidden;
}

.skip-link {
  position: absolute;
  top: var(--space-3);
  left: var(--space-3);
  z-index: 200;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  background: var(--surface-elevated);
  border: 1px solid var(--border);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  transform: translateY(-200%);
  transition: transform var(--transition-fast);
}

.skip-link:focus {
  transform: translateY(0);
}

.landing-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 253, 248, 0.88);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-subtle);
}

.landing-nav-inner {
  display: flex;
  align-items: center;
  gap: var(--space-6);
  padding: var(--space-4) var(--space-6);
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  text-decoration: none;
  font-weight: var(--font-bold);
  font-size: var(--text-lg);
  font-family: var(--font-display);
}

.nav-links {
  display: flex;
  gap: var(--space-6);
  margin-right: auto;
}

.nav-links a {
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  transition: color var(--transition-fast);
}

.nav-links a:hover {
  color: var(--primary);
}

.nav-actions {
  display: flex;
  gap: var(--space-3);
}

.mobile-menu-btn {
  display: none;
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
  width: 2.5rem;
  height: 2.5rem;
  align-items: center;
  justify-content: center;
}

.menu-icon {
  display: block;
  width: 1rem;
  height: 2px;
  background: var(--text-primary);
  box-shadow: 0 -5px 0 var(--text-primary), 0 5px 0 var(--text-primary);
}

.mobile-nav {
  display: none;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border);
}

.mobile-nav a {
  text-decoration: none;
  padding: var(--space-2) 0;
  color: var(--text-secondary);
  font-weight: var(--font-medium);
}

.hero {
  padding: var(--space-16) 0 var(--space-12);
  background: var(--gradient-hero);
}

.hero-inner {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-10);
  align-items: center;
}

.hero-copy {
  max-width: 36rem;
}

.hero-copy .display-title {
  margin-bottom: var(--space-5);
}

.hero-tagline {
  margin-top: var(--space-6);
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.hero-tagline strong {
  color: var(--primary);
}

.section {
  padding: var(--space-16) 0;
}

.section-alt {
  background: var(--background-alt);
}

.academy-section {
  background: linear-gradient(180deg, var(--surface) 0%, var(--accent-soft) 100%);
}

.section-header.centered {
  text-align: center;
  margin-bottom: var(--space-10);
}

.section-header.centered p:not(.eyebrow) {
  margin: 0 auto;
  max-width: 36rem;
  color: var(--text-muted);
}

.section-header.centered h2 {
  margin-bottom: var(--space-3);
  font-size: clamp(1.5rem, 3vw, var(--text-3xl));
}

.section-footnote {
  margin-top: var(--space-8);
  font-size: var(--text-base);
}

.section-footnote.centered {
  text-align: center;
}

.principles-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-5);
}

.principle h3 {
  margin: 0 0 var(--space-3);
  color: var(--primary);
  font-size: var(--text-lg);
}

.principle p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-10);
  align-items: center;
}

.cta-section {
  text-align: center;
  padding: var(--space-20) 0;
  background: var(--gradient-dark);
  color: var(--text-on-dark);
}

.cta-inner h2 {
  max-width: 40rem;
  margin: 0 auto var(--space-6);
  color: var(--text-on-dark);
  font-size: clamp(1.5rem, 3vw, var(--text-3xl));
}

.cta-inner .actions {
  justify-content: center;
}

.demo-credentials {
  margin-top: var(--space-5);
  font-size: var(--text-sm);
  color: var(--text-on-dark-muted);
}

.landing-footer {
  border-top: 1px solid var(--border);
  padding: var(--space-8) 0;
}

.footer-inner {
  text-align: center;
}

.footer-inner p {
  margin: var(--space-2) 0;
}

@media (max-width: 960px) {
  .hero-inner {
    grid-template-columns: 1fr;
    gap: var(--space-8);
  }

  .hero-copy {
    max-width: none;
    text-align: center;
  }

  .hero-copy .actions {
    justify-content: center;
  }

  .two-col {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .nav-links,
  .nav-actions {
    display: none;
  }

  .mobile-menu-btn {
    display: flex;
    margin-left: auto;
  }

  .mobile-nav {
    display: flex;
  }

  .section {
    padding: var(--space-12) 0;
  }
}
</style>
