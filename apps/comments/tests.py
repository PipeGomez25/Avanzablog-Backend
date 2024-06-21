from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.comments.factories import CommentsFactory
from apps.users.factories import UserFactory, TeamFactory
from apps.posts.factories import PostFactory, CategoriesFactory
from .models import Comments

class CommentViewSetTest(APITestCase):

    def setUp(self):
        self.team1 = TeamFactory(tname="Test Team 1")
        self.team2 = TeamFactory(tname="Test Team 2")
        self.user1 = UserFactory(username="testuser1", email="testuser1@example.com", team=self.team1, password="testpassword")
        self.user2 = UserFactory(username="testuser2", email="testuser2@example.com", team=self.team2, password="testpassword")
        self.user3 = UserFactory(username="testuser3", email="testuser3@example.com", team=self.team1, password="testpassword", is_admin=True)
        
        self.Public_category = CategoriesFactory(category_name='Public')
        self.Authenticated_category = CategoriesFactory(category_name='Authenticated')
        self.Team_category = CategoriesFactory(category_name='Team')
        self.Author_category = CategoriesFactory(category_name='Author')
        
        self.post1 = PostFactory(author=self.user1, title='title post 1', 
            permissions_set=[
                {'category': self.Public_category, 'access': 'read_edit'},
                {'category': self.Authenticated_category, 'access': 'none'},
                {'category': self.Team_category, 'access': 'none'},
                {'category': self.Author_category, 'access': 'none'}
            ])
        
        self.post2 = PostFactory(author=self.user1, title='title post 2', 
            permissions_set=[
                {'category': self.Public_category, 'access': 'none'},
                {'category': self.Authenticated_category, 'access': 'read'},
                {'category': self.Team_category, 'access': 'none'},
                {'category': self.Author_category, 'access': 'none'}
            ])
        
        self.post3 = PostFactory(author=self.user1, title='title post 3', 
            permissions_set=[
                {'category': self.Public_category, 'access': 'none'},
                {'category': self.Authenticated_category, 'access': 'none'},
                {'category': self.Team_category, 'access': 'read_edit'},
                {'category': self.Author_category, 'access': 'none'}
            ])
        
        self.post4 = PostFactory(author=self.user1, title='title post 4', 
            permissions_set=[
                {'category': self.Public_category, 'access': 'none'},
                {'category': self.Authenticated_category, 'access': 'none'},
                {'category': self.Team_category, 'access': 'none'},
                {'category': self.Author_category, 'access': 'read'}
            ])
        
        self.post5 = PostFactory(author=self.user1, title='title post 5', 
            permissions_set=[
                {'category': self.Public_category, 'access': 'read'},
                {'category': self.Authenticated_category, 'access': 'read'},
                {'category': self.Team_category, 'access': 'read'},
                {'category': self.Author_category, 'access': 'read'}
            ])
        
        self.Comment1 = CommentsFactory(post=self.post1, user=self.user1)
        self.Comment2 = CommentsFactory(post=self.post2, user=self.user1)
        self.Comment3 = CommentsFactory(post=self.post5, user=self.user1)
        self.Comment4 = CommentsFactory(post=self.post5, user=self.user2)

    def test_create_comment_without_user(self):
        url = reverse('comments-list')
        data = {'post': self.post1.id,
                'comment': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comments.objects.count(), 4)
    
    def test_create_comment_without_content(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('comments-list')
        data = {'post': self.post2.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Comments.objects.count(), 4)
        
    def test_create_comment_with_view_permission(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('comments-list')
        data = {'post': self.post2.id,
                'comment': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comments.objects.count(), 5)
       
    def test_create_comment_in_unexistent_post(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('comments-list')
        data = {'post': 40,
                'comment': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Comments.objects.count(), 4)
    
    def test_create_comment_without_view_permission(self):
        self.client.force_authenticate(user=self.user2)
        self.client.login(username='testuser2', password='testpassword')
        url = reverse('comments-list')
        data = {'post': self.post3.id,
                'comment': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Comments.objects.count(), 4)
    
    def test_delete_comment_without_user(self):
        url = reverse('comments-detail', kwargs={'pk': self.Comment1.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comments.objects.count(), 4)
    
    def test_delete_comment_other_user_with_permissions_in_view(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('comments-detail', kwargs={'pk': self.Comment2.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comments.objects.count(), 4)
                
    def test_delete_comment_with_permissions(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('comments-detail', kwargs={'pk': self.Comment3.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comments.objects.count(), 3)
        
    def test_delete_comment_without_permissions(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('comments-detail', kwargs={'pk': self.Comment2.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comments.objects.count(), 4)
    
    def test_delete_unexistent_comment(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('comments-detail', kwargs={'pk': 80})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Comments.objects.count(), 4)
    
    def test_list_1_comment_permission(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('comments-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_2_comment_permission(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('comments-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
    def test_list_3_comment_permission(self):
        self.client.force_authenticate(user=self.user3)
        url = reverse('comments-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        
    def test_list_filter_by_post_comment_permission(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('comments-list')
        response = self.client.get(url, {'post': self.post5.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
    def test_list_filter_by_user_comment_permission(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('comments-list')
        response = self.client.get(url, {'user': self.user1.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_filter_by_user_and_post_comment_permission(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('comments-list')
        response = self.client.get(url, {'user': self.user2.id, 'post': self.post5.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_list_filter_by_post_comment_without_permission(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('comments-list')
        response = self.client.get(url, {'post': self.post1.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
