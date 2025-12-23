# https://docs.langchain.com/oss/python/integrations/splitters#document-structure-based
# lagnchain直接提供一个markdown的splitter哎 感觉可以尝试一下
# 默认情况下，都推荐用这个 https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter
# 这里文档还讲了中文该怎么处理。我觉得就用这个就行了


# 我们要上传知识库，做QA，
# 上传知识库，一个文档，需要一个文档的id作为filter，在做semantic search的时候，就可以根据这个文档id进行过滤
# 我们假设输入的文本都是中文的，方便测试

from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_chinese_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=300,  # adjust per model/tokenizer
        chunk_overlap=50,
        separators=[
            "\n\n",  # paragraphs
            "\n",
            "。",
            "！",
            "？",  # Chinese sentences
            ".",
            "!",
            "?",  # English sentences
            "；",
            ";",
            "，",
            ",",
            "、",
            "：",
            ":",
            " ",  # words
            "",  # single characters fallback
        ],
    )
