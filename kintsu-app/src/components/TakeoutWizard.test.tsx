// @vitest-environment jsdom
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TakeoutWizard } from './TakeoutWizard';

describe('TakeoutWizard', () => {
  it('renders step 1 initially', () => {
    render(<TakeoutWizard userId="test-user" />);
    expect(screen.getByText(/Filter your Email/i)).toBeDefined();
  });
});
