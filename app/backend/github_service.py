import httpx

async def get_user_repos(username):

    url = f"https://api.github.com/users/{username}/repos"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    repos = response.json()

    filtered = []

    for repo in repos:

        if repo["fork"]:
            continue

        filtered.append({
            "name": repo["name"],
            "stars": repo["stargazers_count"],
            "commits_url": repo["commits_url"].replace("{/sha}", ""),
            "url": repo["clone_url"],
            "size": repo["size"],
            "language": repo["language"]
        })

    filtered.sort(key=lambda x: x["stars"] + x["size"], reverse=True)

    return filtered[:3]