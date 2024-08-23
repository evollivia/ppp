from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.dbfactory import get_db
from app.schema.member import NewMember
from app.service.member import MemberService

member_router = APIRouter()
templates = Jinja2Templates(directory='views/templates')


@member_router.get('/login', response_class=HTMLResponse)
async def login(req: Request):
    return templates.TemplateResponse('member/login.html', {'request': req})


@member_router.post('/login', response_class=HTMLResponse)
async def loginok(req: Request, db: Session = Depends(get_db)):
    data = await req.json()
    try:
        print('전송한 데이터 : ', data)
        redirect_url = '/member/loginfail'
        if MemberService.login_member(db, data):
            req.session['logined_uid'] = data.get('userid')
            redirect_url = '/member/mainpage'
        print('리디렉션 URL : ', redirect_url)
        return RedirectResponse(url=redirect_url, status_code=303)

    except Exception as ex:
        print(f'▷▷▷ loginok 오류 : {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)


@member_router.get("/logout", response_class=HTMLResponse)
async def logout(req: Request):
    req.session.clear()  # 생성된 세션 객체 제거
    return RedirectResponse('/', status_code=303)


@member_router.get('/signup', response_class=HTMLResponse)
async def signup(req: Request):
    return templates.TemplateResponse('member/signup.html', {'request': req})


@member_router.post('/signup', response_class=HTMLResponse)
async def signupok(member: NewMember, db: Session = Depends(get_db)):
    try:
        print(member)
        result = MemberService.insert_member(db, member)
        print('처리결과 : ', result.rowcount)
        if result.rowcount > 0:  # 회원가입이 성공적으로 완료되면
            return RedirectResponse(url='/', status_code=303)
    except Exception as ex:
        print(f'▷▷▷ signupok에서 오류 발생: {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)


@member_router.get('/mainpage', response_class=HTMLResponse)
async def mainpage(req: Request, db: Session = Depends(get_db)):
    try:
        if 'logined_uid' not in req.session:   # 로그인하지 않았다면
            return RedirectResponse(url = '/', status_code=303)

        myinfo = MemberService.selectone_member(db, req.session['logined_uid'])
        print('--> ', myinfo)

        return templates.TemplateResponse('member/mainpage.html', {'request': req, 'mainpafe': myinfo})
    except Exception as ex:
        print(f'▷▷▷ mainpage 오류 발생: {str(ex)}')
        return RedirectResponse(url = '/member/error', status_code=303)


@member_router.get("/error", response_class=HTMLResponse)
async def error(req: Request):
    return templates.TemplateResponse('member/error.html', {'request': req})


@member_router.get("/loginfail", response_class=HTMLResponse)
async def loginfail(req: Request):
    return templates.TemplateResponse('member/loginfail.html', {'request': req})
