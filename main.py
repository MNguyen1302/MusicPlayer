import os.path
import time
import random
import eyed3

from PyQt5.QtWidgets import *
from PyQt5 import QtMultimedia, QtGui, QtWidgets
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from music import Ui_MainWindow
from add_playlist_dialog import Ui_Dialog
from add_song_playlist_dialog import Ui_add_to_playlist_dialog
import db_func as db

class MusicPlayer(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.window = QMainWindow()
        self.setupUi(self)
        self.show()
        self.stackedWidget.setCurrentIndex(0)

        self.current_songs = []
        self.current_volume = 50

    #     self.frame.lower()

        global stopped
        stopped = False

        self.player = QtMultimedia.QMediaPlayer()
        self.player.setVolume(self.current_volume)

        self.volume_slider.setValue(self.current_volume)

        #Timer
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.move_slider)

        #Connect database
        self.connection = db.connect_to_database()

        #Connections
        self.music_slider.sliderMoved[int].connect(lambda: self.player.setPosition(self.music_slider.value()))
        self.volume_slider.sliderMoved[int].connect(lambda: self.volume_changed())
        self.player.stateChanged.connect(self.media_player_changed)
        self.player.mediaStatusChanged.connect(self.end_song)
        self.btn_play_pause.clicked.connect(self.play_pause_song)
        self.btn_next.clicked.connect(self.default_next)
        self.btn_prev.clicked.connect(self.prev_song)
        self.btn_add_playlist.clicked.connect(self.show_add_playlist_dialog)
        self.btn_remove_song.clicked.connect(self.remove_one_song)
        self.btn_song_list.clicked.connect(lambda: self.change_page(0))
        self.btn_playlists.clicked.connect(lambda: self.change_page(1))
        self.btn_add_file.clicked.connect(self.add_songs)
        self.btn_add_song_playlist.clicked.connect(self.show_add_to_playlist_dialog)
        self.btn_load_playlist.clicked.connect(self.load_song_of_playlist)
        self.btn_loop.clicked.connect(self.loop_song)
        self.btn_shuffle.clicked.connect(self.shuffle_song)
        self.btn_remove_playlist.clicked.connect(self.delete_playlist)
        self.btn_delete_all_playlists.clicked.connect(self.delete_all_playlist)
        self.btn_delete_all_songs.clicked.connect(self.delete_all_songs)
        self.loaded_songs_widget.itemDoubleClicked.connect(self.item_double_clicked)
        self.playlists_list_widget.itemDoubleClicked.connect(self.load_song_of_playlist)

    def loop_song(self):
        if self.btn_loop.isChecked():
            self.btn_loop.setChecked(True)
            self.btn_shuffle.setChecked(False)
        else:
            self.btn_loop.setChecked(False)

    def shuffle_song(self):
        if self.btn_shuffle.isChecked():
            self.btn_shuffle.setChecked(True)
            self.btn_loop.setChecked(False)
        else:
            self.btn_shuffle.setChecked(False)

    def load_song_of_playlist(self):
        index = self.playlists_list_widget.currentRow()
        playlist = self.playlists[index]
        self.current_songs = db.load_song_of_playlist(self.connection, playlist.id)
        if len(self.current_songs) == 0:
            self.show_info_messagebox("Chưa có nhạc trong playlist này!")
            return
        self.load_song_list()

    def show_add_playlist_dialog(self):
        dialog = QtWidgets.QDialog()
        self.add_playlist_dialog = Ui_Dialog()
        self.add_playlist_dialog.setupUi(dialog)

        self.add_playlist_dialog.btn_add.clicked.connect(self.add_new_playlist)
        dialog.exec_()

    def add_new_playlist(self):
        name = self.add_playlist_dialog.txtNamePlaylist.text()
        result = db.add_playlist(self.connection, name)
        if result:
            self.add_playlist_dialog.txtNamePlaylist.setText("")
            self.show_info_messagebox("Thêm playlist mới thành công")
            self.load_playlists()
        else:
            self.show_info_messagebox("Thêm playlist mới thất bại")

    def show_add_to_playlist_dialog(self):
        dialog = QtWidgets.QDialog()
        self.add_to_playlist_dialog = Ui_add_to_playlist_dialog()
        self.add_to_playlist_dialog.setupUi(dialog)

        self.add_to_playlist_dialog.btn_add.clicked.connect(self.add_song_to_playlist)
        dialog.exec_()

    def add_song_to_playlist(self):
        index = self.loaded_songs_widget.currentRow()
        playlist_id = self.add_to_playlist_dialog.cbPLaylists.currentText().split("-")[0]
        result = db.add_song_to_playlist(self.connection, self.current_songs[index], playlist_id)
        if result:
            self.show_info_messagebox("Thêm bài hát vào playlist thành công")
        else:
            self.show_info_messagebox("Thêm bài hát vào playlist thất bại")

    def load_playlists(self):
        self.playlists = db.load_playlists(self.connection)

        self.playlists_list_widget.clear()
        for item in self.playlists:
            self.playlists_list_widget.addItem(
                    QListWidgetItem(
                        QIcon('icons/playlist_48px.png'),
                        item.name
                    )
                )
            
    def delete_playlist(self):
        current_selection = self.playlists_list_widget.currentRow()
        result = db.delete_playlist(self.connection, self.playlists[current_selection].id)
        if result:
            self.show_info_messagebox("Bạn đã xóa playlist này thành công")
            print(current_selection)
            self.playlists.pop(current_selection)
            self.load_playlists()
            self.loaded_songs_widget.clear()
        else:
            self.show_info_messagebox("Bạn đã xóa playlist này thất bại")

    def delete_all_playlist(self):
        result = db.delete_all_playlists(self.connection)
        if result:
            self.show_info_messagebox("Bạn đã xóa tất cả playlist")
            self.playlists.clear()
            self.load_playlists()
            self.loaded_songs_widget.clear()
        else:
            self.show_info_messagebox("Bạn đã xóa thất bại")
    def load_song_list(self):
        self.loaded_songs_widget.clear()
        for item in self.current_songs:
            self.loaded_songs_widget.addItem(
                    QListWidgetItem(
                        QIcon('icons/music_record_32px.png'),
                        os.path.basename(item)
                    )
                )
        self.play_song()

    def change_page(self, page):
        self.stackedWidget.setCurrentIndex(page)
        if page == 1:
            self.load_playlists()

    def volume_changed(self):
        try:
            self.current_volume = self.volume_slider.value()
            self.player.setVolume(self.current_volume)
            if self.current_volume < 3:
                self.player.setVolume(0)
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("icons/no_audio_64px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.btn_volume.setIcon(icon)
            else:
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("icons/speaker_64px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.btn_volume.setIcon(icon)
        except Exception as e:
            print(f"Changing volume error: {e}")

    def add_songs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, caption = 'Add Songs',
            directory = ':\\', filter = "Supported Files (*.mp3;*.mpeg;*.ogg;*.m4a;*.MP3;*.wma;*.acc;*.amr)"
        )

        if files:
            for file in files:
                self.current_songs.append(file)
                self.loaded_songs_widget.addItem(
                    QListWidgetItem(
                        QIcon('icons/music_record_32px.png'),
                        os.path.basename(file)
                    )
                )
        # self.play_song()

    def play_song(self):
        try:
            self.loaded_songs_widget.setCurrentRow(0)
            current_song = self.current_songs[0]

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.load_info_song()
            self.move_slider()
        except Exception as e:
            print(f"Play song error: {e}")

    def play_pause_song(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

            
    def media_player_changed(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.btn_play_pause.setChecked(True)
        else:
            self.btn_play_pause.setChecked(False)

    def end_song(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.next_song()

    def stop_song(self):
        try:
            self.player.stop()
            self.music_slider.setValue(0)
            self.start_time_label.setText("00:00")
            self.end_time_label.setText("00:00")
        except Exception as e:
            print(f"Stop song error {e}")

    def move_slider(self):
        if stopped:
            return
        else:
            if self.player.state() == QMediaPlayer.PlayingState:
                self.music_slider.setMinimum(0)
                self.music_slider.setMaximum(self.player.duration())
                slider_position = self.player.position()
                self.music_slider.setValue(slider_position)

                current_time = time.strftime('%M:%S', time.localtime(self.player.position() / 1000))
                song_duration = time.strftime('%M:%S', time.localtime(self.player.duration() / 1000))
                
                self.start_time_label.setText(f"{current_time}")
                self.end_time_label.setText(f"{song_duration}")

    def item_double_clicked(self):
        try:
            current_selection = self.loaded_songs_widget.currentRow()

            current_song = self.current_songs[current_selection]

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.load_info_song()
            self.player.play()
            self.move_slider()
        except Exception as e:
            print(f"Next song error: {e}")

    def default_next(self):
        try:
            current_selection = self.loaded_songs_widget.currentRow()

            if current_selection + 1 == len(self.current_songs):
                next_index = 0
            else:
                next_index = current_selection + 1

            current_song = self.current_songs[next_index]
            self.loaded_songs_widget.setCurrentRow(next_index)

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.load_info_song()
            self.player.play()
            self.move_slider()
        except Exception as e:
            print(f"Next song error: {e}")

    def looped_next(self):
        try:
            current_selection = self.loaded_songs_widget.currentRow()

            current_song = self.current_songs[current_selection]
            self.loaded_songs_widget.setCurrentRow(current_selection)

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.load_info_song()
            self.player.play()
            self.move_slider()
        except Exception as e:
            print(f"Next song error: {e}")

    def shuffled_next(self):
        try:
            song_index = random.randint(0, len(self.current_songs) - 1)

            current_song = self.current_songs[song_index]
            self.loaded_songs_widget.setCurrentRow(song_index)

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.load_info_song()
            self.player.play()
            self.move_slider()
        except Exception as e:
            print(f"Next song error: {e}")

    def next_song(self):
        if self.btn_loop.isChecked():
            self.looped_next()
        elif self.btn_shuffle.isChecked():
            self.shuffled_next()
        else: 
            self.default_next()

    def prev_song(self):
        try:
            current_selection = self.loaded_songs_widget.currentRow()

            if current_selection == 0:
                prev_index = len(self.current_songs) - 1
            else:
                prev_index = current_selection - 1

            current_song = self.current_songs[prev_index]
            self.loaded_songs_widget.setCurrentRow(prev_index)
        
            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.load_info_song()
            self.player.play()
            self.move_slider()
        except Exception as e:
            print(f"Previous song error: {e}")

    def remove_one_song(self):
        current_selection = self.loaded_songs_widget.currentRow()
        self.current_songs.pop(current_selection)
        self.loaded_songs_widget.takeItem(current_selection)

    def delete_all_songs(self):
        self.current_songs.clear()
        self.loaded_songs_widget.clear()

    def load_info_song(self):
        current_selection = self.loaded_songs_widget.currentRow()
        audio_file = eyed3.load(self.current_songs[current_selection])
        self.name_song.setText(audio_file.tag.title)
        self.name_artist.setText(audio_file.tag.artist)
        for image in audio_file.tag.images:
            self.image_song.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage.fromData(image.image_data)))

    def show_info_messagebox(self, message): 
        msg = QMessageBox() 
        msg.setIcon(QMessageBox.Information) 
    
        msg.setText(message) 
        
        msg.setWindowTitle("Thông báo") 
        
        msg.setStandardButtons(QMessageBox.Ok) 
        
        retval = msg.exec_()