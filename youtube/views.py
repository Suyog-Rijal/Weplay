from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import requests
import re
import json


def format_number(num_str):
	try:
		num = int(num_str.replace(",", ""))
		if num >= 1_000_000_000:
			return f"{num/1_000_000_000:.1f}B"
		elif num >= 1_000_000:
			return f"{num/1_000_000:.1f}M"
		elif num >= 1_000:
			return f"{num/1_000:.1f}K"
		else:
			return str(num)
	except:
		return num_str


class SearchView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(tags=["Youtube"], description="Search for YouTube videos by query.")
	def get(self, request, query=None):
		max_results = 25
		if not query:
			return Response([], status=status.HTTP_200_OK)

		headers = {
			"User-Agent": "Mozilla/5.0",
			"Accept-Language": "en-US,en;q=0.9"
		}

		url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
		response = requests.get(url, headers=headers)
		if response.status_code != 200:
			return Response([], status=status.HTTP_200_OK)

		match = re.search(r"var ytInitialData = (.*?);</script>", response.text)
		if not match:
			return Response([], status=status.HTTP_200_OK)

		data = json.loads(match.group(1))
		results = []

		try:
			contents = (
				data["contents"]["twoColumnSearchResultsRenderer"]
				["primaryContents"]["sectionListRenderer"]["contents"][0]
				["itemSectionRenderer"]["contents"]
			)

			for item in contents:
				if "videoRenderer" not in item:
					continue
				video = item["videoRenderer"]

				channel_avatar = (
					video.get("channelThumbnailSupportedRenderers", {})
					.get("channelThumbnailWithLinkRenderer", {})
					.get("thumbnail", {})
					.get("thumbnails", [{}])[0]
					.get("url", "")
				)

				views_text = video.get("viewCountText", {}).get("simpleText", "N/A")
				if "views" in views_text:
					views_number = views_text.replace(" views", "").replace(" views", "")
					formatted_views = format_number(views_number)
				else:
					formatted_views = views_text

				video_data = {
					"id": video["videoId"],
					"title": video["title"]["runs"][0]["text"],
					"views": formatted_views,
					"duration": video.get("lengthText", {}).get("simpleText", "LIVE"),
					"channel": video["ownerText"]["runs"][0]["text"],
					"published_time": video.get("publishedTimeText", {}).get("simpleText", "N/A"),
					"channel_url": f"https://www.youtube.com{video['ownerText']['runs'][0]['navigationEndpoint']['browseEndpoint']['canonicalBaseUrl']}",
					"thumbnail": video["thumbnail"]["thumbnails"][-1]["url"],
					"channel_avatar": channel_avatar
				}
				results.append(video_data)
				if len(results) >= max_results:
					break

		except Exception as e:
			print("Parsing error:", e)
			return Response({'detail': 'Something went wrong.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		print("Number of results:", len(results))
		return Response(results, status=status.HTTP_200_OK)


class SelectView(APIView):
	permission_classes = [IsAuthenticated]
	pass
