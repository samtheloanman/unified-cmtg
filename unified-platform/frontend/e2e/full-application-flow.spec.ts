import { test, expect } from '@playwright/test';

test('Full Application Flow: Quote to Lead Submission', async ({ page }) => {
  // 1. Setup Network Interception
  // Mock the Quote API response using the fixture
  await page.route('**/api/v1/quote/', async route => {
    // Introduce a small delay to simulate network
    await new Promise(f => setTimeout(f, 500));
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      path: './e2e/fixtures/quote-response.json'
    });
  });

  // Mock the Lead Submission API response
  await page.route('**/api/v1/leads/', async route => {
    await new Promise(f => setTimeout(f, 500));

    // Verify the request payload
    const request = route.request();
    const postData = request.postDataJSON();

    // Validate required fields are present
    if (postData.first_name === 'John' &&
        postData.last_name === 'Doe' &&
        postData.email === 'john.doe@example.com') {

      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          floify_id: 'mock-floify-123',
          message: 'Lead created successfully'
        })
      });
    } else {
      await route.fulfill({
        status: 400,
        body: JSON.stringify({ success: false, error: 'Invalid payload' })
      });
    }
  });

  // 2. Start the User Journey
  await page.goto('/quote');

  // Verify we are on the Quote Page
  await expect(page.getByText('Get Your Custom Quote')).toBeVisible();

  // 3. Wizard Step 1: Property State
  // Select 'California'
  await page.getByRole('combobox').selectOption('CA');
  await page.getByRole('button', { name: 'Continue' }).click();

  // 4. Wizard Step 2: Loan Amount
  // Enter 750,000
  await expect(page.getByText('Loan Amount', { exact: true })).toBeVisible();
  const loanInput = page.getByRole('textbox');
  await loanInput.click();
  await loanInput.fill('750000');
  await page.getByRole('button', { name: 'Continue' }).click();

  // 5. Wizard Step 3: Credit Score
  // Enter 740
  await expect(page.getByText('Credit Score', { exact: true })).toBeVisible();
  const creditInput = page.getByRole('spinbutton'); // input type="number"
  await creditInput.fill('740');
  await page.getByRole('button', { name: 'Continue' }).click();

  // 6. Wizard Step 4: Property Value
  // Enter 1,000,000
  await expect(page.getByText('Property Value', { exact: true })).toBeVisible();
  const valueInput = page.getByRole('textbox'); // Reusing textbox selector since there is only one per page
  await valueInput.click();
  await valueInput.fill('1000000');

  // Submit Quote Request
  await page.getByRole('button', { name: 'Get My Quote' }).click();

  // 7. Verify Results Page
  // Check that the "Best Match" card appears (from fixture data)
  // Use 'heading' role to distinguish from table rows
  await expect(page.getByRole('heading', { name: 'Acra Lending' })).toBeVisible();

  // Scope to the Best Match card for other details to avoid strict mode violations
  // The Best Match card typically has a distinctive class or structure, but purely text-based:
  await expect(page.getByText('DSCR 30-Year Fixed').first()).toBeVisible();
  await expect(page.getByText('7.875%').first()).toBeVisible(); // Adjusted rate from fixture

  // 8. Initiate Application
  // Click "Apply Now" on the best match card
  await page.getByRole('button', { name: 'Apply Now' }).first().click();

  // 9. Fill Lead Form in Modal
  // The modal implementation uses a div, not a semantic dialog, so we target unique content.
  // We verify the Modal Header "Apply Now" appears.
  await expect(page.getByRole('heading', { name: 'Apply Now' })).toBeVisible();

  await page.getByLabel('First Name').fill('John');
  await page.getByLabel('Last Name').fill('Doe');
  await page.getByLabel('Email').fill('john.doe@example.com');
  await page.getByLabel('Phone').fill('(555) 123-4567');

  // 10. Submit Application
  await page.getByRole('button', { name: 'Start Your Application' }).click();

  // 11. Verify Success State
  await expect(page.getByText('Application Submitted!')).toBeVisible();
  await expect(page.getByText("Check your email for your personalized application link")).toBeVisible();
});
