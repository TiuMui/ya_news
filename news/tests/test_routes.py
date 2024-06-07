from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Comment, News

User = get_user_model()


class TestRoutes(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # БД, на которой проводится тестирование, перед запуском тестов не
        # содержит никаких объектов. Создаём объект для теста.
        # Добавляем фикстуру с созданием первой новости:
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        # Для программного создания пользователей принято использовать метод
        # Django ORM create_user(), который правильным образом устанавливает
        # пароль для пользователя. Но в тестах мы пароли не используем —
        # и можем обойтись обычным create().
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        # От имени одного пользователя создаём комментарий к новости:
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text='Текст комментария'
        )

    '''
    def test_home_page(self):
        """Главная страница доступна анонимному пользователю."""
        # Вместо прямого указания адреса 
        # получаем его при помощи функции reverse().
        url = reverse('news:home')
        # Вызываем метод get для клиента (self.client)
        # и загружаем главную страницу.
        response = self.client.get(url)
        # Проверяем, что код ответа равен статусу OK (он же 200).
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_page(self):
        """Страница отдельной новости доступна анонимному пользователю"""
        # Передать необходимые значения в функцию reverse() можно через
        # позиционные args=(self.news.id,) или именованные
        # kwargs={'pk': self.news.id}) аргументы, вместо id можно использовать
        # pk, но в модели News id является pk.
        url = reverse('news:detail', args=(self.news.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
    '''

    def test_pages_availability(self):
        """Доступность нескольких страниц анонимным пользователям."""
        # Создаём набор тестовых данных - кортеж кортежей.
        # Каждый вложенный кортеж содержит два элемента:
        # имя пути и позиционные аргументы для функции reverse().
        urls = (
            # Путь для главной страницы не принимает
            # никаких позиционных аргументов, 
            # поэтому вторым параметром ставим None.
            ('news:home', None),
            # Путь для страницы новости 
            # принимает в качестве позиционного аргумента
            # id записи; передаём его в кортеже.
            ('news:detail', (self.news.id,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        # Итерируемся по внешнему кортежу 
        # и распаковываем содержимое вложенных кортежей:
        for name, args in urls:
            with self.subTest(name=name, args=args):
                # Передаём имя и позиционный аргумент в reverse()
                # и получаем адрес страницы для GET-запроса:
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        """Доступ к редактированию и удалению комментария автора комментария
        и читателя новости.
        """
        # При обращении к страницам редактирования и удаления комментария
        users_statuses = (
            (self.author, HTTPStatus.OK),  # автор комментария должен получить ответ OK,
            (self.reader, HTTPStatus.NOT_FOUND),  # читатель должен получить ответ NOT_FOUND.
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('news:edit', 'news:delete'):  
                with self.subTest(user=user, name=name):        
                    url = reverse(name, args=(self.comment.id,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """При попытке зайти на страницу редактирования или удаления чужого
        комментария анонимный пользователь должен быть переадресован на
        страницу логина.
        """
        # Сохраняем адрес страницы логина:
        login_url = reverse('users:login')
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for name in ('news:edit', 'news:delete'):
            with self.subTest(name=name):
                # Получаем адрес страницы редактирования или удаления комментария:
                url = reverse(name, args=(self.comment.id,))
                # Получаем ожидаемый адрес страницы логина, 
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url) 
