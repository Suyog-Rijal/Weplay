import json
import time
import random
import logging
import csv
import re
from io import StringIO
from dataclasses import dataclass
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, TimeoutError
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class VideoData:
	video_id: str
	title: str
	views: str
	duration: str
	channel: str
	published: str
	thumbnail: str
	description: str = ""
	channel_id: str = ""
	subscribers: str = ""
	likes: str = ""
	url: str = ""

	def __post_init__(self):
		self.url = f"https://www.youtube.com/watch?v={self.video_id}"

class YouTubeScraperMadness:
	def __init__(self):
		self.ua = UserAgent()

	def extract_yt_initial_data(self, html: str) -> Dict:
		"""Extract ytInitialData with regex and BeautifulSoup fallbacks"""
		# Save HTML for debugging
		with open(f"debug_html_{int(time.time())}.html", "w", encoding="utf-8") as f:
			f.write(html)
		logger.info("Saved HTML for debugging")

		# Regex patterns for ytInitialData
		patterns = [
			r"var ytInitialData = ({.*?});</script>",
			r"window\[\"ytInitialData\"\] = ({.*?});",
			r"ytInitialData\s*=\s*({.*?});",
		]

		for pattern in patterns:
			match = re.search(pattern, html, re.DOTALL)
			if match:
				try:
					return json.loads(match.group(1))
				except json.JSONDecodeError as e:
					logger.warning(f"Regex pattern {pattern} JSON decode error: {e}")
					continue

		# Fallback to BeautifulSoup
		soup = BeautifulSoup(html, 'html.parser')
		scripts = soup.find_all('script')
		for script in scripts:
			if script.string and 'ytInitialData' in script.string:
				try:
					# Extract JSON content
					start = script.string.find('ytInitialData') + 13
					json_str = script.string[start:].strip()
					if json_str.startswith('='):
						json_str = json_str[1:].strip()
					end = json_str.rfind('};') + 2
					json_str = json_str[:end]
					return json.loads(json_str)
				except json.JSONDecodeError as e:
					logger.warning(f"BeautifulSoup JSON decode error: {e}")
					continue

		raise RuntimeError("ytInitialData not found in HTML")

	def extract_video_data(self, video_renderer: Dict) -> Optional[VideoData]:
		"""Extract comprehensive video data from renderer"""
		try:
			video_id = video_renderer.get("videoId")
			if not video_id:
				return None

			title_runs = video_renderer.get("title", {}).get("runs", [])
			title = "".join(run.get("text", "") for run in title_runs) if title_runs else ""

			views = "N/A"
			view_count = video_renderer.get("viewCountText")
			if view_count:
				if "simpleText" in view_count:
					views = view_count["simpleText"]
				elif "runs" in view_count:
					views = "".join(run.get("text", "") for run in view_count["runs"])

			duration_text = video_renderer.get("lengthText", {})
			duration = duration_text.get("simpleText", "LIVE") if duration_text else "LIVE"

			owner_text = video_renderer.get("ownerText", {}).get("runs", [])
			channel = owner_text[0].get("text", "") if owner_text else ""

			channel_id = ""
			if owner_text:
				nav_endpoint = owner_text[0].get("navigationEndpoint", {})
				channel_endpoint = nav_endpoint.get("commandMetadata", {}).get("webCommandMetadata", {})
				channel_url = channel_endpoint.get("url", "")
				if "/channel/" in channel_url:
					channel_id = channel_url.split("/channel/")[-1]

			published_text = video_renderer.get("publishedTimeText", {})
			published = published_text.get("simpleText", "N/A") if published_text else "N/A"

			thumbnails = video_renderer.get("thumbnail", {}).get("thumbnails", [])
			thumbnail = thumbnails[-1].get("url", "") if thumbnails else ""

			description_snippet = video_renderer.get("detailedMetadataSnippets", [])
			description = ""
			if description_snippet:
				desc_runs = description_snippet[0].get("snippetText", {}).get("runs", [])
				description = "".join(run.get("text", "") for run in desc_runs)

			return VideoData(
				video_id=video_id,
				title=title,
				views=views,
				duration=duration,
				channel=channel,
				channel_id=channel_id,
				published=published,
				thumbnail=thumbnail,
				description=description
			)
		except Exception as e:
			logger.error(f"Error extracting video data: {e}")
			return None

	def extract_videos_from_contents(self, contents: List[Dict]) -> List[VideoData]:
		"""Extract videos from various content types"""
		videos = []
		for item in contents:
			if "videoRenderer" in item:
				video = self.extract_video_data(item["videoRenderer"])
				if video:
					videos.append(video)
			elif "compactVideoRenderer" in item:
				video = self.extract_video_data(item["compactVideoRenderer"])
				if video:
					videos.append(video)
			elif "gridVideoRenderer" in item:
				video = self.extract_video_data(item["gridVideoRenderer"])
				if video:
					videos.append(video)
			elif "itemSectionRenderer" in item:
				section_contents = item["itemSectionRenderer"].get("contents", [])
				videos.extend(self.extract_videos_from_contents(section_contents))
		return videos

	def scrape(self, query: str, max_results: int = 100, max_retries: int = 3) -> List[VideoData]:
		"""Scrape YouTube search results using Playwright"""
		all_videos = []
		retry_count = 0

		with sync_playwright() as p:
			browser = p.chromium.launch(headless=True)
			context = browser.new_context(
				user_agent=self.ua.random,
				viewport={'width': 1280, 'height': 720}
			)
			page = context.new_page()

			while retry_count < max_retries:
				try:
					logger.info(f"Fetching page for query: '{query}' (attempt {retry_count + 1})")
					url = f"https://www.youtube.com/results?search_query={query}&sp=CAI%253D"
					page.goto(url, timeout=60000)
					page.wait_for_load_state('networkidle', timeout=60000)

					html = page.content()
					if "captcha" in html.lower() or "unusual traffic" in html.lower():
						logger.error("CAPTCHA or unusual traffic detected")
						with open(f"captcha_html_{int(time.time())}.html", "w", encoding="utf-8") as f:
							f.write(html)
						raise RuntimeError("CAPTCHA detected")

					yt_data = self.extract_yt_initial_data(html)
					contents = (yt_data.get("contents", {})
					            .get("twoColumnSearchResultsRenderer", {})
					            .get("primaryContents", {})
					            .get("sectionListRenderer", {})
					            .get("contents", []))

					videos = self.extract_videos_from_contents(contents)
					all_videos.extend(videos)
					logger.info(f"Extracted {len(videos)} videos")
					break

				except TimeoutError as e:
					logger.error(f"Timeout error: {e}")
					retry_count += 1
					if retry_count < max_retries:
						time.sleep(2 ** retry_count + random.uniform(0, 1))
					continue
				except Exception as e:
					logger.error(f"Fetch attempt {retry_count + 1} failed: {e}")
					retry_count += 1
					if retry_count < max_retries:
						time.sleep(2 ** retry_count + random.uniform(0, 1))
					else:
						logger.error("Max retries reached")
						break

			browser.close()

		logger.info(f"Scraping completed! Total videos: {len(all_videos)}")
		return all_videos[:max_results]

	def export_results(self, videos: List[VideoData], format: str = "json") -> str:
		"""Export results in various formats"""
		if not videos:
			return "[]"
		if format.lower() == "json":
			return json.dumps([video.__dict__ for video in videos], indent=2, ensure_ascii=False)
		elif format.lower() == "csv":
			output = StringIO()
			writer = csv.DictWriter(output, fieldnames=videos[0].__dict__.keys())
			writer.writeheader()
			for video in videos:
				writer.writerow(video.__dict__)
			return output.getvalue()
		else:
			return str(videos)

def main():
	scraper = YouTubeScraperMadness()

	print("🚀 YOUTUBE SCRAPER - ABSOLUTE MADNESS MODE 🚀")
	print("=" * 60)

	query = input("Enter search query: ").strip()
	if not query:
		query = "tmkoc"

	max_results = input("How many videos (default 100): ").strip()
	max_results = int(max_results) if max_results.isdigit() else 100

	export_format = input("Export format (json/csv/console) [default: console]: ").strip().lower()
	if not export_format:
		export_format = "console"

	print(f"\n🎯 Searching for: '{query}'")
	print(f"📊 Target results: {max_results}")
	print(f"📁 Export format: {export_format}")
	print("-" * 60)

	start_time = time.time()
	results = scraper.scrape(query, max_results)
	end_time = time.time()

	print(f"\n✅ MISSION FUCKING ACCOMPLISHED!")
	print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
	print(f"📹 Videos found: {len(results)}")
	print(f"📈 Success rate: {len(results) / max_results * 100:.1f}%")
	print("=" * 60)

	if export_format == "console":
		for i, video in enumerate(results, 1):
			print(f"\n{i}. 📺 {video.title}")
			print(f"   🆔 ID: {video.video_id}")
			print(f"   👀 Views: {video.views}")
			print(f"   ⏰ Duration: {video.duration}")
			print(f"   📺 Channel: {video.channel}")
			print(f"   📅 Published: {video.published}")
			print(f"   🔗 URL: {video.url}")
			if video.description:
				print(f"   📝 Description: {video.description[:100]}...")
	else:
		output = scraper.export_results(results, export_format)
		filename = f"youtube_results_{int(time.time())}.{export_format}"
		with open(filename, 'w', encoding='utf-8') as f:
			f.write(output)
		print(f"📁 Results exported to: {filename}")

if __name__ == "__main__":
	main()