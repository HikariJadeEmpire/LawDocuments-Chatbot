# LawDocuments-Chatbot
> A multilingual chatbot that can learn from documents.

# <h3>Preview</h3>

<img width="952" alt="image" src="https://github.com/HikariJadeEmpire/LawDocuments-Chatbot/assets/118663358/c4ba0d4c-3891-43fa-99a1-7cfd042b2639">

Overall

<br>

## Details

- vector database : ```chromadb```
- Chatbot (algorithm) : ```OpenAI ChatGPT 3.5```
- Embedding model : ```vary```

**note** : Everyone can use this repository as a starter kit to build yourself a chatbot with ability to learn from documents. With chatbot algorithm 
, it does not necessary to be ```OpenAI ChatGPT 3.5```. You can customize it by yourself if your PC or any of your devices can handle a local LLM. By the way, this is free to use and safer for privacy use.

## Usage

- clone this repo
- set current directory to ```this_repo```
- run ```docker build -t docchat:0 .```
- run ```docker run --name docchat -d -p 8080:8080 docchat:0```
- open your browser and type ```localhost:8080```

<h3>To close & delete</h3>

- to close, run ```docker stop docchat```
- to delete all *images & containers*, run ```docker system prune -a```
