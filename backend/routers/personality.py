"""
旅行人格测试 API 路由
TBTI - Travel Behavioral Type Indicator
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from models.database import get_db, TravelPersonalityResult
from algorithms.personality_algorithm import (
    calculate_personality,
    get_questions,
    get_all_personality_types,
    PERSONALITY_TYPES
)

router = APIRouter()


class PersonalityTestRequest(BaseModel):
    answers: List[int]
    user_id: Optional[int] = None


class PersonalitySaveRequest(BaseModel):
    answers: List[int]
    user_id: int


@router.get("/questions")
def get_test_questions():
    """获取测试题目列表"""
    questions = get_questions()
    return {
        "total": len(questions),
        "questions": questions
    }


@router.post("/test")
def submit_test(data: PersonalityTestRequest, db: Session = Depends(get_db)):
    """提交测试答案，返回人格结果（不保存）"""
    if len(data.answers) != 20:
        raise HTTPException(status_code=400, detail="必须提供20个答案")

    for ans in data.answers:
        if ans < 1 or ans > 5:
            raise HTTPException(status_code=400, detail="答案必须在1-5之间")

    result = calculate_personality(data.answers)

    return {
        "type_code": result['type_code'],
        "name": result['personality']['name'],
        "tagline": result['personality']['tagline'],
        "description": result['personality']['description'],
        "strengths": result['personality']['strengths'],
        "weaknesses": result['personality']['weaknesses'],
        "recommend_spots": result['personality']['recommend_spots'],
        "travel_style": result['personality']['travel_style'],
        "dimension_details": result['dimension_details']
    }


@router.post("/save")
def save_result(data: PersonalitySaveRequest, db: Session = Depends(get_db)):
    """保存测试结果到用户账号"""
    if len(data.answers) != 20:
        raise HTTPException(status_code=400, detail="必须提供20个答案")

    for ans in data.answers:
        if ans < 1 or ans > 5:
            raise HTTPException(status_code=400, detail="答案必须在1-5之间")

    result = calculate_personality(data.answers)

    # 检查是否已有结果
    existing = db.query(TravelPersonalityResult).filter(
        TravelPersonalityResult.user_id == data.user_id
    ).first()

    if existing:
        existing.personality_type = result['type_code']
        existing.dimension_scores = result['dimension_details']
        existing.answers = data.answers
        existing.updated_at = datetime.now().isoformat()
    else:
        new_result = TravelPersonalityResult(
            user_id=data.user_id,
            personality_type=result['type_code'],
            dimension_scores=result['dimension_details'],
            answers=data.answers
        )
        db.add(new_result)

    db.commit()
    return {
        "message": "保存成功",
        "type_code": result['type_code'],
        "name": result['personality']['name'],
        "tagline": result['personality']['tagline']
    }


@router.get("/my")
def get_my_result(user_id: int = Query(..., description="用户ID"), db: Session = Depends(get_db)):
    """获取当前用户的测试结果"""
    result = db.query(TravelPersonalityResult).filter(
        TravelPersonalityResult.user_id == user_id
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="尚未进行人格测试")

    personality = PERSONALITY_TYPES.get(result.personality_type, PERSONALITY_TYPES['WRsc'])

    return {
        "type_code": result.personality_type,
        "name": personality['name'],
        "tagline": personality['tagline'],
        "description": personality['description'],
        "strengths": personality['strengths'],
        "weaknesses": personality['weaknesses'],
        "recommend_spots": personality['recommend_spots'],
        "travel_style": personality['travel_style'],
        "dimension_scores": result.dimension_scores,
        "created_at": result.created_at,
        "updated_at": result.updated_at
    }


@router.get("/types")
def get_all_types():
    """获取所有人格类型列表"""
    types = []
    for code, info in PERSONALITY_TYPES.items():
        types.append({
            "type_code": code,
            "name": info['name'],
            "tagline": info['tagline'],
            "travel_style": info['travel_style']
        })
    return {"total": len(types), "types": types}


@router.get("/types/{type_code}")
def get_type_detail(type_code: str):
    """获取特定人格类型详情"""
    personality = PERSONALITY_TYPES.get(type_code)
    if not personality:
        raise HTTPException(status_code=404, detail="人格类型不存在")

    return {
        "type_code": type_code,
        "name": personality['name'],
        "tagline": personality['tagline'],
        "description": personality['description'],
        "strengths": personality['strengths'],
        "weaknesses": personality['weaknesses'],
        "recommend_spots": personality['recommend_spots'],
        "travel_style": personality['travel_style']
    }


@router.delete("/my")
def delete_my_result(user_id: int = Query(..., description="用户ID"), db: Session = Depends(get_db)):
    """删除用户的测试结果"""
    result = db.query(TravelPersonalityResult).filter(
        TravelPersonalityResult.user_id == user_id
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="尚未进行人格测试")

    db.delete(result)
    db.commit()
    return {"message": "删除成功"}
