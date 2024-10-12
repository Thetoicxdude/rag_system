import os
import random
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
import weaviate
from dotenv import load_dotenv

from database import SessionLocal, Prompt, Response, Feedback
from weaviate_client import client as weaviate_client

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

load_dotenv()

app = FastAPI(title="带有 A/B 测试和反馈循环的 RAG 系统")

LLAMA_MODEL_NAME = os.getenv("LLAMA_MODEL_NAME", "meta-llama/Llama-2-7b-chat-hf")  # 示例模型名称
try:
    tokenizer = AutoTokenizer.from_pretrained(LLAMA_MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        LLAMA_MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto" 
    )
    print(f"LLaMA 模型 '{LLAMA_MODEL_NAME}' 加载成功。")
except Exception as e:
    print(f"加载 LLaMA 模型失败：{e}")
    raise e

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 定义请求和响应模型
class QueryRequest(BaseModel):
    prompt: str

class QueryResponse(BaseModel):
    response: str
    model_version: str

class PromptResponse(BaseModel):
    id: int
    content: str
    created_at: str

class FeedbackRequest(BaseModel):
    response_id: int
    user_rating: int  
    comments: str = None

MODEL_VERSIONS = ["RAG", "No_RAG"]

@app.post("/query", response_model=QueryResponse)
def query_rag_system(request: QueryRequest, db: Session = Depends(get_db)):
    prompt_text = request.prompt.strip()

    if not prompt_text:
        raise HTTPException(status_code=400, detail="提示内容不能为空。")

    existing_prompt = db.query(Prompt).filter(Prompt.content == prompt_text).first()
    if not existing_prompt:
        new_prompt = Prompt(content=prompt_text)
        db.add(new_prompt)
        db.commit()
        db.refresh(new_prompt)
        prompt_id = new_prompt.id
    else:
        prompt_id = existing_prompt.id

    model_version = random.choice(MODEL_VERSIONS)

    if model_version == "RAG":
        try:
            response = weaviate_client.query.get("Prompt", ["content"]) \
                .with_near_text({"concepts": [prompt_text]}) \
                .with_limit(5) \
                .do()
            retrieved_prompts = [hit["content"] for hit in response["data"]["Get"]["Prompt"]]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Weaviate 查询失败：{e}")

        context = "\n".join(retrieved_prompts) if retrieved_prompts else ""
    else:
        context = ""

    try:
        if context:
            input_text = f"上下文信息：\n{context}\n\n用户：{prompt_text}"
        else:
            input_text = f"用户：{prompt_text}"

        inputs = tokenizer.encode(input_text, return_tensors="pt").to(model.device)

        outputs = model.generate(
            inputs,
            max_length=512,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            eos_token_id=tokenizer.eos_token_id
        )

        generated_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if "助手：" in generated_response:
            generated_response = generated_response.split("助手：")[-1].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLaMA 模型生成失败：{e}")

    new_response = Response(
        prompt_id=prompt_id,
        content=generated_response,
        model_version=model_version
    )
    db.add(new_response)
    db.commit()
    db.refresh(new_response)

    try:
        weaviate_client.data_object.create(
            {
                "content": prompt_text
            },
            "Prompt"
        )
    except weaviate.exceptions.WeaviateException as e:
        print(f"Weaviate 插入失败：{e}")

    return QueryResponse(response=generated_response, model_version=model_version)

@app.get("/prompts/search", response_model=List[PromptResponse])
def search_prompts(query: str, db: Session = Depends(get_db)):
    if not query:
        raise HTTPException(status_code=400, detail="查询参数不能为空。")

    results = db.query(Prompt).filter(Prompt.content.ilike(f"%{query}%")).all()
    return [
        PromptResponse(
            id=p.id,
            content=p.content,
            created_at=p.created_at.isoformat()
        )
        for p in results
    ]

@app.post("/feedback")
def submit_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    if feedback.user_rating < 1 or feedback.user_rating > 5:
        raise HTTPException(status_code=400, detail="user_rating 必须在 1 到 5 之间。")

    response_entry = db.query(Response).filter(Response.id == feedback.response_id).first()
    if not response_entry:
        raise HTTPException(status_code=404, detail="响应未找到。")

    new_feedback = Feedback(
        response_id=feedback.response_id,
        user_rating=feedback.user_rating,
        comments=feedback.comments
    )
    db.add(new_feedback)
    db.commit()

    return {"message": "反馈提交成功。"}
