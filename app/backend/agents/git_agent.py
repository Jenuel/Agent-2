from git import Repo

def analyze_git(path):

    repo = Repo(path)

    commits = list(repo.iter_commits())

    commit_count = len(commits)

    descriptive = 0

    for commit in commits[:50]:

        msg = commit.message.lower()

        if len(msg.split()) > 3:
            descriptive += 1

    quality_ratio = descriptive / max(len(commits[:50]), 1)

    commit_score = min(commit_count / 100, 10)

    message_score = quality_ratio * 10

    return round((commit_score + message_score) / 2, 2)