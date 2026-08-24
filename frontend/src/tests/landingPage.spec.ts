import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import { createMemoryHistory, createRouter } from 'vue-router';
import LandingPage from '@/pages/LandingPage.vue';

describe('Landing page', () => {
  it('renders hero, product story, and core sections', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/welcome', component: LandingPage },
        { path: '/login', component: { template: '<div />' } },
      ],
    });
    await router.push('/welcome');
    await router.isReady();

    const wrapper = mount(LandingPage, {
      global: { plugins: [router] },
    });

    expect(wrapper.find('[data-testid="landing-page"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('Community infrastructure for Muslim student organizations.');
    expect(wrapper.text()).toContain(
      'Preserve context. Protect people. Track outcomes. Turn community learning into action.',
    );
    expect(wrapper.text()).toContain('AI assists. Humans decide.');
    expect(wrapper.text()).toContain('Preserve context. Protect people. Respond responsibly.');
    expect(wrapper.text()).toContain('Uncertainty is a valid outcome.');
    expect(wrapper.find('[data-testid="product-story-workflow"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="community-shield-before-after"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="multi-msa-tree"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="landing-explore-cta"]').exists()).toBe(true);
  });

  it('includes navigation to login/demo', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/welcome', component: LandingPage },
        { path: '/login', component: { template: '<div />' } },
      ],
    });
    await router.push('/welcome');
    await router.isReady();

    const wrapper = mount(LandingPage, {
      global: { plugins: [router] },
    });

    const exploreLink = wrapper.find('[data-testid="hero-explore-cta"]');
    expect(exploreLink.attributes('href')).toBe('/login');
    expect(exploreLink.text()).toContain('Explore the Demo');
  });
});
