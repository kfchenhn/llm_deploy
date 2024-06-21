from transformers import AutoTokenizer
from copy import deepcopy
from typing import List
from qanything_kernel.configs.model_config import LOCAL_RERANK_MODEL_PATH, LOCAL_RERANK_MAX_LENGTH, \
    LOCAL_RERANK_MODEL_NAME, \
    LOCAL_RERANK_BATCH, LOCAL_RERANK_PATH, LOCAL_RERANK_REPO
from qanything_kernel.utils.custom_log import debug_logger
from modelscope import snapshot_download
from abc import ABC, abstractmethod
import subprocess
import os
from rank_bm25 import BM25Okapi
import jieba
from openai import OpenAI
import torch

# 如果模型不存在, 下载模型
if not os.path.exists(LOCAL_RERANK_MODEL_PATH):
    # snapshot_download(repo_id=LOCAL_RERANK_REPO, local_dir=LOCAL_RERANK_PATH, local_dir_use_symlinks="auto")
    debug_logger.info(f"开始下载rerank模型：{LOCAL_RERANK_REPO}")
    cache_dir = snapshot_download(model_id=LOCAL_RERANK_REPO)
    # 如果存在的话，删除LOCAL_EMBED_PATH
    os.system(f"rm -rf {LOCAL_RERANK_PATH}")
    output = subprocess.check_output(['ln', '-s', cache_dir, LOCAL_RERANK_PATH], text=True)
    debug_logger.info(f"模型下载完毕！cache地址：{cache_dir}, 软链接地址：{LOCAL_RERANK_PATH}")


class RerankBackend(ABC):
    def __init__(self, use_cpu):
        self.use_cpu = use_cpu
        self._tokenizer = AutoTokenizer.from_pretrained(LOCAL_RERANK_PATH)
        self.spe_id = self._tokenizer.sep_token_id
        self.overlap_tokens = 80
        self.batch_size = LOCAL_RERANK_BATCH
        self.max_length = LOCAL_RERANK_MAX_LENGTH
        self.return_tensors = None
        self.client = OpenAI(api_key="sk-xxx",base_url="https://api.openai-proxy.com/v1")
    
    @abstractmethod
    def inference(self, batch) -> List:
        pass
         
    def merge_inputs(self, chunk1_raw, chunk2):
        chunk1 = deepcopy(chunk1_raw)
        chunk1['input_ids'].extend(chunk2['input_ids'])
        chunk1['input_ids'].append(self.spe_id)
        chunk1['attention_mask'].extend(chunk2['attention_mask'])
        chunk1['attention_mask'].append(chunk2['attention_mask'][0])
        if 'token_type_ids' in chunk1:
            token_type_ids = [1 for _ in range(len(chunk2['token_type_ids']) + 1)]
            chunk1['token_type_ids'].extend(token_type_ids)
        return chunk1

    def tokenize_preproc(self,
                         query: str,
                         passages: List[str],
                         ):
        query_inputs = self._tokenizer.encode_plus(query, truncation=False, padding=False)
        max_passage_inputs_length = self.max_length - len(query_inputs['input_ids']) - 1
        assert max_passage_inputs_length > 10
        overlap_tokens = min(self.overlap_tokens, max_passage_inputs_length * 2 // 7)

        # 组[query, passage]对
        merge_inputs = []
        merge_inputs_idxs = []
        for pid, passage in enumerate(passages):
            passage_inputs = self._tokenizer.encode_plus(passage, truncation=False, padding=False,
                                                        add_special_tokens=False)
            passage_inputs_length = len(passage_inputs['input_ids'])

            if passage_inputs_length <= max_passage_inputs_length:
                qp_merge_inputs = self.merge_inputs(query_inputs, passage_inputs)
                merge_inputs.append(qp_merge_inputs)
                merge_inputs_idxs.append(pid)
            else:
                start_id = 0
                while start_id < passage_inputs_length:
                    end_id = start_id + max_passage_inputs_length
                    sub_passage_inputs = {k: v[start_id:end_id] for k, v in passage_inputs.items()}
                    start_id = end_id - overlap_tokens if end_id < passage_inputs_length else end_id

                    qp_merge_inputs = self.merge_inputs(query_inputs, sub_passage_inputs)
                    merge_inputs.append(qp_merge_inputs)
                    merge_inputs_idxs.append(pid)

        return merge_inputs, merge_inputs_idxs

    def tokenize_preproc_no_merge(self,
                         query: str,
                         passages: List[str],
                         ):
        query_inputs = self._tokenizer.encode_plus(query, truncation=False, padding=False, add_special_tokens=False)
        max_passage_inputs_length = self.max_length - len(query_inputs['input_ids']) - 1
        assert max_passage_inputs_length > 10
        overlap_tokens = min(self.overlap_tokens, max_passage_inputs_length * 2 // 7)

        # 组[query, passage]对
        all_passage_input=[]

        for pid, passage in enumerate(passages):
            passage_inputs = self._tokenizer.encode_plus(passage, truncation=False, padding=False,
                                                        add_special_tokens=False)
            passage_inputs_length = len(passage_inputs['input_ids'])

            if passage_inputs_length <= max_passage_inputs_length:
                # qp_merge_inputs = self.merge_inputs(query_inputs, passage_inputs)
                # merge_inputs.append(qp_merge_inputs)
                # merge_inputs_idxs.append(pid)
                all_passage_input.append(passage_inputs)
            else:
                start_id = 0
                while start_id < passage_inputs_length:
                    end_id = start_id + max_passage_inputs_length
                    sub_passage_inputs = {k: v[start_id:end_id] for k, v in passage_inputs.items()}
                    start_id = end_id - overlap_tokens if end_id < passage_inputs_length else end_id

                    # qp_merge_inputs = self.merge_inputs(query_inputs, sub_passage_inputs)
                    # merge_inputs.append(qp_merge_inputs)
                    # merge_inputs_idxs.append(pid)
                    all_passage_input.append(sub_passage_inputs)

        all_passage_input.insert(0, query_inputs)

        return all_passage_input, [i for i in range(len(all_passage_input))]

    def predict(self,
                query: str,
                passages: List[str],
                grain: str
                ):
        if grain == "coarse":
            tokenized_corpus = [list(jieba.cut(doc,cut_all=True)) for doc in passages]
            bm25 = BM25Okapi(tokenized_corpus)
            tokenized_query = list(jieba.cut(query,cut_all=True))
            # filter_passage=bm25.get_top_n(tokenized_query, passages, n=5)
            merge_tot_scores=bm25.get_scores(tokenized_query)
            merge_tot_scores=merge_tot_scores.tolist()
            print("merge_tot_scores:", merge_tot_scores, flush=True)
            return merge_tot_scores
        
        elif grain == "fine":
            ### OpenAI ada embedding.
            # query_embeding = self.client.embeddings.create(input = query, model="text-embedding-ada-002").data[0].embedding
            # doc_embeddings = [self.client.embeddings.create(input = doc, model="text-embedding-ada-002").data[0].embedding for doc in passages]
            # merge_tot_scores=torch.cosine_similarity(torch.tensor(query_embeding).expand(torch.tensor(doc_embeddings).shape),torch.tensor(doc_embeddings)).tolist()

            tot_batches, _ = self.tokenize_preproc_no_merge(query, passages)

            tot_embeddings = []
            
            for k in range(0, len(tot_batches), self.batch_size):
                batch = self._tokenizer.pad(
                    tot_batches[k:k + self.batch_size],
                    padding=True,
                    max_length=None,
                    pad_to_multiple_of=None,
                    return_tensors=self.return_tensors
                )
                embeddings = self.inference(batch)
                tot_embeddings.extend(embeddings)

            query_embeding = torch.tensor(tot_embeddings[0])
            doc_embeddings = torch.tensor(tot_embeddings[1:])
            merge_tot_scores=torch.cosine_similarity(query_embeding.expand(doc_embeddings.shape), doc_embeddings).tolist()

            print("merge_tot_scores:", merge_tot_scores, flush=True)
            return merge_tot_scores

        else:
            assert 0, f"Error! The grain is error."
        

        # tot_batches, merge_inputs_idxs_sort = self.tokenize_preproc(query, passages)

        # tot_scores = []
        
        # for k in range(0, len(tot_batches), self.batch_size):
        #     batch = self._tokenizer.pad(
        #         tot_batches[k:k + self.batch_size],
        #         padding=True,
        #         max_length=None,
        #         pad_to_multiple_of=None,
        #         return_tensors=self.return_tensors
        #     )
        #     scores = self.inference(batch)
        #     tot_scores.extend(scores)

        # merge_tot_scores = [0 for _ in range(len(passages))]
        # for pid, score in zip(merge_inputs_idxs_sort, tot_scores):
        #     merge_tot_scores[pid] = max(merge_tot_scores[pid], score)
        # print("merge_tot_scores:", merge_tot_scores, flush=True)
        # return merge_tot_scores
