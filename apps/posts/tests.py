from rest_framework.test import APITestCase
from django.test import TestCase
from rest_framework import status
from django.urls import reverse
import json
from apps.posts.models import Post, Categories
from apps.users.factories import UserFactory, TeamFactory
from apps.users.models import Team
from apps.posts.factories import PostFactory, CategoriesFactory

class CreatePostTestCase(APITestCase):
    def setUp(self):
        self.team = TeamFactory(tname="Test Team")
        self.user = UserFactory(username="testuser", email="testuser@example.com", team=self.team, password="testpassword")
        self.client.login(username='testuser', password='testpassword')
        self.categories = [
            Categories.objects.create(category_name='Public'),
            Categories.objects.create(category_name='Authenticated'),
            Categories.objects.create(category_name='Team'),
            Categories.objects.create(category_name='Author')
        ]
        
    def test_user_create_post_with_permissions(self):
        contest='Esta prueba crea una publicación con permisos específicos y verifica que la creación haya sido exitosa, que la publicación se haya guardado correctamente en la base de datos y que tenga los permisos esperados.'
        post_data = {
            'title': 'Test Title',
            'content': contest,
            'permissions_set': [
                {'category': 'Public', 'access': 'none'},
                {'category': 'Authenticated', 'access': 'read'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
            }
        post_data_json = json.dumps(post_data)
        response = self.client.post(reverse('list-posts'), post_data_json, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.title, 'Test Title')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.content, contest)
        self.assertEqual(post.excerpt, contest[:200])
        self.assertIn('timestamp', response.data)
        self.assertEqual(post.permissions_set.count(), 4)
        self.assertEqual(post.permissions_set.first().access, 'none')

    def test_user_create_post_without_content(self):
        post_data = {
            'title': 'Test Title',
            'permissions_set': [
                {'category': 'Public', 'access': 'none'},
                {'category': 'Authenticated', 'access': 'read'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        post_data_json = json.dumps(post_data)
        response = self.client.post(reverse('list-posts'), post_data_json, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_post_without_title(self):
        post_data = {
            'content': 'Test Content',
            'permissions_set': [
                {'category': 'Public', 'access': 'none'},
                {'category': 'Authenticated', 'access': 'read'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        post_data_json = json.dumps(post_data)
        response = self.client.post(reverse('list-posts'), post_data_json, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_user_create_post_without_permissions(self):
        post_data = {
            'title': 'Test Title',
            'content': 'Test Content',
        }
        post_data_json = json.dumps(post_data)
        response = self.client.post(reverse('list-posts'), post_data_json, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  
        
    def test_create_post_with_invalid_permissions(self):
        post_data = {
            'title': 'Test Title',
            'content': 'Test Content',
            'permissions_set': [
                {'category': 'Public', 'access': 'none'},
                {'category': 'Authenticated', 'access': 'read'},
                {'category': 'Team', 'access': 'read_edit'},
            ]
        }
        post_data_json = json.dumps(post_data)
        response = self.client.post(reverse('list-posts'), post_data_json, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_post_with_invalid_name_of_permissions(self):
        post_data = {
            'title': 'Test Title',
            'content': 'Test Content',
            'permissions_set': [
                {'category': 'Public', 'access': 'none'},
                {'category': 'InvalidCategory', 'access': 'read'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        #post_data_json = json.dumps(post_data)
        response = self.client.post(reverse('list-posts'), post_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_post_without_name_of_permissions(self):
        post_data = {
            'title': 'Test Title',
            'content': 'Test Content',
            'permissions_set': [
                {'category': 'Public', 'access': 'none'},
                {'category': '', 'access': 'read'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        #post_data_json = json.dumps(post_data)
        response = self.client.post(reverse('list-posts'), post_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_post_with_duplicate_permissions(self):
        post_data = {
            'title': 'Test Title',
            'content': 'Test Content',
            'permissions_set': [
                {'category': 'Public', 'access': 'none'},
                {'category': 'Authenticated', 'access': 'read'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Team', 'access': 'read_edit'},
            ]
        }
        post_data_json = json.dumps(post_data)
        response = self.client.post(reverse('list-posts'), post_data_json, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)      
        
    def test_no_user_create_post(self):
        self.client.logout()
        post_data = {
            'title': 'Test Title',
            'content': 'Test Content',
            'permissions_set': [
                {'category': 'Public', 'access': 'none'},
                {'category': 'Authenticated', 'access': 'read'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        post_data_json = json.dumps(post_data)
        response = self.client.post(reverse('list-posts'), post_data_json, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DetailViewTest(APITestCase):

    def setUp(self):
        self.team1 = TeamFactory(tname="Test Team 1")
        self.team2 = TeamFactory(tname="Test Team 2")
        self.user1 = UserFactory(username="testuser1", email="testuser1@example.com", team=self.team1, password="testpassword")
        self.user2 = UserFactory(username="testuser2", email="testuser2@example.com", team=self.team2, password="testpassword")
        self.user3 = UserFactory(username="testuser3", email="testuser3@example.com", team=self.team1, is_admin=True, password="testpassword")
        self.Public_category = CategoriesFactory(category_name='Public')
        self.Authenticated_category = CategoriesFactory(category_name='Authenticated')
        self.Team_category = CategoriesFactory(category_name='Team')
        self.Author_category = CategoriesFactory(category_name='Author')
        
        self.post1 = PostFactory(author=self.user1, title='title post 1', 
            permissions_set=[
                {'category': self.Public_category, 'access': 'read_edit'},
                {'category': self.Authenticated_category, 'access': 'read_edit'},
                {'category': self.Team_category, 'access': 'read_edit'},
                {'category': self.Author_category, 'access': 'read_edit'}
            ])
        
        self.post2 = PostFactory(author=self.user1, title='title post 2', 
            permissions_set=[
                {'category': self.Public_category, 'access': 'read'},
                {'category': self.Authenticated_category, 'access': 'read'},
                {'category': self.Team_category, 'access': 'read'},
                {'category': self.Author_category, 'access': 'read'}
            ])
        
        self.post3 = PostFactory(author=self.user1, title='title post 3', 
            permissions_set=[
                {'category': self.Public_category, 'access': 'none'},
                {'category': self.Authenticated_category, 'access': 'none'},
                {'category': self.Team_category, 'access': 'none'},
                {'category': self.Author_category, 'access': 'none'}
            ])
        
        self.post4 = PostFactory(author=self.user3, title='title post 4', 
            permissions_set=[
                {'category': self.Public_category, 'access': 'none'},
                {'category': self.Authenticated_category, 'access': 'read'},
                {'category': self.Team_category, 'access': 'read_edit'},
                {'category': self.Author_category, 'access': 'none'}
            ])
        
        self.post5 = PostFactory(author=self.user3, title='title post 5', 
            permissions_set=[
                {'category': self.Public_category, 'access': 'read'},
                {'category': self.Authenticated_category, 'access': 'read'},
                {'category': self.Team_category, 'access': 'none'},
                {'category': self.Author_category, 'access': 'read'}
            ])
        
        self.post6 = PostFactory(author=self.user2, title='title post 6', 
            permissions_set=[
                {'category': self.Public_category, 'access': 'read'},
                {'category': self.Authenticated_category, 'access': 'none'},
                {'category': self.Team_category, 'access': 'read'},
                {'category': self.Author_category, 'access': 'read_edit'}
            ])
        
        self.post7 = PostFactory(author=self.user1, title='title post 7', 
            permissions_set=[
                {'category': self.Public_category, 'access': 'none'},
                {'category': self.Authenticated_category, 'access': 'read_edit'},
                {'category': self.Team_category, 'access': 'read'},
                {'category': self.Author_category, 'access': 'none'}
            ])

    
    def test_retrieve_public_with_permission(self):
        url = reverse('post-detail', kwargs={'pk': self.post2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'title post 2')

    def test_retrieve_public_without_permission(self):
        url = reverse('post-detail', kwargs={'pk': self.post4.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            
    def test_retrieve_authenticated_with_permission_read(self):
        self.client.login(username='testuser2', password='testpassword')
        url = reverse('post-detail', kwargs={'pk': self.post4.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'title post 4')
        
    def test_retrieve_authenticated_with_permission_edit(self):
        self.client.login(username='testuser2', password='testpassword')
        url = reverse('post-detail', kwargs={'pk': self.post1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'title post 1')

    def test_retrieve_authenticated_without_permission(self):
        self.client.login(username='testuser1', password='testpassword')
        url = reverse('post-detail', kwargs={'pk': self.post6.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_retrieve_team_with_permission(self):
        self.client.login(username='testuser1', password='testpassword')
        url = reverse('post-detail', kwargs={'pk': self.post4.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'title post 4')

    def test_retrieve_team_without_permission(self):
        self.client.login(username='testuser1', password='testpassword')
        url = reverse('post-detail', kwargs={'pk': self.post5.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_retrieve_author_with_permission(self):
        self.client.login(username='testuser1', password='testpassword')
        url = reverse('post-detail', kwargs={'pk': self.post2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'title post 2')

    def test_retrieve_author_without_permission(self):
        self.client.login(username='testuser1', password='testpassword')
        url = reverse('post-detail', kwargs={'pk': self.post3.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_retrieve_admin_with_permission(self):
        self.client.login(username='testuser3', password='testpassword')
        url = reverse('post-detail', kwargs={'pk': self.post1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'title post 1')

    def test_retrieve_admin_without_permission(self):
        self.client.login(username='testuser3', password='testpassword')
        url = reverse('post-detail', kwargs={'pk': self.post3.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'title post 3')
      
    def test_delete_public_with_permission(self):
        pk=self.post1.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)        
        self.assertEqual(response.data['message'], 'post deleted')
        self.assertFalse(Post.objects.filter(pk=pk).exists())

    def test_delete_public_without_permission(self):
        pk=self.post2.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.filter(pk=pk).exists())
            
    def test_delete_authenticated_with_permission(self):
        self.client.login(username='testuser2', password='testpassword')
        pk=self.post1.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)        
        self.assertEqual(response.data['message'], 'post deleted')
        self.assertFalse(Post.objects.filter(pk=pk).exists())

    def test_delete_authenticated_without_permission(self):
        self.client.login(username='testuser2', password='testpassword')
        pk=self.post4.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.filter(pk=pk).exists())
     
    def test_delete_team_with_permission(self):
        self.client.login(username='testuser1', password='testpassword')
        pk=self.post4.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)        
        self.assertEqual(response.data['message'], 'post deleted')
        self.assertFalse(Post.objects.filter(pk=pk).exists())

    def test_delete_team_without_permission(self):
        self.client.login(username='testuser2', password='testpassword')
        pk=self.post4.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.filter(pk=pk).exists())
        
    def test_delete_author_with_permission(self):
        self.client.login(username='testuser2', password='testpassword')
        pk=self.post6.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)        
        self.assertEqual(response.data['message'], 'post deleted')
        self.assertFalse(Post.objects.filter(pk=pk).exists())

    def test_delete_author_without_permission(self):
        self.client.login(username='testuser1', password='testpassword')
        pk=self.post2.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.filter(pk=pk).exists())
    
    def test_delete_admin_with_permission(self):
        self.client.login(username='testuser3', password='testpassword')
        pk=self.post3.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)        
        self.assertEqual(response.data['message'], 'post deleted')
        self.assertFalse(Post.objects.filter(pk=pk).exists())

    def test_delete_admin_without_permission(self):
        self.client.login(username='testuser3', password='testpassword')
        pk=self.post4.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)        
        self.assertEqual(response.data['message'], 'post deleted')
        self.assertFalse(Post.objects.filter(pk=pk).exists())
        
    def test_edit_post_with_permission(self):
        post=self.post1
        pk = post.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        updated_data = {
            'title': 'Updated title post 1',
            'content': 'Updated content for post 1',
            'permissions_set': [
                {'category': 'Public', 'access': 'read_edit'},
                {'category': 'Authenticated', 'access': 'read_edit'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, updated_data['title'])
        self.assertEqual(post.content, updated_data['content'])
     
    def test_edit_public_without_permission(self):
        post=self.post6
        pk=post.pk
        title=post.title
        content=post.content
        url = reverse('post-detail', kwargs={'pk': pk})
        updated_data = {
            'title': 'Updated title post',
            'content': 'Updated content for post',
            'permissions_set': [
                {'category': 'Public', 'access': 'read_edit'},
                {'category': 'Authenticated', 'access': 'read_edit'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.post1.refresh_from_db()
        self.assertEqual(post.title, title)
        self.assertEqual(post.content, content)
          
    def test_edit_authenticated_with_permission(self):
        self.client.login(username='testuser2', password='testpassword')
        post=self.post7
        pk = post.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        updated_data = {
            'title': 'Updated title post',
            'content': 'Updated content for post',
            'permissions_set': [
                {'category': 'Public', 'access': 'read_edit'},
                {'category': 'Authenticated', 'access': 'read_edit'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, updated_data['title'])
        self.assertEqual(post.content, updated_data['content'])

    def test_edit_authenticated_without_permission(self):
        self.client.login(username='testuser1', password='testpassword')
        post=self.post6
        pk=post.pk
        title=post.title
        content=post.content
        url = reverse('post-detail', kwargs={'pk': pk})
        updated_data = {
            'title': 'Updated title post',
            'content': 'Updated content for post',
            'permissions_set': [
                {'category': 'Public', 'access': 'read_edit'},
                {'category': 'Authenticated', 'access': 'read_edit'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        post.refresh_from_db()
        self.assertEqual(post.title, title)
        self.assertEqual(post.content, content)
     
    def test_edit_team_with_permission(self):
        self.client.login(username='testuser1', password='testpassword')
        post=self.post4
        pk = post.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        updated_data = {
            'title': 'Updated title post',
            'content': 'Updated content for post',
            'permissions_set': [
                {'category': 'Public', 'access': 'read_edit'},
                {'category': 'Authenticated', 'access': 'read_edit'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, updated_data['title'])
        self.assertEqual(post.content, updated_data['content'])

    def test_edit_team_without_permission(self):
        self.client.login(username='testuser1', password='testpassword')
        post=self.post5
        pk=post.pk
        title=post.title
        content=post.content
        url = reverse('post-detail', kwargs={'pk': pk})
        updated_data = {
            'title': 'Updated title post',
            'content': 'Updated content for post',
            'permissions_set': [
                {'category': 'Public', 'access': 'read_edit'},
                {'category': 'Authenticated', 'access': 'read_edit'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        post.refresh_from_db()
        self.assertEqual(post.title, title)
        self.assertEqual(post.content, content)
         
    def test_edit_author_with_permission(self):
        self.client.login(username='testuser2', password='testpassword')
        post=self.post6
        pk = post.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        updated_data = {
            'title': 'Updated title post',
            'content': 'Updated content for post',
            'permissions_set': [
                {'category': 'Public', 'access': 'read_edit'},
                {'category': 'Authenticated', 'access': 'read_edit'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, updated_data['title'])
        self.assertEqual(post.content, updated_data['content'])

    def test_edit_author_without_permission(self):
        self.client.login(username='testuser1', password='testpassword')
        post=self.post7
        pk=post.pk
        title=post.title
        content=post.content
        url = reverse('post-detail', kwargs={'pk': pk})
        updated_data = {
            'title': 'Updated title post',
            'content': 'Updated content for post',
            'permissions_set': [
                {'category': 'Public', 'access': 'read_edit'},
                {'category': 'Authenticated', 'access': 'read_edit'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        post.refresh_from_db()
        self.assertEqual(post.title, title)
        self.assertEqual(post.content, content)
    
    def test_edit_admin_permission(self):
        self.client.login(username='testuser3', password='testpassword')
        post=self.post3
        pk = post.pk
        url = reverse('post-detail', kwargs={'pk': pk})
        updated_data = {
            'title': 'Updated title post',
            'content': 'Updated content for post',
            'permissions_set': [
                {'category': 'Public', 'access': 'read_edit'},
                {'category': 'Authenticated', 'access': 'read_edit'},
                {'category': 'Team', 'access': 'read_edit'},
                {'category': 'Author', 'access': 'read_edit'}
            ]
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, updated_data['title'])
        self.assertEqual(post.content, updated_data['content'])
        
    def test_list_public_posts(self):
        url = reverse('list-posts')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.post1.title)
        self.assertContains(response, self.post2.title)
        self.assertContains(response, self.post5.title)
        self.assertContains(response, self.post6.title)
        self.assertNotContains(response, self.post3.title)
        self.assertNotContains(response, self.post4.title)
        self.assertNotContains(response, self.post7.title)
    
    def test_list_authenticated_posts(self):
        self.client.login(username='testuser2', password='testpassword')
        url = reverse('list-posts')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.post1.title)
        self.assertContains(response, self.post2.title)
        self.assertContains(response, self.post4.title)
        self.assertContains(response, self.post5.title)
        self.assertContains(response, self.post6.title)
        self.assertContains(response, self.post7.title)
        self.assertNotContains(response, self.post3.title)
        
    def test_list_team_posts(self):
        self.client.login(username='testuser1', password='testpassword')
        url = reverse('list-posts')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.post1.title)
        self.assertContains(response, self.post2.title)
        self.assertContains(response, self.post4.title)
        self.assertNotContains(response, self.post3.title) 
        self.assertNotContains(response, self.post5.title)
        self.assertNotContains(response, self.post6.title)
        self.assertNotContains(response, self.post7.title)
    
    def test_list_admin_posts(self):
        self.client.login(username='testuser3', password='testpassword')
        url = reverse('list-posts')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 7)
        self.assertContains(response, self.post1.title)
        self.assertContains(response, self.post2.title)
        self.assertContains(response, self.post3.title)
        self.assertContains(response, self.post4.title)
        self.assertContains(response, self.post5.title)
        self.assertContains(response, self.post6.title)
        self.assertContains(response, self.post7.title)
        
    def test_empty_list_posts(self):
        self.post1.delete()
        self.post2.delete()
        self.post5.delete()
        self.post6.delete()
        url = reverse('list-posts')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

        