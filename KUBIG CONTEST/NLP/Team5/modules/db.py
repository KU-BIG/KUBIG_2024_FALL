from langchain_teddynote.retrievers import KiwiBM25Retriever
from langchain.retrievers import EnsembleRetriever, MultiQueryRetriever


def create_vector_db(chunks, model_path="intfloat/multilingual-e5-base"):
    """FAISS DB 생성"""
    # 임베딩 모델 설정
    model_kwargs = {'device': 'cuda'}
    encode_kwargs = {'normalize_embeddings': True}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_path,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    # FAISS DB 생성 및 반환
    db = FAISS.from_documents(chunks, embedding=embeddings)
    return db


def normalize_path(path):
    """경로 유니코드 정규화"""
    return unicodedata.normalize('NFC', path)


def process_pdfs_from_dataframe(df, base_directory):
    """딕셔너리에 pdf명을 키로해서 DB, retriever 저장"""
    pdf_databases = {}
    unique_paths = df['Source_path'].unique()

    for path in tqdm(unique_paths, desc="Processing PDFs"):
        # 경로 정규화 및 절대 경로 생성
        normalized_path = normalize_path(path)
        full_path = os.path.normpath(os.path.join(base_directory, normalized_path.lstrip('./'))) if not os.path.isabs(normalized_path) else normalized_path

        pdf_title = os.path.splitext(os.path.basename(full_path))[0]
        print(f"Processing {pdf_title}...")

        # PDF 처리 및 벡터 DB 생성
        chunks = process_pdf(full_path)
        db = create_vector_db(chunks)

        # Ensemble Retriever
        kiwi_bm25_retriever = KiwiBM25Retriever.from_documents(chunks)
        faiss_retriever = db.as_retriever()

        retriever = EnsembleRetriever(
            retrievers=[kiwi_bm25_retriever, faiss_retriever],
            weights=[0.5, 0.5],
            search_type="mmr",
            search_kwargs={'k': 3, 'fetch_k': 8}
        )

        # 결과 저장
        pdf_databases[pdf_title] = {
                'db': db,
                'retriever': retriever
        }
    return pdf_databases
