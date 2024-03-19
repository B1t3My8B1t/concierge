import streamlit as st
from concierge_backend_lib.status import get_status
from concierge_streamlit_lib.collections import SELECTED_COLLECTION, init_collection_cached
from concierge_backend_lib.ingesting import insert
from loaders.pdf import load_pdf
from loaders.web import load_web
from pathlib import Path
from stqdm import stqdm

LOADER_PROCESSING = "loader_processing"
UPLOAD_DIR = 'uploads'

@st.cache_data(ttl="10s")
def get_status_cached():
    return get_status()

def sidebar_status():
    status = get_status_cached()
    if status["ollama"]:
        st.sidebar.success("Ollama is up and running", icon="🟢")
    else:
        st.sidebar.error("Ollama server not found, please ensure the ollama Docker container is running! If so you may have to take down the docker compose and put it up again", icon="🔴")
    if status["milvus"]:
        st.sidebar.success("Milvus is up and running", icon="🟢")
    else:
        st.sidebar.error("Milvus database not found, please ensure the milvus-standalone, etcd and minio Docker containers are running! If so you may have to take down the docker compose and put it up again", icon="🔴")

def document_loader():
    if "input_urls" not in st.session_state:
        st.session_state["input_urls"] = []
        st.session_state["processing_urls"] = []

    if LOADER_PROCESSING not in st.session_state:
        st.session_state[LOADER_PROCESSING] = False

    if st.session_state[LOADER_PROCESSING]:
        collection = init_collection_cached(st.session_state[SELECTED_COLLECTION])
        files = st.session_state["processing_files"]
        if files and len(files):
            st.write('Processing files...')
            for file in files:
                if file.type == 'application/pdf':
                    print(file.name)
                    with open(Path(UPLOAD_DIR, file.name), "wb") as f:
                        f.write(file.getbuffer())
                    pages = load_pdf(UPLOAD_DIR, file.name)
                    page_progress = stqdm(total=len(pages), desc=f"Loading PDF {file.name}", backend=True)
                    for x in insert(pages, collection):
                        page_progress.n = x[0] + 1
                        page_progress.refresh()
                    page_progress.close()
            collection.flush()
            print('done loading files\n')

        if len(st.session_state["processing_urls"]):
            st.write('Processing URLs...')
            for url in st.session_state["processing_urls"]:
                if not url:
                    continue
                print(url)
                pages = load_web(url)
                page_progress = stqdm(total=len(pages), desc=f"Loading URL {url}", backend=True)
                for x in insert(pages, collection):
                    page_progress.n = x[0] + 1
                    page_progress.refresh()
                page_progress.close()
            print('done loading URLs\n')
            st.session_state["processing_urls"] = []
        st.session_state[LOADER_PROCESSING] = False
        st.rerun()
