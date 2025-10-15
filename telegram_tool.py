#!/usr/bin/env python3
#By r0otk3r

import asyncio
import argparse
import json
import random
from telethon import TelegramClient
from telethon.errors import (
    UsernameNotOccupiedError, 
    UsernameInvalidError, 
    FloodWaitError,
    PeerIdInvalidError,
    RPCError
)
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import ChannelParticipantsSearch

# Your credentials from https://my.telegram.org/apps
API_ID = 89765782  # Replace with your actual API ID
API_HASH = '66c0898366d87a42123tdav5fe6vs45'  # Replace with your actual API Hash

# SAFETY SETTINGS - ADJUST THESE CAREFULLY
CONCURRENCY_LIMIT = 1  # Keep at 1 for maximum safety
MIN_DELAY = 3.0        # Minimum delay between requests
MAX_DELAY = 8.0        # Maximum delay between requests (adds randomness)
MAX_REQUESTS_PER_HOUR = 100  # Conservative limit
MAX_MESSAGES_PER_DAY = 50    # Very conservative for messaging

class TelegramTool:
    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash
        self.request_count = 0
        self.message_count = 0
        
    def _get_random_delay(self):
        """Return random delay to avoid pattern detection"""
        return random.uniform(MIN_DELAY, MAX_DELAY)
    
    async def _safety_delay(self):
        """Apply delay between requests"""
        delay = self._get_random_delay()
        await asyncio.sleep(delay)
    
    async def _check_rate_limit(self, operation_type="request"):
        """Check if we're approaching rate limits"""
        if operation_type == "message":
            if self.message_count >= MAX_MESSAGES_PER_DAY:
                print(f"[SAFETY] Daily message limit ({MAX_MESSAGES_PER_DAY}) reached. Stopping.")
                return False
            self.message_count += 1
        else:
            if self.request_count >= MAX_REQUESTS_PER_HOUR:
                print(f"[SAFETY] Hourly request limit ({MAX_REQUESTS_PER_HOUR}) reached. Consider pausing.")
                # You might want to implement hourly reset logic here
            self.request_count += 1
        return True

    async def check_usernames(self, usernames_file, output_file):
        """Check if Telegram usernames exist"""
        try:
            with open(usernames_file, 'r') as f:
                usernames = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"File not found: {usernames_file}")
            return

        if len(usernames) > MAX_REQUESTS_PER_HOUR:
            print(f"[WARNING] You're attempting to check {len(usernames)} usernames, but hourly limit is {MAX_REQUESTS_PER_HOUR}")
            proceed = input("Continue anyway? (y/N): ").lower().strip()
            if proceed != 'y':
                return

        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        results = []

        async with TelegramClient('session', self.api_id, self.api_hash) as client:
            for i, username in enumerate(usernames):
                if not await self._check_rate_limit():
                    print("[SAFETY] Rate limit approached. Stopping early.")
                    break
                    
                print(f"[PROGRESS] Processing {i+1}/{len(usernames)}")
                result = await self._check_single_username(client, username, semaphore)
                results.append(result)
                
                # Save progress periodically
                if i % 10 == 0:
                    with open(output_file, 'w') as out_file:
                        json.dump(results, out_file, indent=4)

        with open(output_file, 'w') as out_file:
            json.dump(results, out_file, indent=4)
        print(f"Done! Results saved to {output_file}")

    async def _check_single_username(self, client, username, semaphore):
        result = {
            "username": username,
            "status": "",
            "owner": None,
            "error": None
        }

        async with semaphore:
            try:
                # Skip obviously invalid usernames
                if not username or len(username) < 5 or not username.replace('_', '').isalnum():
                    result["status"] = "invalid"
                    return result
                    
                entity = await client.get_entity(username)
                name = getattr(entity, 'first_name', None) or getattr(entity, 'title', 'N/A')
                print(f"[VALID] @{username} exists - Owner: {name}")
                result["status"] = "exists"
                result["owner"] = name
            except UsernameNotOccupiedError:
                print(f"[NOT FOUND] @{username} does not exist.")
                result["status"] = "not_found"
            except UsernameInvalidError:
                print(f"[INVALID] @{username} is invalid.")
                result["status"] = "invalid"
            except ValueError:
                print(f"[UNKNOWN] @{username} not found.")
                result["status"] = "unknown"
            except FloodWaitError as e:
                print(f"[FLOOD WAIT] Need to wait {e.seconds} seconds. Consider increasing delays.")
                result["status"] = "flood_wait"
                result["error"] = f"Flood wait: {e.seconds} seconds"
                await asyncio.sleep(e.seconds + 5)
            except Exception as e:
                print(f"[ERROR] Error on @{username}: {e}")
                result["status"] = "error"
                result["error"] = str(e)

            await self._safety_delay()
        return result

    async def get_group_members(self, group_username, output_file):
        """Get usernames from a Telegram group - USE SPARINGLY"""
        print("[WARNING] Group member scraping is high-risk. Use cautiously.")
        
        async with TelegramClient('session', self.api_id, self.api_hash) as client:
            try:
                group = await client.get_entity(group_username)
                print(f"[INFO] Getting members from group: {group.title}")

                usernames = set()
                total = 0
                batch_count = 0

                async for user in client.iter_participants(group, filter=ChannelParticipantsSearch('')):
                    if not await self._check_rate_limit():
                        print("[SAFETY] Rate limit approached. Stopping early.")
                        break
                        
                    total += 1
                    if user.username:
                        usernames.add(user.username.lower())

                    if total % 50 == 0:  # Reduced from 100
                        batch_count += 1
                        print(f"[INFO] Checked {total} members so far...")
                        
                        # Longer delay every few batches
                        if batch_count % 3 == 0:
                            print("[SAFETY] Taking a longer break...")
                            await asyncio.sleep(10)
                        else:
                            await self._safety_delay()

            except FloodWaitError as e:
                print(f"[WAIT] Flood wait: sleeping for {e.seconds} seconds...")
                await asyncio.sleep(e.seconds + 10)  # Extra buffer
            except Exception as e:
                print(f"[ERROR] Error: {e}")
                return

            print(f"[SUCCESS] Total usernames collected: {len(usernames)}")

            with open(output_file, 'w', encoding='utf-8') as f:
                for username in sorted(usernames):
                    f.write(f"{username}\n")

            print(f"[SUCCESS] Usernames saved to '{output_file}'")

    async def send_messages(self, usernames_file, message_text):
        """Send messages to a list of Telegram usernames - HIGH RISK"""
        print("[WARNING] Bulk messaging is HIGH RISK and likely to get accounts banned.")
        print(f"Limit: {MAX_MESSAGES_PER_DAY} messages per day.")
        
        confirmation = input("Are you sure you want to continue? (yes/NO): ").lower().strip()
        if confirmation != 'yes':
            print("Operation cancelled.")
            return

        try:
            with open(usernames_file, 'r') as file:
                usernames = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"[ERROR] File '{usernames_file}' not found.")
            return

        if len(usernames) > MAX_MESSAGES_PER_DAY:
            print(f"[SAFETY] Truncating to {MAX_MESSAGES_PER_DAY} messages (daily limit)")
            usernames = usernames[:MAX_MESSAGES_PER_DAY]

        async with TelegramClient('session', self.api_id, self.api_hash) as client:
            for i, username in enumerate(usernames):
                if not await self._check_rate_limit("message"):
                    break
                    
                print(f"[PROGRESS] Message {i+1}/{len(usernames)}")
                await self._send_single_message(client, username, message_text)
                
                # Longer, random delays for messaging
                await asyncio.sleep(random.uniform(10, 30))

    async def _send_single_message(self, client, username, message):
        try:
            entity = await client.get_entity(username)
            await client(SendMessageRequest(peer=entity, message=message))
            print(f"[SUCCESS] Message sent to @{username}")
        except UsernameNotOccupiedError:
            print(f"[ERROR] Username @{username} does not exist.")
        except UsernameInvalidError:
            print(f"[ERROR] Username @{username} is invalid.")
        except PeerIdInvalidError:
            print(f"[ERROR] Cannot send message to @{username} (user has privacy settings).")
        except FloodWaitError as e:
            print(f"[WAIT] Rate limited. Must wait {e.seconds} seconds.")
            await asyncio.sleep(e.seconds + 10)  # Extra buffer
        except RPCError as e:
            print(f"[ERROR] RPCError while messaging @{username}: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error for @{username}: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Safer Telegram Tool")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Check usernames command
    check_parser = subparsers.add_parser('check', help='Check if usernames exist')
    check_parser.add_argument('--usernames', required=True, help='Path to usernames file')
    check_parser.add_argument('--output', default='results.json', help='Output JSON file')

    # Get group members command
    get_parser = subparsers.add_parser('get-members', help='Get members from a group')
    get_parser.add_argument('--group', required=True, help='Group username')
    get_parser.add_argument('--output', default='usernames.txt', help='Output file')

    # Send messages command
    send_parser = subparsers.add_parser('send', help='Send messages to usernames')
    send_parser.add_argument('--usernames', required=True, help='Path to usernames file')
    send_parser.add_argument('--message', required=True, help='Message to send')

    args = parser.parse_args()

    tool = TelegramTool(API_ID, API_HASH)

    if args.command == 'check':
        await tool.check_usernames(args.usernames, args.output)
    elif args.command == 'get-members':
        await tool.get_group_members(args.group, args.output)
    elif args.command == 'send':
        await tool.send_messages(args.usernames, args.message)
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
