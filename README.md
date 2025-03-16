# BookingBuzzer

A Scrapy spider for monitoring booking.com prices and sending notifications via Telegram.

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```
   python -m playwright install firefox
   ```

## Configuration

The scraper can be configured using the following methods:

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID

### Command-line Parameters
```
scrapy crawl booking-price-spider -a telegram_bot_token=YOUR_TOKEN -a telegram_chat_id=YOUR_CHAT_ID
```

## GitHub Actions Deployment

This project is configured to run automatically via GitHub Actions:

1. Push this repository to GitHub
2. Add your Telegram credentials as GitHub repository secrets:
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add new repository secrets:
     - `TELEGRAM_BOT_TOKEN`
     - `TELEGRAM_CHAT_ID`
3. The scraper will run daily at 9 AM UTC, or you can trigger it manually from the Actions tab.