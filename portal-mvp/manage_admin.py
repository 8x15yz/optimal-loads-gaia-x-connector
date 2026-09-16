"""운영자(operator) 계정 생성 / 비밀번호 재설정 / 권한 해제. 서버를 멈춘 상태에서 실행.

운영자는 데이터스페이스 참여자(provider/consumer) 역할이 아닌 플랫폼 관리 권한이므로
웹 가입으로는 부여하지 않는다. 권한은 DB의 accounts.is_operator에 기록된다.
"""
import argparse
import getpass
import portal

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='운영자 계정 생성 / 비밀번호 재설정 / 권한 해제')
    parser.add_argument('--username',default='admin')
    parser.add_argument('--port',type=int,default=8000)
    parser.add_argument('--revoke',action='store_true',help='운영자 권한만 해제 (계정·VC·서비스 유지)')
    args=parser.parse_args()
    portal.app.state.db=portal.ROOT/'data'/f'portal-{args.port}.sqlite3'
    if args.revoke:
        if portal.revoke_operator(args.username):
            print('운영자 권한을 해제했습니다. PORTAL_ADMIN_USERS에 이 아이디가 남아 있다면 함께 제거하세요.')
        else:
            parser.error('해당 아이디의 계정이 없습니다')
    else:
        password=getpass.getpass('운영자 비밀번호 (8~128자): ')
        if password != getpass.getpass('비밀번호 확인: '):
            parser.error('비밀번호가 일치하지 않습니다')
        portal.bootstrap_admin(args.username,password)
        print('운영자 계정 준비 완료. PORTAL_ADMIN_USERS 지정 없이 바로 서버를 실행하면 됩니다.')
