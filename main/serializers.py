from sqlite3 import IntegrityError
from rest_framework import serializers
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError
import random
from django.conf import settings

from main.gemini import get_method
from .models import WatchHistory, PlayList, Labels

from main.models import Video

class SearchSerializer(serializers.Serializer):
    q = serializers.CharField(max_length=255)

    def search(self, search_string, user):
        region = user.userprofile.region
        try:
            youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_DEVELOPER_KEY)
            request = youtube.search().list(
                q=search_string,
                part='snippet',
                type='video',
                regionCode=region,
                videoDuration='medium',
                relevanceLanguage='ur',
                maxResults=10
            )

            response = request.execute()

            response_list = []
            for obj in response['items']:
                response_list.append({"video_id": obj['id']['videoId'], "title": obj['snippet']["title"], "description": obj['snippet']['description'], "thumbnail": obj['snippet']['thumbnails']['high']["url"], "channel_name": obj['snippet']["channelTitle"], "method": [], "ingredient_list": []})

             # Save each video in the database using the serializer 
            for video_data in response_list: 
                serializer = VideoSerializer(data=video_data) 
                if serializer.is_valid(): 
                    try: 
                        serializer.save() 
                    except IntegrityError: 
                        continue
                else: 
                    print(f"Invalid data for video ID {video_data['video_id']}: {serializer.errors}")
            return response['items']
        except HttpError as e:
            raise serializers.ValidationError(f"An error occurred: {e}")

    # def search(self, search_string):
    #     try:
    #         # Implement caching
    #         youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_DEVELOPER_KEY)
            
    #         # Batch API calls
    #         request = youtube.search().list(
    #             q=search_string,
    #             part='snippet,statistics',  # Reduce number of API calls
    #             type='video',
    #             regionCode="us",
    #             videoDuration='medium',
    #             relevanceLanguage='en',
    #             maxResults=5
    #         )

    #         response = request.execute()

    #         response_list = []
    #         for item in response['items']:
    #             try:
    #                 ingredients, method = get_method(item['id']['videoId'])
                    
    #                 video_data = {
    #                     "video_id": item['id']['videoId'],
    #                     "title": item['snippet']["title"],
    #                     "description": item['snippet']['description'],
    #                     "thumbnail": item['snippet']['thumbnails']['default']["url"],
    #                     "channel_name": item['snippet']["channelTitle"],
    #                     "view_count": item['statistics'].get('viewCount', '0'),
    #                     "method": method,
    #                     "ingredient_list": ingredients
    #                 }
                    
    #                 # Use serializer validation
    #                 serializer = VideoSerializer(data=video_data)
    #                 if serializer.is_valid():
    #                     serializer.save()
                    
    #                 response_list.append(video_data)
                
    #             except Exception as e:
    #                 print(e)
            
    #         return response_list
        
    #     except HttpError as e:
    #         raise serializers.ValidationError(f"Search failed: {e}")
        
    def validate(self, attrs):
        search_string = attrs.get('q')
        user = self.context.get('user')
        results =self.search(search_string, user)
        return {'results': results}
    

    
class VideoSerializer(serializers.ModelSerializer): 
    ingredient_list = serializers.JSONField(default=[]) 
    method = serializers.JSONField(default={})
    class Meta: 
        model = Video 
        fields = ['id', 'video_id', 'title', 'description', 'channel_name', 'thumbnail', 'ingredient_list', 'method']

    def create(self, validated_data):
        """
        Create or get existing video based on video_id
        """
        video, created = Video.objects.get_or_create(
            video_id=validated_data['video_id'],
            defaults=validated_data
        )
        return video

class HistorySearchSerializer(serializers.Serializer): 
    q = serializers.CharField(max_length=255) 
    
    def search(self, query): 
        result = [] 
        user = self.context.get('user') 
        try: 
            history = WatchHistory.objects.get(user=user) 
            query_words = query.lower().split() 
            for video in history.videos.all(): 
                video_title_words = video.title.lower().split() 
                if any(word in video_title_words for word in query_words): 
                    data = VideoSerializer(video).data 
                    result.append(data) 
            return result 
        except WatchHistory.DoesNotExist: 
            return {"result": "no history created yet"}
        
    def validate(self, attrs): 
        try:
            search_string = attrs.get('q') 
            results = self.search(search_string) 
            return {'results': results}
        except Exception as e:
            return {'results': e}
                

class RecommendationSerializer(serializers.Serializer):
    
    def build_recommendation(self):
        user = self.context.get('user')
        result = []
        try:
            history = WatchHistory.objects.get(user=user)
            videos = list(history.videos.all())
            random_videos = random.sample(videos, min(len(videos), 10))
            for video in random_videos:
                title = video.title
                response= SearchSerializer().search(search_string=title)
                result.append(list(response))
            return result
        except WatchHistory.DoesNotExist: 
            return {"result": "no history created yet"}

    

    def validate(self, attrs):
        results = self.build_recommendation()
        return {'results': results}

class PlayListSerializer(serializers.ModelSerializer):
    """
    Serializer for PlayList model with comprehensive validation and custom create/update methods
    """
    add_video_ids = serializers.ListField(
        child=serializers.CharField(), 
        write_only=True,
        required=False
        ) # Assuming video_id is an IntegerField
    remove_video_ids = serializers.ListField(
        child=serializers.CharField(), 
        write_only=True,
        required=False
        ) 
    class Meta:
        model = PlayList
        fields = ['id', 'name', 'videos', 'user',
                  'add_video_ids', 'remove_video_ids']
        read_only_fields = ['user', 'videos']  # Prevent user manipulation from request data

    def create(self, validated_data):
        """
        Custom create method to ensure the playlist is associated with the current user
        """

        
        # Get the user from context (passed from the view)
        user = self.context.get('user')
        video_ids = validated_data.pop('video_ids', [])
        
        # Create playlist for the current user
        playlist = PlayList.objects.create(user=user, **validated_data)

        return playlist

    def update(self, instance, validated_data):
        """
        Custom update method to append new videos to existing playlist
        """
        # Extract video_ids if provided
        add_video_ids = validated_data.pop('add_video_ids', None)
        remove_video_ids = validated_data.pop('remove_video_ids', None)
        
        # Update playlist basic info
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle videos
        add_video_intances = []
        if add_video_ids is not None:
            for id in add_video_ids:
                video = Video.objects.get(video_id=id)
                if video not in instance.videos.all():
                    add_video_intances.append(video)
            instance.videos.add(*add_video_intances)

        
        if remove_video_ids is not None:
            for id in remove_video_ids:
                video = Video.objects.get(video_id=id)
                if video in instance.videos.all():
                    instance.videos.remove(video)
            
        instance.save()
        return instance

    
    def to_representation(self, instance):
        """
        Custom representation to ensure videos are serialized as full objects
        """
        representation = super().to_representation(instance)
        # Ensure videos are fully serialized
        representation['videos'] = VideoSerializer(instance.videos.all(), many=True).data
        return representation
    

class UpdateWatchHistorySerializer(serializers.Serializer):
    
    video_id = serializers.CharField(max_length=255)

    def validate(self, attrs):
       
        id = attrs.get('video_id')
        if not id:
            raise serializers.ValidationError("Video ID is required.")
        return attrs
    
    def save(self):
        video_id = self.validated_data['video_id']
        video = Video.objects.get(video_id=video_id)

        user = self.context['user']
        history, created = WatchHistory.objects.get_or_create(user=user)
        history.videos.add(video)
        user.save()



class LabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Labels
        fields = ['id', 'name', 'videos', 'region', 'last_updated']
        read_only_fields = ['last_updated', 'id',]