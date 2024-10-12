import os
import weaviate
from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")

client = weaviate.Client(WEAVIATE_URL)

def setup_weaviate_schema():
    schema = {
        "classes": [
            {
                "class": "Prompt",
                "description": "RAG 系统的用户提示",
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "提示的内容",
                    }
                ],
            }
        ]
    }

    existing_classes = client.schema.get()["classes"]
    class_names = [cls["class"] for cls in existing_classes]

    if "Prompt" not in class_names:
        client.schema.create(schema)
        print("Weaviate 模式创建成功。")
    else:
        print("Weaviate 模式已存在。")

if __name__ == "__main__":
    setup_weaviate_schema()
