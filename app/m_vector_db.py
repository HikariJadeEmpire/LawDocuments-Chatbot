import os, shutil
import chromadb
import chromadb.utils.embedding_functions as embedding_functions

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

    def remove_db(self, table_name):
        db_check = os.listdir(self.db_path/"vectors_db")

        if os.path.exists(self.db_path/"vectors_db"):
            self.db.delete_collection(name = table_name)
            shutil.rmtree(self.db_path/"vectors_db")

            # for i in db_check:
            #     if os.path.exists(self.db_path/"vectors_db"/i):
            #         os.remove(self.db_path/"vectors_db"/i)
            # os.rmdir(self.db_path/"vectors_db")

            print("Vector database has been removed")


    def add(self, table_name):
        upload_docs = upload.LangChainDocLoaders(pdf_loader="pymupdf")
        collection = self.db.get_or_create_collection(name=table_name, embedding_function=self.huggingface_ef)

        for file in os.listdir(self.docs_path) :

            file_type = "."+file.split('.')[1]
            if file_type in upload_docs.supported_doc :

                chunks = upload_docs.load_document(os.path.join(self.docs_path,file))
                texts = chunks['child_documents']

                # prepare chunks to be added to collection

                current_data = collection.count()

                meta = [{"chunk_no":i, "file_type": file_type, "source_name":file} for i in range(len(texts))]
                idd = ["id{a}".format(a=(i+1)+current_data) for i in range(len(texts))]

                doc_embed = self.huggingface_ef(texts)

                collection.add(
                                    embeddings = doc_embed,
                                    documents = texts,
                                    metadatas = meta,
                                    ids = idd
                                )
                
                print(F"{file} has been added")

    def retrieve(self, query, table_name, n_results = 5):
        collection = self.db.get_or_create_collection(name=table_name, embedding_function=self.huggingface_ef)
        results = collection.query(
                                        query_texts=query,
                                        n_results=n_results
                                    )

        return results
