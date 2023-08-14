from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status,viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import  IsAuthenticated
from .models import Post,Comment, Plan, Group
from .serializers import PostSerializer,CommentSerializer, GroupPlanSerializer
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from . import models
from . import serializers
from rest_framework.views import APIView
# 특정 그룹 게시글 작성 
class PostViewSet(viewsets.ModelViewSet):
    #post_list
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def post(self, request, code):
        data = request.data
        data['group_code'] = code  # 그룹 코드를 요청 데이터에 추가

        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print('게시글저장')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #post_create
    def create(self,request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            writer = request.user #request.user를 writer로 받아오기 
            serializer.save(writer=writer)
            headers = self.get_success_headers(serializer.data) #성공시 헤더로 전달할 값들을 headers에 담기
            return Response(serializer.data,headers=headers)
        else:
            print("이거 뜨면 세션값 못 받고 있는거임 수정해야함.ㅜㅜ")
            return Response(serializer.data,{'error'}, status=status.HTTP_401_UNAUTHORIZED)
    #post_delete (권한 삭제 추가 필요)

# 그룹별 게시글 목록 
class GroupPostView(views.APIView):
    def get(self, request, group_code):
        try:
            group = models.Group.objects.get(code=group_code)
            posts = Post.objects.filter(group_code=group)
            serializer = serializers.GroupPostSerializer(posts, many=True)
            return Response(serializer.data)
        except models.Group.DoesNotExist:
            return Response({'error': '그룹 x'},status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, group_code, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = serializers.GroupPostSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = request.user  # 로그인한 사용자 가져오기

            group = get_object_or_404(models.Group, code=group_code)
            post = serializer.save(writer=request.user, group_code=group)  # group_code에 해당 그룹 할당
            
            return Response(serializers.GroupPostSerializer(post).data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': '사용자 x'},status=status.HTTP_401_UNAUTHORIZED)

#그룹의 게시글 상세 페이지 
class GroupPostDetailView(views.APIView):
    def get(self, request, code, post_id):
        try:
            post = Post.objects.get(group_code_code=code, id=post_id)
            serializer = serializers.GroupPostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': '게시글x'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, code, post_id):
        user = request.user 
        post = get_object_or_404(Post, id=post_id)

        userinfo = user.userinfo
        if post in userinfo.like_posts.all():
            print('이미 좋아요 누름')
            return Response(status=status.HTTP_400_BAD_REQUEST)

        userinfo.like_posts.add(post)

        is_liked = post in userinfo.like_posts.all()
        
        serializer = serializers.GroupPostSerializer(post)
        data = serializer.data
        data['is_liked'] = is_liked

        return Response(data, status=status.HTTP_201_CREATED)

    def patch(self, request, code, post_id):
        try:
            post = Post.objects.get(group_code__code=code, id=post_id)
        except Post.DoesNotExist:
            return Response({'error': '게시글이 없음'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != post.writer:
            return Response({'error': '작성자랑 유저랑 다름, 권한 X'}, status=status.HTTP_403_FORBIDDEN)

        serializer = serializers.GroupPostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code, post_id):
        try:
            post = Post.objects.get(group_code__code=code, id=post_id)
        except Post.DoesNotExist:
            return Response({'error': '게시글이 없음'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != post.writer:
            return Response({'error': '작성자랑 유저랑 다름, 권한 X'}, status=status.HTTP_403_FORBIDDEN)

        post.delete()
        return Response({'success': '게시글 삭제 성공!'}, status=status.HTTP_204_NO_CONTENT)


#댓글
class CommentView(views.APIView):

    def get(self, request, group_code, post_id):
        comments = Comment.objects.filter(post_id=post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    # ... other methods ...

    def post(self, request, group_code, post_id):
        if request.user.is_authenticated:
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(writer=request.user, post_id=post_id)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '사용자가 없어'}, status=status.HTTP_401_UNAUTHORIZED)

    
    # 댓글 수정 
    def patch(self, request, group_code, post_id, comment_id):
        comment = Comment.objects.get(id=comment_id, post_id=post_id)
        if request.user == comment.writer:
            serializer = CommentSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '작성자랑 유저랑 불일치'}, status=status.HTTP_403_FORBIDDEN)
        
    #댓글 삭제
    def delete(self, request, group_code, post_id, comment_id):    
        comment = Comment.objects.get(id=comment_id, post_id=post_id)
        if request.user == comment.writer:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': '작성자랑 유저랑 불일치'}, status=status.HTTP_403_FORBIDDEN)

# 그룹별 앨범 사진목록 
class AlbumViewSet(views.APIView):
    def get(self, request, group_code):
        try:
            group = models.Group.objects.get(code=group_code)
            posts = Post.objects.filter(group_code=group)
            serializer = serializers.AlbumSerializer(posts, many=True)
            return Response(serializer.data)
        except models.Group.DoesNotExist:
            return Response({'error': '그룹 x'},status=status.HTTP_404_NOT_FOUND)
    
# 앨범 상세 페이지
class AlbumDetailViewSet(views.APIView):
    def get(self, request, group_code, post_id):
        try:
            post = get_object_or_404(models.Post, id=post_id)
            serializer = serializers.AlbumSerializer(post)
            return Response(serializer.data)
        except models.Group.DoesNotExist:
            return Response({'error': '그룹 x'},status=status.HTTP_404_NOT_FOUND)

# 앨범 사진 다운로드 
class AlbumDownloadView(viewsets.ViewSet):
    def download(self, request, group_code, post_id): 
        post = get_object_or_404(models.Post, id=post_id, group_code=group_code)
        image = post.image
        path = image.path

        try:
            response = FileResponse(open(path, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="{image.name}"'
            return response
        except FileNotFoundError:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):  
        return Response({"detail": "This endpoint supports GET only."})

# 그룹별 일정 목록 
class GroupPlanView(views.APIView):
    def get(self, request, group_code):
        try:
            group_code = models.Group.objects.get(code=group_code)
            plan = models.Plan.objects.filter(group_code=group_code)
            serializer = serializers.GroupPlanSerializer(plan, many=True)
            return Response(serializer.data)
        
        except models.Plan.DoesNotExist:
            return Response({'error': '일정x'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, group_code):
        if request.user.is_authenticated:
            serializer = serializers.GroupPlanSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = request.user  # 로그인한 사용자 가져오기

            group = get_object_or_404(models.Group, code=group_code)
            plan = serializer.save(group_code=group)  # group_code에 해당 그룹 할당

            return Response(serializers.GroupPlanSerializer(plan).data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': '사용자 x'},status=status.HTTP_401_UNAUTHORIZED)

#그룹 일정 상세 페이지 
class GroupPlanDetailView(APIView):
    def get_object(self, id, code):
        try:
            return Plan.objects.get(id=id, group_code__code=code)
        except Plan.DoesNotExist:
            return None
    
    def get(self, request, code, id):
        plan = self.get_object(id=id, code=code)
        if plan is None:
            return Response({'error': '일정 x'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GroupPlanSerializer(plan)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, code, id, format=None):
        try:
            plan = self.get_object(id=id, code=code)
            if plan is None:
                return Response({'실패': '해당 모임 없음'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = GroupPlanSerializer(plan, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'실패': '해당 모임 없음'}, serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'실패': '모임생성안됨'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, code, id, format=None):
        plan = self.get_object(id=id, code=code)
        if plan is None:
            return Response({'실패': '해당 모임 없음'}, status=status.HTTP_404_NOT_FOUND)
        
        plan.delete()
        return Response({'성공': '삭제완료'}, status=status.HTTP_204_NO_CONTENT)
