from django.shortcuts import render
import logging

# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from main.gemini import get_method
from .models import PlayList, Video, WatchHistory
from main.serializers import HistorySearchSerializer, PlayListSerializer, RecommendationSerializer, SearchSerializer, UpdateWatchHistorySerializer, VideoSerializer

class SearchView(GenericAPIView):
    serializer_class = SearchSerializer
    

    def get(self, request):
        serializer = self.serializer_class(data = request.query_params)
        print("Checking the serializer")
        logger = logging.getLogger(__name__)
        logger.debug("Payment system is not responding")
        logger.debug("Checking the serializer")
        if serializer.is_valid():
            return Response(serializer.validated_data, status= status.HTTP_200_OK)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)


class HistorySearchView(GenericAPIView):
    serializer_class = HistorySearchSerializer
    
    def get(self, request):
        serializer = self.serializer_class(data = request.query_params, context= {"user": request.user})

        if serializer.is_valid():
            return Response(serializer.validated_data, status= status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecommendationView(GenericAPIView):
    serializer_class = RecommendationSerializer
    
    def get(self, request):
        serializer = self.serializer_class(data = request.query_params, context= {"user": request.user})

        if serializer.is_valid():
            return Response(serializer.validated_data, status= status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PlayListView(GenericAPIView):
    """
    API View for PlayList CRUD operations with comprehensive error handling
    """
    serializer_class = PlayListSerializer
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access

    def get(self, request):
        """
        Retrieve all playlists for the current user
        """
        queryset = PlayList.objects.filter(user=request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new playlist for the current user
        """
        serializer = self.serializer_class(
            data=request.data, 
            context={'user': request.user}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PlayListDetailView(GenericAPIView):
    """
    API View for individual playlist operations (Retrieve, Update, Delete)
    """
    serializer_class = PlayListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Ensure users can only access their own playlists
        """
        return PlayList.objects.filter(user=self.request.user)

    def get(self, request, pk):
        """
        Retrieve a specific playlist by primary key
        """
        try:
            playlist = self.get_queryset().get(pk=pk)
            serializer = self.serializer_class(playlist)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PlayList.DoesNotExist:
            return Response(
                {"detail": "Playlist not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk):
        """
        Fully update a specific playlist
        """
        try:
            playlist = self.get_queryset().get(pk=pk)
            serializer = self.serializer_class(
                playlist, 
                data=request.data, 
                context={'user': request.user}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except PlayList.DoesNotExist:
            return Response(
                {"detail": "Playlist not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, pk):
        """
        Partially update a specific playlist
        """
        try:
            playlist = self.get_queryset().get(pk=pk)
            serializer = self.serializer_class(
                playlist, 
                data=request.data, 
                partial=True,  # Allow partial updates
                context={'user': request.user}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except PlayList.DoesNotExist:
            return Response(
                {"detail": "Playlist not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        """
        Delete a specific playlist
        """
        try:
            playlist = self.get_queryset().get(pk=pk)
            playlist.delete()
            return Response(
                {"detail": "Playlist successfully deleted"}, 
                status=status.HTTP_204_NO_CONTENT
            )
        except PlayList.DoesNotExist:
            return Response(
                {"detail": "Playlist not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )


class UpdateWatchHistoryView(GenericAPIView):
    
    def post(self, request):
        serializer = UpdateWatchHistorySerializer(data=request.data, context={'user': request.user})

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Watch history updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VideoView(GenericAPIView):
    serializer_class = VideoSerializer

    def get(self, request, id):
        try:
            # Retrieve the video by its video_id
            query = Video.objects.get(video_id=id)
            
            # Serialize the video object
            serializer = self.serializer_class(query)
            
            # Return the serialized data directly
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Video.DoesNotExist:
            # Handle case where video is not found
            return Response(
                {"detail": "Video not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )


class HistoryListView(GenericAPIView):
    permission_class= [IsAuthenticated]

    def get(self, request):
        try:
            watch_history = WatchHistory.objects.get(user=request.user)
            qs = watch_history.videos.all()
            serializer = VideoSerializer(qs, many=True)
            return Response(serializer.data, status= status.HTTP_200_OK)
        except WatchHistory.DoesNotExist:
            return Response(
                {"detail": "Watch History not found"},
                status= status.HTTP_404_NOT_FOUND
            )
    
    

class IngredientMethodView(GenericAPIView):

    def get(self, request, id):
        instance = Video.objects.get(video_id=id)
        try:
            if instance.method == [] or instance.ingredient_list== []:
                ingredient_list, method = get_method(instance.video_id)
                instance.method = method
                instance.ingredient_list = ingredient_list
                instance.save()
            else:
                ingredient_list = instance.ingredient_list
                method = instance.method
        except Video.DoesNotExist:
            return Response({
                "error": f"No Video with videoID {id} exist."
            }, status=status.HTTP_404_NOT_FOUND)
        return Response({"ingredient_list": ingredient_list,
                         "method": method})