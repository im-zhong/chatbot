from pymilvus import MilvusClient


# ok! 最起码证明local模式的milvus是可以创建索引的
def test_milvus():
    client = MilvusClient(uri="1milvus_demo.db")

    if not client.has_collection("my_knowledges"):
        client.create_collection("my_knowledges", dimension=2048, metric_type="IP")

    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        # index_type="HNSW",
        index_type="FLAT",
        metric_type="IP",
        # params={"M": 16, "efConstruction": 200},
        index_name="vec_idx",
    )
    client.create_index(collection_name="my_knowledges", index_params=index_params)
    client.load_collection("my_knowledges")

    print(
        client.describe_index(
            collection_name="my_knowledges",
            index_name="vec_idx",
        )
    )  # should show index on vector, state Finished
