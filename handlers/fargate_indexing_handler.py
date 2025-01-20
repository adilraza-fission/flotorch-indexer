from chunking.fixedsize_chunking import FixedSizeChunker
from embedding.bedrock_embedding import TitanV2Embedding
# from embedding.llama_embedding import LlamaEmbedding
from indexing.indexing import Index
from reader.pdf_reader import PDFReader
from storage.db.vector import OpenSearchClient
from storage.local_storage import LocalStorageProvider
from storage.s3_storage import S3StorageProvider
from config.env_config_provider import EnvConfigProvider
from config.config import Config


def main():
    env_config_provider = EnvConfigProvider()
    config = Config(env_config_provider)
    storage_provider = S3StorageProvider('flotorch-data-677276078734-us-east-1-qgp1f5')
    pdf_reader = PDFReader(storage_provider)
    chunker = FixedSizeChunker(128, 5)
    embedder = TitanV2Embedding('amazon.titan-embed-text-v2:0', config.get_region(), 256, True)
    index = Index(pdf_reader, chunker, embedder)
    embeddings = index.index(path="C:\\Projects\\refactor\\FloTorch\\medical_abstracts_100_169Kb.pdf")

    open_search_client = OpenSearchClient(
        host=config.get_opensearch_host(),
        port=config.get_opensearch_port(),
        username=config.get_opensearch_username(),
        password=config.get_opensearch_password(),
        index=config.get_opensearch_index()
    )

    # should this be included in Utils?
    bulk_data = []
    for embedding in embeddings:
        bulk_data.append({"index": {"_index": config.get_opensearch_index()}})
        bulk_data.append({
            "embedding": embedding.embeddings,
            "metadata": {
                "input_tokens": embedding.metadata.input_tokens,
                "latency_ms": embedding.metadata.latency_ms
            }
        })

    open_search_client.write_bulk(body=bulk_data)


if __name__ == "__main__":
    main()
