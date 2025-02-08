import sys
import os

# on Linux the parent directory isn't automatically included for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from concierge_backend_lib.opensearch import get_client, get_documents

parser = argparse.ArgumentParser()
parser.add_argument(
    "-c",
    "--collection",
    required=True,
    help="Collection containing the vectorized data.",
)
args = parser.parse_args()

collection_name = args.collection

client = get_client()
documents = get_documents(client, collection_name)

for document in documents:
    print(
        f"id: {document['id']}, source: {document['source']}, type: {document['type']}, pages: {document['page_count']}, vectors: {document['vector_count']}"
    )
