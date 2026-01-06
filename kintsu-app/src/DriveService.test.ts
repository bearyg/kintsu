// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { DriveService } from './DriveService';

// Mock gapi-script
vi.mock('gapi-script', () => {
  return {
    gapi: {
      load: vi.fn((_libs, callback) => callback()),
      client: {
        init: vi.fn().mockResolvedValue(undefined),
        setToken: vi.fn(),
        drive: {
            files: {
                list: vi.fn(),
                create: vi.fn()
            }
        }
      }
    }
  };
});

// Mock window.google
const mockInitTokenClient = vi.fn();
(globalThis as any).window = (globalThis as any).window || {};
(globalThis as any).window.google = {
  accounts: {
    oauth2: {
      initTokenClient: mockInitTokenClient
    }
  }
};

describe('DriveService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with correct scopes including Gmail', async () => {
    await DriveService.init('test-client-id', 'test-api-key');

    // This assertion should pass (existing functionality)
    expect(mockInitTokenClient).toHaveBeenCalledWith(expect.objectContaining({
      client_id: 'test-client-id',
      scope: expect.stringContaining('https://www.googleapis.com/auth/drive.appdata'),
    }));

    // This assertion should FAIL (new requirement)
    expect(mockInitTokenClient).toHaveBeenCalledWith(expect.objectContaining({
        scope: expect.stringContaining('https://www.googleapis.com/auth/gmail.readonly')
    }));
  });
});
