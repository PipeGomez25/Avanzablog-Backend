from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.likes.factories import LikeFactory
from apps.users.factories import UserFactory, TeamFactory
from apps.posts.factories import PostFactory, CategoriesFactory
from apps.likes.models import Like

class LikeViewSetTest(APITestCase):

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
        
        self.like1 = LikeFactory(post=self.post1, user=self.user1)
        self.like2 = LikeFactory(post=self.post2, user=self.user1)
        self.like3 = LikeFactory(post=self.post5, user=self.user1)
        self.like4 = LikeFactory(post=self.post5, user=self.user2)

    def test_create_like_without_user(self):
        url = reverse('like-list')
        data = {'post': self.post1.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 4)
    
    def test_create_like_with_view_permission(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('like-list')
        data = {'post': self.post2.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 5)
    
    def test_create_like_in_unexistent_post(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('like-list')
        data = {'post': 40}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Like.objects.count(), 4)
    
    def test_create_duplicated_like_with_view_permission(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('like-list')
        data = {'post': self.post1.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Like.objects.count(), 4)
    
    def test_create_like_without_view_permission(self):
        self.client.force_authenticate(user=self.user2)
        self.client.login(username='testuser2', password='testpassword')
        url = reverse('like-list')
        data = {'post': self.post3.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Like.objects.count(), 4)
    
    def test_delete_like_with_permissions(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('like-detail', kwargs={'pk': self.like3.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Like.objects.count(), 3)
    #
    def test_delete_like_without_user(self):
        url = reverse('like-detail', kwargs={'pk': self.like1.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 4)
    #
    def test_delete_like_other_user_with_permissions_in_view(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('like-detail', kwargs={'pk': self.like2.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 4)
            
    def test_delete_like_without_permissions(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('like-detail', kwargs={'pk': self.like2.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Like.objects.count(), 4)
        
    def test_delete_unexistent_like(self):
        #import pdb;pdb.set_trace()
        self.client.force_authenticate(user=self.user1)
        url = reverse('like-detail', kwargs={'pk': 80})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Like.objects.count(), 4)
    
    def test_list_1_like_permission(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('like-list')
        response = self.client.get(url, format='json')
        self.assertEqual(len(response.data['results']), 2)

    def test_list_2_like_permission(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('like-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
    def test_list_3_like_permission(self):
        self.client.force_authenticate(user=self.user3)
        url = reverse('like-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        
    def test_list_filter_by_post_like_permission(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('like-list')
        response = self.client.get(url, {'post': self.post5.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
    def test_list_filter_by_user_like_permission(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('like-list')
        response = self.client.get(url, {'user': self.user1.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_filter_by_user_and_post_like_permission(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('like-list')
        response = self.client.get(url, {'user': self.user2.id, 'post': self.post5.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_list_filter_by_post_like_without_permission(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('like-list')
        response = self.client.get(url, {'post': self.post1.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
  