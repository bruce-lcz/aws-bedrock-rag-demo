import boto3
import os
from dotenv import load_dotenv

load_dotenv()

region = os.getenv("AWS_REGION", "us-east-1")
kb_id = os.getenv("KB_ID")
model_arn = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"

agent = boto3.client("bedrock-agent-runtime", region_name=region)

while True:
    user_question = input("🧑‍💻 你想問什麼？（輸入 q 離開）\n> ")
    if user_question.lower() in ['q', 'quit', 'exit']:
        print("👋 已離開問答模式。")
        break

    response = agent.retrieve_and_generate(
        input={"text": user_question},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": kb_id,
                "modelArn": model_arn,
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {
                        "numberOfResults": 3
                    }
                },
                "generationConfiguration": {
                    "promptTemplate": {
                        "textPromptTemplate": (
                            "You are a question-answering assistant. "
                            "I will provide you with a set of retrieved passages (search results), and the user will ask a question. "
                            "Your task is to answer the user's question based solely on the information provided in the retrieved passages. "
                            "Do not use any external knowledge beyond the provided passages. "
                            "If the answer cannot be found in the passages, clearly state: "
                            "\"The answer to this question could not be found in the provided document.\"\n\n"
                            "Question:\n"
                            "$query$\n\n"
                            "Here are the search results:\n"
                            "$search_results$\n\n"
                            "$output_format_instructions$\n\n"
                            "Language rule: If the user's question includes Chinese, always answer in Chinese. Otherwise, answer in the same language as the question."
                        )
                    },
                    "inferenceConfig": {
                        "textInferenceConfig": {
                            "maxTokens": 300,
                            "temperature": 0.5
                        }
                    }
                },
                "orchestrationConfiguration": {
                    "promptTemplate": {
                        "textPromptTemplate": (
                            "You are a helpful assistant. Below is the conversation history:\n"
                            "$conversation_history$\n\n"
                            "The user just asked:\n"
                            "$query$\n\n"
                            "Please interpret the user's intent and improve the clarity of the question if needed.\n\n"
                            "$output_format_instructions$"
                        )
                    }
                }
            }
        }
    )

    print("\n🤖 回答：\n" + response['output']['text'] + "\n" + "-" * 50)
