from pathlib import Path
from scrapy_playwright.page import PageMethod
import scrapy
import requests


class BookingPriceSpider(scrapy.Spider):
    name = "booking-price-spider"
    # Tell Scrapy to handle redirect status codes
    handle_httpstatus_list = [301, 302]
    # Telegram configuration
    # You should set these as environment variables before running the spider
    
    def __init__(self, telegram_bot_token=None, telegram_chat_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Try to get values from environment variables if not provided directly
        import os
        self.telegram_bot_token = telegram_bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = telegram_chat_id or os.getenv('TELEGRAM_CHAT_ID')
    
    def send_telegram_message(self, message):
        """Send a message to Telegram"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            self.logger.warning("Telegram credentials not configured. Skipping notification.")
            return False
        
        telegram_api_url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(telegram_api_url, data=payload)
            if response.status_code == 200:
                self.logger.info("Telegram notification sent successfully")
                return True
            else:
                self.logger.error(f"Failed to send Telegram notification: {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error sending Telegram notification: {str(e)}")
            return False
    
    def start_requests(self):
        urls = [
            "https://www.booking.com/Share-SNzpVA",
            "https://www.booking.com/Share-YEFeTW",
            "https://www.booking.com/Share-Ip64xnj"
        ]
        for url in urls:
            yield scrapy.Request(
                url=url,
                meta = dict(
                    playwright_page_methods=[
                        # Add JS to intercept and log redirects
                        PageMethod("add_init_script", """
                            window.addEventListener('beforeunload', function(e) {
                                console.log('Navigating away from page:', window.location.href);
                            });
                        """),
                        # Wait longer for page to fully load/process redirects
                        PageMethod("wait_for_load_state", "networkidle")
                        #PageMethod("wait_for_timeout", 10000),
                    ],
                    playwright=True,
                    # Force Scrapy to process the page even after redirect
                    handle_httpstatus_list=[301, 302]
                ),
                callback=self.parse,
                # Add browser-like headers
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Referer': 'https://www.booking.com/',
                    'DNT': '1',
                }
            )

    def parse(self, response):
        # Log actual URL after potential redirects
        self.logger.info(f"Processing URL: {response.url}")
        
        # Log status code
        self.logger.info(f"Status code: {response.status}")
        
        # Check if there was a redirect
        if response.request.meta.get('redirect_urls'):
            self.logger.info(f"Redirected from: {response.request.meta['redirect_urls']}")
        
        # Extract price from the specified class
        price = response.css(".prco-valign-middle-helper::text").get()
        hotel_name = response.css(".d2fee87262.pp-header__title::text").get()
        hotel_address = response.css(".a53cbfa6de.f17adf7576::text").get()

        # Try alternative selectors if the direct approach didn't work
        if not price:
            price = response.css(".prco-valign-middle-helper *::text").get()

        # Try even more selectors that might contain price information
        if not price:
            # Look for any element containing price information
            price = response.css("span.prco-price::text, .bui-price-display__value::text").get()

        # Clean up the extracted price
        if price:
            price = price.strip()
        
        self.logger.info(f"Extracted price: {price}")
        self.logger.info(f"Extracted hotel name: {hotel_name}")
        self.logger.info(f"Extracted hotel address: {hotel_address}")

        # Send notification to Telegram
        message = f"<b>📋 Booking Information</b>\n\n"
        if hotel_name:
            message += f"<b>🏨 Hotel:</b> {hotel_name}\n"
        if price:
            message += f"<b>💰 Price:</b> {price}\n"
        if hotel_address:
            message += f"<b>📍 Address:</b> {hotel_address}\n"
        #message += f"\n<b>🔗 Link:</b> {response.url}"
        
        self.send_telegram_message(message)
        
        
        yield {"price": price, "url": response.url, "status": response.status}
