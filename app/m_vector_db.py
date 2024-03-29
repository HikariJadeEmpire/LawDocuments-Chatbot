import os, shutil
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer, util
from pythainlp.tokenize import sent_tokenize, word_tokenize
from rank_bm25 import BM25Okapi

from pathlib import Path

import upload

class vectordb_start():
    def __init__(self, huggingface_api_key, embed_model_name = 'intfloat/multilingual-e5-base') -> None:
        self.main_path = Path("main.py").parent
        self.db_path = Path(self.main_path,"..")
        self.docs_path = Path(self.main_path,"..","docs_storage")

        self.db = chromadb.PersistentClient(
            path=os.path.join(self.db_path,"vectors_db/"),
            settings=Settings(allow_reset=True)
                                            )
        self.huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
                                                api_key=huggingface_api_key,
                                                model_name=embed_model_name
                                        )
        self.embed_model = SentenceTransformer(embed_model_name)

    def remove_db(self, table_name) -> None:
        # db_check = os.listdir(self.db_path/"vectors_db")

        if os.path.exists(self.db_path/"vectors_db"):
            self.db.delete_collection(name = table_name)
            shutil.rmtree(self.db_path/"vectors_db")

            # for i in db_check:
            #     if os.path.exists(self.db_path/"vectors_db"/i):
            #         os.remove(self.db_path/"vectors_db"/i)
            # os.rmdir(self.db_path/"vectors_db")

            print(f"[ VectorDB ] Vector database and Table : {table_name} has been removed\n")


    def add(self, table_name) -> None:
        upload_docs = upload.LangChainDocLoaders(pdf_loader="pymupdf")

        try:
            collection = self.db.get_or_create_collection(name=table_name, embedding_function=self.huggingface_ef)
            print(f"\n[ VectorDB ] Table name has been CREATED/GET as : {table_name}")
        except :
            raise TypeError(f"[ VectorDB ] Creating or getting table name >>> {table_name} >>> FAILED")

        for file in os.listdir(self.docs_path) :

            file_type = "."+file.split('.')[-1]

            if file_type in upload_docs.supported_doc :

                chunks = upload_docs.load_document(os.path.join(self.docs_path,file))
                texts = chunks['child_documents']

                # prepare chunks to be added to collection

                current_data = collection.count()

                meta = [{"chunk_no":i, "file_type": file_type, "source_name":file} for i in range(len(texts))]
                idd = ["id{a}".format(a=(i+1)+current_data) for i in range(len(texts))]
                print("[ VectorDB ] Text embeddings ...")
                doc_embed = self.huggingface_ef(texts)
                
                try :
                    print("[ VectorDB ] Start adding documents to vector database.")
                    collection.add(
                                    embeddings = doc_embed,
                                    documents = texts,
                                    metadatas = meta,
                                    ids = idd
                                )
                except :
                    self.db.delete_collection(name = table_name)
                    print(f"[ VectorDB ] Adding documents to vector database >> Table name : {table_name} >> FAILED\n")
                    raise TypeError
                
                print(F"[ VectorDB ] {file} has been added.")
            else :
                print(f"The document name : {file} , you provided is not supported.")

    def retrieve(self, query, table_name, n_results = 5) -> dict :
        collection = self.db.get_or_create_collection(name=table_name, embedding_function=self.huggingface_ef)
        results = collection.query(
                                        query_texts=query,
                                        n_results=n_results
                                    )

        return results
    
    def retrieve_by_keyword(self, query, table_name, n_results = 5) -> dict :
        collection = self.db.get_or_create_collection(name=table_name, embedding_function=self.huggingface_ef)
        ### attucut >> Tokenization >> some_token : list()
        some_token = word_tokenize(text=query,engine='attacut')
        
        keyw = {"$or":[]}
        for i in some_token:
            keyw["$or"].append({"$contains":i})
        
        results = collection.query(
                                        query_texts=some_token,
                                        n_results=n_results,
                                        where=keyw
                                    )

        return results
    
    def retrieve_rerank(self, query, table_name, n_results = 30) -> dict:
        collection = self.db.get_or_create_collection(name=table_name, embedding_function=self.huggingface_ef)
        current_data = collection.count()

        while (n_results >= current_data) :
            n_results -= 2

        if (n_results <= current_data) :
            results = collection.query(
                                        query_texts=query,
                                        n_results=n_results
                                    )
            docs = (results['documents'])[0]

            # Compute embedding for both lists
            tokenized_corpus = [word_tokenize(text=docs[i],engine='attacut') for i in range(len(docs))]
            bm25 = BM25Okapi(tokenized_corpus)

            tokenized_query = word_tokenize(text=query,engine='attacut')
            doc_scores = bm25.get_scores(tokenized_query)
            rs = bm25.get_top_n(tokenized_query, docs, n=1)

            results = {'doc':rs[0], 'score':float(doc_scores.max())}

            return results
        else :
            raise ValueError("The number of results has exceeded the maximum limit.")

# def retrieve_rerank_by_adding_query(self, query, table_name, n_results = 30) -> dict:
#         collection = self.db.get_or_create_collection(name=table_name, embedding_function=self.huggingface_ef)
#         current_data = collection.count()

#         while (n_results >= current_data) :
#             n_results -= 2

#         if (n_results <= current_data) :
#             results = collection.query(
#                                         query_texts=query,
#                                         n_results=n_results
#                                     )
#             docs = ((results['documents'])[0])[:n_results]