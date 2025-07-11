import os
import json
from datetime import datetime
from pathlib import Path
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import MessageMediaPhoto
import asyncio

from .logger import get_logger

logger = get_logger("telegram_scraper")

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

# Folder for session file
SESSION_NAME = "kara_scraper"

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


async def scrape_channel(channel_url: str, limit: int = 100):
    """Scrape messages from a Telegram channel with media download support."""
    try:
        await client.start()
        logger.info(f"Scraping channel: {channel_url}")

        entity = await client.get_entity(channel_url)
        messages = []
        today = datetime.now().strftime("%Y-%m-%d")
        out_dir = Path(f"data/raw/{today}/{entity.username}")
        out_dir.mkdir(parents=True, exist_ok=True)

        # Create images directory if needed
        img_path = out_dir / "images"
        img_path.mkdir(exist_ok=True)

        # Process messages asynchronously
        message_count = 0
        async for message in client.iter_messages(entity, limit=limit):
            try:
                msg = message.to_dict()
                messages.append(msg)
                message_count += 1

                # Save images if present
                if message.media and isinstance(message.media, MessageMediaPhoto):
                    filename = f"{message.id}.jpg"
                    try:
                        await message.download_media(file=str(img_path / filename))
                        logger.debug(f"Downloaded image: {filename}")
                    except Exception as media_error:
                        logger.warning(f"Failed to download media {filename}: {str(media_error)}")

                # Periodic progress logging
                if message_count % 10 == 0:
                    logger.info(f"Processed {message_count} messages...")

            except Exception as msg_error:
                logger.error(f"Error processing message {message.id}: {str(msg_error)}")
                continue

        # Save JSON dump
        json_file = out_dir / "messages.json"
        try:
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2,default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o))
            logger.info(f"Successfully saved {len(messages)} messages to {json_file}")
        except Exception as json_error:
            logger.error(f"Failed to save JSON file: {str(json_error)}")
            raise

        return messages

    except Exception as e:
        logger.error(f"Error scraping channel {channel_url}: {str(e)}")
        raise
    finally:
        await client.disconnect()


def main():
    channels = [
        "https://t.me/lobelia4cosmetics",
        "https://t.me/tikvahpharma",
        "https://t.me/CheMed123",
        "https://t.me/Thequorachannel",
        "https://t.me/tenamereja",
        "https://t.me/HakimApps_Guideline",
        "https://t.me/lobelia4cosmetics",
        # Add more here
    ]

    with client:
        for ch in channels:
            client.loop.run_until_complete(scrape_channel(ch))


if __name__ == "__main__":
    main()
