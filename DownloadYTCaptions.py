import re
import xml.etree.ElementTree as ET
from pytube import YouTube


def parse_youtube_xml_captions(xml_content):
    """
    Parse YouTube's custom XML caption format.
    
    :param xml_content: Raw XML caption content
    :return: List of caption entries with timing and text
    """
    root = ET.fromstring(xml_content)
    
    captions = []
    current_time = 0
    
    # Iterate through body elements
    for elem in root.findall('.//p'):
        # Get timing information
        start_time = int(elem.get('t', 0)) / 1000  # Convert to seconds
        duration = int(elem.get('d', 0)) / 1000 if elem.get('d') else 0
        
        # Extract text from subelements
        text_parts = []
        for s_elem in elem.findall('s'):
            # Get text content of each segment
            segment_text = s_elem.text or ''
            text_parts.append(segment_text.strip())
        
        # Join text segments
        full_text = ' '.join(text_parts).strip()
        
        # Only add non-empty captions
        if full_text:
            captions.append({
                'start_time': start_time,
                'end_time': start_time + duration,
                'text': full_text
            })
    
    return captions

def convert_to_srt(captions):
    """
    Convert parsed captions to SRT format.
    
    :param captions: List of caption dictionaries
    :return: SRT formatted string
    """
    srt_entries = []
    
    for i, caption in enumerate(captions, 1):
        # Convert times to SRT time format
        def format_time(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millisecs = int((seconds - int(seconds)) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
        
        srt_entry = (
            f"{i}\n"
            f"{format_time(caption['start_time'])} --> {format_time(caption['end_time'])}\n"
            f"{caption['text']}\n\n"
        )
        srt_entries.append(srt_entry)
    
    return ''.join(srt_entries)

def save_custom_captions(xml_content, output_file='captions.srt'):
    """
    Save captions from YouTube's custom XML format to SRT.
    
    :param xml_content: Raw XML caption content
    :param output_file: Output SRT filename
    """
    try:
        # Parse the XML captions
        captions = parse_youtube_xml_captions(xml_content)
        
        # Convert to SRT
        srt_content = convert_to_srt(captions)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        print(f"Captions saved to {output_file}")
        print(f"Total captions parsed: {len(captions)}")
    
    except Exception as e:
        print(f"Error processing captions: {e}")

# Example usage (you would replace this with your actual XML content)
# xml_content = """Your XML string here"""
# save_custom_captions(xml_content)


def download_captions(youtube_url, language_code=None, output_file='captions.srt'):
    """
    Download captions from a YouTube video with improved error handling.
    
    :param youtube_url: URL of the YouTube video
    :param language_code: Language code of captions (optional)
    :return: SRT formatted captions
    """
    try:
        # Create YouTube object
        yt = YouTube(youtube_url)
        
        # Print available captions with more details
        print("Available captions:")
        i=0
        for caption in yt.captions:
            print(f"Code: {caption.code}, Language: {caption.name}")
            if i == 0:
                firstCaptionCode=caption.code
                if language_code==None:
                    language_code = firstCaptionCode
            i += 1
        
        # Find the correct caption
        caption = next((cap for cap in yt.captions if cap.code == language_code), None)
        
        if not caption:
            raise ValueError(f"No captions found for language code: {language_code}")
        
        # Debug: Print raw XML captions
        print("Raw XML Captions:")
        print(caption.xml_captions[:500] + "..." if len(caption.xml_captions) > 500 else caption.xml_captions)
        

        # Fetch XML captions
        xml_captions = caption.xml_captions
        save_custom_captions(xml_captions)
    except Exception as e:
        print("Some error occured")
        pass 
    
    
def save_captions(youtube_url, output_file='captions.srt', language_code=None):
    """
    Save captions to an SRT file
    
    :param youtube_url: URL of the YouTube video
    :param output_file: Name of the output SRT file
    :param language_code: Language code of captions (optional)
    """
    print("Starting caption download...")
    download_captions(youtube_url, language_code)

from pytube.innertube import _default_clients

_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID"]

save_captions("https://www.youtube.com/watch?v=0_Zcpfb6fBo")