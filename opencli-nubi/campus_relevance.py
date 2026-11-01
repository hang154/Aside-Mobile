"""Evidence-based triage of a verified scholarship notice, not an award decision."""

def doosan_2027(profile):
    """Assess only explicit criteria observed in the 2026-10-15 UNIST notice.

    Facts absent from the profile are unknown. GPA conversion is never guessed.
    """
    if not isinstance(profile,dict):raise ValueError('profile must be an object')
    allowed={'level','nationality','year_2027_spring','enrolled_both_2027_terms','income_bracket_2026_fall','ceremony_available','gpa','gpa_scale'}
    if set(profile)-allowed:raise ValueError('unsupported profile field')
    fields=[
        ('level','학적 구분',lambda v:v=='학부'),
        ('nationality','대한민국 국적',lambda v:v=='대한민국'),
        ('year_2027_spring','2027년 1학기 진학 학년',lambda v:v==2),
        ('enrolled_both_2027_terms','2027년 1·2학기 재학 가능',lambda v:v is True),
        ('income_bracket_2026_fall','2026년 2학기 소득분위 6 이내',lambda v:isinstance(v,int) and not isinstance(v,bool) and 0<=v<=6),
        ('ceremony_available','장학증서 수여식 참석 가능',lambda v:v is True),
    ]
    yes=[];no=[];unknown=[]
    for key,label,check in fields:
        value=profile.get(key)
        if value is None:unknown.append(label)
        elif check(value):yes.append(label)
        else:no.append(label)
    grade=profile.get('gpa');scale=profile.get('gpa_scale')
    if grade is None or scale!=4.5 or not isinstance(grade,(int,float)) or isinstance(grade,bool) or not 0<=grade<=4.5:unknown.append('평점 3.0/4.5 이상 (다른 만점 체계는 재단 확인)')
    elif grade>=3.0:yes.append('평점 3.0/4.5 이상')
    else:no.append('평점 3.0/4.5 이상')
    # The notice allows alternative documents when the income bracket is absent.
    if profile.get('income_bracket_2026_fall') is None:
        unknown.remove('2026년 2학기 소득분위 6 이내');unknown.append('소득분위 또는 대체 서류 인정 여부')
    return {'assessment':'조건 불일치 가능' if no else '추가 확인 필요' if unknown else '명시된 조건 확인됨',
            'matched':yes,'not_matched':no,'unknown':unknown,
            'notice':'2027년 두산연강재단 장학생 선발', 'deadline':'2026-11-13T18:00:00+09:00',
            'note':'원문과 첨부 공고를 재확인해야 하며, 합격이나 최종 자격 판단이 아닙니다.'}
