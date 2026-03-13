import 'dotenv/config';
import express from 'express';
import puppeteer from 'puppeteer';
import { Redis } from '@upstash/redis';
import fetch from 'node-fetch';
import cron from 'node-cron';

const app = express();
const port = process.env.PORT || 3000;

let redis;
try {
  if (process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_URL.includes('upstash.io')) {
    redis = new Redis({
      url: process.env.UPSTASH_REDIS_REST_URL,
      token: process.env.UPSTASH_REDIS_REST_TOKEN,
    });
  } else {
    console.warn('Invalid or missing UPSTASH_REDIS_REST_URL. Redis functionality will be disabled.');
  }
} catch (error) {
  console.error('Failed to initialize Redis:', error.message);
}

async function sendWhatsAppMessage(message) {
  const phone = process.env.WA_PHONE;
  const apikey = process.env.WA_APIKEY;
  const url = `https://api.callmebot.com/whatsapp.php?phone=${phone}&text=${encodeURIComponent(message)}&apikey=${apikey}`;
  const response = await fetch(url);
  return response.ok;
}

let isChecking = false;

async function checkH1BSlots(forceSend = false) {
  if (isChecking && !forceSend) {
    console.log('Previous check still in progress. Skipping...');
    return { status: 'busy' };
  }
  
  isChecking = true;
  let browser;
  try {
    browser = await puppeteer.launch({
      headless: "new",
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    page.setDefaultNavigationTimeout(60000);
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

    await page.goto('https://checkvisaslots.com/latest-us-visa-availability/h-1b-regular/', {
      waitUntil: 'networkidle2',
    });

    const pageInfo = await page.evaluate(() => {
      const headers = Array.from(document.querySelectorAll('th'));
      const lastSeenIndex = headers.findIndex(th => th.textContent.includes('Last Seen At'));
      const locationIndex = headers.findIndex(th => th.textContent.includes('Visa Location'));
      
      let tableData = '';
      if (lastSeenIndex !== -1) {
        const rows = Array.from(document.querySelectorAll('tbody tr'));
        tableData = rows.map(row => {
          const cells = row.querySelectorAll('td');
          if (cells.length > lastSeenIndex) {
            const location = locationIndex !== -1 ? cells[locationIndex].textContent.trim() : 'Unknown';
            const value = cells[lastSeenIndex].textContent.trim();
            return `${location}: ${value}`;
          }
          return null;
        }).filter(Boolean).join(' | ');
      }

      const allElements = Array.from(document.querySelectorAll('div, p, span'));
      let generatedAt = '';
      for (const el of allElements) {
        const match = el.textContent.match(/The current info is generated at\s+([\w\s,:]+)/);
        if (match) {
          generatedAt = match[0].trim();
          break;
        }
      }

      return { tableData, generatedAt };
    });

    const lastSeenAt = pageInfo.tableData;
    const generatedAt = pageInfo.generatedAt;

    if (!lastSeenAt) {
      throw new Error('Could not find "Last Seen At" value on page');
    }

    const storedValue = redis ? await redis.get('last_seen_h1b') : null;
    const isChanged = lastSeenAt !== storedValue;
    const displayGeneratedAt = generatedAt ? `\n(${generatedAt})` : '';

    if (isChanged || forceSend) {
      const prefix = forceSend && !isChanged ? 'Scheduled H1B Status: ' : 'H1B Slot Update: ';
      const message = `${prefix}Last Seen At ${lastSeenAt}${displayGeneratedAt}`;
      
      const success = await sendWhatsAppMessage(message);
      if (success && redis) {
        await redis.set('last_seen_h1b', lastSeenAt);
      }
      return { status: 'sent', newValue: lastSeenAt, isChanged, forceSend };
    }

    return { status: 'no_change', value: lastSeenAt };

  } catch (error) {
    console.error('Check failed:', error.message);
    throw error;
  } finally {
    isChecking = false;
    if (browser) await browser.close();
  }
}

// Schedule check every 1 minute for immediate detection
cron.schedule('* * * * *', async () => {
  const now = new Date();
  const isFiveMinuteInterval = now.getMinutes() % 5 === 0;
  
  // We only log the "Status Report" intent every 5 mins to keep logs clean
  if (isFiveMinuteInterval) {
    console.log('Running 5-minute scheduled status report...');
  }

  try {
    // forceSend is true only on 5-minute intervals. 
    // On other minutes, checkH1BSlots() will only send if it detects a change.
    await checkH1BSlots(isFiveMinuteInterval);
  } catch (err) {
    console.error('Scheduled check failed:', err.message);
  }
});

app.get('/ping', (req, res) => {
  res.send('pong');
});

app.get('/', (req, res) => {
  res.send('H1B Monitor Running');
});

app.get('/check', async (req, res) => {
  try {
    const result = await checkH1BSlots();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
