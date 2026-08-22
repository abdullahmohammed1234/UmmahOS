import { describe, expect, it } from 'vitest';
import { organizationPath } from '@/services/organizations';

describe('organization-aware API paths', () => {
  it('scopes requests to the current organization', () => {
    expect(organizationPath(7)).toBe('/organizations/7');
    expect(organizationPath(7, '/members')).toBe('/organizations/7/members');
    expect(organizationPath('demo-msa-alpha', '/context')).toBe(
      '/organizations/demo-msa-alpha/context',
    );
  });
});
