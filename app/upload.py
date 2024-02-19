from typing import Dict
from langchain.document_loaders import PyPDFLoader, PyMuPDFLoader, UnstructuredMarkdownLoader, Docx2txtLoader, JSONLoader
from langchain.document_loaders.csv_loader import CSVLoader

from langchain.document_loaders import BSHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever # on testing

from fixthaipdf import clean
from pathlib import Path
import json

class LangChainDocLoaders:
  def __init__(self, pdf_loader = "pymupdf"):
    self.supported_doc = ['.pdf', '.csv', '.json', '.jsonl', '.md', '.docx', '.txt', '.html']
    allowed_pdf_loaders = ["pypdf", "pymupdf"]  #Check for pdf_loader type
    if pdf_loader not in allowed_pdf_loaders:
        raise ValueError(f"Unsupported pdf loader type. Allowed pdf loaders are: {', '.join(allowed_pdf_loaders)}")
    self.pdf_loader = pdf_loader

  def load_document(self, document_path, *args, **kwargs) -> Dict:

    #Case insensitive file extension checking
    path_type = document_path.split('.')[-1]
    document_path = document_path.split('.')
    document_path[-1] = path_type.lower()
    document_path = '.'.join(document_path)

    chunk_size = kwargs.get('chunk_size', 400)
    chunk_overlap = kwargs.get('chunk_overlap', 100)

    parent_chunk_size = kwargs.get('parent_chunk_size', 2000)
    parent_chunk_overlap = kwargs.get('parent_chunk_overlap', 0)

    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=parent_chunk_overlap) # PUN Added
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap) # PUN Added

    #Load PDF File.
    if document_path.endswith(".pdf"):
      if self.pdf_loader == "pymupdf":
        loader = PyPDFLoader(document_path)
        original_pages = loader.load_and_split()
      else:
        loader = PyMuPDFLoader(document_path)
        original_pages = loader.load()

      pages = text_splitter.split_documents(original_pages) # PUN Added
      parent_pages = parent_splitter.split_documents(original_pages)

      data = [clean(page.page_content) for page in pages]
      parent_data = [clean(page.page_content) for page in parent_pages]

      return {'child_documents':data, 'parent_documents':parent_data}

    # Load CSV File.
    elif document_path.endswith(".csv"):
      loader = CSVLoader(file_path=document_path)
      rows = loader.load()

      data = [clean(page.page_content) for page in rows]

      return {'child_documents':data, 'parent_documents':None}

    #Load JSON File.
    #For JSON and JSON line File, please provide {jq_schema} as additional argument for better extraction. example: https://python.langchain.com/docs/modules/data_connection/document_loaders/json
    elif document_path.endswith(".json"):
      jq_schema = kwargs.get('jq_schema', None)
      if jq_schema:
        loader = JSONLoader(
          file_path=document_path,
          jq_schema=jq_schema,
          text_content=False
        )
        json_datas = loader.load()

        data = [clean(page.page_content) for page in json_datas]

      else:
        print("For JSON File, please provide {jq_schema} as additional argument for better extraction. example: https://python.langchain.com/docs/modules/data_connection/document_loaders/json")
        data = [json.loads(Path(document_path).read_text(encoding='UTF-8' ))]
      return {'child_documents':data, 'parent_documents':None}

    #Load JSON line File.
    elif document_path.endswith(".jsonl"):
      jq_schema = kwargs.get('jq_schema', None)
      if jq_schema:
        loader = JSONLoader(
          file_path=document_path,
          jq_schema=jq_schema,
          text_content=False,
          json_lines=True
        )
        json_datas = loader.load()

        data = [clean(page.page_content) for page in json_datas]
      else:
        print("For JSON line File, please provide {jq_schema} as additional argument for better extraction. example: https://python.langchain.com/docs/modules/data_connection/document_loaders/json")
        data = [Path(document_path).read_text(encoding='UTF-8' )]
      return {'child_documents':data, 'parent_documents':None}

    #Load Markdown File.
    elif document_path.endswith(".md"):
      loader = UnstructuredMarkdownLoader(file_path=document_path)
      original_pages = loader.load()

      pages = text_splitter.split_documents(original_pages) # PUN Added
      parent_pages = parent_splitter.split_documents(original_pages)

      data = [clean(page.page_content) for page in pages]
      parent_data = [clean(page.page_content) for page in parent_pages]

      return {'child_documents':data, 'parent_documents':parent_data}

    #Load docx File.
    elif document_path.endswith(".docx"):
      loader = Docx2txtLoader(file_path=document_path)
      original_pages = loader.load()

      pages = text_splitter.split_documents(original_pages) # PUN Added
      parent_pages = parent_splitter.split_documents(original_pages)

      data = [clean(page.page_content) for page in pages]
      parent_data = [clean(page.page_content) for page in parent_pages]

      return {'child_documents':data, 'parent_documents':parent_data}

    #Load txt File.
    elif document_path.endswith(".txt"):

      # PUN Added
      with open(document_path, encoding="UTF-8") as f:
        original_pages = f.read()

      pages = text_splitter.create_documents([original_pages]) # PUN Added
      parent_pages = parent_splitter.create_documents([original_pages])

      data = [clean(page.page_content) for page in pages]
      parent_data = [clean(page.page_content) for page in parent_pages]

      return {'child_documents':data, 'parent_documents':parent_data}

    #Load HTML File.
    elif document_path.endswith(".html"):
      loader = BSHTMLLoader(file_path=document_path)
      original_pages = loader.load()

      pages = text_splitter.split_documents(original_pages) # PUN Added
      parent_pages = parent_splitter.split_documents(original_pages)

      data = [clean(page.page_content) for page in pages]
      parent_data = [clean(page.page_content) for page in parent_pages]

      return {'child_documents':data, 'parent_documents':parent_data}

    else:
      raise ValueError(f"Unsupported document type. Supported documents are {self.supported_doc}")


