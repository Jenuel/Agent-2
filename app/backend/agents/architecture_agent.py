def detect_architecture(path):

    indicators = {
        "docker": False,
        "api": False,
        "database": False,
        "frontend": False
    }

    for root, dirs, files in os.walk(path):

        for file in files:

            f = file.lower()

            if "dockerfile" in f:
                indicators["docker"] = True

            if "requirements.txt" in f or "package.json" in f:
                indicators["api"] = True

            if "models.py" in f or "schema" in f:
                indicators["database"] = True

            if "react" in root.lower():
                indicators["frontend"] = True

    score = sum(indicators.values()) / len(indicators) * 10

    return round(score, 2)