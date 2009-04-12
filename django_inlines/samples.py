import re
from django_inlines.inlines import TemplateInline


class YoutubeInline(TemplateInline):
    """
    An inline that takes a youtube URL or video id and returns the proper embed.
    
    Examples::
    
        {{ youtube http://www.youtube.com/watch?v=4R-7ZO4I1pI&hd=1 }}
        {{ youtube 4R-7ZO4I1pI }}
        
    The inluded template supports width and height arguments::
    
        {{ youtube 4R-7ZO4I1pI width=850 height=500 }}
    
    """
    
    def get_context(self):
        video_id = self.value
        match = re.search(r'(?<=v\=)[\w]+', video_id)
        if match:
            video_id = match.group()
        return { 'video_id': video_id }
