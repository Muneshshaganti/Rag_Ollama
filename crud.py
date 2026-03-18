from database import SessionLocal
from models import RagHistory

def save_qa(db, question, answer):
    qa = RagHistory(question=question, answer=answer)
    db.add(qa)
    db.commit()
    db.refresh(qa)
    return qa

def save_history(question, answer, sources, document_name):

    db = SessionLocal()

    history = RagHistory(
        question=question,
        answer=answer,
        sources=sources,
        document_name=document_name
    )

    db.add(history)
    db.commit()
    db.close()