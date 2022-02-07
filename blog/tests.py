from unicodedata import category
from urllib import response
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category

# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')
        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name="music", slug="music")

        self.post_001 = Post.objects.create(
            title='1번',
            content = 'hello world',
            author = self.user_trump,
            category = self.category_programming,
        )

        self.post_002 = Post.objects.create(
            title='2번',
            content = '1등이 전부는 아니자나',
            author = self.user_obama,
            category = self.category_music,
        )

        self.post_003 = Post.objects.create(
            title='3번',
            content = 'no category',
            author = self.user_trump,
        )


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

        post_001_card = main_area.find('div', id = 'post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        
        post_002_card = main_area.find('div', id = 'post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)

        post_003_card = main_area.find('div', id = 'post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text)


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

        #1.1 포스트가 하나있다.

        post_001 = Post.objects.create(
            title = '첫 포스트',
            content = 'hello world',
            author = self.user_trump,
        )

        #1.2 그 포스트의 url은 '/blog/1/' 이다.
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        #2. 첫 번째 포스트의 상세 페이지 테스트    
        #2.1 첫 번째 포스트의 url로 접근하면 정상적으로 작동한다 status code:200
        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        
        #2.2 포스트 목록 페이지와 똑같은 내비게이션 바가 있다.
        soup = BeautifulSoup(response.content, 'html.parser')
        #navbar = soup.nav
        #self.assertIn('Blog', navbar.text)
        #self.assertIn('About Me', navbar.text)
        self.navbar_test(soup)
        
        #2.3 첫 번쨰 포스트의 제목이 웹 브라우저 탬 타이틀에 들어 있다.
        self.assertIn(post_001.title, soup.title.text)
        
        #2.4 첫 번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(post_001.title, post_area.text )

        #2.5 첫 번째 포스트의 작성자(author)가 포스트 영역에 있다.(아직 구현할수 없음)
        

        #2.6 첫 번째 포스트 내용(content)이 포스트 영역에 있다.
        self.assertIn(post_001.content, post_area.text)


        self.assertIn(self.user_trump.username.upper(), main_area.text.upper())

