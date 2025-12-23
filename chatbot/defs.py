#


def get_testing_text() -> str:
    with open("docs/DiGraph.txt", encoding="utf-8") as file:
        return file.read()
