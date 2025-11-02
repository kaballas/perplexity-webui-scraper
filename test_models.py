import requests

headers = {
    "Authorization": "Bearer eVyRP_j8tCcDTvzAV0x7aNqSuHETG9rxV6C7BXqxi2X8NoHUEwybJa_ros0JgdCmjY_IHohKRfsZVZSDk_tSWQ",
    "Content-Type": "application/json"
}

response = requests.get("https://portal.qwen.ai/v1/models", headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {response.headers}")
print(f"Response Text: {response.text}")
print(f"Content Length: {len(response.content)}")

if response.status_code == 200 and response.text:
    print(response.json())
else:
    print(f"Error: Status {response.status_code}, Empty body")
