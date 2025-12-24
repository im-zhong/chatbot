# 2025/12/22
# zhangzhong
# milvus as vector store
# use simple local sqlite as db for quick dev
from pymilvus import MilvusClient
from langchain_core.documents import Document
from langchain.embeddings.base import Embeddings
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
from pprint import pprint
from pymilvus.milvus_client.index import IndexParams

## set up vector database
# To create a local Milvus vector database, simply instantiate a MilvusClient by specifying a file name to store all data, such as "milvus_demo.db".


## pymilvus stype

# there are two ways to use pymilvus,

# 1. client.query(collection_name, xxx)
# 2. coll.query(xxx)
# which is the better way consider of best practise?

## client first
# Both work; pick one style and stick to it.

# MilvusClient.query(...): newer high-level client (v2.4+) geared toward “service-like” usage; simpler constructor (MilvusClient(uri=...)), convenient helpers (create_collection, create_index, load_collection, insert, search/query), and easy to mock for tests. Good default for small/medium projects and scripts.
# Collection.query(...): ORM-style API; more granular control, supports multi-collection/index management, partitions, hybrid search options, and closer to lower-level Milvus concepts. Better if you need advanced operations or already use the ORM style.
# Best practice: choose one interface per codebase/service to avoid mixing; use MilvusClient for straightforward apps, the Collection ORM when you need fine-grained Milvus features.


## TODO: async milvus client
# Yes. Pymilvus exposes async variants:
# client style: AsyncMilvusClient (client-style) mirrors MilvusClient with awaitable methods.
# ORM style: coll.search(..., _async=True).
# 综合感觉还是client style更好一点


# 我应该设计一个VectorStore的类
# 不应该叫做VectorStore，KnowledgeBase


class VectorStore:
    def __init__(self, embeddings: Embeddings) -> None:
        self.embeddings = embeddings

        # sqlite只能有一个进程hold！不支持
        # 好像创建了一个 .milvus_demo.db.lock 文件，文件锁
        # MilvusClient("milvus_demo.db") uses Milvus Lite with a local SQLite-backed file. SQLite enforces a file lock (.milvus_demo.db.lock) so only one process can open/write the DB at a time. If another process (e.g., a prior test run, another app, or an interactive shell) already has the DB open, new connections will fail with “Open local milvus failed” because the lock prevents concurrent access. In short: the lock file is created to serialize access; you can’t have multiple processes using that same local Milvus DB simultaneously.
        self.client = MilvusClient("milvus_demo.db")

        ## Create a Collection
        # In Milvus, we need a collection to store vectors and their associated metadata. You can think of it as a table in traditional SQL databases
        # When creating a collection, you can define schema and index params to configure vector specs such as dimensionality, index types and distant metrics.

        # 必须得加上schema，否则太乱了

        collection_name = "my_knowledges"
        if self.client.has_collection(collection_name):
            self.client.load_collection("my_knowledges")
            return
            # self.client.drop_collection(collection_name)
            # 因为我们使用zhipuai的embedding api，所以dim是2048
        self.client.create_collection(
            collection_name,
            schema=CollectionSchema(
                fields=[
                    # Use auto generated id as primary key
                    FieldSchema(
                        name="id", dtype=DataType.INT64, is_primary=True, auto_id=True
                    ),
                    # Store the original text to retrieve based on semantically distance
                    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096),
                    # Milvus now supports both sparse and dense vectors,
                    # we can store each in a separate field to conduct hybrid search on both vectors
                    # FieldSchema(name="sparse_vector", dtype=DataType.SPARSE_FLOAT_VECTOR),
                    # pymilvus.exceptions.MilvusException: <MilvusException: (code=700, message=No index found in field [vector]: index not found)>
                    # 还必须得创建index。。。
                    # https://milvus.io/docs/index-explained.md
                    # 小/中规模（几十万级以内）通常优先选 HNSW 或直接 FLAT/IVF_FLAT：
                    # HNSW：Milvus 默认推荐，小到中规模时内存占用可控，查准率高、延迟低，调 M、efConstruction（建索引）、ef（查询）权衡速度/精度。
                    # FLAT / IVF_FLAT：精度最高，适合数据量不大、延迟可接受或需要做评测基线；IVF_FLAT 通过 nlist/nprobe 在精度与速度间折中。
                    # 不建议 PQ/IVF_PQ 等压缩索引，除非内存压力明显。
                    # 如果你只有几千～几万向量，直接 FLAT/IVF_FLAT 简单可靠；再大一些（10万+）可用 HNSW 获取更好延迟。
                    FieldSchema(
                        name="vector",
                        dtype=DataType.FLOAT_VECTOR,
                        dim=2048,
                        # index_type="FLAT",
                        # metric_type="IP",
                    ),
                    FieldSchema(name="metadata", dtype=DataType.JSON),
                ]
            ),
        )
        # self.client.create_index(
        #     collection_name="my_knowledges",
        #     field_name="vector",
        #     index_params={
        #         "index_type": "HNSW",
        #         "metric_type": "IP",
        #         "params": {"M": 16, "efConstruction": 200},
        #     },
        # )
        # 这么麻烦？
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            # index_type="HNSW",
            index_type="FLAT",
            metric_type="IP",  # or "L2"
            # params={"M": 16, "efConstruction": 200},
        )

        self.client.create_index(
            collection_name=collection_name, index_params=index_params
        )

        self.client.load_collection("my_knowledges")

        # TODO: could create index for better performance
        # TODO： Before searching, call coll.load() (loads index/data into memory)
        self.client.load_collection(collection_name=collection_name)
        # create index
        # coll = Collection(name=collection_name, schema=)

    # https://docs.langchain.com/oss/javascript/langchain/knowledge-base#1-documents-and-document-loaders
    async def aadd_documents(
        self, documents: list[Document], collection_name="my_knowledges"
    ):
        # 这里咱们使用langchain的embedding function来做embed的工作
        texts = [document.page_content for document in documents]
        # 这里一次性可以做的并发数量是有限制的
        # zhipu的限制是64
        # 那么可以简单的做成一个for
        vectors: list[list[float]] = []
        step = 64
        for i in range(0, len(texts), step):
            vectors.extend(
                await self.embeddings.aembed_documents(texts=texts[i : i + step])
            )

        # store the documents, metadata, vectors into milvus
        # construct data to be inserted into milvus

        # milvis document id only could be a integer
        data = [
            {
                # "id": documents[i].id,
                # "id": i,
                "vector": vectors[i],
                "text": texts[i],
                "metadata": documents[i].metadata,
            }
            for i in range(len(documents))
        ]
        # TODO: check for async operations
        res = self.client.insert(collection_name, data=data)

    def delete_documents(self, ids: list[str]):
        pass

    # 还需要一个函数来展示collection所有的内容，用来调试

    # TODO: 还可以根据milvus支持的参数，来设计查询的参数
    def hybrid_search(self, query: str):
        pass

    async def semantic_search(
        self, query: str, collection_name: str = "my_knowledges"
    ) -> list[str]:
        # 目前只实现了embedding 所以只实现这个就行
        # first, embed the query and get the embedding
        query_embedding = await self.embeddings.aembed_query(text=query)

        res = self.client.search(
            collection_name=collection_name,
            data=[query_embedding],
            anns_field="vector",  # your vector field name
            # param={
            #     "metric_type": "IP",
            #     "params": {"ef": 64},
            # },  # or L2; params depend on index
            limit=5,  # top-k
            output_fields=["id", "text", "metadata"],  # fields to return
            filter="",  # optional boolean filter on scalar fields
            # consistency_level="Eventually",
        )
        print(f"semantic search by {query}, get: {res}")

        return [hit.entity.get("text") for hits in res for hit in hits]

    def full_text_search(self, query: str):
        #
        pass

    # 还可以实现一种最简单的filter
    def select_documents(
        self, filter_expr: str, collection_name: str = "my_knowledges"
    ) -> None:
        results = self.client.query(
            collection_name=collection_name,
            filter=filter_expr,
            output_fields=["id", "text", "metadata"],
            limit=50,  # how many rows to return
            offset=0,  # optional pagination
            # consistency_level="Strong",  # or "Strong" per your needs
        )
        for row in results:
            pprint(row)
