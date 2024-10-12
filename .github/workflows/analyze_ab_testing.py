from sqlalchemy.orm import Session
from database import SessionLocal, Response, Feedback
import pandas as pd

def analyze():
    db: Session = SessionLocal()
    try:
        responses = db.query(Response).all()

        data = [{
            "response_id": resp.id,
            "prompt_id": resp.prompt_id,
            "content": resp.content,
            "model_version": resp.model_version
        } for resp in responses]

        if not data:
            print("数据库中未找到响应。")
            return

        df = pd.DataFrame(data)

        df['response_length'] = df['content'].apply(len)

        avg_length = df.groupby('model_version')['response_length'].mean()
        print("每个模型的平均响应长度：")
        print(avg_length)
        print("\n")

        count_responses = df['model_version'].value_counts()
        print("每个模型的响应数量：")
        print(count_responses)
        print("\n")

        feedbacks = db.query(Feedback).all()
        if feedbacks:
            feedback_data = [{
                "feedback_id": fb.id,
                "response_id": fb.response_id,
                "user_rating": fb.user_rating,
                "comments": fb.comments
            } for fb in feedbacks]

            feedback_df = pd.DataFrame(feedback_data)

            merged_df = feedback_df.merge(df, left_on='response_id', right_on='response_id', how='left')

            avg_rating = merged_df.groupby('model_version')['user_rating'].mean()
            print("每个模型的平均用户评分：")
            print(avg_rating)
            print("\n")
            count_feedback = merged_df['model_version'].value_counts()
            print("每个模型的反馈数量：")
            print(count_feedback)
            print("\n")
        else:
            print("数据库中未找到反馈条目。")
    finally:
        db.close()

if __name__ == "__main__":
    analyze()
