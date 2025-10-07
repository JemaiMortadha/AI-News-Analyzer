from rest_framework import serializers

class AnalyzeRequestSerializer(serializers.Serializer):
    text = serializers.CharField(required=True, allow_blank=False)

class AnalyzeResponseSerializer(serializers.Serializer):
    sentiment = serializers.CharField()
    confidence = serializers.FloatField()

class ArticleSerializer(serializers.Serializer):
    _id = serializers.CharField()
    text = serializers.CharField()
    sentiment = serializers.CharField()
    confidence = serializers.FloatField()
    created_at = serializers.CharField()