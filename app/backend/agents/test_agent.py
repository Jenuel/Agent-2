import os

def detect_tests(path):

    test_files = 0

    for root, dirs, files in os.walk(path):

        for file in files:

            if "test" in file.lower():
                test_files += 1

    score = min(test_files / 5, 10)

    return round(score, 2)