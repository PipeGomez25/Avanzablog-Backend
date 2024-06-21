from rest_framework import serializers
from rest_framework import exceptions
from .models import Post, Permission, Categories

class PermissionsSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Categories.objects.all(), source='category_name')
    
    class Meta:
        model = Permission
        fields = ['category', 'access']
        
   

class post_serializer(serializers.ModelSerializer):
    permissions_set = PermissionsSerializer(many=True)
    
    class Meta:
        model = Post
        fields = ['author', 'title', 'content', 'excerpt', 'timestamp', 'permissions_set']
        read_only_fields = ['author', 'excerpt', 'timestamp']
    
    def to_internal_value(self, data):
        permissions_set_data = data.get('permissions_set', [])
        for perm_data in permissions_set_data:
            category_name = perm_data.get('category')
            if category_name:
                try:
                    category = Categories.objects.get(category_name=category_name)
                    perm_data['category'] = category.id
                except Categories.DoesNotExist:
                    raise serializers.ValidationError(f"Category with name {category_name} does not exist.")
            else:
                raise serializers.ValidationError("Category name is required in permissions.")
        data['permissions_set'] = permissions_set_data
      
        return data
    
    def validate(self, data):
        
        if 'title' not in data or not data['title']:
            raise exceptions.ValidationError("title is required.")
        
        if 'content' not in data or not data['content']:
            raise exceptions.ValidationError("content is required.")
        
        permissions_set = data.get('permissions_set', [])
        provided_category_ids = [perm['category'] for perm in permissions_set]

        if len(provided_category_ids) != 4:
            raise exceptions.ValidationError("You must provide exactly 4 permissions, one for each category.")

        if len(set(provided_category_ids)) != 4:
            raise exceptions.ValidationError("Each permission must correspond to a different category.")

        all_category_ids = set(Categories.objects.values_list('id', flat=True))
        if not set(provided_category_ids).issubset(all_category_ids):
            raise exceptions.ValidationError("One or more provided categories are invalid.")

        return data
    
    def create(self, validated_data):
        permissions_data = validated_data.pop('permissions_set')
        author = self.context['request'].user
        post = Post.objects.create(
            author=author,
            title=validated_data['title'],
            content=validated_data['content'],
            excerpt=validated_data['content'][:200],
        )
        
        for perm_data in permissions_data:
            Permission.objects.create(post=post, category_id=perm_data['category'], access=perm_data['access'])
        return post
    
    def update(self, instance, validated_data):
        permissions_data = validated_data.pop('permissions_set')
        
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.excerpt = validated_data.get('content', instance.content)[:200]
        instance.save()

        instance.permissions_set.all().delete()
        for perm_data in permissions_data:
            Permission.objects.create(post=instance, category_id=perm_data['category'], access=perm_data['access'])
        return instance
    
    def to_representation(self, instance):
        represent=dict()
        represent['id']=instance.id
        represent['author']=instance.author.username
        represent['title']=instance.title
        represent['content']=instance.content
        represent['excerpt']=instance.excerpt
        represent['timestamp']=instance.timestamp
        permissions = instance.permissions_set.all()
        represent['permissions'] = {permission.category.category_name: permission.access for permission in permissions}
        return represent
    

