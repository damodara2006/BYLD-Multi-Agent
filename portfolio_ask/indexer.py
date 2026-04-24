from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document

def load_and_split_documents(data_dir: str = "data") -> list[Document]:
    """Loads markdown context and splits them using RecursiveCharacterTextSplitter."""
    text_loader_kwargs={'autodetect_encoding': True}
    
    news_loader = DirectoryLoader(f"{data_dir}/news", glob="**/*.md", loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)
    glossary_loader = DirectoryLoader(f"{data_dir}", glob="glossary.md", loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)
    
    docs = news_loader.load() + glossary_loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    
    split_docs = splitter.split_documents(docs)
    
    # Ensure source path is cleanly preserved in metadata
    for doc in split_docs:
        # Simplify source path to be relative rather than absolute if needed
        source = doc.metadata.get('source', '')
        if 'data/' in source:
            doc.metadata['source'] = 'data/' + source.split('data/', 1)[-1]
            
    return split_docs
