import os, shutil
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from sentence_transformers import SentenceTransformer, util

from pathlib import Path

import upload

class vectordb_start():
    def __init__(self, huggingface_api_key, embed_model_name = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2') -> None:
        self.main_path = Path("main.py").parent
        self.db_path = Path(self.main_path,"..")
        self.docs_path = Path(self.main_path,"..","docs_storage")

        self.db = chromadb.PersistentClient(path=os.path.join(self.db_path,"vectors_db/"))
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

            print(f"Vector database and Table : {table_name} has been removed\n")


    def add(self, table_name) -> None:
        upload_docs = upload.LangChainDocLoaders(pdf_loader="pymupdf")

        collection = self.db.get_or_create_collection(name=table_name, embedding_function=self.huggingface_ef)
        print(f"\nTable name has been CREATED/GET as : {table_name}")

        for file in os.listdir(self.docs_path) :

            file_type = "."+file.split('.')[-1]

            if file_type in upload_docs.supported_doc :

                chunks = upload_docs.load_document(os.path.join(self.docs_path,file))
                texts = chunks['child_documents']

                # prepare chunks to be added to collection

                current_data = collection.count()

                meta = [{"chunk_no":i, "file_type": file_type, "source_name":file} for i in range(len(texts))]
                idd = ["id{a}".format(a=(i+1)+current_data) for i in range(len(texts))]

                doc_embed = self.huggingface_ef(texts)
                
                try :
                    collection.add(
                                    embeddings = doc_embed,
                                    documents = texts,
                                    metadatas = meta,
                                    ids = idd
                                )
                except :
                    self.db.delete_collection(name = table_name)
                    print(f"Table name : {table_name} ERROR\n")
                    raise TypeError
                
                print(F"{file} has been added.")
            else :
                print(f"The document name : {file} , you provided is not supported.")

    def retrieve(self, query, table_name, n_results = 5) -> dict :
        collection = self.db.get_or_create_collection(name=table_name, embedding_function=self.huggingface_ef)
        results = collection.query(
                                        query_texts=query,
                                        n_results=n_results
                                    )

        return results
    
    def retrieve_rerank(self, query, table_name, n_results = 15) -> str:
        collection = self.db.get_or_create_collection(name=table_name, embedding_function=self.huggingface_ef)
        current_data = collection.count()

        if (n_results <= current_data) :
            results = collection.query(
                                        query_texts=query,
                                        n_results=n_results
                                    )
            docs = ((results['documents'])[0])[:n_results]

            # Compute embedding for both lists
            question = self.embed_model.encode([query], convert_to_tensor=True)
            docs_vector = self.embed_model.encode(docs, convert_to_tensor=True)

            # Compute cosine-similarities
            cosine_scores = util.cos_sim(question, docs_vector)

            # Output the pairs with their score
            see = {'q':[], 'a':[], 'score':[]}
            for i in range(len(question)):
                for j in range(len(docs_vector)):
                    see['q'].append(question[i])
                    see['a'].append(docs_vector[j])
                    see['score'].append( float(cosine_scores[i][j]) )

            # Get the most relevant doc
            
            for i in see['score']:
                if i == float(cosine_scores.max()):
                    retrieve_doc = see['score'].index(i)
            most_relevant_doc = (see['a'])[retrieve_doc]

            return most_relevant_doc
        else :
            print("\nThe number of results has exceeded the maximum limit.\n")
            raise ValueError
