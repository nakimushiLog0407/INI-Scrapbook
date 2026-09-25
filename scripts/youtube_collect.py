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


# ② YouTubeから動画をすべて取得
youtube_videos = []
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

        youtube_videos.append(
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


# ③ 既存のJSONを読み込む
existing_videos = {}

if DATA_FILE.exists():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        old_videos = json.load(file)

    for video in old_videos:
        existing_videos[video["video_id"]] = video


# ④ 新しい動画だけ追加する
new_count = 0

for video in youtube_videos:
    video_id = video["video_id"]

    if video_id not in existing_videos:
        video["checked"] = False
        video["scrapped"] = False

        existing_videos[video_id] = video
        new_count += 1


# ⑤ 既存動画に管理項目がなければ追加する
for video in existing_videos.values():
    if "checked" not in video:
        video["checked"] = False

    if "scrapped" not in video:
        video["scrapped"] = False


# ⑥ 日付順に並べる
videos = list(existing_videos.values())

videos.sort(
    key=lambda video: video["published_at"],
    reverse=True
)


# ⑦ dataフォルダを作成
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


# ⑧ JSONを保存
with DATA_FILE.open("w", encoding="utf-8") as file:
    json.dump(videos, file, ensure_ascii=False, indent=2)


print(f"YouTubeから取得した動画数: {len(youtube_videos)}件")
print(f"新しく追加した動画数: {new_count}件")
print(f"保存されている動画数: {len(videos)}件")
print(f"保存先: {DATA_FILE}")
