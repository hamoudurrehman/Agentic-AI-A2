import { test, expect } from '@playwright/test';

const BASE_URL = process.env.PLAYWRIGHT_TEST_BASE_URL || 'http://localhost:8000';

test.describe('GigBid End-to-End Workflow Suite', () => {

  test('1. Onboarding and Profile Verification', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page.locator('text=GigBid Copilot')).toBeVisible();
    await expect(page.locator('#connectsBalance')).toContainText('120');
  });

  test('2. Inbox Loading and Running Copilot on Job', async ({ page }) => {
    await page.goto(BASE_URL);
    const runBtn = page.locator('button:has-text("Run GigBid Copilot")').first();
    await expect(runBtn).toBeVisible();
    await runBtn.click();
    await expect(page.locator('text=Live Agent Execution Telemetry')).toBeVisible();
  });

  test('3. Proposal Studio Claim Grounding Hover and Approval', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.click('button:has-text("Proposal Studio")');
    await expect(page.locator('text=Proposal Studio & Approval Gate')).toBeVisible();
    await expect(page.locator('#claimsContainer')).toBeVisible();
  });

  test('4. Editing Draft and Diffing into Style Memory', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.click('button:has-text("Settings & Memory")');
    await expect(page.locator('text=Style Memory')).toBeVisible();
    await expect(page.locator('text=Outcome Memory')).toBeVisible();
  });

  test('5. Degraded Mode Resilience Banner when Marketplace Server Offline', async ({ page }) => {
    await page.goto(BASE_URL);
    const modeSelect = page.locator('#marketModeSelect');
    await expect(modeSelect).toBeVisible();
    await modeSelect.selectOption('upwork_live');
    await expect(page.locator('#marketMode')).toHaveText('Upwork Live');
  });

});
