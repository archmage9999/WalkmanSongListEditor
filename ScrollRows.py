#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from ScrollCanvas import ScrollCanvas
from componentProperty import update_all_property, get_default_component_info


def create_default_component(master, component_type, component_name, prop=None, use_name=True):
    """
    创建默认控件
    :param master: 父控件
    :param component_type: 控件类型
    :param component_name: 控件名字
    :param prop: 需要更新的属性
    :param use_name: 是否使用控件名字
    :return: 控件
    """
    class_name = getattr(sys.modules[__name__], component_type)
    if use_name:
        component = class_name(master, name=component_name)
    else:
        component = class_name(master)

    component_info = get_default_component_info(component_type, prop)
    update_all_property(component, component_info, component_type)

    return component, component_info


class ScrollRows(ScrollCanvas):

    def __init__(self, master=None, cnf={}, **kw):
        ScrollCanvas.__init__(self, master, cnf, **kw)
        self.created_row_num = 0                                        # 已创建的行数
        self.row_distance = 1                                           # 行间距
        self.pos_y_default = 0                                          # 列初始位置y
        self.rows = {}                                                  # 存储所有的行
        self.data = {}                                                  # 存储额外的数据
        self.selected_row = None                                        # 当前选中的行
        self.handle_cancel_select_row = None                            # 取消选中行回调
        self.handle_select_row = None                                   # 选中行回调

    def get_created_row_num(self):
        return self.created_row_num

    def set_created_row_num(self, created_row_num):
        if self.created_row_num == created_row_num:
            return
        self.created_row_num = created_row_num

    def get_row_distance(self):
        return self.row_distance

    def set_row_distance(self, row_distance):
        if self.row_distance == row_distance:
            return
        self.row_distance = row_distance

    def get_pos_y_default(self):
        return self.pos_y_default

    def set_pos_y_default(self, pos_y_default):
        if self.pos_y_default == pos_y_default:
            return
        self.pos_y_default = pos_y_default

    def get_selected_row(self):
        return self.selected_row

    def set_selected_row(self, selected_row):
        if self.selected_row == selected_row:
            return
        self.on_cancel_select_row(self.selected_row)
        self.selected_row = selected_row
        self.on_select_row(selected_row)

    def get_data_by_index(self, index):
        if index not in self.data:
            return None
        return self.data[index]

    def set_data_by_index(self, index, extra_data):
        self.data[index] = extra_data

    def set_handle_cancel_select_row(self, handle_cancel_select_row):
        self.handle_cancel_select_row = handle_cancel_select_row

    def set_handle_select_row(self, handle_select_row):
        self.handle_select_row = handle_select_row

    def on_update(self):
        ScrollCanvas.on_update(self)

    def get_row_by_index(self, index):
        return self.rows.get(index, None)

    def clear_rows(self):
        """
        清空所有row
        :return:None
        """
        for k, v in self.rows.items():
            v.destroy()
        self.set_created_row_num(0)
        self.rows.clear()

    def add_row_base(self, row_control, is_do_layout=True, extra_data=None):
        """
        增加一行
        :param row_control:行控件
        :param is_do_layout:是否do_layout
        :return: None
        """
        created_num = self.get_created_row_num()
        self.rows[created_num] = row_control
        self.set_created_row_num(created_num + 1)
        self.set_data_by_index(created_num, extra_data)

        if is_do_layout:
            self.do_layout_row()

    def add_rows_base(self, row_control_list):
        """
        增加多行
        :param row_control_list:行控件
        :return: None
        """
        for col_control in row_control_list:
            self.add_row_base(col_control, False)

        self.do_layout_row()

    def delete_row_base(self, index, is_do_layout=True):
        """
        删除一行
        :param index: 索引
        :param is_do_layout: 是否重新布局
        :return: None
        """
        if index not in self.rows:
            return

        # 如果删除的是当前选中的则先取消选中
        if self.get_selected_row() == index:
            self.on_cancel_select_row(index)

        self.rows[index].destroy()
        del self.rows[index]

        if index in self.data:
            del self.data[index]

        if is_do_layout:
            self.do_layout_row()

        if self.get_selected_row() == index:
            self.select_first_row_base()

    def get_sorted_rows(self):

        sorted_keys = sorted(self.rows.keys())
        sorted_rows = []
        for key in sorted_keys:
            sorted_rows.append(self.rows[key])

        return sorted_rows

    def do_layout_row(self):
        """
        重新布局界面
        :return:None
        """
        sorted_children = self.get_sorted_rows()
        pos_y = self.get_pos_y_default()
        for child in sorted_children:
            child.place(x=child.place_info().get("x", 0), y=pos_y)
            pos_y += child.winfo_reqheight() + self.get_row_distance()
        self.update_scroll()

    def on_cancel_select_row(self, cancel_row):
        """
        取消选中行时调用
        :param cancel_row: 需要选中的行
        :return: None
        """
        if cancel_row is None:
            return

        if self.handle_cancel_select_row is not None:
            self.handle_cancel_select_row(cancel_row)

    def on_select_row(self, select_row):
        """
        选中行时调用
        :param select_row: 选中的行
        :return: None
        """
        if select_row is None:
            return

        if self.handle_select_row is not None:
            self.handle_select_row(select_row)

    def get_selected_keys_base(self):
        """
        获取所有可选择的key
        :return: list
        """
        return sorted(self.rows.keys())

    def select_first_row_base(self):
        """
        选中第一行
        :return: None
        """
        sorted_keys = self.get_selected_keys_base()
        for index in sorted_keys:
            self.set_selected_row(index)
            break
        else:
            self.set_selected_row(None)