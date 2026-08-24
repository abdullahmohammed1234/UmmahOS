<template>
  <div class="landing" data-testid="landing-page">
    <a class="skip-link" href="#landing-main">Skip to content</a>
    <header class="landing-nav">
      <div class="landing-nav-inner landing-wide">
        <RouterLink to="/" class="brand" aria-label="UmmahOS home">
          <span class="brand-mark" aria-hidden="true">U</span>
          <span class="brand-name">UmmahOS</span>
        </RouterLink>
        <nav class="nav-links" aria-label="Landing navigation">
          <a href="#community-shield">Community Shield</a>
          <a href="#ethics">Ethics</a>
          <a href="#multi-msa">Multi-MSA</a>
        </nav>
        <div class="nav-actions">
          <RouterLink class="button secondary" to="/login">Sign in</RouterLink>
          <RouterLink class="button" to="/login" data-testid="landing-explore-cta">
            Open Demo
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
        <a href="#community-shield" @click="mobileOpen = false">Community Shield</a>
        <a href="#ethics" @click="mobileOpen = false">Ethics</a>
        <a href="#multi-msa" @click="mobileOpen = false">Multi-MSA</a>
        <RouterLink to="/login" @click="mobileOpen = false">Sign in</RouterLink>
        <RouterLink to="/login" @click="mobileOpen = false">Open Demo</RouterLink>
      </nav>
    </header>

    <main id="landing-main" tabindex="-1">
      <!-- Hero -->
      <section class="hero">
        <div class="hero-inner landing-wide">
          <div class="hero-copy">
            <p class="eyebrow">Community infrastructure for MSAs</p>
            <h1 class="display-title">Build stronger, safer Muslim student communities.</h1>
            <p class="lede">
              UmmahOS brings MSA operations, community safety, evidence-based review, and adaptive
              education into one platform — designed for the communities themselves.
            </p>
            <div class="actions">
              <RouterLink class="button large" to="/login" data-testid="hero-explore-cta">
                Explore UmmahOS
              </RouterLink>
              <a class="button secondary large" href="#community-shield">See Community Shield</a>
            </div>
            <p class="hero-tagline">
              <strong>AI assists. Humans decide.</strong>
            </p>
          </div>
          <HeroVisual />
        </div>
      </section>

      <!-- Problem / Solution -->
      <section class="section">
        <div class="landing-wide">
          <div class="section-header centered">
            <p class="eyebrow">The challenge</p>
            <h2>Disconnected tools create disconnected communities.</h2>
            <p>
              MSAs manage members, events, resources, education, and community safety across
              fragmented systems. When something concerning happens online, context gets lost.
            </p>
          </div>
          <ProblemComparison />
        </div>
      </section>

      <!-- Community Shield flagship -->
      <CommunityShieldShowcase />

      <!-- AI vs Human -->
      <section id="ethics" class="section section-alt">
        <div class="landing-wide">
          <div class="section-header centered">
            <p class="eyebrow">Ethics</p>
            <h2>AI assists. Humans decide.</h2>
            <p>Three principles that guide every Community Shield workflow.</p>
          </div>
          <AiHumanComparison />
          <div class="principles-row">
            <article v-for="p in principles" :key="p.title" class="principle panel content">
              <h3>{{ p.title }}</h3>
              <p>{{ p.body }}</p>
            </article>
          </div>
        </div>
      </section>

      <!-- Uncertainty -->
      <section class="section">
        <div class="landing-wide">
          <UncertaintySection />
        </div>
      </section>

      <!-- Outcome Tracking -->
      <section class="section section-alt">
        <div class="landing-wide">
          <OutcomeTimeline />
        </div>
      </section>

      <!-- Academy + ADAPT -->
      <section class="section academy-section">
        <div class="landing-wide">
          <div class="section-header centered">
            <p class="eyebrow">Academy + ADAPT</p>
            <h2>From community experience to adaptive education.</h2>
            <p>
              Turn confirmed community patterns into adaptive education. ADAPT challenges adapt based
              on learner evidence.
            </p>
          </div>
          <AcademyAdaptFlow />
        </div>
      </section>

      <!-- Multi-MSA -->
      <section id="multi-msa" class="section">
        <div class="landing-wide two-col">
          <div class="section-header">
            <p class="eyebrow">Multi-MSA</p>
            <h2>One platform. Multiple organizations.</h2>
            <p>
              Organization-scoped permissions and data isolation prevent cross-MSA access. Switch
              organizations without leaving the platform.
            </p>
          </div>
          <MultiMsaNetwork />
        </div>
      </section>

      <!-- Final CTA -->
      <section class="section cta-section">
        <div class="landing-wide cta-inner">
          <h2>Community infrastructure, built for the communities themselves.</h2>
          <div class="actions">
            <RouterLink class="button large" to="/login" data-testid="landing-final-cta">
              Explore UmmahOS
            </RouterLink>
            <RouterLink class="button secondary large" to="/login">Open Demo</RouterLink>
          </div>
          <p class="muted demo-credentials">
            Demo accounts are provided in the repository documentation. All demo data is clearly
            labeled as seeded content.
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
import HeroVisual from '@/components/landing/HeroVisual.vue';
import ProblemComparison from '@/components/landing/ProblemComparison.vue';
import CommunityShieldShowcase from '@/components/landing/CommunityShieldShowcase.vue';
import AiHumanComparison from '@/components/landing/AiHumanComparison.vue';
import UncertaintySection from '@/components/landing/UncertaintySection.vue';
import OutcomeTimeline from '@/components/landing/OutcomeTimeline.vue';
import AcademyAdaptFlow from '@/components/landing/AcademyAdaptFlow.vue';
import MultiMsaNetwork from '@/components/landing/MultiMsaNetwork.vue';

const mobileOpen = ref(false);

const principles = [
  {
    title: 'Context before conclusions',
    body: 'Reports capture platform, visibility, surrounding conversation, and related copies — not just the reported item in isolation.',
  },
  {
    title: 'Uncertainty is allowed',
    body: 'When AI analysis is uncertain, reviewers see it clearly. High uncertainty triggers visible guidance — not false confidence.',
  },
  {
    title: 'Human review remains authoritative',
    body: 'Trained reviewers make determinations independently. AI output is labeled advisory throughout the product.',
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

.brand-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--radius-md);
  background: var(--gradient-emerald);
  color: #fff;
  font-size: var(--text-sm);
  font-weight: var(--font-extrabold);
  box-shadow: var(--shadow-sm);
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

.principles-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: var(--space-5);
  margin-top: var(--space-10);
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
