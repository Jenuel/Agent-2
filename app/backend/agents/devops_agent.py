def detect_ci(path):

    ci_path = os.path.join(path, ".github", "workflows")

    if os.path.exists(ci_path):

        files = os.listdir(ci_path)

        return min(len(files) * 3, 10)

    return 0