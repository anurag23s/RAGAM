from flask import render_template, request, redirect, url_for, flash,session, send_file 
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from models import db, User, Song, Playlist, PlaylistSong, Rating, Album
from app import app 
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime 
from matplotlib.dates import date2num

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        
        return render_template('register.html')

    elif request.method == 'POST':
        
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']

        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        
        hashed_password = generate_password_hash(password)

        
        new_user = User(username=username, name=name, password=hashed_password, role=role)

        
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('user_login'))

@app.route('/userlogin', methods=['GET', 'POST'])
def user_login():
    if request.method == 'GET':
        
        return render_template('userlogin.html')

    elif request.method == 'POST':
        # Handle user login form submission
        username = request.form['username']
        password = request.form['password']

        
        user = User.query.filter_by(username=username).first()

        if user:
            
            if check_password_hash(user.password, password):
                if user.role in ['user', 'creator']:
                    
                    session['user_id'] = user.id
                    session['username'] = user.username
                    session['name'] = user.name
                    session['is_creator'] = user.is_creator
                    session['blacklist'] = user.blacklist

                    flash('User Login Successful', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid role for user login.', 'error')
            else:
                flash('Invalid password.', 'error')
        else:
            flash('Invalid username.', 'error')

        return redirect(url_for('user_login'))

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('profile.html', user=user)
    else:
        flash('Please log in to view your profile.', 'error')
        return redirect(url_for('user_login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        
        if request.method == 'GET':
            return render_template('edit_profile.html', user=user)
        elif request.method == 'POST':
            new_name = request.form['new_name']
            user.name = new_name
            db.session.commit()
            flash('Name updated successfully!', 'success')
            return redirect(url_for('profile'))
    else:
        flash('Please log in to edit your profile.', 'error')
        return redirect(url_for('user_login'))

@app.route('/adminlogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
      
        return render_template('adminlogin.html')

    elif request.method == 'POST':
        # Handle admin login form submission
        username = request.form['username']
        password = request.form['password']

        
        user = User.query.filter_by(username=username).first()

        if user:
            
            if check_password_hash(user.password, password):
                if user.role == 'admin':
                    
                    session['admin_id'] = user.id
                    session['admin_username'] = user.username

                    flash('Admin Login Successful', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Invalid role for admin login.', 'error')
            else:
                flash('Invalid password.', 'error')
        else:
            flash('Invalid username.', 'error')

        return redirect(url_for('admin_login'))

@app.route('/logout', methods=['POST'])
def logout():
    
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        
        songs = Song.query.all()
        user_playlists = Playlist.query.filter_by(user_id=session['user_id']).all()
        albums = Album.query.all()
        rock_songs = Song.query.filter_by(genre='rock').all()  # Add this line
        jazz_songs = Song.query.filter_by(genre='jazz').all()  # Add this line
        electronic_songs = Song.query.filter_by(genre='electronic').all()  # Add this line
        pop_songs = Song.query.filter_by(genre='pop').all()  # Add this line


        return render_template('dashboard.html', songs=songs, user_playlists=user_playlists, albums=albums, rock_songs=rock_songs, jazz_songs=jazz_songs, electronic_songs=electronic_songs, pop_songs=pop_songs)
    else:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('user_login'))

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp3'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploadsong', methods=['GET', 'POST'])
def uploadsong():
    
    if 'user_id' not in session:
        flash('You must be logged in to upload a song.', 'error')
        return redirect(url_for('user_login'))

    
    if request.method == 'GET':
        
        return render_template('uploadsong.html')
    elif request.method == 'POST':
        if 'user_id' not in session :
            flash('You must be logged in to upload a song.', 'error')
            return redirect(url_for('user_login'))

        
        title = request.form['title']
        lyrics = request.form['lyrics']
        duration = request.form['duration']
        genre = request.form['genre']
        song_file = request.files['song_file']

        
        if song_file and '.' in song_file.filename and song_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            
            user_id = session['user_id']
            user_name = User.query.get(user_id).name

            
            user_folder = os.path.join(app.config['UPLOAD_FOLDER'])
            os.makedirs(user_folder, exist_ok=True)

            
            filename = secure_filename(song_file.filename)
            song_path = os.path.join(user_folder, filename)
            song_file.save(song_path)

            
            new_song = Song(title=title, lyrics=lyrics, duration=duration, artist=user_name, file_path=song_path, genre=genre)
            db.session.add(new_song)
            db.session.commit()

            
            user = User.query.get(user_id)
            user.is_creator = True
            db.session.commit()

            flash('Song uploaded successfully! You are now a creator.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid file format. Please upload a valid MP3 file.', 'error')
            return redirect(url_for('uploadsong'))


@app.route('/play_song/<int:song_id>')
def play_song(song_id):
    
    song = Song.query.get(song_id)

    max_song_id = db.session.query(db.func.max(Song.id)).scalar()

    
    if song:
        return send_file(song.file_path, as_attachment=False)
    else:
        flash('Song not found.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/read_lyrics/<int:song_id>')
def read_lyrics(song_id):
    
    song = Song.query.get(song_id)

    
    max_song_id = db.session.query(db.func.max(Song.id)).scalar()

   
    if song:
        return render_template('lyrics.html', lyrics=song.lyrics, song=song, path=song.file_path, max_song_id=max_song_id)
    else:
        flash('Song not found.', 'error')
        return redirect(url_for('dashboard'))



@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    if 'user_id' not in session:
        flash('Please log in to create a playlist.', 'error')
        return redirect(url_for('user_login'))

    if request.method == 'GET':
        
        songs = Song.query.all()
        return render_template('create_playlist.html', songs=songs)

    elif request.method == 'POST':
        
        user_id = session['user_id']
        playlist_name = request.form['playlist_name']
        selected_song_ids = request.form.getlist('selected_songs')
        new_playlist = Playlist(name=playlist_name, user_id=user_id)
        db.session.add(new_playlist)
        db.session.commit()

        
        for song_id in selected_song_ids:
            song = Song.query.get(song_id)
            if song:
                new_playlist.songs.append(song)

        db.session.commit()

        flash('Playlist created successfully!', 'success')
        return redirect(url_for('dashboard'))

@app.route('/view_playlist/<int:playlist_id>')
def view_playlist(playlist_id):
    
    playlist = Playlist.query.get(playlist_id)

    if not playlist:
        flash('Playlist not found.', 'error')
        return redirect(url_for('dashboard'))

    return render_template('view_playlist.html', playlist=playlist)

@app.route('/edit_playlist/<int:playlist_id>', methods=['GET', 'POST'])
def edit_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if not playlist:
        flash('Playlist not found.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'GET':
        songs = Song.query.all()
        return render_template('edit_playlist.html', playlist=playlist, songs=songs)

    elif request.method == 'POST':
        
        playlist.name = request.form['playlist_name']
        selected_song_ids = request.form.getlist('selected_songs')

        
        playlist.songs = []

        
        for song_id in selected_song_ids:
            song = Song.query.get(song_id)
            if song:
                playlist.songs.append(song)

        db.session.commit()

        flash('Playlist updated successfully!', 'success')
        return redirect(url_for('dashboard'))

@app.route('/delete_playlist/<int:playlist_id>', methods=['GET', 'POST'])
def delete_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if playlist:
        db.session.delete(playlist)
        db.session.commit()
        flash('Playlist deleted successfully!', 'success')
    else:
        flash('Playlist not found.', 'error')

    return redirect(url_for('dashboard'))

@app.route('/playlistsongread/<int:playlist_id>/<int:song_index>')
def playlistsongread(playlist_id, song_index):
    
    playlist = Playlist.query.get(playlist_id)

    if not playlist:
        flash('Playlist not found.', 'error')
        return redirect(url_for('dashboard'))

    
    songs = playlist.songs

    
    if 0 <= song_index < len(songs):
        
        song = songs[song_index]
        return render_template('playlistsongread.html', lyrics=song.lyrics, song=song, playlist=playlist, song_index=song_index)
    else:
        flash('Song not found in the playlist.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/search_results')
def search_results():
    query = request.args.get('query', '')
    
    
    search_results = Song.query.filter(
        (Song.title.ilike(f'%{query}%')) |
        (Song.artist.ilike(f'%{query}%'))
    ).all()

    return render_template('search_results.html', query=query, results=search_results)

@app.route('/creator-profile')
def creator_profile():
    if 'user_id' in session and session['is_creator']:
        # Get creator's information
        creator_id = session['user_id']
        creator_name = session['name']
        creator_status = session['blacklist']


        creator_songs = Song.query.filter_by(artist=creator_name).all()

        
        creator_albums = Album.query.filter_by(user_id=creator_id).all()

        
        total_ratings = sum(song.average_rating for song in creator_songs)
        average_rating = total_ratings / len(creator_songs) if len(creator_songs) > 0 else 0.0

        
        total_songs = len(creator_songs)

        
        return render_template('creator_profile.html', 
                               total_songs=total_songs,
                               average_rating=average_rating,
                               uploaded_songs=creator_songs,
                               creator_albums=creator_albums)
    else:
        flash('Please log in as a creator to access the creator profile.', 'error')
        return redirect(url_for('user_login'))

        
@app.route('/edit_song/<int:song_id>', methods=['GET', 'POST'])
def edit_song(song_id):
    song = Song.query.get(song_id)

    if not song:
        flash('Song not found.', 'error')
        return redirect(url_for('creator_profile'))

    if request.method == 'GET':
        
        return render_template('edit_song.html', song=song)

    elif request.method == 'POST':
        
        song.title = request.form['title']
        song.lyrics = request.form['lyrics']
        song.duration = request.form['duration']
        song.genre = request.form['genre'] 

        db.session.commit()

        flash('Song updated successfully!', 'success')
        return redirect(url_for('creator_profile'))

@app.route('/delete_song/<int:song_id>', methods=['GET', 'POST'])
def delete_song(song_id):
    song = Song.query.get(song_id)

    if not song:
        flash('Song not found.', 'error')
        return redirect(url_for('creator_profile'))

    
    ratings = Rating.query.filter_by(song_id=song_id).all()
    for rating in ratings:
        db.session.delete(rating)

    
    db.session.delete(song)
    db.session.commit()

    flash('Song deleted successfully!', 'success')
    return redirect(url_for('creator_profile'))

@app.route('/submit_rating/<int:song_id>', methods=['POST'])
def submit_rating(song_id):
    if 'user_id' not in session:
        flash('Please log in to submit a rating.', 'error')
        return redirect(url_for('user_login'))

    rating_value = int(request.form['rating'])
    user_id = session['user_id']

    
    existing_rating = Rating.query.filter_by(user_id=user_id, song_id=song_id).first()
    if existing_rating:
        existing_rating.rating = rating_value
    else:
        new_rating = Rating(user_id=user_id, song_id=song_id, rating=rating_value)
        db.session.add(new_rating)

    db.session.commit()

    flash('Rating submitted successfully!', 'success')
    return redirect(url_for('read_lyrics', song_id=song_id))

@app.route('/create_album', methods=['GET', 'POST'])
def create_album():
    if 'user_id' not in session or not session['is_creator']:
        flash('Please log in as a creator to create an album.', 'error')
        return redirect(url_for('user_login'))

    if request.method == 'GET':
        
        creator_id = session['user_id']
        creator_songs = Song.query.filter_by(artist=User.query.get(creator_id).name).all()
        return render_template('create_album.html', songs=creator_songs)

    elif request.method == 'POST':
        
        album_name = request.form['album_name']
        selected_song_ids = request.form.getlist('selected_songs')

        
        user_id = session['user_id']

        
        new_album = Album(name=album_name, user_id=user_id)
        db.session.add(new_album)
        db.session.commit()

        
        for song_id in selected_song_ids:
            song = Song.query.get(song_id)
            if song:
                song.album = new_album

        db.session.commit()

        flash('Album created successfully!', 'success')
        return redirect(url_for('creator_profile'))
    return render_template('create_album.html')

@app.route('/view_album/<int:album_id>')
def view_album(album_id):
    
    album = Album.query.get(album_id)

    if not album:
        flash('Album not found.', 'error')
        return redirect(url_for('creator_profile'))

    return render_template('view_album.html', album=album)

@app.route('/uview_album/<int:album_id>')
def uview_album(album_id):
    
    album = Album.query.get(album_id)

    if not album:
        flash('Album not found.', 'error')
        return redirect(url_for('creator_profile'))

    return render_template('uview_album.html', album=album)

@app.route('/edit_album/<int:album_id>', methods=['GET', 'POST'])
def edit_album(album_id):
    album = Album.query.get(album_id)
    
    if not album:
        flash('Album not found.', 'error')
        return redirect(url_for('creator_profile'))

    if request.method == 'GET':
        creator_id = session['user_id']
        creator_songs = Song.query.filter_by(artist=User.query.get(creator_id).name).all()
        return render_template('edit_album.html', album=album, songs=creator_songs)

    elif request.method == 'POST':
        
        album.name = request.form['album_name']
        selected_song_ids = request.form.getlist('selected_songs')

        
        album.songs = []

        
        for song_id in selected_song_ids:
            song = Song.query.get(song_id)
            if song:
                album.songs.append(song)

        db.session.commit()

        flash('Album updated successfully!', 'success')
        return redirect(url_for('view_album', album_id=album.id))

@app.route('/delete_album/<int:album_id>', methods=['GET', 'POST'])
def delete_album(album_id):
    album = Album.query.get(album_id)

    if not album:
        flash('Album not found.', 'error')
        return redirect(url_for('creator_profile'))

    if request.method == 'POST':
        
        for song in album.songs:
            song.album = None

        
        db.session.delete(album)
        db.session.commit()
        flash('Album deleted successfully!', 'success')
        return redirect(url_for('creator_profile'))

    return render_template('delete_album.html', album=album)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' in session:
        
        admin_id = session['admin_id']
        admin_username = session['admin_username']
        
        
        total_users = User.query.count()
        total_non_creators = User.query.filter_by(is_creator=False).count()
        total_songs = Song.query.count()
        total_albums = Album.query.count()

        

        song_upload_data = db.session.query(
            db.func.strftime('%Y-%m-%d', Song.date_created),
            db.func.count(Song.id)
        ).group_by(db.func.strftime('%Y-%m-%d', Song.date_created)).all()

        days, song_counts = zip(*song_upload_data)

        
        days = [datetime.strptime(day, '%Y-%m-%d').date() for day in days]

        plt.figure(figsize=(10, 6))
        plt.stem(date2num(days), song_counts, markerfmt='C3o', linefmt='C3-', basefmt='C0-')
        plt.xlabel('Day')
        plt.ylabel('Number of Songs Uploaded')
        plt.title('Daily Song Uploads')


        plt.xticks(date2num(days), days, rotation=45)

        plt.tight_layout()




        
        image_stream = BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)
        plt.close()

        
        graph_data = base64.b64encode(image_stream.read()).decode('utf-8')

    
        return render_template('admin_dashboard.html', user={'id': admin_id, 'username': admin_username},
                           total_users=total_users, total_non_creators=total_non_creators,
                           total_songs=total_songs, total_albums=total_albums,
                           graph_data=graph_data)

        
        
    else:
        
        flash('Please log in to access the admin dashboard.', 'error')
        return redirect(url_for('home'))

@app.route('/admin_search_results')
def admin_search_results():
    query = request.args.get('query', '')
    
    
    search_results = Song.query.filter(
        (Song.title.ilike(f'%{query}%')) |
        (Song.artist.ilike(f'%{query}%'))
    ).all()
    
    return render_template('admin_search_results.html', query=query, results=search_results)

    
@app.route('/flag_song/<int:song_id>', methods=['POST'])
def flag_song(song_id):
    song = Song.query.get(song_id)

    if song:
        song.flag = True  
        db.session.commit()
    
    flash('Song flagged successfully!', 'success')
    return redirect(url_for('admin_search_results'))

@app.route('/delete_asong/<int:song_id>', methods=['POST'])
def delete_asong(song_id):
    
    song = Song.query.get(song_id)
    if song:
        ratings = Rating.query.filter_by(song_id=song.id).all()
        for rating in ratings:
            db.session.delete(rating)

        db.session.delete(song)
        db.session.commit()
        flash('Song deleted successfully!', 'success')
    else:
        flash('Song not found.', 'error')

    return redirect(url_for('admin_search_results'))

@app.route('/songs_and_albums')
def songs_and_albums():
    
    all_songs = Song.query.all()
    all_albums = Album.query.all()
    all_creators = User.query.filter_by(is_creator=1).all()

    
    return render_template('songs_and_albums.html', all_songs=all_songs, all_albums=all_albums, all_creators=all_creators)

@app.route('/aflag_song/<int:song_id>', methods=['POST'])
def aflag_song(song_id):
    song = Song.query.get(song_id)

    if song:
        
        song.flag = True  
        db.session.commit()

    return redirect(url_for('songs_and_albums'))

@app.route('/adelete_song/<int:song_id>', methods=['POST'])
def adelete_song(song_id):
    
    song = Song.query.get(song_id)
    if song:
        ratings = Rating.query.filter_by(song_id=song.id).all()
        for rating in ratings:
            db.session.delete(rating)

        db.session.delete(song)
        db.session.commit()
        flash('Song deleted successfully!', 'success')
    else:
        flash('Song not found.', 'error')
    return redirect(url_for('songs_and_albums'))

@app.route('/adelete_album/<int:album_id>', methods=['GET', 'POST'])
def adelete_album(album_id):
    album = Album.query.get(album_id)

    if not album:
        flash('Album not found.', 'error')
        return redirect(url_for('songs_and_albums'))

    if request.method == 'POST':
        
        for song in album.songs:
            song.album = None

        
        db.session.delete(album)
        db.session.commit()
        flash('Album deleted successfully!', 'success')

    return redirect(url_for('songs_and_albums'))


@app.route('/aflag_album/<int:album_id>', methods=['POST'])
def aflag_album(album_id):
    
    album = Album.query.get(album_id)

    if album:
        
        album.flag = True  

        
        db.session.commit()
        
    return redirect(url_for('songs_and_albums'))

@app.route('/blacklist_creator/<int:creator_id>', methods=['GET', 'POST'])
def blacklist_creator(creator_id):
    
    creator = User.query.get_or_404(creator_id)

    
    if not creator.blacklist:
        
        creator.blacklist = True
        db.session.commit()

    return redirect(url_for('songs_and_albums'))  

@app.route('/whitelist_creator/<int:creator_id>', methods=['GET', 'POST'])
def whitelist_creator(creator_id):
    
    creator = User.query.get_or_404(creator_id)

    
    if creator.blacklist:
        
        creator.blacklist = False
        db.session.commit()

    return redirect(url_for('songs_and_albums'))

@app.route('/aread_lyrics/<int:song_id>', methods=['POST'])
def aread_lyrics(song_id):
    
    song = Song.query.get(song_id)

    if song:
        return render_template('aread_lyrics.html', song=song)
    else:
       
        return render_template('songs_and_albums.html')

@app.route('/aview_album/<int:album_id>')
def aview_album(album_id):
   
    album = Album.query.get(album_id)

    if not album:
        flash('Album not found.', 'error')
        return redirect(url_for('songs_and_albums'))

    
    return render_template('aview_album.html', album=album)

@app.route('/view_acreator_profile/<int:creator_id>')
def view_acreator_profile(creator_id):
    
    creator = User.query.get(creator_id)

    if not creator:
        flash('Creator not found.', 'error')
        return redirect(url_for('songs_and_albums'))

    
    creator_songs = Song.query.filter_by(artist=creator.name).all()

    
    total_ratings = sum(song.average_rating for song in creator_songs)
    average_rating = total_ratings / len(creator_songs) if len(creator_songs) > 0 else 0.0

    
    total_songs = len(creator_songs)


    return render_template('acreatorprofile.html', 
                           creator=creator,
                           total_songs=total_songs,
                           average_rating=average_rating,
                           uploaded_songs=creator_songs)
