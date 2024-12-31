import torch
import torch.nn.functional as F
from safetensors.torch import save_file
from typing import List, Optional

import torch
import torch.nn.functional as F

class TokenEmbeddingsHandler:
    def __init__(self, text_encoders, tokenizers):
        self.text_encoders = text_encoders
        self.tokenizers = tokenizers
        self.train_ids = None
        self.inserting_tokens = None
        self.embeddings_settings = {}

    def initialize_new_tokens(self, inserting_tokens, initializer_tokens):
        assert isinstance(inserting_tokens, list), "inserting_tokens should be a list of strings."
        assert all(isinstance(tok, str) for tok in inserting_tokens), "All elements in inserting_tokens should be strings."

        self.inserting_tokens = inserting_tokens
        for idx, (tokenizer, text_encoder) in enumerate(zip(self.tokenizers, self.text_encoders)):
            # Add new token
            special_tokens_dict = {"additional_special_tokens": inserting_tokens}
            tokenizer.add_special_tokens(special_tokens_dict)
            text_encoder.resize_token_embeddings(len(tokenizer))

            # Converting new tokens to IDs
            self.train_ids = tokenizer.convert_tokens_to_ids(inserting_tokens)
            std_token_embedding = text_encoder.text_model.embeddings.token_embedding.weight.data.std().item()
            self.embeddings_settings[f"std_token_embedding_{idx}"] = std_token_embedding

            print(f"{idx} text encoder's std_token_embedding: {std_token_embedding}")

            embeddings = []
            embeddings_norm = []

            for initializer_token in initializer_tokens:
                if not initializer_token:
                    emb = torch.randn(1, text_encoder.text_model.config.hidden_size) * std_token_embedding
                    emb = emb.to(device=self.device, dtype=self.dtype)
                else:
                    initializer_token_id = tokenizer.convert_tokens_to_ids([initializer_token])[0]
                    emb = text_encoder.text_model.embeddings.token_embedding.weight.data[initializer_token_id].clone()
                embeddings.append(emb)
                embeddings_norm.append(emb.norm().item())

            embeddings = torch.cat(embeddings)
            text_encoder.text_model.embeddings.token_embedding.weight.data[self.train_ids] = embeddings
            embeddings_norm = torch.tensor(embeddings_norm).unsqueeze(1)
            self.embeddings_settings[f"token_embedding_norm_{idx}"] = embeddings_norm

            # Store original embeddings
            self.embeddings_settings[f"original_embeddings_{idx}"] = text_encoder.text_model.embeddings.token_embedding.weight.data.clone()

            index_no_updates = torch.ones(len(tokenizer), dtype=torch.bool)
            index_no_updates[self.train_ids] = False
            self.embeddings_settings[f"index_no_updates_{idx}"] = index_no_updates

    def save_embeddings(self, file_path: str):
        assert self.train_ids is not None, "Initialize new tokens before saving embeddings."
        tensors = {}
        idx_to_text_encoder_name = {0: "clip_l", 1: "clip_g"}

        for idx, text_encoder in enumerate(self.text_encoders):
            new_token_embeddings = text_encoder.text_model.embeddings.token_embedding.weight.data[self.train_ids]
            tensors[idx_to_text_encoder_name[idx]] = new_token_embeddings

        save_file(tensors, file_path)

    @property
    def dtype(self):
        return self.text_encoders[0].dtype

    @property
    def device(self):
        return self.text_encoders[0].device

    @torch.no_grad()
    def retract_embeddings(self):
        for idx, text_encoder in enumerate(self.text_encoders):
            index_no_updates = self.embeddings_settings[f"index_no_updates_{idx}"]
            # original 임베딩s tore
            original_embeddings = self.embeddings_settings[f"original_embeddings_{idx}"]
            text_encoder.text_model.embeddings.token_embedding.weight.data[index_no_updates] = (
                original_embeddings[index_no_updates]
                .to(device=text_encoder.device, dtype=text_encoder.dtype)
            )

            # Normalize
            index_updates = ~index_no_updates
            new_embeddings = text_encoder.text_model.embeddings.token_embedding.weight.data[index_updates]
            norm_factors = self.embeddings_settings[f"token_embedding_norm_{idx}"].to(device=text_encoder.device)
            new_embeddings = F.normalize(new_embeddings, dim=-1) * norm_factors
            text_encoder.text_model.embeddings.token_embedding.weight.data[index_updates] = new_embeddings

def tokenize_prompt(tokenizer, prompt):
    text_inputs = tokenizer(
        prompt,
        padding="max_length",
        max_length=tokenizer.model_max_length,
        truncation=True,
        return_tensors="pt",
    )
    text_input_ids = text_inputs.input_ids
    return text_input_ids
    
def encode_prompt(text_encoders, tokenizers, prompt, text_input_ids_list=None):
    prompt_embeds_list = []

    for i, text_encoder in enumerate(text_encoders):
        if tokenizers is not None:
            tokenizer = tokenizers[i]
            text_inputs = tokenizer(
                prompt,
                padding="max_length",
                max_length=tokenizer.model_max_length,
                truncation=True,
                return_tensors="pt",
            )
            text_input_ids = text_inputs.input_ids
        else:
            assert text_input_ids_list is not None, "text_input_ids_list must be provided if tokenizers is None."
            text_input_ids = text_input_ids_list[i]

        outputs = text_encoder(
            text_input_ids.to(text_encoder.device),
            output_hidden_states=True,
        )

        hidden_states = outputs.hidden_states
        penultimate_hidden_state = hidden_states[-2]
        bs_embed, seq_len, _ = penultimate_hidden_state.shape

        prompt_embeds_list.append(penultimate_hidden_state.view(bs_embed, seq_len, -1))
        pooled_prompt_embeds = outputs[0]

    final_prompt_embeds = torch.cat(prompt_embeds_list, dim=-1)
    final_pooled_embeds = pooled_prompt_embeds.view(bs_embed, -1)

    return final_prompt_embeds, final_pooled_embeds


