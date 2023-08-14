from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from accounts.serializers import UserInfoSerializer
from .models import Post, Comment, Plan

class PostSerializer(ModelSerializer):
    writer = UserInfoSerializer(many=True, source='user.all')
    class Meta:
        model = Post
        fields = '__all__'
    
    def get_writer(self, obj):
        return obj.writer.user.username if obj.writer else None

class AlbumSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = [ 'id', 'image','created_at' ]

class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = [ 'id','post','comment','writer','created_at' ]

class GroupPostSerializer(ModelSerializer):
    liked = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'writer','content','created_at', 'image','liked']

class GroupPlanSerializer(ModelSerializer) :
    class Meta :
        model = Plan
        fields = ['id', 'month', 'date', 'title', 'memo']