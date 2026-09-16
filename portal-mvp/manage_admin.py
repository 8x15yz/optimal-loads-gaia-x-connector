"""Local administrator provisioning. Run while the server is stopped."""
import argparse
import getpass
import portal

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='관리자 계정 생성 / 비밀번호 재설정')
    parser.add_argument('--username',default='admin')
    parser.add_argument('--port',type=int,default=8000)
    args=parser.parse_args()
    portal.app.state.db=portal.ROOT/'data'/f'portal-{args.port}.sqlite3'
    password=getpass.getpass('관리자 비밀번호 (8~128자): ')
    if password != getpass.getpass('비밀번호 확인: '):
        parser.error('비밀번호가 일치하지 않습니다')
    portal.bootstrap_admin(args.username,password)
    print('계정 준비 완료. 서버 실행 시 PORTAL_ADMIN_USERS에 해당 아이디를 지정하세요.')
