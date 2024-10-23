import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

def setup_weaviate_schema():
    schema = {
        "classes": [
            {
                "class": "Prompt",
                "description": "User prompts for RAG system",
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "Content of the prompt",
                    },
                    {
                        "name": "category",
                        "dataType": ["text"],
                        "description": "Category of the prompt",
                    }
                ],
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WEAVIATE_API_KEY}" if WEAVIATE_API_KEY else None
    }

    response = requests.get(f"{WEAVIATE_URL}/v1/schema", headers=headers)
    existing_classes = response.json().get("classes", [])
    class_names = [cls["class"] for cls in existing_classes]

    if "Prompt" not in class_names:
        response = requests.post(f"{WEAVIATE_URL}/v1/schema", headers=headers, json=schema)
        if response.status_code == 200:
            print("Weaviate schema created successfully.")
        else:
            print(f"Failed to create schema: {response.status_code}, {response.text}")
    else:
        print("Weaviate schema already exists.")

def hybrid_search(query_text, limit=5, alpha=0.5, category=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WEAVIATE_API_KEY}" if WEAVIATE_API_KEY else None
    }

    where_filter = 'where: {}'
    if category:
        where_filter = f'where: {{ path: ["category"], operator: Equal, valueString: "{category}" }}'

    query = {
        "query": f"""
        {{
          Hybrid {{
            search(
              query: "{query_text}",
              alpha: {alpha},
              limit: {limit},
              {where_filter}
            ) {{
              content
              category
              _additional {{
                score
                id
                vector
                certainty
                distance
              }}
            }}
          }}
        }}
        """
    }

    response = requests.post(f"{WEAVIATE_URL}/v1/graphql", headers=headers, json=query)
    return response.json()

def add_prompt(content, category):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WEAVIATE_API_KEY}" if WEAVIATE_API_KEY else None
    }

    data = {
        "class": "Prompt",
        "properties": {
            "content": content,
            "category": category
        }
    }

    response = requests.post(f"{WEAVIATE_URL}/v1/objects", headers=headers, json=data)
    return response.json()

def delete_prompt(prompt_id):
    headers = {
        "Authorization": f"Bearer {WEAVIATE_API_KEY}" if WEAVIATE_API_KEY else None
    }

    response = requests.delete(f"{WEAVIATE_URL}/v1/objects/Prompt/{prompt_id}", headers=headers)
    return response.status_code == 204

def update_prompt(prompt_id, new_content, new_category):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WEAVIATE_API_KEY}" if WEAVIATE_API_KEY else None
    }

    data = {
        "properties": {
            "content": new_content,
            "category": new_category
        }
    }

    response = requests.patch(f"{WEAVIATE_URL}/v1/objects/Prompt/{prompt_id}", headers=headers, json=data)
    return response.json()

if __name__ == "__main__":
    setup_weaviate_schema()

    while True:
        print("\nPlease choose an operation:")
        print("1. Add new prompt")
        print("2. Search prompts")
        print("3. Update prompt")
        print("4. Delete prompt")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            new_prompt = input("Enter the new prompt content: ")
            category = input("Enter the prompt category: ")
            add_result = add_prompt(new_prompt, category)
            print("Add result:", json.dumps(add_result, indent=2))

        elif choice == '2':
            search_text = input("Enter the text to search: ")
            category = input("Enter category to filter (optional, press Enter to skip): ")
            alpha = float(input("Enter alpha value (0-1, default 0.5): ") or 0.5)
            limit = int(input("Enter the number of results to return (default 5): ") or 5)
            search_results = hybrid_search(search_text, limit, alpha, category if category else None)
            print("Search results:", json.dumps(search_results, indent=2))

        elif choice == '3':
            prompt_id = input("Enter the prompt ID to update: ")
            new_content = input("Enter the new prompt content: ")
            new_category = input("Enter the new prompt category: ")
            update_result = update_prompt(prompt_id, new_content, new_category)
            print("Update result:", json.dumps(update_result, indent=2))

        elif choice == '4':
            prompt_id = input("Enter the prompt ID to delete: ")
            delete_result = delete_prompt(prompt_id)
            print("Delete result:", "Success" if delete_result else "Failed")

        elif choice == '5':
            print("Thank you for using the program. Goodbye!")
            break

        else:
            print("Invalid choice, please try again.")
