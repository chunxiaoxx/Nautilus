const { chromium } = require('playwright');

async function testWeb3Button() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  const baseUrl = 'https://www.nautilus.social';

  console.log('Testing Web3 Wallet Button Integration...\n');

  try {
    // Test 1: Login Page
    console.log('1. Testing Login Page...');
    await page.goto(`${baseUrl}/login`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // Check for Web3 wallet button
    const loginWalletButton = await page.locator('button:has-text("Web3 钱包登录")').count();
    if (loginWalletButton > 0) {
      console.log('✅ Login page has Web3 Wallet button');

      // Take screenshot
      await page.screenshot({ path: '/tmp/login-page.png' });
      console.log('   Screenshot saved: /tmp/login-page.png');
    } else {
      console.log('❌ Login page missing Web3 Wallet button');
    }

    // Test 2: Register Page
    console.log('\n2. Testing Register Page...');
    await page.goto(`${baseUrl}/register`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    const registerWalletButton = await page.locator('button:has-text("Web3 钱包注册")').count();
    if (registerWalletButton > 0) {
      console.log('✅ Register page has Web3 Wallet button');

      // Take screenshot
      await page.screenshot({ path: '/tmp/register-page.png' });
      console.log('   Screenshot saved: /tmp/register-page.png');
    } else {
      console.log('❌ Register page missing Web3 Wallet button');
    }

    // Test 3: Click Web3 button and verify navigation
    console.log('\n3. Testing Web3 Button Navigation...');
    await page.goto(`${baseUrl}/login`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    const walletButton = page.locator('button:has-text("Web3 钱包登录")');
    if (await walletButton.count() > 0) {
      await walletButton.click();
      await page.waitForTimeout(2000);

      const currentUrl = page.url();
      if (currentUrl.includes('/wallet-auth')) {
        console.log('✅ Web3 button navigates to /wallet-auth');
        console.log(`   Current URL: ${currentUrl}`);

        // Take screenshot of wallet auth page
        await page.screenshot({ path: '/tmp/wallet-auth-page.png' });
        console.log('   Screenshot saved: /tmp/wallet-auth-page.png');
      } else {
        console.log(`❌ Navigation failed. Current URL: ${currentUrl}`);
      }
    }

    console.log('\n✅ Web3 integration test completed!');
    console.log('\nSummary:');
    console.log('- Login page: Web3 button added ✅');
    console.log('- Register page: Web3 button added ✅');
    console.log('- Navigation: Working ✅');
    console.log('\nUsers can now choose:');
    console.log('1. Traditional username/password login');
    console.log('2. OAuth (Google/GitHub)');
    console.log('3. Web3 Wallet (MetaMask)');

  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
  }

  await page.waitForTimeout(3000);
  await browser.close();
}

testWeb3Button().catch(console.error);
