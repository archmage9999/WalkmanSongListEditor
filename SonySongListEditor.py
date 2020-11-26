# -*- coding: UTF-8 -*-

import os

from tkinter import *
from tinytag import TinyTag
from functools import partial
from componentMgr import componentMgr
from components import create_default_component
from tkinter.filedialog import askopenfilenames, asksaveasfilename

M3U_HEAD = '#EXTM3U\n'
M3U_NEW_LINE = '#EXTINF:,'


class SonySongListEditor(componentMgr):

    def __init__(self, master, gui_path):
        componentMgr.__init__(self, master)
        self.load_from_xml(master, gui_path, True)
        self.music_path_list = []
        self.song_index = 0
        self.right_edit_menu_1 = None
        self.right_edit_menu_2 = None
        self.build_music_path()
        self.init_frame()

    @property
    def editor_window(self):
        return self.master.children.get("sonySongListEditor", None)

    @property
    def song_list_list(self):
        return self.editor_window.children.get("songlistlist", None)

    @property
    def song_list(self):
        return self.editor_window.children.get("songlist", None)

    def build_music_path(self):
        """
        创建音乐路径
        :return: None
        """
        for i in range(ord("A"), ord("Z") + 1):
            path = chr(i) + ":\\" + "MUSIC"
            self.music_path_list.append(path)

    def init_frame(self):
        """
        初始化窗口
        :return: None
        """
        self.init_menu()
        self.init_song_list_list()
        self.init_song_list()
        self.scan_music_list()

    def init_menu(self):
        """
        初始化菜单
        :return: None
        """
        main_menu = Menu(self.master, tearoff=0, name="menu")

        edit_menu = Menu(main_menu, tearoff=0, name="edit")
        edit_menu.add_command(label="create_song_list", command=self.create_song_list)
        edit_menu.add_command(label="delete_song_list", command=self.delete_song_list)
        edit_menu.add_command(label="add_songs", command=self.add_songs)
        edit_menu.add_command(label="delete_songs", command=self.delete_songs)

        main_menu.add_cascade(label="edit", menu=edit_menu)
        self.master.config(menu=main_menu)

        self.right_edit_menu_1 = Menu(self.master, tearoff=0)
        self.right_edit_menu_1.add_command(label="delete_song_list", command=self.delete_song_list)

        self.right_edit_menu_2 = Menu(self.master, tearoff=0)
        self.right_edit_menu_2.add_command(label="delete_songs", command=self.delete_songs)

    def init_song_list_list(self):
        """
        初始化播放列表列表控件
        :return: None
        """
        self.song_list_list.set_handle_cancel_select_row(self.cancel_select_song_list)
        self.song_list_list.set_handle_select_row(self.select_song_list)

    def cancel_select_song_list(self, index):
        """
        取消选中播放列表
        :param index: 索引
        :return: None
        """
        row = self.song_list_list.get_row_by_index(index)
        if not row:
            return

        row.configure(state="normal")

    def select_song_list(self, index):
        """
        选中播放列表
        :param index: 索引
        :param event:
        :return:
        """
        row = self.song_list_list.get_row_by_index(index)
        if not row:
            return

        row.configure(state="active")
        data = self.song_list_list.get_data_by_index(index)
        self.add_songs_from_path(data["list_path"], data["path"])

    def add_songs_from_path(self, song_list_path, path):
        """
        从给定的路径读取歌曲信息
        :param song_list_path: 歌单路径
        :param path: 歌单所在文件夹路径
        :return: None
        """
        self.song_list.clear_all_node()
        all_lines = []
        self.song_index = 0
        with open(song_list_path, 'r', encoding='utf-8') as f:
            line_head = f.readline()
            if line_head != M3U_HEAD:
                return
            line = f.readline()
            i = 1
            while line:
                if i % 2 == 0:
                    all_lines.append(os.path.join(path, line[:-1]))
                i += 1
                line = f.readline()

        for line in all_lines:
            self.add_song(line)

        self.song_list.update_scroll()

    def add_song(self, song_path):
        """
        添加一首歌曲
        :param song_path: 歌曲路径
        :param index: 歌曲索引
        :return: None
        """
        tag = TinyTag.get(song_path)
        title = self.calc_name(tag.title, song_path)
        self.song_list.add_node("", self.song_index, values=(str(self.song_index), title, tag.artist, tag.album, tag.duration, song_path))
        self.song_index += 1

    @staticmethod
    def calc_name(title, song_path):
        """
        如果没有读取出title则直接读取名字
        :param title: 读取出来的title
        :param song_path: 歌曲路径
        :return: string
        """
        if title:
            return title

        index = song_path.find("/")
        return song_path[index:]

    def sort_song_list(self, col, reverse):
        """
        歌曲排序
        :param col: 要排序的列
        :param reverse: 是否倒序
        :return: None
        """
        l = []
        for child in self.song_list.tree.get_children(''):
            l.append((self.song_list.tree.set(child, col), child))
        l.sort(key=lambda t:t[0], reverse=reverse)

        for index, (val, child) in enumerate(l):
            self.song_list.tree.move(child, '', index)

        self.song_list.tree.heading(col, command=partial(self.sort_song_list, col, not reverse))

    def init_song_list(self):
        """
        初始化播放列表控件
        :return: None
        """
        columns = ("index", "title", "artist", "album", "duration")
        self.song_list.tree.configure(columns=columns)
        for name in columns:
            self.song_list.tree.column(name, anchor="center", width=170)
            self.song_list.tree.heading(name, text=name, command=partial(self.sort_song_list, name, False))

        self.song_list.set_on_select_tree(self.on_select_song)

    def on_select_song(self, event):
        """
        选中歌曲时触发
        :param event:
        :return: None
        """
        self.right_edit_menu_2.post(event.x_root, event.y_root)

    def scan_music_list(self):
        """
        扫描歌单
        :return:None
        """
        self.song_list_list.clear_rows()
        for path in self.music_path_list:
            if not os.path.exists(path):
                continue
            for file_name in os.listdir(path):
                self.scan_music_list_next(path, file_name)

        self.song_list_list.do_layout_row()
        self.song_list_list.select_first_row_base()

    def scan_music_list_next(self, path, file_name):
        """
        扫描歌单下一步
        :param path: 扫描路径
        :param file_name: 文件路径
        :return: int
        """
        file_name_base, file_ext = os.path.splitext(file_name)
        if file_ext != ".m3u":
            return

        list_path = os.path.join(path, file_name)
        created_num = self.song_list_list.get_created_row_num()

        prop = {
            "text": list_path, "activebackground": "red", "font_anchor": "w", "width": 40,
        }
        row, info = create_default_component(self.song_list_list.get_child_master(), "Label", "row_" + str(created_num), prop)
        row.bind("<ButtonRelease-1>", lambda event:self.song_list_list.set_selected_row(created_num))

        def right_click(event):
            self.song_list_list.set_selected_row(created_num)
            self.right_edit_menu_1.post(event.x_root, event.y_root)

        row.bind("<ButtonRelease-3>", right_click)
        data = {"list_path": list_path, "path": path,}
        self.song_list_list.add_row_base(row, False, data)

        return created_num

    def create_song_list(self):
        """
        创建播放列表
        :return: None
        """
        file_path = asksaveasfilename(title=u"选择文件", filetypes=[("m3u files", "m3u"), ], defaultextension=".m3u")
        if not file_path:
            return

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(M3U_HEAD)

        base_path, file_name = os.path.split(file_path)
        index = self.scan_music_list_next(base_path, file_name)

        self.song_list_list.do_layout_row()
        self.song_list_list.set_selected_row(index)

    def delete_song_list(self):
        """
        删除播放列表
        :return: None
        """
        selected = self.song_list_list.get_selected_row()
        if selected is None:
            return

        data = self.song_list_list.get_data_by_index(selected)
        os.remove(data["list_path"])

        self.song_list.clear_all_node()
        self.song_list_list.delete_row_base(selected)

    def add_songs(self):
        """
        将歌曲添加到播放列表
        :return: None
        """
        selected = self.song_list_list.get_selected_row()
        if selected is None:
            return

        data = self.song_list_list.get_data_by_index(selected)
        music_files = askopenfilenames(initialdir=data["path"])
        if not music_files:
            return

        for music_path in music_files:
            self.add_song(music_path)

        self.save_song_list(data["list_path"], data["path"])

    def delete_songs(self):
        """
        从播放列表中删除歌曲
        :return: None
        """
        selected = self.song_list_list.get_selected_row()
        if selected is None:
            return

        select_songs = self.song_list.tree.selection()
        for idx in select_songs:
            self.song_list.tree.delete(idx)

        data = self.song_list_list.get_data_by_index(selected)
        self.save_song_list(data["list_path"], data["path"])

    def save_song_list(self, song_list, base_path):
        """
        保存播放列表
        :param song_list: 播放列表路径
        :param base_path: 播放列表base路径
        :return: None
        """
        with open(song_list, "w", encoding="utf-8") as f:
            f.writelines(M3U_HEAD)
            songs = self.get_all_songs()
            song_list_new = []
            for song in songs:
                new_path = self.get_relatively_path(song, base_path)
                song_list_new.append(M3U_NEW_LINE + '\n')
                if not new_path.endswith('\n'):
                    new_path += '\n'
                song_list_new.append(new_path)
            f.writelines(song_list_new)

    def get_all_songs(self):
        """
        获取所有歌曲
        :return: None
        """
        all_songs = []
        for item in self.song_list.tree.get_children():
            item_text = self.song_list.tree.item(item, "values")
            all_songs.append(item_text[5])

        return all_songs

    @staticmethod
    def get_relatively_path(music_path, base_path):
        """
        计算相对路径
        :param music_path:音乐路径
        :param base_path:歌单路径
        :return:string
        """
        index = os.path.normpath(music_path).find(os.path.normpath(base_path))
        if index == -1:
            raise Exception("音乐文件必须在MUSIC目录中")

        return music_path[index + len(base_path) + 1:]


def main():
    root = Tk()
    path = os.path.join(os.getcwd(), 'SonySongListEditor.xml')
    SonySongListEditor(root, path)
    root.mainloop()


if __name__ == "__main__":
    main()
