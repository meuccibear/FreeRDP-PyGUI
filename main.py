import subprocess
import json
import os, re
import time
import gi
import PySimpleGUI as sg
import hashlib

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio

class Login:
    def __init__(self, MainApplication):
        # 创建窗口并设置默认界面为登录界面
        window = self.create_login_window()

        self.serv_list: list[Account] = list()
        self.load_servers()

        # 创建事件循环
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                break
            # 处理登录界面的事件
            if event == '登录':
                for index in range(len(self.serv_list)):
                    new_password = self.encryption(self.serv_list[index].get_dict()['passwd'])

                    # 进行登录验证
                    if values['username'] == self.serv_list[index].get_dict()['username'] and values['password'] == new_password:
                        # 登录成功，关闭登录窗口，打开主界面窗口
                        window.close()
                        MainApplication.start()
                        return
                        # window = self.create_main_window()
                    else:
                        # 登录失败，弹出提示框
                        sg.popup('用户名或密码错误！')
                    if index + 1 < len(self.serv_list):
                        sg.popup('没找到该用户名！')
            # 处理注册界面的事件
            elif event == '注册账号':
                # 关闭登录窗口，打开注册窗口
                window.close()
                window = self.create_register_window()
            # 处理注册界面的事件
            elif event == '注册':
                # 进行注册操作
                if values['password'] == values['confirm_password']:
                    newAccount = Account()
                    newAccount.name = values['username']
                    newAccount.passwd = self.encryption(values['password'])
                    self.serv_list.append(newAccount)
                    self.save_servers()
                    # 注册成功，弹出提示框
                    sg.popup('注册成功！')
                    # 关闭注册窗口，打开登录窗口
                    window.close()
                    # window.show()
                    window = self.create_login_window()
                else:
                    # 注册失败，弹出提示框
                    sg.popup('两次输入的密码不一致！')
            # 处理主界面的事件
            elif event == '退出':
                # 关闭主界面窗口，退出程序
                window.close()
                break
        # 退出事件循环，程序结束

    def encryption(self, password):
        hash = hashlib.md5('python'.encode('utf-8'))
        hash.update(password.encode("utf-8"))
        # b0758ad1aad20530044668775f389922
        return hash.hexdigest()

    def create_login_window(self):
        # 定义登录界面的布局
        login_layout = [
            [sg.Text('账号：'), sg.Input(key='username')],
            [sg.Text('密码：'), sg.Input(key='password', password_char='*')],
            [sg.Button('登录'), sg.Button('注册账号')]
        ]
        return sg.Window("智谱远程视频管理平台", login_layout)

    def create_register_window(self):
        # 定义注册界面的布局
        register_layout = [ [sg.Text('账号：'), sg.Input(key='username')], [sg.Text('密码：'), sg.Input(key='password', password_char='*')], [sg.Text('确认密码：'), sg.Input(key='confirm_password', password_char='*')], [sg.Button('注册')] ]
        return sg.Window('PySimpleGUI注册系统', register_layout)

    def create_main_window(self):
        # 定义主界面的布局
        main_layout = [ [sg.Text('欢迎使用PySimpleGUI')], [sg.Button('退出')] ]
        return sg.Window('智谱远程视频管理平台', main_layout)

    def load_servers(self):
        fileName = 'account.json'
        if os.path.exists(fileName):
            with open(fileName, 'r', encoding='utf-8') as fp:
                servs_dict = json.load(fp)
                for index in range(len(servs_dict)):
                # for serv_dict in servs_dict:
                    serv = Account()
                    # serv.set_from_dict(serv_dict)
                    print(servs_dict[index])
                    serv.set_from_dict(servs_dict[index])
                    serv.index = index + 1
                    self.serv_list.append(serv)

    def save_servers(self):
        fileName = 'account.json'
        servs_dict = [serv.get_dict() for serv in self.serv_list]
        if os.path.exists(fileName):
            os.remove(fileName)
        with open(fileName, 'w', encoding='utf-8') as fp:
            json.dump(servs_dict, fp)

class Account:
    def __init__(self):
        self.index: int = 0
        self.username: str = ""
        self.passwd: str = ""

    def get_liststore_item(self) -> (int, str, str):
        return self.index, self.username, self.passwd

    def set_from_dict(self, data: dict):
        username = data.get("username")
        if username:
            self.username = username
        passwd = data.get("passwd")
        if passwd:
            self.passwd = passwd

    def get_dict(self):
        return {
            "username": self.username,
            "passwd": self.passwd
        }

class RDPServ:
    def __init__(self):
        self.index: int = 0
        self.name: str = "server name"
        self.address: str = "example.com"
        self.port: int = 3389
        self.user: str = "user"
        self.pwd: str = ""
        self.width: int = 1920
        self.height: int = 1080
        self.remarks: str = ""

    def get_liststore_item(self) -> (int, str, str, str):
        return self.index, self.name, self.user, self.remarks

    def get_command(self) -> tuple[str, str, str, str, str, str]:
        # print ("./WIN-X.exe", f"/v:{self.address}", f"/port:{self.port}", f"/u:{self.user}",
        #       f"/p:{self.pwd}", f"/w:{self.width}", f"/h:{self.height}")
        return ("./WIN-X.exe", f"/v:{self.address}",f"/u:{self.user}",
                f"/p:{self.pwd}", f"/size:{self.width}x{self.height}")

    def set_from_dict(self, data: dict):
        name = data.get("name")
        if name:
            self.name = name
        address = data.get("address")
        if address:
            self.address = address
        port = data.get("port")
        if port is not None:
            self.port = port
        user = data.get("user")
        if user:
            self.user = user
        pwd = data.get("pwd")
        if pwd:
            self.pwd = pwd
        width = data.get("width")
        if width is not None:
            self.width = width
        height = data.get("height")
        if height is not None:
            self.height = height
        remarks = data.get("remarks")
        if remarks is not None:
            self.remarks = remarks

    def get_dict(self):
        return {
            "name": self.name,
            "address": self.address,
            "port": self.port,
            "user": self.user,
            "pwd": self.pwd,
            "width": self.width,
            "height": self.height,
            "remarks": self.remarks
        }

class MainApplication(Gtk.Application):
    def __init__(self, *args, **kargs):
        super().__init__(
            *args,
            application_id="org.example.freerdp-pygui",
            **kargs
        )
        self.connect("activate", self.on_activate)

    def on_activate(self, app: Gtk.Application):
        self.app = app
        Login(self)

    def start(self):
        window = MainWindow(self.app)
        window.show_all()

class ServEditWindow(Gtk.Window):
    def __init__(self, title: str, serv: RDPServ):
        self.confirmed = False
        self.edited_serv = RDPServ()

        super().__init__(title=title)
        self.set_resizable(False)

        # grid layout
        self.grid = Gtk.Grid(column_homogeneous=True,
                             column_spacing=10,
                             row_spacing=10)
        self.add(self.grid)

        # labels
        name_label = Gtk.Label(label="Name:")
        remarks_label = Gtk.Label(label="影像别名:")
        # host_label = Gtk.Label(label="Host:")
        # port_label = Gtk.Label(label="Port:")
        # user_label = Gtk.Label(label="User:")
        # pwd_label = Gtk.Label(label="Password:")
        # screensize_label = Gtk.Label(label="Screen Size:")
        # x_label = Gtk.Label(label=" x ")

        # entries
        # self.name_entry = Gtk.Entry()
        self.remarks_entry = Gtk.Entry()
        # self.host_entry = Gtk.Entry()
        # self.port_entry = Gtk.Entry()
        # self.user_entry = Gtk.Entry()
        # self.pwd_entry = Gtk.Entry()
        # self.width_entry = Gtk.Entry()
        # self.height_entry = Gtk.Entry()
        # self.pwd_entry.set_visibility(False)

        # buttons
        self.confirm_button = Gtk.Button(label="确定")
        self.cancel_button = Gtk.Button(label="取消")
        # signals
        self.confirm_button.connect("clicked", self.on_confirm_button_clicked)
        self.cancel_button.connect("clicked", self.on_cancel_button_clicked)

        # add to grid layout
        # self.grid.attach(name_label,       0, 0, 1, 1)
        self.grid.attach(remarks_label,       0, 0, 1, 1)
        # self.grid.attach(host_label,       0, 1, 1, 1)
        # self.grid.attach(port_label,       0, 2, 1, 1)
        # self.grid.attach(user_label,       0, 3, 1, 1)
        # self.grid.attach(pwd_label,        0, 4, 1, 1)
        # self.grid.attach(screensize_label, 0, 5, 1, 1)

        # self.grid.attach(self.name_entry, 1, 0, 3, 1)
        self.grid.attach(self.remarks_entry, 1, 0, 3, 1)
        # self.grid.attach(self.host_entry, 1, 1, 3, 1)
        # self.grid.attach(self.port_entry, 1, 2, 3, 1)
        # self.grid.attach(self.user_entry, 1, 3, 3, 1)
        # self.grid.attach(self.pwd_entry,  1, 4, 3, 1)

        # self.grid.attach(self.width_entry,  1, 5, 1, 1)
        # self.grid.attach(x_label,           2, 5, 1, 1)
        # self.grid.attach(self.height_entry, 3, 5, 1, 1)

        self.grid.attach(self.confirm_button, 1, 4, 1, 1)
        self.grid.attach(self.cancel_button,  3, 4, 1, 1)

        # set entry text
        # self.name_entry.set_text(serv.name)
        self.remarks_entry.set_text(serv.remarks)
        # self.host_entry.set_text(serv.address)
        # self.port_entry.set_text(str(serv.port))
        # self.user_entry.set_text(serv.user)
        # self.pwd_entry.set_text(serv.pwd)
        # self.width_entry.set_text(str(serv.width))
        # self.height_entry.set_text(str(serv.height))

    def on_cancel_button_clicked(self, button: Gtk.Button):
        self.destroy()

    def on_confirm_button_clicked(self, button: Gtk.Button):
        try:
            # self.edited_serv.name = self.name_entry.get_text()
            self.edited_serv.remarks = self.remarks_entry.get_text()
            # self.edited_serv.address = self.host_entry.get_text()
            # self.edited_serv.port = int(self.port_entry.get_text())
            # self.edited_serv.user = self.user_entry.get_text()
            # self.edited_serv.pwd = self.pwd_entry.get_text()
            # self.edited_serv.width = int(self.width_entry.get_text())
            # self.edited_serv.height = int(self.height_entry.get_text())

            if not(
                len(self.edited_serv.remarks)
                # len(self.edited_serv.name) and len(self.edited_serv.address) and
                # len(self.edited_serv.user) and len(self.edited_serv.pwd)
            ):
                msg_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Error"
                )
                msg_dialog.format_secondary_text("No Empty.")
                msg_dialog.run()
                msg_dialog.destroy()
                return
        except:
            msg_dialog = Gtk.MessageDialog(
                transient_for = self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error"
            )
            msg_dialog.format_secondary_text("Port or Width or Height must be a intager.")
            msg_dialog.run()
            msg_dialog.destroy()
            return

        self.confirmed = True
        self.destroy()

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application):
        # server list, type: RDPServ
        self.serv_list: list[RDPServ] = list()
        self.load_servers()
        # 智谱远程视频管理平台
        super().__init__(title="智谱远程视频管理平台", application=app)
        # window size
        self.set_default_size(800, 400)

        # header bar
        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)
        self.hb.props.title = "智谱远程视频管理平台"
        self.set_titlebar(self.hb)
        self.module_name = 'zprtserver.exe'
        # add_button with icon
        # self.add_button = Gtk.Button()
        # icon = Gio.ThemedIcon(name="document-new-symbolic")
        # image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        # self.add_button.add(image)
        #
        # # add add_button to header bar
        # self.hb.pack_start(self.add_button)

        # model
        self.serv_liststore = Gtk.ListStore(int, str, str, str)
        self.set_liststore_from_serv_list()

        # view
        self.treeview = Gtk.TreeView(model=self.serv_liststore)

        renderer_serv_index = Gtk.CellRendererText()
        renderer_serv_index.set_fixed_size(60, 50)
        column_text_serv_index = Gtk.TreeViewColumn("ID", renderer_serv_index, text=0)
        self.treeview.append_column(column_text_serv_index)

        # name column
        renderer_serv_name = Gtk.CellRendererText()
        renderer_serv_name.set_fixed_size(100, 50)
        column_text_serv_name = Gtk.TreeViewColumn("服务器编号", renderer_serv_name, text=1)
        self.treeview.append_column(column_text_serv_name)

        # server address column
        renderer_serv_addr = Gtk.CellRendererText()
        renderer_serv_addr.set_fixed_size(200, 50)
        column_text_serv_addr = Gtk.TreeViewColumn("窗口编号", renderer_serv_addr, text=2)
        self.treeview.append_column(column_text_serv_addr)

        renderer_serv_remarks = Gtk.CellRendererText()
        renderer_serv_remarks.set_fixed_size(200, 50)
        column_text_serv_remarks = Gtk.TreeViewColumn("影像别名", renderer_serv_remarks, text=3)
        self.treeview.append_column(column_text_serv_remarks)

        # renderer_serv_host = Gtk.CellRendererText()
        # renderer_serv_host.set_fixed_size(600, 50)
        # column_text_serv_host = Gtk.TreeViewColumn("host", renderer_serv_host, text=3)
        # self.treeview.append_column(column_text_serv_host)

        # menu
        self.menu = Gtk.Menu()
        # Edit menu item
        edit_menuitem = Gtk.MenuItem(label="修改")
        self.menu.append(edit_menuitem)

        open_file_menuitem = Gtk.MenuItem(label="打开录像路径")
        self.menu.append(open_file_menuitem)

        # Push flow
        restart_push_flow_file_menuitem = Gtk.MenuItem(label="重启推流")
        self.menu.append(restart_push_flow_file_menuitem)

        # Delete menu item
        # del_menuitem = Gtk.MenuItem(label="Delete")
        # self.menu.append(del_menuitem)
        self.menu.show_all()

        # signals
        # self.add_button.connect("clicked", self.on_new_button_press)
        self.treeview.connect("row-activated", self.on_treeview_row_activated)
        self.treeview.connect("button-press-event", self.on_treeview_button_press)
        edit_menuitem.connect("activate", self.on_edit_menuitem_activate)
        restart_push_flow_file_menuitem.connect("activate", self.on_restart)
        open_file_menuitem.connect("activate", self.on_open)
        # del_menuitem.connect("activate", self.on_del_menuitem_activate)

        # add treeview to main window
        self.add(self.treeview)

    def set_liststore_from_serv_list(self):
        self.serv_liststore.clear()
        for serv in self.serv_list:
            self.serv_liststore.append(serv.get_liststore_item())

    def on_treeview_row_activated(self, treeview: Gtk.TreeView, path: Gtk.TreePath, column: Gtk.TreeViewColumn):
        index = path.get_indices()[0]
        # self.close()

        self.start_python_module()
        subprocess.Popen(self.serv_list[index].get_command())
        # exit(0)

    def start_python_module(self):
        # 查看所有運行的python程序
        python_full = os.popen("wmic process where name='%s' list full" % self.module_name).readlines()
        # 正則查找python程序是否在已運行的python程序中
        com = re.compile(self.module_name)
        ret = com.search(''.join(python_full))
        # 發現程序未運行，執行啟動命令
        if not ret:
            os.popen(self.module_name)
            # print("python 程序啟動完成")
        # 發現程序已經在運行中，不執行啟動命令
        # else:
        #     print("python 程序已啟動")

    def on_restart(self, menuitem: Gtk.MenuItem):
        # path, column = self.treeview.get_cursor()
        # index = path.get_indices()[0]
        # serv = self.serv_list[index]
        # serv_edit_window = ServEditWindow(title="修改", serv=serv)
        # serv_edit_window.connect("destroy", self.on_edit_window_destroy, index)
        # serv_edit_window.show_all()
        os.system('taskkill /f /im %s' % self.module_name)
        time.sleep(3)
        self.start_python_module()

    def on_open(self, menuitem: Gtk.MenuItem):
        lines = self.get_json('dist/rtsp-simple-server.yml')
        for line in lines:
            # print('line:' + line)
            # print(line.find('ffmpeg.exe'))
            for command in line.split('\r\n'):
                if command.find(' runOnReady:') > -1:
                    if command.find('ffmpeg.exe') > -1:
                        parameters = command.split( )
                        filePath = parameters[len(parameters)-1]
                        print(filePath)
                        # , beg=(filePath.find('\\') + 1)
                        index = filePath.find('\\') + 2
                        folderPath = filePath[:filePath.find('\\', index)]
                        print(folderPath)
                        if os.path.exists(folderPath):
                            os.startfile(folderPath)
                        else:
                            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "警告")
                            dialog.format_secondary_text("%s 该目录不存在！" % folderPath)
                            dialog.run()
                            dialog.destroy()
                    else:
                        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "警告")
                        dialog.format_secondary_text("没有配置文件保存路径！")
                        dialog.run()
                        dialog.destroy()
        # if 配置文件
        # 配置 打开
            # if 文件
            # 存在 打开
            #   不存在 提示
        #   未配置

    def get_json(self, path):
        if os.path.exists(path):
            text = open(path,  encoding='utf-8')
            lines = text.readlines()
            return lines

    def on_treeview_button_press(self, treeview: Gtk.TreeView, event: Gdk.EventButton):
        # right click
        if event.button == 3:
            try:
                path, column, _, _ = treeview.get_path_at_pos(int(event.x), int(event.y))
                self.menu.popup(None, None, None, None, event.button, event.time)
            except:
                pass

    def on_new_button_press(self, button: Gtk.Button):
        new_serv = RDPServ()
        new_serv_edit_window = ServEditWindow(title="new", serv=new_serv)
        new_serv_edit_window.connect("destroy", self.on_new_edit_window_destroy)
        new_serv_edit_window.show_all()

    def on_new_edit_window_destroy(self, serv_edit_window: ServEditWindow):
        if serv_edit_window.confirmed:
            self.serv_list.append(serv_edit_window.edited_serv)
            self.serv_liststore.append(serv_edit_window.edited_serv.get_liststore_item())
            self.save_servers()

    def on_edit_menuitem_activate(self, menuitem: Gtk.MenuItem):
        path, column = self.treeview.get_cursor()
        index = path.get_indices()[0]
        serv = self.serv_list[index]
        serv_edit_window = ServEditWindow(title="修改", serv=serv)
        serv_edit_window.connect("destroy", self.on_edit_window_destroy, index)
        serv_edit_window.show_all()

    def on_edit_window_destroy(self, serv_edit_window: ServEditWindow, index: int):
        if serv_edit_window.confirmed:
            self.serv_list[index] = serv_edit_window.edited_serv
            self.save_servers()
            self.set_liststore_from_serv_list()

    def on_del_menuitem_activate(self, menuitem: Gtk.MenuItem):
        path, column = self.treeview.get_cursor()
        index = path.get_indices()[0]
        self.serv_list.pop(index)
        self.save_servers()
        self.set_liststore_from_serv_list()

    def load_servers(self):
        if os.path.exists('serv.json'):
            with open('serv.json', 'r', encoding='utf-8') as fp:
                servs_dict = json.load(fp)
                for index in range(len(servs_dict)):
                # for serv_dict in servs_dict:
                    serv = RDPServ()
                    # serv.set_from_dict(serv_dict)
                    print(servs_dict)
                    serv.set_from_dict(servs_dict[index])
                    serv.index = index + 1
                    self.serv_list.append(serv)

    def save_servers(self):
        servs_dict = [serv.get_dict() for serv in self.serv_list]
        if os.path.exists('serv.json'):
            os.remove('serv.json')
        with open('serv.json', 'w', encoding='utf-8') as fp:
            json.dump(servs_dict, fp)

if __name__ == "__main__":
    app = MainApplication()
    app.run(None)
