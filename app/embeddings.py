from sentence_transformers import SentenceTransformer

class embeddings_model:
    def __init__(self, model : str = "kornwtp/simcse-model-phayathaibert") -> None:
        self.loaded_model = SentenceTransformer(model)
        self.model = model

    def to_vec(self, vectors : list):
        if type(vectors) == list :
            # vec = SentenceTransformer(self.model)
            vec = self.loaded_model
            vec = vec.encode(vectors)

            return vec