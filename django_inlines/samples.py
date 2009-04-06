import re
from django_inlines.inlines import TemplateInline

class YoutubeInline(TemplateInline):
    """
    An inline that takes a youtube URL or video id and returns the proper embed.
    """
    def get_context(self):
        video_id = self.value
        match = re.search(r'(?<=v\=)[\w]+', video_id)
        if match:
            video_id = match.group()
        return { 'video_id': video_id }
    