def load_and_preprocess_df(tokenizer):
    
    import pandas as pd
    from datasets import Dataset
    
    train_df = pd.read_csv("/content/drive/MyDrive/KUBIG Contest/AIhub_data/train_df.csv")
    valid_df = pd.read_csv("/content/drive/MyDrive/KUBIG Contest/AIhub_data/valid_df.csv")


    ''' 큰따옴표 제거 '''
    def remove_quotes(value):
        value = value.replace('"', '')
        return value
    train_df = train_df.applymap(remove_quotes)
    valid_df = valid_df.applymap(remove_quotes)


    ''' input, output을 eos 토큰으로 연결 '''
    # tokenizer.eos_token : <|endoftext|>
    train_df['text'] = train_df['input'] + tokenizer.eos_token + train_df['output']
    valid_df['text'] = valid_df['input'] + tokenizer.eos_token + valid_df['output']


    ''' load Dataset from Pandas DataFrame '''
    train_dataset = Dataset.from_pandas(train_df[['text']])
    valid_dataset = Dataset.from_pandas(valid_df[['text']])


    ''' dataset 토큰화 '''
    def tokenize_function(examples):
        return tokenizer(examples['text'], 
                         truncation=True, 
                         padding='max_length', 
                         max_length=175)
    tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True)
    tokenized_valid_dataset = valid_dataset.map(tokenize_function, batched=True)

    return tokenized_train_dataset, tokenized_valid_dataset