# LawDocuments-Chatbot
> Detail

# <h3>Preview</h3>

<img width="952" alt="image" src="https://github.com/HikariJadeEmpire/LawDocuments-Chatbot/assets/118663358/c4ba0d4c-3891-43fa-99a1-7cfd042b2639">

Overall

<br>

## Usage

- clone this repo
- set current directory to ```this_repo```
- run ```docker build -t docchat:0 .```
- run ```docker run --name docchat -d -p 8080:8080 docchat:0```
- open your browser and type ```localhost:8080```

<h3>To close & delete</h3>

- to close, run ```docker stop docchat```
- to delete all *images & containers*, run ```docker system prune -a```
