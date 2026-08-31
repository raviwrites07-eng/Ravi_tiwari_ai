import os

from dotenv import load_dotenv
from groq import Groq

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from sentence_transformers import SentenceTransformer



# 1. Load environment variables


load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found")

if not qdrant_url:
    raise ValueError("QDRANT_URL not found")

if not qdrant_api_key:
    raise ValueError("QDRANT_API_KEY not found")



# 2. Create clients

groq_client = Groq(
    api_key=groq_api_key
)

qdrant_client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key
)

print("Qdrant client initialized successfully.")



# 3. Load embedding model


embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model is ready.")



# 4. Project constants


COLLECTION_NAME = "knowledge"
EMBEDDING_SIZE = 384
LLM_MODEL = "openai/gpt-oss-20b"



# 5. Knowledge data


knowledge_text = """
COMPANY LEAVE POLICY
1. Employees receive 24 days of paid annual leave each year.
2. Employees receive 12 days of paid sick leave each year.
3. Employees receive 6 days of casual leave each year.
4. Annual leave should normally be requested 5 working days in advance.
5. Employees may carry forward up to 10 unused annual leave days.
6. Sick leave and casual leave cannot be carried forward.
7. Eligible employees receive 26 weeks of maternity leave.
8. Eligible employees receive 10 working days of paternity leave.
9. Public holidays are separate from annual leave.
10. Leave requests must normally be submitted through the company's HR portal.
"""



# 6. Convert knowledge into documents


documents = [
    line.strip()
    for line in knowledge_text.splitlines()
    if line.strip()
]

print(f"Loaded {len(documents)} documents.")



# 7. Create / reset Qdrant collection


if qdrant_client.collection_exists(
    collection_name=COLLECTION_NAME
):
    print(
        f"Deleting existing collection '{COLLECTION_NAME}'..."
    )

    qdrant_client.delete_collection(
        collection_name=COLLECTION_NAME
    )


qdrant_client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=EMBEDDING_SIZE,
        distance=Distance.COSINE
    )
)

print(f"Created collection: {COLLECTION_NAME}")



# 8. Create embeddings for document

embeddings = embedding_model.encode(documents)

print(
    f"Generated {len(embeddings)} embeddings."
)

print(
    f"Embedding size: {len(embeddings[0])}"
)



# 9. Create Qdrant points


points = []

for i, embedding in enumerate(embeddings):

    point = PointStruct(
        id=i + 1,
        vector=embedding.tolist(),
        payload={
            "text": documents[i]
        }
    )

    points.append(point)



# 10. Upload points to Qdrant
#

qdrant_client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)

print(
    f"Uploaded {len(points)} documents to Qdrant."
)



# 11. Search function


def search(query, top_k=3):

    # Convert the user's query into an embedding
    query_vector = embedding_model.encode(query).tolist()

    # Search Qdrant for the most similar vectors
    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True
    ).points

    return results


# ---------------------------------------------------------
# 12. Test query
# ---------------------------------------------------------

query = "What is the company's leave policy?"

results = search(
    query,
    top_k=3
)


# ---------------------------------------------------------
# 13. Display retrieved results
# ---------------------------------------------------------

print("\nSearch Results:")

for result in results:

    print(
        f"Score: {result.score:.3f}"
    )

    print(
        result.payload["text"]
    )

    print()


# ---------------------------------------------------------
# 14. Create context from retrieved documents
# ---------------------------------------------------------

context = "\n".join(
    result.payload["text"]
    for result in results
)


# ---------------------------------------------------------
# 15. Send context to LLM
# ---------------------------------------------------------

def ask_llm(question, context):

    prompt = f"""
Answer the question using only the provided context.

Context:
{context}

Question:
{question}

Explain the answer clearly.

If the answer is not available in the context, say:

"I don't know based on the provided information."
"""

    response = groq_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


# ---------------------------------------------------------
# 16. Generate final answer
# ---------------------------------------------------------

answer = ask_llm(
    query,
    context
)


# ---------------------------------------------------------
# 17. Print final answer
# ---------------------------------------------------------

print("\nFinal Answer:")
print(answer)