import json
import os
import time

import pygame
from pynput import keyboard

pygame.init()
pygame.mixer.init()

# Constants
MEDIA_FOLDER = 'media/'
MEDIA_JSON_FILE = 'media.json'
media_list = []

# Load or create media.json file
if not os.path.exists(MEDIA_JSON_FILE):
    with open(MEDIA_JSON_FILE, 'w') as f:
        json.dump([], f)

with open(MEDIA_JSON_FILE, 'r') as f:
    media_list = json.load(f)

# Add media files to json if not already present
for filename in os.listdir(MEDIA_FOLDER):
    filepath = os.path.join(MEDIA_FOLDER, filename)

    if not any(media['file_path'] == filepath for media in media_list):
        media_list.append({
            'media_index': len(media_list),
            'media_start': 0,
            'file_path': filepath,
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
    pygame.mixer_music.fadeout(media_list[current_media_index]['fade_duration'])


# Function to play media
def play_media(media):
    stop_media()
    pygame.mixer_music.load(media['file_path'])
    pygame.mixer_music.play(start=media['media_start'], fade_ms=media['fade_duration'])
    print(f"Playing {media['file_path']} from {media['media_start']} seconds")


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
        print(f"Paused {media_list[current_media_index]['file_path']} at {current_media_time} seconds")
    else:
        pygame.mixer_music.load(media_list[current_media_index]['file_path'])
        pygame.mixer_music.play(start=current_media_time, fade_ms=media_list[current_media_index]['fade_duration'])
        print(f"Resumed {media_list[current_media_index]['file_path']} from {current_media_time} seconds")


def next_media(e):
    global current_media_index
    # Next media
    current_media_index = (current_media_index + 1) % len(media_list)
    play_media(media_list[current_media_index])


keyboard.on_press_key("j", suppress=True, callback=previous_media)
keyboard.on_press_key("k", suppress=True, callback=pause_media)
keyboard.on_press_key("l", suppress=True, callback=next_media)

current_media_index = 0
current_media_time = 0

keyboard.wait("i", suppress=True)

print("Stopping")
stop_media()
time.sleep(10)
