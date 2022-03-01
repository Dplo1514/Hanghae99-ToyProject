# from main import * : main에 선언된 모든 값을 가져온다 , __init__ file에 선언된 라이브러리를 가져와 사용할 수 있음.
from main import *
from flask import Blueprint
import requests

# 객체 = Blueprint("name" , __name__ , url_prefix="") : (이름, 모듈명, URL 프리픽스 값)
# 이름은 url_for함수에서 사용되며 , 모듈명은 init.py에서 선언한 모듈을 뜻함 , url_prefix="주소" 주소에는 브라우져에서 선언될 url을 입력한다

blueprint = Blueprint("my_page", __name__, url_prefix="/my_page")


@blueprint.route("/")  # <- 데코레이터
def mypage_template():
    return render_template("my_page.html")


# 사용자의 input 값인 link 를 크롤링해서 이미지 링크와 영화의 주소 값을 추출하는 함수
def link_select(link_data):
    # URL을 읽어서 HTML를 받아오고,
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(link_data, headers=headers)

    # HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
    soup = BeautifulSoup(data.text, 'html.parser')

    # select를 이용해서, tr들을 불러오기
    link = soup.select_one(
        '#content > div.article > div.mv_info_area > div.poster > a')
    img = link.select_one('img')['src']
    name = link.select_one('img')['alt']

    return {'img': img, 'name': name}


# user_index가 1이면 POST로 받아온 정보들을 user_index1로 db에 저장한다.
# session에 담겨있는 user_index를 받아 user_index를 별도로 할당해 저장할 것
@blueprint.route("/save", methods=["POST"])
def input_save():  # user의 input 정보 저장하기
    link_receive = request.form['link_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']

    parsing = link_select(link_receive)
    
    link = link_receive
    img = parsing['img']
    name = parsing['name']
    star = star_receive
    comment = comment_receive
    count = list(db.my_page.find({}, {'_id': False}))
    num = len(count) + 1

    doc = {'link' : link , 'post_num': num, 'img': img, 'name': name,
           'star': star, 'comment': comment}
    db.my_page.insert_one(doc)
    return jsonify({'msg': '저장 완료 되었습니다!'})

# user_index에 따라 저장돼 있는 데이터들을 temp_html로 붙힐 수 있게 리턴한다.


@blueprint.route("/data_post", methods=["GET"])
def input_post():
    data_page = list(db.my_page.find({}, {'_id': False}))
    return jsonify({'data_page': data_page})

# 삭제하기 버튼을 누르면 클라이언트에서 영화의 이름을 Post로 db에 보내줌 -> db에서 똑같은 이름의 data를 찾아 삭제함


@blueprint.route("/delete", methods=["POST"])
def delete():  # db에서 user정보 가져오기
    num_receive = request.form['num_give']
    db.my_page.delete_one({'post_num': int(num_receive)})
    return jsonify({'msg': '삭제완료 되었습니다.'})

# 수정을 누르면 팝업이 뜬다. 팝업창에 입력한 link , 평점 , comment가 변경된 데이터로 저장된다.
# 수정 창 팝업을 띄움과 동시에 num을 받고 num을 리턴해준다


@blueprint.route("/correction_page")  # <- 데코레이터
def mypage_correction_template():
    return render_template("my_page_correction.html")

# link , 평점 , comment가 변경됨 (기존의 data를 index해야함)
# 기존의 link , 평점 , comment 전부 index할 것
# 새롭게 들어온 link를 크롤링할 것


@blueprint.route("/correction_update", methods=["POST"])
def correction_update():
    num_receive = request.form['num_give']  # 팝업을 띄울 때 받았다.
    correction_link = request.form['correction_link_give']
    correction_star = request.form['correction_star_give']
    correction_comment = request.form['correction_comment_give']

    parsing = link_select(correction_link)
    correction_img = parsing['img']
    correction_name = parsing['name']

    db.my_page.update_many({'post_num': int(num_receive)}, {
                           '$set': {"img": correction_img}})
    db.my_page.update_many({'post_num': int(num_receive)}, {
                           '$set': {"name": correction_name}})
    db.my_page.update_many({'post_num': int(num_receive)}, {
                           '$set': {"star": correction_star}})
    db.my_page.update_many({'post_num': int(num_receive)}, {
                           '$set': {"comment": correction_comment}})

    return jsonify({'msg': '수정 완료 되었습니다.'})
