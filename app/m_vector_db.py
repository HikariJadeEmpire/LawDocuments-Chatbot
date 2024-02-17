import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions

from pathlib import Path

class vectordb_start():
    def __init__(self) -> None:
        self.main_path = Path("main.py").parent
        self.db_path = Path(self.main_path,"..")
        self.docs_path = Path(self.main_path,"..","docs_storage")

        self.db = chromadb.PersistentClient(path=os.path.join(self.db_path,"vectors_db/"))

    def add(self, embed_model, huggingface_api_key, doclist):
        huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
                                                api_key=huggingface_api_key,
                                                model_name=embed_model.model
                                        )
        
        for file in os.listdir(self.docs_path) :
            file_name = file.split(".")[0]
            self.db.get_or_create_collection(name=file_name, embedding_function=huggingface_ef)
