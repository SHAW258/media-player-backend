import datetime
import random
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.category import Category
from app.models.artist import Artist
from app.models.album import Album
from app.models.track import Track
from app.models.podcast import PodcastShow, PodcastEpisode
from app.models.playlist import Playlist, PlaylistTrack
from app.models.favorite import Favorite
from app.models.history import PlaybackHistory
from app.models.queue import UserQueue
from app.utils.security import get_password_hash
from app.config import settings

# Pool of available playable audio files
AUDIO_POOL = [
    "/static/audio/kesariya_lofi.mp3",
    "/static/audio/raataan_lambiyan.mp3",
    "/static/audio/tum_hi_ho_acoustic.mp3",
    "/static/audio/apna_bana_le.mp3",
    "/static/audio/punjabi_vibes.mp3",
    "/static/audio/hindi_podcast_ep1.mp3",
]

# Curated High-Quality Music Cover Images
COVER_POOL = [
    "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=600",
    "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=600",
    "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600",
    "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600",
    "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=600",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=600",
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=600",
    "https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=600",
    "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=600",
    "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=600",
    "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=600",
    "https://images.unsplash.com/photo-1520523839898-50712213d969?w=600",
]

# Raw Data for 105+ Diverse Songs
SONG_CATALOG_DATA = [
    # --- 1. Arijit Singh & Romantic Blockbusters ---
    ("Kesariya (Lo-Fi Romantic)", 1, 1, 1, 268, "Mujhko itna bataye koyi, kaise tujhse dil na lagaye koyi... Kesariya tera ishq hai piya...", True, True),
    ("Raataan Lambiyan", 1, 1, 1, 230, "Teri meri gallan ho gayi mashhoor, kar na kabhi tu mujhe nazron se door... Raataan lambiyan lambiyan re...", True, True),
    ("Tum Hi Ho (Acoustic Version)", 1, 2, 1, 285, "Hum tere bin ab reh nahi sakte, tere bina kya wajood mera... Kyunki tum hi ho, ab tum hi ho...", True, False),
    ("Apna Bana Le", 1, 1, 1, 245, "Tu mera koi na hoke bhi kuch laage... Kiya re jo bhi toone kaise kiya re... Apna bana le piya...", True, True),
    ("Channa Mereya", 1, 2, 1, 289, "Achha chalta hoon duaaon mein yaad rakhna... Mere zikr ka zubaan pe swaad rakhna...", True, False),
    ("Agar Tum Saath Ho", 1, 3, 1, 341, "Pal bhar thehar jaao dil ye sambhal jaaye... Kaise tumhe rokein ye dil...", True, False),
    ("Shayad (Love Aaj Kal)", 1, 1, 1, 247, "Shayad kabhi na keh sakoon main tumko... Jo tum na ho toh hum bhi hum nahi...", True, True),
    ("Hawayein (Lo-Fi Chill)", 1, 4, 2, 290, "Tujhko main kitni shiddat se chaahun... Le jaayein jaane kahaan hawayein...", True, False),
    ("Gerua", 1, 2, 1, 345, "Rang de tu mohe gerua... Dhoop nikli jahaan chaanv baanti jahaan...", False, False),
    ("Zaalima", 1, 1, 1, 299, "Jo teri khatir tadpe pehle se hi... Jo tu kare thoda sa pyaar...", False, False),
    ("Ae Dil Hai Mushkil", 1, 2, 1, 269, "Tu safar mera, hai tu hi meri manzil... Tere bina guzara ae dil hai mushkil...", True, False),
    ("Ghungroo (Party Mix)", 1, 5, 9, 302, "Ghungroo toot gaye jab se mile hum... Chaand taare gawaah hai...", True, True),
    ("Ilahi (Acoustic Wanderlust)", 1, 3, 2, 228, "Shaamein malang si, raatein surang si... Kal pe sawaal hai, jeena filhaal hai... Ilahi mera jee aaye...", True, False),
    ("Mast Magan", 1, 2, 1, 280, "Ishq ki dhooni roz jalaaye... Uthe dhuaan toh kaise chhupaaye...", False, False),
    ("Pal (Jalebi)", 1, 4, 2, 246, "Har lamha har ghadi har pal... Tujhko hi dhoondein meri nazar...", True, False),
    
    # --- 2. Shreya Ghoshal & Melodious Classics ---
    ("Sunn Raha Hai Na Tu (Female)", 2, 2, 1, 312, "Waqt bhi thehra hai, kaise kahoonga main... Sunn raha hai na tu, ro rahi hoon main...", True, False),
    ("Teri Ore (Acoustic Lo-Fi)", 2, 6, 2, 338, "Dil kho gaya, ho gaya kisi ka... Teri ore khincha chala jaata hoon...", True, True),
    ("Deewani Mastani", 2, 7, 1, 340, "Nazar jo teri laagi main deewani ho gayi... Mashhoor mere ishq ki kahani ho gayi...", False, False),
    ("Ghoomar", 2, 7, 9, 281, "Ghoomar ghoomar ghoomar ghoomar ghoome re... Mhaaro dil ghoome...", True, False),
    ("Tujh Mein Rab Dikhta Hai", 2, 6, 1, 295, "Tu hi toh jannat meri, tu hi mera junoon... Tujh mein rab dikhta hai yaara main kya karoon...", True, False),
    ("Samjhawan (Soulful Acoustic)", 2, 6, 2, 265, "Nahi jeena tere baaju, nahi jeena nahi jeena... Main tenu samjhawan ki...", True, True),
    ("Bahara (I Hate Luv Storys)", 2, 6, 1, 325, "Chali hawa mastani, ban gayi ek kahani... Bahara bahara hua dil pehli baar ve...", False, False),
    ("Radha (Student of the Year)", 2, 5, 9, 341, "Gopiyon sang ghoome Kanhaiya... O Radha teri chunri, O Radha tera chhalla...", False, False),
    ("Piyu Bole", 2, 6, 4, 260, "Piyu bole piya bole kya ye bole jaano na... Hawaayein jab chalein to gaayein...", False, False),
    ("Barso Re Megha (Rainy Rhythms)", 2, 7, 10, 315, "Barso re megha megha, barso re megha barso... Meethe meethe paani ke jharnon...", True, True),

    # --- 3. Diljit Dosanjh & Punjabi Power Beats ---
    ("G.O.A.T - Pure Punjabi Vibe", 3, 8, 3, 223, "Ho jithe hundi ae pabandi yaar othe khade ne... G.O.A.T Diljit Dosanjh...", True, True),
    ("Lover (Summer Pop Hit)", 3, 8, 3, 192, "Tera ni main lover, tera ni main lover... Chaare paase teri gallan...", True, True),
    ("Born to Shine", 3, 8, 3, 214, "Gaddiyan uchiyan rakhiyan, jatt ne shonk vakhre... Born to shine...", True, True),
    ("Lemonade (Late Night Drive)", 3, 8, 12, 185, "Aankhan vich nasha tera, gallan vich pyar... Sip sip lemonade...", False, True),
    ("Proper Patola", 3, 9, 3, 238, "Proper patola nakhra ae swaari... Lagdi tu saari di saari qatl-e-aam...", True, False),
    ("Do You Know", 3, 8, 2, 230, "Do you know kinna pyaar karda... Do you know kinna tenu chaaunda...", True, False),
    ("Clash (Desi Hip-Hop)", 3, 8, 3, 175, "Panga jehda lauga sidha chakk lange... Full clash mode...", False, True),
    ("Peaches", 3, 8, 3, 190, "Sweet like peaches, driving down the street... Teri smile lage kaint...", True, True),
    ("Naina (Crew Bollywood)", 3, 1, 1, 180, "Naina tere kajrare, naina tere matwaare... Dil luteya tere naina ne...", True, True),
    ("5 Taara (Bhangra Energy)", 3, 9, 9, 199, "5 Taara theke utte behke taareya main... Yaaran naal peg laa ke...", False, False),

    # --- 4. A.R. Rahman & Masterpiece Symphonies ---
    ("Kun Faya Kun (Sufi Soul)", 4, 10, 6, 473, "Jab kahin pe kuch nahi, wahi tha wahi tha... Kun Faya Kun...", True, False),
    ("Jai Ho (Global Anthem)", 4, 11, 5, 319, "Jai Ho, Jai Ho... Aaja aaja jind shamiyane ke tale...", False, False),
    ("Maa Tujhe Salaam (Vande Mataram)", 4, 11, 6, 370, "Yahan wahan saara jahaan dekh liya... Vande Mataram...", True, False),
    ("Khwaja Mere Khwaja", 4, 10, 6, 418, "Khwaja ji, khwaja ji... Ya Moinuddin, Ya Khwaja ji...", False, False),
    ("Tum Tak (Raanjhanaa)", 4, 10, 1, 304, "Meri har manzil tum tak, meri har dhoop tum tak...", True, True),
    ("Nadaan Parinde (Rockstar)", 4, 10, 1, 386, "Kaga re kaga re mori itni araj tose... Nadaan parinde ghar aaja...", True, False),
    ("Rehna Tu (Delhi-6 Lo-Fi)", 4, 10, 2, 395, "Rehna tu, hai jaisa tu... Thoda sa meetha thoda sa khata...", False, False),
    ("Patakha Guddi (Highway)", 4, 10, 3, 284, "Mithe ber wargi ae, jugni ud jaavegi... Ali maula ali maula...", True, False),
    ("Tere Bina (Guru)", 4, 10, 1, 310, "Tere bina beswadi beswadi ratiyaan... Oh saajna re...", False, False),
    ("Chaiyya Chaiyya (Evergreen)", 4, 11, 9, 399, "Jinke sar ho ishq ki chhaanv... Chal chaiyya chaiyya chaiyya...", True, False),

    # --- 5. Atif Aslam & Soulful Nostalgia ---
    ("Jeena Jeena (Badlapur)", 5, 12, 1, 229, "Dehleez pe mere dil ki jo rakhe hain tune kadam... Tere sang laagi aisi lagan...", True, True),
    ("Tera Hone Laga Hoon", 5, 12, 1, 300, "Shining in the setting sun like a pearl upon the ocean... Tera hone laga hoon...", True, False),
    ("Pehli Nazar Mein", 5, 12, 1, 314, "Pehli nazar mein kaisa jaadu kar diya... Tera ban baitha hai mera jiya...", True, False),
    ("Tu Jaane Na (Lo-Fi Rework)", 5, 12, 2, 337, "Kaise bataayein kyun tujhko chaahein... Tu jaane na, tu jaane na...", True, True),
    ("Tajdar-e-Haram", 5, 10, 6, 615, "Qismat mein meri chain se jeena likh de... Tajdar-e-haram ho nigaah-e-karam...", True, False),
    ("Woh Lamhe Woh Baatein", 5, 12, 5, 318, "Woh lamhe, woh baatein, koi na jaane... Thi kaisi raatein...", False, False),
    ("Aadat (Deep Rock Anthem)", 5, 12, 11, 273, "Juda hoke bhi tu mujh mein kahin baaki hai... Ab toh aadat si hai...", True, False),
    ("Dil Diyan Gallan", 5, 1, 1, 260, "Kacchi doriyon doriyon doriyon se... Dil diyan gallan karange roz roz...", True, True),
    ("O Saathi (Baaghi 2)", 5, 12, 1, 251, "Allah mujhe dard ke kaabil bana diya... O saathi tere bina...", False, False),
    ("Main Rang Sharbaton Ka", 5, 12, 1, 263, "Main rang sharbaton ka, tu meethe ghaat ka paani...", False, False),

    # --- 6. KK & 2000s Bollywood Nostalgia ---
    ("Zara Sa (Jannat)", 6, 13, 5, 303, "Zara sa jhoom loon main, zara sa ghoom loon main... Zara sa dil mein de jagah tu...", True, True),
    ("Kya Mujhe Pyar Hai", 6, 13, 5, 278, "Kya mujhe pyar hai ya kaisa khumaar hai ya... O jaana...", True, False),
    ("Labon Ko (Bhool Bhulaiyaa)", 6, 13, 2, 342, "Labon ko labon pe sajaao, kya ho tum mujhe ab bataao...", False, False),
    ("Tu Hi Meri Shab Hai", 6, 13, 1, 388, "Tu hi meri shab hai subah hai tu hi din hai mera... Tu hi mera rab hai...", True, False),
    ("Alvida (Life in a Metro)", 6, 13, 11, 340, "Chupke se kahin dheeme paanv se... Alvida yaara alvida...", False, False),
    ("Dil Ibaadat", 6, 13, 1, 325, "Dil ibaadat kar raha hai dhadkanein meri sun... Mujhko de tu bas ek pal...", True, True),
    ("Beete Lamhein", 6, 13, 2, 328, "Dard mein bhi ye lab muskura jaate hain... Beete lamhein...", False, False),
    ("Yaaron Dosti", 6, 13, 5, 290, "Yaaron dosti badi hi haseen hai... Yeh na ho to kya phir...", True, False),
    ("Pal (Hum Rahein Ya Na Rahein)", 6, 13, 2, 350, "Hum rahein ya na rahein kal... Kal yaad aayenge ye pal...", True, False),
    ("Tadap Tadap Ke", 6, 13, 1, 395, "Lut gaye haan lut gaye hum teri mohabbat mein... Tadap tadap ke is dil se...", False, False),

    # --- 7. Prateek Kuhad & Anuv Jain (Indie Acoustic) ---
    ("cold/mess (Acoustic Original)", 7, 14, 7, 283, "When I feel cold, I'll keep you warm... Caught in your mess...", True, True),
    ("Kasoor", 7, 14, 7, 203, "Kyun hai tu itni khoobsurat... Kya ye mera kasoor hai...", True, True),
    ("Baarishein - Anuv Jain", 8, 14, 7, 217, "Hawaayein aisi chali hain ki baarishein le aayi... Teri kami mehsoos hoti hai...", True, True),
    ("Alag Aasmaan - Anuv Jain", 8, 14, 7, 232, "Naye naye raste, naye naye log... Ek hi aasmaan ke neeche...", True, True),
    ("Gul - Anuv Jain", 8, 14, 7, 218, "Dekho kaise phool khile hain bagiyaan mein... Gul ban ke tu khil jaana...", True, True),
    ("Mishri - Anuv Jain", 8, 14, 7, 211, "Mishri si meethi baatein teri... Shaam dhale jab aate ho...", False, True),
    ("Kho Gaye Hum Kahan - Jasleen Royal", 9, 14, 2, 214, "Kho gaye hum kahan, rangon sa ye jahaan... Tedhe medhe raaste...", True, False),
    ("Din Shagna Da - Wedding Acoustic", 9, 14, 1, 215, "Din shagna da chadheya... Aao sakhiyon ni vekhein...", True, False),
    ("Co2 - Prateek Kuhad", 7, 14, 7, 172, "Hold me close and never let me go... Breathing in your love...", False, True),
    ("pause - Prateek Kuhad", 7, 14, 7, 195, "Can we just pause this moment right here... Let the world spin...", False, False),

    # --- 8. AP Dhillon & Sidhu Moose Wala & Desi Hip-Hop ---
    ("Excuses (Kehndi Hundi Si)", 10, 15, 3, 176, "Kehndi hundi si chan tak raah bana de... Taare ne pasand mainu...", True, True),
    ("Brown Munde", 10, 15, 3, 267, "Desi munde town vich ghumde... Brown munde...", True, True),
    ("Insane - AP Dhillon", 10, 15, 3, 203, "Aankhan vich nasha, moves insane... AP Dhillon on the track...", True, True),
    ("With You - AP Dhillon", 10, 15, 2, 154, "Tere naal jeena, tere naal marna... Always with you...", True, True),
    ("295 - Sidhu Moose Wala", 11, 16, 3, 270, "Dass keda karda sach di gallan... 295...", True, False),
    ("The Last Ride - Sidhu Moose Wala", 11, 16, 3, 261, "Aakhri ride utte nikleya jatt... Legend never dies...", True, False),
    ("So High - Sidhu Moose Wala", 11, 16, 3, 237, "Sir utte crown, shonk high-end... So High...", False, False),
    ("Same Beef - Bohemia & Sidhu", 11, 16, 3, 278, "Ohi same yaar, ohi same beef...", True, False),
    ("Mercy - Badshah", 12, 17, 9, 162, "Have some mercy on me... Jaane jigar dekh idhar...", False, True),
    ("Kala Chashma - Party Banger", 12, 17, 9, 187, "Tenu kala chashma jachda ae, jachda ae gore mukhde pe...", True, False),

    # --- 9. Kishore Kumar & 90s Golden Era ---
    ("Pal Pal Dil Ke Paas", 13, 18, 5, 329, "Pal pal dil ke paas tum rehti ho... Jeevan meethi pyaas ye kehti ho...", True, False),
    ("O Mere Dil Ke Chain", 13, 18, 5, 276, "O mere dil ke chain, chain aaye mere dil ko dua kijiye...", True, False),
    ("Roop Tera Mastana", 13, 18, 5, 225, "Roop tera mastana pyaar mera deewana... Bhool koi humse na ho jaaye...", False, False),
    ("Yeh Shaam Mastani", 13, 18, 5, 277, "Yeh shaam mastani madhosh kiye jaaye... Mujhe dor koi khinche...", True, False),
    ("Kora Kagaz Tha Yeh Man Mera", 13, 18, 5, 338, "Kora kagaz tha yeh man mera, likh liya naam ispe tera...", False, False),
    ("Tujhe Dekha Toh Yeh Jaana Sanam", 14, 18, 5, 302, "Tujhe dekha toh yeh jaana sanam... Pyaar hota hai deewana sanam...", True, False),
    ("Tip Tip Barsa Paani", 14, 18, 10, 355, "Tip tip barsa paani, paani ne aag lagaayi...", False, False),
    ("Chura Ke Dil Mera", 14, 18, 5, 470, "Chura ke dil mera goriya chali... Udake nindiyaan kahan tu chali...", True, False),
    ("Kuch Kuch Hota Hai", 14, 18, 5, 296, "Tum paas aaye, yoon muskuraaye... Tumne na jaane kya sapne dikhaaye...", True, False),
    ("Dilwale Dulhania Le Jayenge Theme", 14, 18, 5, 240, "Ho gaya hai tujhko toh pyaar sajna... Laakh kar le tu inkaar sajna...", False, False),

    # --- 10. Ghazals & Indian Classical (Jagjit Singh & Ustad) ---
    ("Hoshwalon Ko Khabar Kya", 15, 19, 8, 303, "Hoshwalon ko khabar kya bekhudi kya cheez hai... Ishq kijiye phir samajhiye...", True, False),
    ("Tum Itna Jo Muskura Rahe Ho", 15, 19, 8, 318, "Tum itna jo muskura rahe ho, kya gham hai jisko chhupa rahe ho...", True, False),
    ("Jhuki Jhuki Si Nazar", 15, 19, 8, 302, "Jhuki jhuki si nazar beqaraar hai ki nahi... Daba daba sa sahi dil mein pyaar...", False, False),
    ("Chithi Na Koi Sandesh", 15, 19, 8, 395, "Chithi na koi sandesh, jaane woh kaun sa desh jahaan tum chale gaye...", True, False),
    ("Wo Kagaz Ki Kashti", 15, 19, 8, 239, "Yeh daulat bhi le lo, yeh shohrat bhi le lo... Wo kagaz ki kashti, wo baarish ka paani...", True, False),
    ("Raga Bhairav - Sitar Morning", 16, 20, 4, 450, "Traditional Hindustani Classical Morning Raga played on authentic sitar and tabla.", False, True),
    ("Raga Darbari - Midnight Calm", 16, 20, 4, 520, "Deep meditative nocturnal Indian classical melody.", False, False),
    ("Flute Symphony (Bansuri Peace)", 16, 20, 4, 380, "Pure bamboo flute vibrations for peace, focus, and meditation.", True, True),
    ("Tabla Beats & Tarana", 16, 20, 4, 310, "Fast-paced classical Indian rhythmic tabla solo and fusion composition.", False, False),
    ("Saraswati Vandana - Veena Classical", 16, 20, 4, 410, "Serene divine acoustic veena instrumental for wisdom and meditation.", False, False),

    # --- 11. Global Pop & EDM Hits ---
    ("Starboy - Synth Pop", 17, 21, 5, 230, "I'm tryna put you in the worst mood, ah... Look what you've done...", True, True),
    ("Blinding Lights (Retro 80s)", 17, 21, 5, 200, "I've been on my own for long enough... I'm blinded by the lights...", True, True),
    ("Levitating - Nu-Disco Pop", 18, 22, 5, 203, "If you wanna run away with me, I know a galaxy... I got you, moonlight...", True, True),
    ("Shape of You - Acoustic Dance", 19, 23, 5, 233, "The club isn't the best place to find a lover so the bar is where I go...", True, False),
    ("Faded - Alan Walker EDM", 20, 24, 5, 212, "You were the shadow to my light... Where are you now? Faded...", True, False),
]

def reset_and_seed_database(db: Session):
    """
    Completely clears all dummy tracks and seeds a massive collection of 105+ diverse,
    authentic music tracks (Bollywood, Hindi Lo-Fi, Punjabi, Classical, Ghazals, Podcasts, Pop).
    """
    print("[1/6] Cleaning up old database records...")
    try:
        db.query(PlaybackHistory).delete()
        db.query(UserQueue).delete()
        db.query(Favorite).delete()
        db.query(PlaylistTrack).delete()
        db.query(Playlist).delete()
        db.query(PodcastEpisode).delete()
        db.query(PodcastShow).delete()
        db.query(Track).delete()
        db.query(Album).delete()
        db.query(Artist).delete()
        db.query(Category).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[Warning] Catalog cleanup notice: {e}")

    # 1. Seed Default Users
    john_doe = db.query(User).filter(User.username == "john_doe").first()
    if not john_doe:
        john_doe = User(
            username="john_doe",
            email="john.doe@example.com",
            password_hash=get_password_hash("password123"),
            full_name="John Doe",
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300",
            role="user",
            is_active=True
        )
        db.add(john_doe)

    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@mediaplayer.io",
            password_hash=get_password_hash("admin123"),
            full_name="Administrator",
            avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300",
            role="admin",
            is_active=True
        )
        db.add(admin_user)
    db.commit()
    john_doe = db.query(User).filter(User.username == "john_doe").first()

    print("[2/6] Seeding diverse categories...")
    categories = [
        Category(id=1, name="Bollywood & Hindi Hits", slug="bollywood", category_type="music", icon="🎵"),
        Category(id=2, name="Hindi Lo-Fi & Acoustic", slug="hindi-lofi", category_type="music", icon="☕"),
        Category(id=3, name="Punjabi & Desi Beats", slug="punjabi", category_type="music", icon="🔥"),
        Category(id=4, name="Indian Classical & Sitar", slug="classical", category_type="music", icon="🪕"),
        Category(id=5, name="Romantic 90s & 2000s", slug="nostalgia-90s", category_type="music", icon="📻"),
        Category(id=6, name="Sufi & Devotional Soul", slug="sufi", category_type="music", icon="🕊️"),
        Category(id=7, name="Indian Indie & Folk", slug="indie", category_type="music", icon="🎸"),
        Category(id=8, name="Ghazals & Late Night", slug="ghazals", category_type="music", icon="🌙"),
        Category(id=9, name="High Energy Party & Dance", slug="party", category_type="music", icon="🎉"),
        Category(id=10, name="Monsoon & Rainy Moods", slug="rainy", category_type="music", icon="🌧️"),
        Category(id=11, name="Workout & Motivation", slug="workout", category_type="music", icon="⚡"),
        Category(id=12, name="Late Night Drives", slug="drive", category_type="music", icon="🚗"),
        Category(id=13, name="Global Pop & EDM", slug="pop-edm", category_type="music", icon="🎧"),
        Category(id=14, name="Hindi Podcasts & Stories", slug="hindi-podcasts", category_type="podcast", icon="🎙️"),
        Category(id=15, name="Tech & Deep Science", slug="tech-podcasts", category_type="podcast", icon="💡"),
    ]
    db.add_all(categories)
    db.commit()

    print("[3/6] Seeding 20+ top artists...")
    artists = [
        Artist(id=1, name="Arijit Singh", bio="India's leading playback singer and melody king.", avatar_url="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500", monthly_listeners=85200000, is_verified=True, is_popular=True, category_id=1),
        Artist(id=2, name="Shreya Ghoshal", bio="Legendary national award-winning playback vocalist.", avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500", monthly_listeners=44600000, is_verified=True, is_popular=True, category_id=1),
        Artist(id=3, name="Diljit Dosanjh", bio="Global Punjabi sensation, actor and live performer.", avatar_url="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=500", monthly_listeners=28400000, is_verified=True, is_popular=True, category_id=3),
        Artist(id=4, name="A.R. Rahman", bio="Oscar and Grammy winning Indian musical genius.", avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500", monthly_listeners=36000000, is_verified=True, is_popular=True, category_id=1),
        Artist(id=5, name="Atif Aslam", bio="Soulful rock-pop playback icon with timeless hits.", avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500", monthly_listeners=32000000, is_verified=True, is_popular=True, category_id=1),
        Artist(id=6, name="KK (Krishnakumar Kunnath)", bio="The voice of a generation and unforgettable 2000s anthems.", avatar_url="https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=500", monthly_listeners=24500000, is_verified=True, is_popular=True, category_id=5),
        Artist(id=7, name="Prateek Kuhad", bio="Acclaimed acoustic singer-songwriter.", avatar_url="https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=500", monthly_listeners=12800000, is_verified=True, is_popular=True, category_id=7),
        Artist(id=8, name="Anuv Jain", bio="Indian Indie sensation with poetic acoustic melodies.", avatar_url="https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=500", monthly_listeners=15400000, is_verified=True, is_popular=True, category_id=7),
        Artist(id=9, name="Jasleen Royal", bio="Composer, multi-instrumentalist and vocalist.", avatar_url="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500", monthly_listeners=18900000, is_verified=True, is_popular=True, category_id=7),
        Artist(id=10, name="AP Dhillon", bio="Indo-Canadian Punjabi trap and hip-hop pioneer.", avatar_url="https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=500", monthly_listeners=26100000, is_verified=True, is_popular=True, category_id=3),
        Artist(id=11, name="Sidhu Moose Wala", bio="Legendary Punjabi hip-hop icon and cultural pioneer.", avatar_url="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=500", monthly_listeners=31000000, is_verified=True, is_popular=True, category_id=3),
        Artist(id=12, name="Badshah", bio="India's #1 party hip-hop producer and rapper.", avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500", monthly_listeners=22000000, is_verified=True, is_popular=True, category_id=9),
        Artist(id=13, name="Kishore Kumar", bio="The evergreen legend of Indian cinema vocals.", avatar_url="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500", monthly_listeners=19800000, is_verified=True, is_popular=True, category_id=5),
        Artist(id=14, name="Lata Mangeshkar & Udit Narayan", bio="The timeless golden duet voices of Bollywood.", avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500", monthly_listeners=21000000, is_verified=True, is_popular=True, category_id=5),
        Artist(id=15, name="Jagjit Singh", bio="The King of Ghazals and timeless poetry.", avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500", monthly_listeners=14300000, is_verified=True, is_popular=True, category_id=8),
        Artist(id=16, name="Pandit Ravi Shankar & Ustad", bio="Maestros of authentic Hindustani classical sitar & flute.", avatar_url="https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=500", monthly_listeners=8500000, is_verified=True, is_popular=True, category_id=4),
        Artist(id=17, name="The Weeknd", bio="Global R&B and synth-pop superstar.", avatar_url="https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=500", monthly_listeners=105000000, is_verified=True, is_popular=True, category_id=13),
        Artist(id=18, name="Dua Lipa", bio="Global dance-pop sensation.", avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=500", monthly_listeners=78000000, is_verified=True, is_popular=True, category_id=13),
        Artist(id=19, name="Ed Sheeran", bio="Global acoustic pop and chart-topping songwriter.", avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500", monthly_listeners=82000000, is_verified=True, is_popular=True, category_id=13),
        Artist(id=20, name="Alan Walker", bio="Norwegian EDM producer and melodic electronic artist.", avatar_url="https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=500", monthly_listeners=45000000, is_verified=True, is_popular=True, category_id=13),
    ]
    db.add_all(artists)
    db.commit()

    print("[4/6] Seeding 25+ iconic albums...")
    albums = [
        Album(id=1, title="Kesariya & Modern Bollywood Romantics", artist_id=1, cover_url=COVER_POOL[0], release_date=datetime.date(2026, 8, 1), album_type="album", is_new_release=True),
        Album(id=2, title="Aashiqui 2 - Definitive Edition", artist_id=1, cover_url=COVER_POOL[1], release_date=datetime.date(2025, 4, 15), album_type="album", is_new_release=False),
        Album(id=3, title="Yeh Jawaani Hai Deewani OST", artist_id=1, cover_url=COVER_POOL[2], release_date=datetime.date(2025, 6, 20), album_type="album", is_new_release=False),
        Album(id=4, title="Midnight Hindi Lo-Fi Sessions", artist_id=1, cover_url=COVER_POOL[3], release_date=datetime.date(2026, 8, 10), album_type="album", is_new_release=True),
        Album(id=5, title="Bollywood Dance & Party Hits", artist_id=1, cover_url=COVER_POOL[4], release_date=datetime.date(2026, 7, 20), album_type="compilation", is_new_release=True),
        Album(id=6, title="Shreya Ghoshal Romantic Classics", artist_id=2, cover_url=COVER_POOL[5], release_date=datetime.date(2025, 9, 1), album_type="album", is_new_release=False),
        Album(id=7, title="Sufi & Grand Bollywood Epics", artist_id=2, cover_url=COVER_POOL[6], release_date=datetime.date(2026, 1, 10), album_type="album", is_new_release=False),
        Album(id=8, title="G.O.A.T & Punjabi World Tour", artist_id=3, cover_url=COVER_POOL[7], release_date=datetime.date(2026, 7, 15), album_type="album", is_new_release=True),
        Album(id=9, title="Desi Party Bangers 2026", artist_id=3, cover_url=COVER_POOL[8], release_date=datetime.date(2026, 6, 1), album_type="album", is_new_release=True),
        Album(id=10, title="Rockstar & Sufi Masterpieces", artist_id=4, cover_url=COVER_POOL[9], release_date=datetime.date(2025, 11, 20), album_type="album", is_new_release=False),
        Album(id=11, title="A.R. Rahman Global Anthems", artist_id=4, cover_url=COVER_POOL[10], release_date=datetime.date(2026, 8, 15), album_type="compilation", is_new_release=True),
        Album(id=12, title="Atif Aslam Unplugged Romance", artist_id=5, cover_url=COVER_POOL[11], release_date=datetime.date(2026, 5, 10), album_type="album", is_new_release=False),
        Album(id=13, title="KK - Evergreen 2000s Memories", artist_id=6, cover_url=COVER_POOL[0], release_date=datetime.date(2025, 5, 31), album_type="compilation", is_new_release=False),
        Album(id=14, title="Indie Acoustic & Heartfelt Stories", artist_id=7, cover_url=COVER_POOL[1], release_date=datetime.date(2026, 7, 28), album_type="album", is_new_release=True),
        Album(id=15, title="Two Hearts - AP Dhillon", artist_id=10, cover_url=COVER_POOL[2], release_date=datetime.date(2026, 8, 5), album_type="album", is_new_release=True),
        Album(id=16, title="Moosetape Definitive", artist_id=11, cover_url=COVER_POOL[3], release_date=datetime.date(2025, 5, 29), album_type="album", is_new_release=False),
        Album(id=17, title="Badshah Club Explosions", artist_id=12, cover_url=COVER_POOL[4], release_date=datetime.date(2026, 6, 15), album_type="album", is_new_release=True),
        Album(id=18, title="Golden Bollywood 70s & 90s", artist_id=13, cover_url=COVER_POOL[5], release_date=datetime.date(2025, 1, 1), album_type="compilation", is_new_release=False),
        Album(id=19, title="Jagjit Singh Ghazal Serenade", artist_id=15, cover_url=COVER_POOL[6], release_date=datetime.date(2025, 3, 10), album_type="album", is_new_release=False),
        Album(id=20, title="Ragas for the Soul (Classical Sitar)", artist_id=16, cover_url=COVER_POOL[7], release_date=datetime.date(2026, 4, 20), album_type="album", is_new_release=False),
        Album(id=21, title="After Hours & Starboy", artist_id=17, cover_url=COVER_POOL[8], release_date=datetime.date(2026, 2, 10), album_type="album", is_new_release=False),
        Album(id=22, title="Future Nostalgia", artist_id=18, cover_url=COVER_POOL[9], release_date=datetime.date(2026, 1, 15), album_type="album", is_new_release=False),
        Album(id=23, title="Divide & Equals Pop", artist_id=19, cover_url=COVER_POOL[10], release_date=datetime.date(2025, 8, 10), album_type="album", is_new_release=False),
        Album(id=24, title="Different World (EDM)", artist_id=20, cover_url=COVER_POOL[11], release_date=datetime.date(2026, 3, 22), album_type="album", is_new_release=False),
    ]
    db.add_all(albums)
    db.commit()

    print(f"[5/6] Seeding {len(SONG_CATALOG_DATA)} diverse, playable tracks...")
    tracks_to_insert = []
    for idx, item in enumerate(SONG_CATALOG_DATA, start=1):
        title, artist_id, album_id, category_id, duration, lyrics, is_trending, is_new = item
        # Pick audio file cyclically from audio pool
        audio_file = AUDIO_POOL[(idx - 1) % len(AUDIO_POOL)]
        cover_image = COVER_POOL[(idx - 1) % len(COVER_POOL)]
        stream_base = random.randint(1500000, 48000000)

        track_obj = Track(
            id=idx,
            title=title,
            artist_id=artist_id,
            album_id=album_id,
            category_id=category_id,
            duration_seconds=duration,
            audio_url=audio_file,
            cover_url=cover_image,
            lyrics=lyrics,
            stream_count=stream_base,
            is_trending=is_trending,
            is_new_release=is_new,
            media_type="music"
        )
        tracks_to_insert.append(track_obj)

    db.add_all(tracks_to_insert)
    db.commit()

    print("[6/6] Seeding Podcast shows and user playlists...")
    podcast_shows = [
        PodcastShow(
            id=1,
            title="The Ranveer Show (TRS Hindi)",
            host_name="Ranveer Allahbadia",
            description="India's leading Hindi podcast on life, music, spiritual power, deep tech, and history.",
            cover_url="https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=600",
            category_id=14,
            rating=4.9
        ),
        PodcastShow(
            id=2,
            title="Tech, AI & Universe Talks (Hindi)",
            host_name="Gaurav Thakur",
            description="Deep dive into artificial intelligence, space mysteries, and the future of audio tech.",
            cover_url="https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=600",
            category_id=15,
            rating=4.8
        )
    ]
    db.add_all(podcast_shows)
    db.commit()

    podcast_episodes = [
        PodcastEpisode(
            id=1,
            show_id=1,
            title="How Indian Music & AI are Changing the World",
            description="Inside the revolutionary shift of Bollywood music production, acoustics, and AI vocal generation.",
            duration_seconds=420,
            audio_url="/static/audio/hindi_podcast_ep1.mp3",
            published_at=datetime.datetime(2026, 8, 20, 10, 0, 0, tzinfo=datetime.timezone.utc),
            episode_number=101
        ),
        PodcastEpisode(
            id=2,
            show_id=1,
            title="Secrets of Indian Classical Ragas & Healing Frequencies",
            description="How Indian Ragas affect emotions and stimulate creativity.",
            duration_seconds=360,
            audio_url="/static/audio/kesariya_lofi.mp3",
            published_at=datetime.datetime(2026, 8, 22, 10, 0, 0, tzinfo=datetime.timezone.utc),
            episode_number=102
        ),
        PodcastEpisode(
            id=3,
            show_id=2,
            title="Artificial General Intelligence & The Future of Entertainment",
            description="What happens when AI composers write chart-topping songs?",
            duration_seconds=480,
            audio_url="/static/audio/hindi_podcast_ep1.mp3",
            published_at=datetime.datetime(2026, 8, 21, 14, 0, 0, tzinfo=datetime.timezone.utc),
            episode_number=1
        )
    ]
    db.add_all(podcast_episodes)
    db.commit()

    # Seed User Playlists
    if john_doe:
        p1 = Playlist(id=1, user_id=john_doe.id, name="Best of Arijit Singh & Romantic Hindi", description="Soulful tracks and Lo-Fi favorites.", cover_url=COVER_POOL[0], is_public=True)
        p2 = Playlist(id=2, user_id=john_doe.id, name="High Energy Punjabi & Workout", description="G.O.A.T, AP Dhillon, and Sidhu Moose Wala.", cover_url=COVER_POOL[7], is_public=True)
        p3 = Playlist(id=3, user_id=john_doe.id, name="Late Night Lo-Fi & Indie Coffee", description="Prateek Kuhad, Anuv Jain, and acoustic chill.", cover_url=COVER_POOL[3], is_public=True)
        db.add_all([p1, p2, p3])
        db.commit()

        # Add tracks to playlist 1
        for rank, track_id in enumerate(range(1, 11), start=1):
            db.add(PlaylistTrack(playlist_id=1, track_id=track_id, position=rank))

        # Add Favorites
        for fid in [1, 2, 3, 4, 5, 26, 27, 41, 51, 61]:
            db.add(Favorite(user_id=john_doe.id, track_id=fid))
        for aid in [1, 2, 3, 8, 10]:
            db.add(Favorite(user_id=john_doe.id, album_id=aid))

        # Add Queue
        for q_pos, q_tid in enumerate([1, 2, 4, 26, 27], start=1):
            db.add(UserQueue(user_id=john_doe.id, track_id=q_tid, position=q_pos))

        # Add History
        db.add(PlaybackHistory(user_id=john_doe.id, track_id=1, progress_seconds=185, completed=False))
        db.add(PlaybackHistory(user_id=john_doe.id, track_id=2, progress_seconds=230, completed=True))
        db.commit()

    print(">> Database seeding complete!")
    return {
        "status": "success",
        "message": f"Successfully loaded {len(tracks_to_insert)} diverse music tracks!",
        "total_tracks": len(tracks_to_insert),
        "total_artists": len(artists),
        "total_albums": len(albums),
        "total_categories": len(categories),
        "total_podcast_episodes": len(podcast_episodes)
    }

def seed_database(db: Session):
    """Initial check during app startup."""
    if db.query(Track).count() >= 50:
        return {"status": "already_seeded", "message": "Database already contains seed data"}
    return reset_and_seed_database(db)
