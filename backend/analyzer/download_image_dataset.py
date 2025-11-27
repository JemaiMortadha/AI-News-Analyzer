#!/usr/bin/env python3
"""
Enhanced Auto-download news image dataset for sentiment analysis
- Validates images to skip corrupted files
- More diverse search queries (75+ per sentiment)
- Downloads 20 images per query for larger dataset
- Total: ~4,500+ valid images
"""

from bing_image_downloader import downloader
import os
from pathlib import Path
from PIL import Image
import shutil

# Create dataset directories
def create_directories():
    dirs = [
        'image_dataset/train/positive',
        'image_dataset/train/negative',
        'image_dataset/train/neutral',
        'image_dataset/val/positive',
        'image_dataset/val/negative',
        'image_dataset/val/neutral',
        'image_dataset/temp'  # Temporary download location
    ]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ Directories created!")

# Expanded search queries - 75+ per sentiment
CATEGORIES = {
    'positive': [
        # Celebrations & Victories (20)
        'celebration news', 'victory parade', 'championship celebration', 'award ceremony',
        'graduation celebration', 'wedding party', 'festival crowd happy', 'new year fireworks',
        'birthday celebration', 'anniversary party', 'success celebration', 'trophy winner',
        'medal ceremony olympic', 'winning team cheering', 'sports victory celebration', 'gold medal athlete',
        'prize winner happy', 'accomplishment celebration', 'achievement recognition', 'honor ceremony',
        
        # Happy Events & Rescue (15)
        'baby announcement happy', 'family reunion joy', 'homecoming celebration', 'peace treaty signing',
        'rescue success happy', 'hero welcome ceremony', 'charity success celebration', 'volunteer appreciation',
        'community celebration', 'neighbors helping each other', 'successful mission', 'happy ending news',
        'friendship celebration', 'unity celebration', 'togetherness event',
        
        # Scientific & Medical Breakthroughs (15)
        'medical breakthrough celebration', 'scientific discovery announcement', 'technology innovation launch',
        'space mission success', 'vaccine celebration', 'cure announcement', 'research success',
        'innovation award', 'invention presentation', 'discovery celebration', 'breakthrough achievement',
        'medical advance', 'health success story', 'science achievement', 'research milestone',
        
        # Economic & Development Success (15)
        'economic growth celebration', 'job fair success', 'business growth', 'market success',
        'hospital opening ribbon cutting', 'school opening ceremony', 'infrastructure inauguration',
        'park opening celebration', 'building inauguration', 'development project launch',
        'construction completion', 'renovation unveiling', 'facility opening', 'expansion celebration',
        'grand opening ceremony',
        
        # Cultural & Social Positive (10)
        'cultural festival celebration', 'art exhibition opening', 'music concert crowd', 'sports event excitement',
        'parade celebration', 'carnival festive', 'dance performance', 'theater opening night',
        'book fair', 'food festival celebration'
    ],
    
    'negative': [
        # Natural Disasters (20)
        'earthquake destruction aftermath', 'flood damaged city', 'hurricane devastation', 'tornado destruction path',
        'wildfire burning forest', 'tsunami wave damage', 'landslide damaged houses', 'volcanic ash damage',
        'drought cracked earth', 'storm damaged buildings', 'cyclone destruction', 'avalanche debris',
        'mudslide damage', 'typhoon aftermath', 'blizzard damage', 'heatwave damage',
        'lightning strike damage', 'hailstorm damage', 'erosion damage', 'sinkhole damage',
        
        # Accidents & Disasters (20)
        'plane crash wreckage', 'train derailment', 'car accident damaged', 'building collapsed debris',
        'bridge collapse', 'explosion damage site', 'fire damage building', 'industrial accident',
        'mining disaster', 'ship wreck', 'boat capsized', 'construction accident site',
        'gas explosion damage', 'chemical spill', 'tanker accident', 'crane collapse',
        'scaffolding collapse', 'roof collapse', 'wall collapse', 'structural failure',
        
        # Conflicts & Crises (15)
        'war destruction', 'bombing rubble', 'protest clash', 'riot damage',
        'conflict zone destroyed', 'military conflict damage', 'battle aftermath', 'attack damage',
        'violence aftermath', 'crisis evacuation', 'refugee camp overcrowded', 'displaced people crisis',
        'emergency evacuation', 'conflict refugees', 'war refugees',
        
        # Social Issues & Suffering (15)
        'poverty slum', 'homeless people', 'unemployment line', 'strike protest angry',
        'hunger crisis malnourished', 'famine victims', 'epidemic hospital', 'pandemic emergency',
        'hospital overcrowded emergency', 'medical crisis', 'environmental pollution', 'toxic pollution',
        'oil spill damage', 'chemical pollution', 'air pollution smog',
        
        # Crime & Tragedy (5)
        'crime scene tape', 'arrest handcuffs', 'courtroom trial serious', 'prison bars', 'tragedy memorial'
    ],
    
    'neutral': [
        # Political & Government (20)
        'press conference podium', 'government official meeting', 'parliament chamber session', 'senate floor hearing',
        'political debate stage', 'diplomatic handshake meeting', 'summit conference table', 'boardroom conference',
        'cabinet meeting table', 'legislative session', 'town hall meeting audience', 'committee hearing room',
        'voting ballot box', 'election polling station', 'political campaign rally', 'official ceremony formal',
        'state visit formal', 'inauguration ceremony formal', 'oath taking ceremony', 'official portrait',
        
        # Business & Professional (20)
        'business meeting boardroom', 'corporate office desk', 'conference room presentation', 'stock exchange trading',
        'financial district skyscrapers', 'trading floor screens', 'business presentation screen', 'office cubicles',
        'seminar audience', 'workshop training session', 'professional handshake', 'business cards exchange',
        'laptop office work', 'desk workspace', 'meeting minutes', 'business documents',
        'office supplies', 'filing cabinets', 'reception desk office', 'corporate lobby',
        
        # Infrastructure & Architecture (15)
        'government building facade', 'office tower building', 'courthouse architecture', 'city hall building',
        'parliament building exterior', 'embassy building', 'corporate headquarters building', 'skyscraper architecture',
        'modern office building', 'business district aerial', 'downtown skyline', 'urban architecture',
        'commercial building', 'institutional building', 'administrative building',
        
        # Media & Broadcasting (10)
        'news studio desk', 'television broadcast studio', 'radio broadcasting studio', 'newsroom computers',
        'journalist microphone', 'press photographer', 'camera crew filming', 'broadcasting equipment',
        'editing suite', 'control room broadcasting',
        
        # Formal Events & Venues (10)
        'conference hall empty', 'symposium venue', 'panel discussion stage', 'lecture hall seats',
        'auditorium interior', 'convention center hall', 'exhibition hall', 'trade show booth',
        'seminar room setup', 'meeting venue'
    ]
}

def validate_image(image_path):
    """Check if image is valid and can be loaded"""
    try:
        img = Image.open(image_path)
        img.verify()  # Verify it's actually an image
        img = Image.open(image_path)  # Reopen after verify
        img.convert('RGB')  # Try converting to RGB
        width, height = img.size
        # Skip images that are too small
        if width < 50 or height < 50:
            return False
        return True
    except:
        return False

def clean_and_validate_images(temp_dir, target_dir, sentiment):
    """Move only valid images from temp to target directory"""
    valid_count = 0
    invalid_count = 0
    
    for image_path in Path(temp_dir).rglob('*'):
        if image_path.is_file() and image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
            if validate_image(image_path):
                # Move to target directory with unique name
                target_path = target_dir / f"{sentiment}_{valid_count}_{image_path.name}"
                try:
                    shutil.move(str(image_path), str(target_path))
                    valid_count += 1
                except:
                    invalid_count += 1
            else:
                invalid_count += 1
                # Delete invalid image
                try:
                    image_path.unlink()
                except:
                    pass
    
    return valid_count, invalid_count

def download_images():
    """Download images for all categories with validation"""
    total_queries = sum(len(queries) for queries in CATEGORIES.values())
    current_query = 0
    total_valid = 0
    total_invalid = 0
    
    print(f"\n🚀 Starting download of {total_queries} queries (20 images each)...")
    print(f"📊 Target: ~{total_queries * 20} images (after validation)\n")
    
    for sentiment, queries in CATEGORIES.items():
        print(f"\n{'='*70}")
        print(f"📥 Downloading {sentiment.upper()} images ({len(queries)} queries)")
        print(f"{'='*70}\n")
        
        sentiment_valid = 0
        
        for idx, query in enumerate(queries, 1):
            current_query += 1
            try:
                print(f"[{current_query}/{total_queries}] '{query}' → {sentiment}", end=' ')
                
                # Download to temp directory
                temp_dir = Path('image_dataset/temp')
                
                downloader.download(
                    query=query,
                    limit=20,  # Download 20 images per query
                    output_dir='image_dataset/temp',
                    adult_filter_off=True,
                    force_replace=False,
                    timeout=20,
                    verbose=False
                )
                
                # Validate and move images
                target_dir = Path(f'image_dataset/train/{sentiment}')
                valid, invalid = clean_and_validate_images(temp_dir, target_dir, sentiment)
                
                sentiment_valid += valid
                total_valid += valid
                total_invalid += invalid
                
                print(f"✅ {valid} valid, {invalid} skipped")
                
                # Clean temp directory
                shutil.rmtree(temp_dir, ignore_errors=True)
                Path('image_dataset/temp').mkdir(exist_ok=True)
                
            except Exception as e:
                print(f"⚠️  Error: {str(e)[:50]}")
                continue
        
        print(f"\n✅ {sentiment.upper()}: {sentiment_valid} valid images downloaded\n")
    
    # Final cleanup
    shutil.rmtree('image_dataset/temp', ignore_errors=True)
    
    print("\n" + "="*70)
    print(f"🎉 DOWNLOAD COMPLETE!")
    print(f"📊 Total valid images: {total_valid}")
    print(f"🗑️  Invalid images skipped: {total_invalid}")
    print("="*70)

def count_images():
    """Count downloaded images"""
    print("\n📊 Dataset Statistics:")
    print("-" * 50)
    
    for split in ['train', 'val']:
        for sentiment in ['positive', 'negative', 'neutral']:
            path = Path(f'image_dataset/{split}/{sentiment}')
            if path.exists():
                count = sum(1 for _ in path.rglob('*.jpg')) + \
                       sum(1 for _ in path.rglob('*.png')) + \
                       sum(1 for _ in path.rglob('*.jpeg')) + \
                       sum(1 for _ in path.rglob('*.gif'))
                print(f"  {split}/{sentiment}: {count} images")

def create_validation_split():
    """Move 20% of images to validation set"""
    import random
    
    print("\n📂 Creating validation split (20%)...")
    
    for sentiment in ['positive', 'negative', 'neutral']:
        train_path = Path(f'image_dataset/train/{sentiment}')
        val_path = Path(f'image_dataset/val/{sentiment}')
        
        # Get all image files
        all_images = []
        for ext in ['*.jpg', '*.png', '*.jpeg', '*.gif']:
            all_images.extend(list(train_path.glob(ext)))
        
        if len(all_images) == 0:
            print(f"  ⚠️  {sentiment}: No images found")
            continue
        
        # Move 20% to validation
        num_val = max(int(len(all_images) * 0.2), 1)
        val_images = random.sample(all_images, num_val)
        
        for img in val_images:
            try:
                shutil.move(str(img), str(val_path / img.name))
            except:
                pass
        
        print(f"  ✅ {sentiment}: {num_val} images moved to validation")
    
    print("✅ Validation split created!")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  ENHANCED NEWS IMAGE SENTIMENT DATASET DOWNLOADER")
    print("  - Auto-validates images")
    print("  - Skips corrupted files")
    print("  - 75+ queries per sentiment")
    print("="*70)
    
    # Step 1: Create directories
    create_directories()
    
    # Step 2: Download and validate images
    download_images()
    
    # Step 3: Count images
    count_images()
    
    # Step 4: Create validation split
    create_validation_split()
    
    # Step 5: Final count
    count_images()
    
    print("\n✅ Dataset ready for training!")
    print("📁 Location: image_dataset/")
    print("\n💡 Next steps:")
    print("  1. Check dataset balance across sentiments")
    print("  2. Run: python3.10 train_image_model.py")
