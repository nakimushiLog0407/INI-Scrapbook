import os
import json
import urllib.parse
import urllib.request
from pathlib import Path

API_KEY = os.environ["YOUTUBE_API_KEY"]
CHANNEL_ID = "UCc-itdQHxLvUlPrDxIiSJrA"

DATA_FILE = Path("data/youtube_videos.json")


def youtube_api(endpoint, params):
    params["key"] = API_KEY

    url = "https://www.googleapis.com/youtube/v3/" + endpoint
    url += "?" + urllib.parse.urlencode(params)

    with urllib.request.urlopen(url) as response:
        return json.load(response)


# ① INIのチャンネル情報から「アップロード動画一覧」のIDを取得
channel_data = youtube_api(
    "channels",
    {
        "part": "contentDetails",
        "id": CHANNEL_ID,
    },
)

uploads_playlist_id = (
    channel_data["items"][0]
    ["contentDetails"]
    ["relatedPlaylists"]
    ["uploads"]
)


# ② アップロード動画をすべて取得
videos = []
page_token = None

while True:
    params = {
        "part": "snippet,contentDetails",
        "playlistId": uploads_playlist_id,
        "maxResults": 50,
    }

    if page_token:
        params["pageToken"] = page_token

    video_data = youtube_api("playlistItems", params)

    for item in video_data["items"]:
        video_id = item["contentDetails"]["videoId"]

        videos.append(
            {
                "video_id": video_id,
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
        )

    page_token = video_data.get("nextPageToken")

    if not page_token:
        break


# ③ dataフォルダを作成
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


# ④ JSONファイルとして保存
with DATA_FILE.open("w", encoding="utf-8") as file:
    json.dump(videos, file, ensure_ascii=False, indent=2)


print(f"{len(videos)}件の動画を取得しました。")
print(f"保存先: {DATA_FILE}")
