import mimetypes

def get_file_type(filename):
    """Categorize file by MIME type"""
    mimetype, _ = mimetypes.guess_type(filename)
    if mimetype:
        if mimetype.startswith('image/'): return 'image'
        if mimetype.startswith('video/'): return 'video'
        if mimetype == 'application/pdf': return 'pdf'
        if mimetype.startswith('text/'): return 'text'
        if mimetype.startswith('audio/'): return 'audio'
        if 'zip' in mimetype or 'rar' in mimetype or '7z' in mimetype: 
            return 'archive'
    return 'generic'
