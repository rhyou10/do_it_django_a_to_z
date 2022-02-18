import re
from unicodedata import category
from urllib import response
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

        # user_obama 스태프 권한 부여
        self.user_obama.is_staff = True
        self.user_obama.save()

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name="music", slug="music")

        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')

        self.post_001 = Post.objects.create(
            title='1번',
            content = 'hello world',
            author = self.user_trump,
            category = self.category_programming,
        )
        self.post_001.tags.add(self.tag_hello)


        self.post_002 = Post.objects.create(
            title='2번',
            content = '1등이 전부는 아니자나',
            author = self.user_trump,
            category = self.category_music,
        )

        self.post_003 = Post.objects.create(
            title='3번',
            content = 'no category',
            author = self.user_obama,
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)

    #tag 페이지 만들어서 test
    def tes_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertIn(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find("div", id= 'main-area')
        self.assertIn(self.tag_hello.name, main_area.text)

        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    ## 카테고리 페이지 테스트
    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_programming.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)


    def navbar_test(self, soup):
        navbar = soup.nav
        
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        ## 블로그 상단의 about me, doit django, home, blog 페이지로 이동되는지 확인
        logo_btn = navbar.find('a', text = 'Do It Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text = 'Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text = 'Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text = 'About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')


    # 카테고리 분류 카드 확인
    def category_card_test(self, soup):
        category_card = soup.find('div', id='categories-card')
        # category-card안에  Categories 확인
        self.assertIn('Categories', category_card.text)

        # category(category.count) 있는여부
        # programming의 경우
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', category_card.text)

        # music의 경우
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})', category_card.text)

        # category 없는경우
        self.assertIn(f'미분류 (1)', category_card.text)
    

    # 포스트 리스트 테스트
    def test_post_list(self):
        # 포스트가 있는경우
        self.assertEqual(Post.objects.count(), 3)

        #1.1 포스트 목록 페이지 가져오기
        response = self.client.get('/blog/')

        #1.2 정상적으로 페이지 로드된다.
        self.assertEqual(response.status_code, 200)

        #1.3 페이지 타이틀은 Blog인가
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')

        #1.4 내비게이션 바가 있다.
        #1.5 blog, aboutme 라는 문구가 내비게이션 바에 있다.
        self.navbar_test(soup)

        # 카테고리 카트여부 테스트
        self.category_card_test(soup)

        #2.2 '아직 게시물이 없습니다' 라는 문구가 보인다.
        main_area = soup.find('div', id='main-area')

        #post_001_card는 post pk 1번게시물을 찾아 놓은것
        post_001_card = main_area.find('div', id = 'post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)
        
        post_002_card = main_area.find('div', id = 'post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id = 'post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)


        #3.2 포스트 목록 페이지를 새로고침 했을 때
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)


        #3.4 아직 게시물이 없습니다. 라는 문구는 더이상 보이지 않는다.
        self.assertNotIn('아직 게시물이 없습니다.', main_area.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text.upper())
        self.assertIn(self.user_obama.username.upper(), main_area.text.upper())


        ### 포스트가 없는경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다.', main_area.text)

    def test_post_detail(self):

        #1.2 그 포스트의 url은 '/blog/1/' 이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        #2. 첫 번째 포스트의 상세 페이지 테스트    
        #2.1 첫 번째 포스트의 url로 접근하면 정상적으로 작동한다 status code:200
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        
        #2.2 포스트 목록 페이지와 똑같은 내비게이션 바가 있다.
        soup = BeautifulSoup(response.content, 'html.parser')
        #navbar = soup.nav
        #self.assertIn('Blog', navbar.text)
        #self.assertIn('About Me', navbar.text)
        self.navbar_test(soup)
        self.category_card_test(soup)
        
        #2.3 첫 번쨰 포스트의 제목이 웹 브라우저 탬 타이틀에 들어 있다.
        self.assertIn(self.post_001.title, soup.title.text)
        
        #2.4 첫 번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text )

        #2.5 첫 번째 포스트의 작성자(author)가 포스트 영역에 있다.(아직 구현할수 없음)
        

        #2.6 첫 번째 포스트 내용(content)이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)


        self.assertIn(self.user_trump.username.upper(), main_area.text.upper())
        self.assertIn(self.post_001.content, post_area.text)

## 포스트 생성 페이지
    def test_create_post(self):
        # 로그인을 하지 않으면 status_code 200안되야 한다.
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        #트럼프 is_staff=false라 포스트 생성 불가 notequal
        self.client.login(username='trump', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff인 오바마로 로그인
        self.client.login(username='obama', password = 'somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)


        soup = BeautifulSoup(response.content, 'html.parser')


        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id = 'main-area')
        self.assertIn('Create New Post', main_area.text)

        tags_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tags_str_input)

        self.client.post(
            '/blog/create_post/',
            {
                'title' : 'post 만들기',
                'content' : "post form test",
                'tags_str' : 'new tag; 한글태그, python'
            }
        )

        self.assertEqual(Post.objects.count(),4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, 'post 만들기')
        self.assertEqual(last_post.content, 'post form test')
        self.assertEqual(last_post.author.username, 'obama')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글태그'))
        self.assertEqual(Tag.objects.count(), 5)
    

    # 포스트 수정 test  
    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 로그인 안함
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인 했는데 작성자 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_trump)
        self.client.login(
            username = self.user_trump,
            password = 'somepassword',
        )

        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)


        #작성자가 obama
        self.client.login(
            username = self.user_obama,
            password = 'somepassword',
        )

        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertIn('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        response = self.client.post(
            update_post_url,
            {
                'title' : '세번째 포스트 수정',
                'content' : '안녕',
                'category' : self.category_music.pk,
            },
            follow=True
        )

        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id = 'main-area')
        self.assertIn('세번째 포스트 수정', main_area.text)
        self.assertIn('안녕', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)
        