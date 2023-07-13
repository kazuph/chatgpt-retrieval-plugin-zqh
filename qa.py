from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.retrievers import ChatGPTPluginRetriever
import readline

retriever = ChatGPTPluginRetriever(
    url="http://localhost:3333", bearer_token="35c4afe3b6aa31bdf621e8cfbe008cadd940fe365ab8e01409e46b57222b7023")

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
# llm = ChatOpenAI(model_name="gpt-4", temperature=0)

chain = RetrievalQA.from_chain_type(llm=llm,
                                    # chain_type="map_rerank",
                                    # chain_type="map_reduce",
                                    # chain_type="refine",
                                    chain_type="stuff",
                                    retriever=retriever,
                                    return_source_documents=True)

while True:
    query = input("query: ")
    answer = chain({'query': query})
    print(answer['result'])

    docs = answer["source_documents"]
    # TypeError: 'Document' object is not subscriptable

    if docs is None:
        continue
    else:
        for doc in docs:
            print(f"- [{doc.metadata['title']}]({doc.metadata['url']})")
    print()
