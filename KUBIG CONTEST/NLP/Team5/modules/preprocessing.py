def extract_pdf_elements(pdf_file_name):
  return partition_pdf (filename=pdf_file_name,
                        #chunking_strategy = "by_title",
                        infer_table_structure=True,
                        max_characters=100,
                        new_after_n_chars=1500,
                        combine_text_under_n_chars=100,
                        strategy="hi_res",
                        extract_images_in_pdf = True,
                        extract_image_block_output_dir = output_dir)


def filtered_df(pdf_file_name):
  raw_elements = extract_pdf_elements(pdf_file_name)
  data = []
  for c in raw_elements:
      #print(type(c).__name__)
      row = {}
      row['Element Type'] = type(c).__name__
      row['Filename'] = c.metadata.filename
      row['Date Modified'] = c.metadata.last_modified
      row['Filetype'] = c.metadata.filetype
      row['Page Number'] = c.metadata.page_number
      row['text'] = c.text
      data.append(row)
  df = pd.DataFrame(data)

  filtered_df = df[df['Element Type'].isin(['Table', 'Title', 'Text', 'FigureCaption', 'ListItem', 'Image', 'NarrativeText'])]
  filtered_df['Element Type'] = filtered_df['Element Type'].replace({
      'ListItem': 'Text',
      'NarrativeText': 'Text'
  })
  return filtered_df


def page_combined(pdf_file_name):
  df = filtered_df(pdf_file_name)
  # 연달아 나오는 Title을 그룹핑하기 위한 변수 초기화
  start_idx = None
  rows_to_drop = []

  # iloc을 사용하여 위치 기반 접근
  for i in range(len(df)):
      if df.iloc[i]['Element Type'] == 'Title':
          if start_idx is None:
              start_idx = i
          else:
              df.iloc[start_idx, df.columns.get_loc('text')] += ' ' + df.iloc[i]['text']
              rows_to_drop.append(i)
      else:
          start_idx = None

  # 삭제할 행의 인덱스가 유효한지 확인 후 제거
  df = df.drop(index=df.index[rows_to_drop]).reset_index(drop=True)

  # text 열에서 5자 이하인 행을 제거
  df = df[df['text'].str.len() > 5]

  # 문자열 변환 함수 정의
  def replace_arrows(text):
      text = text.replace('↓', '→')
      text = text.replace('⇨', '→')
      text = text.replace('⇦', '<-')
      text = text.replace('⇩', '→')
      return text

  # 'text' 열에 함수 적용
  df['text'] = df['text'].apply(replace_arrows)

  # 인덱스를 재설정하여 깔끔하게 정리
  df = df.reset_index(drop=True)

  # 1. Page Number가 바뀌었고, 해당 행의 Element Type이 Title이 아닌 경우 이전 페이지로 돌아가 Title부터 텍스트를 합침
  for i in range(1, len(df)):
      if df.loc[i, 'Page Number'] != df.loc[i-1, 'Page Number']:  # Page Number가 바뀌었는지 확인
          if df.loc[i, 'Element Type'] != 'Title':  # 바뀐 행의 Element Type이 Title이 아닌 경우
              current_page = df.loc[i, 'Page Number']
              combined_text = df.loc[i, 'text']  # 현재 페이지의 텍스트를 시작점으로 설정
              for j in range(i-1, -1, -1):  # 이전 페이지로 거슬러 올라가며 Title부터 텍스트를 합침
                  if df.loc[j, 'Page Number'] < current_page:
                      combined_text = df.loc[j, 'text'] + ' ' + combined_text
                      if df.loc[j, 'Element Type'] == 'Title':
                          break
              df.loc[i, 'text'] = combined_text  # 최종적으로 결합된 텍스트를 현재 페이지의 텍스트로 설정


  # 2. Page Number가 같은 행들을 하나의 행으로 합치기
  df_combined = df.groupby('Page Number').agg({
      'Element Type': lambda x: ' '.join(x),
      'Filename': 'first',
      'Date Modified': 'first',
      'Filetype': 'first',
      'text': ' '.join
  }).reset_index()

  return df_combined


def process_pdf(file_path, chunk_size=800, chunk_overlap=50):

  df = page_combined(file_path)

  text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=chunk_size,
      chunk_overlap=chunk_overlap,
      separators=["\n\n", "\n", ".", "", " "]
  )

  chunks=[]

  for index, row in df.iterrows():
      text_chunk = text_splitter.split_text(row['text'])
      chunks.extend(text_chunk)

  chunks = [Document(page_content=t) for t in chunks]

  return chunks
