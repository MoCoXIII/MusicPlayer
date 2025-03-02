import json
import os
import time
import pygame
from pynput import keyboard

pygame.init()
pygame.mixer.init()

# Constants
AUDIO_FOLDER = 'audios/'
PDF_FOLDER = 'pdf/'
MEDIA_JSON_FILE = 'operations.json'
media_list = []

# Load or create media.json file
if not os.path.exists(MEDIA_JSON_FILE):
    with open(MEDIA_JSON_FILE, 'w') as f:
        json.dump([], f)

with open(MEDIA_JSON_FILE, 'r') as f:
    media_list = json.load(f)

# Add media files to json if not already present
for filename in os.listdir(AUDIO_FOLDER):
    if not any(media.get('audio') == filename for media in media_list):
        media_list.append({
            'media_index': len(media_list),
            'media_start': 0,
            'audio': filename,
            'fade_duration': 3000
        })

for i, media in enumerate(media_list):
    if isinstance(media['media_index'], list):
        new_media_list = []
        for j in range(len(media['media_index'])):
            new_media = {key: value[j] if isinstance(value, list) else value for key, value in media.items()}
            new_media['media_index'] = media['media_index'][j]
            new_media_list.append(new_media)
        media_list[i:i+1] = new_media_list

media_list.sort(key=lambda media: media['media_index'])

# Save updated media.json file
with open(MEDIA_JSON_FILE, 'w') as f:
    json.dump(media_list, f, indent=4, sort_keys=True)


def stop_media():
    global current_media_time, media_list
    fd = media_list[current_media_index].get('fade_duration')
    pygame.mixer_music.fadeout(fd if fd else 3000)


# Function to play media
def play_media(media):
    stop_media()
    if media.get('audio'):
        pygame.mixer_music.load(AUDIO_FOLDER + media.get('audio'))
        pygame.mixer_music.play(start=media['media_start'], fade_ms=media.get('fade_duration'))
        print(f"Playing {media.get('audio')} from {media['media_start']} seconds")
    if media.get('pdf'):
        print(f"Opening {media['pdf']}")
        os.system(f"start {PDF_FOLDER}{media['pdf']}")


# Function to handle keypresses
def previous_media(e):
    global current_media_index
    current_media_index = (current_media_index - 1) % len(media_list)
    play_media(media_list[current_media_index])


def pause_media(e):
    global current_media_time
    if pygame.mixer_music.get_busy():
        current_media_time = pygame.mixer_music.get_pos() / 1000
        stop_media()
        print(f"Paused {media_list[current_media_index].get('audio')} at {current_media_time} seconds")
    else:
        pygame.mixer_music.load(AUDIO_FOLDER + media_list[current_media_index].get('audio'))
        pygame.mixer_music.play(start=current_media_time, fade_ms=media_list[current_media_index].get('fade_duration'))
        print(f"Resumed {media_list[current_media_index].get('audio')} from {current_media_time} seconds")


def next_media(e):
    global current_media_index
    # Next media
    current_media_index = (current_media_index + 1) % len(media_list)
    play_media(media_list[current_media_index])


def on_press(key):
    if key == keyboard.KeyCode.from_char('i'):
        print("Stopping")
        stop_media()
        time.sleep(3)
        exit()
    elif key == keyboard.KeyCode.from_char('j'):
        previous_media(None)
    elif key == keyboard.KeyCode.from_char('k'):
        pause_media(None)
    elif key == keyboard.KeyCode.from_char('l'):
        next_media(None)


current_media_index = 0
current_media_time = 0

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
