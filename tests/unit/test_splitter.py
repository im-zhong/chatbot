from chatbot.defs import get_testing_text
from chatbot.splitter import get_chinese_splitter


def test_chinese_splitter():
    # TODO: split的好差呀！把chunk size调小一点，感觉还行
    splitter = get_chinese_splitter()
    text = get_testing_text()

    splitted_texts = splitter.split_text(text)
    # 写到文件里面更容易观察
    with open("docs/splitted_texts.tmp.txt", mode="w", encoding="utf-8") as file:
        for text in splitted_texts:
            file.write(text)
            file.write("\n===============================================\n")
