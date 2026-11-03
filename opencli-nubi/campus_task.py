"""Task capabilities shared by the campus runner and its chat adapter."""
import re

def user_context(task):
    marker='사용자 제공 맥락:\n'
    if marker in task:
        return task.split(marker,1)[1].rsplit('\n로그인이나 지원 도구가 없으면',1)[0]
    return task

def local_report_only(task):
    task=user_context(task)
    return (bool(re.search(r'사용자\s*제공.{0,12}(?:만|내용)|외부\s*조사.{0,8}(?:말|않)|조사.{0,8}하지\s*말',task))
            and bool(re.search(r'보고서|발표|DOCX|PPTX',task,re.I))
            and not bool(re.search(r'메일|포털|블랙보드|조회|검색|업로드',task)))


def local_schedule_only(task):
    task=user_context(task)
    return bool(re.search(r'팀.*일정|회의.*시간|가능\s*시간',task)) and bool(re.search(r'사용자\s*제공|웹\s*탐색\s*없이|외부\s*조회\s*없이',task)) and not bool(re.search(r'메일|포털|블랙보드|업로드|초대.*보내',task))


def local_meal_only(task):
    task=user_context(task)
    task=re.sub(r'(?:알림|알람|통지)\s*(?:을|를)?\s*(?:예약|설정)', '', task)
    return bool(re.search(r'학식|식단|특식|밥먹어',task)) and not bool(re.search(r'포털|메일|블랙보드|기차|KTX|버스|업로드|예약',task,re.I))

def wants_meal_plan(task):
    task=user_context(task)
    return local_meal_only(task) and bool(re.search(r'시간표|11:50|피크|일찍|미리|출발|도착|수업',task,re.I))


def echoed_request(task,answer):
    normalize=lambda x: re.sub(r"[\W_]+", "", user_context(x).lower())
    a=normalize(answer); t=normalize(task)
    return len(t)>=20 and a==t

def answer_needs_review(task,answer,succeeded):
    if echoed_request(task,answer):return True
    if wants_meal_plan(task):return 'nubi_campus_meal_plan' not in succeeded
    if local_meal_only(task):return not succeeded.intersection({'nubi_campus_meals','nubi_campus_meal_plan'})
    return bool(re.search(r'확인하지 못|수행하지 못|진행하지 못|확인 불가|수행 불가|실행 불가',answer))
