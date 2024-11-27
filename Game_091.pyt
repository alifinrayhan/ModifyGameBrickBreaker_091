import tkinter as tk


# Class GameObject adalah kelas dasar untuk semua objek dalam permainan (bola, paddle, brick).
class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        # Mengembalikan posisi koordinat dari objek.
        return self.canvas.coords(self.item)

    def move(self, x, y):
        # Memindahkan objek sejauh x dan y.
        self.canvas.move(self.item, x, y)

    def delete(self):
        # Menghapus objek dari kanvas.
        self.canvas.delete(self.item)


# Class Ball untuk merepresentasikan bola dalam permainan.
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10  # Radius bola.
        self.direction = [1, -1]  # Arah awal bola (kanan atas).
        self.speed = 10  # Kecepatan bola.
        item = canvas.create_oval(
            x - self.radius, y - self.radius,
            x + self.radius, y + self.radius,
            fill='white'  # Warna bola.
        )
        super().__init__(canvas, item)

    def update(self):
        # Memperbarui posisi bola berdasarkan arah dan kecepatan.
        coords = self.get_position()
        width = self.canvas.winfo_width()

        # Membalik arah jika bola menyentuh sisi kiri atau kanan kanvas.
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        # Membalik arah jika bola menyentuh sisi atas.
        if coords[1] <= 0:
            self.direction[1] *= -1

        # Menggerakkan bola.
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        # Mengatur respons bola jika terjadi tabrakan dengan paddle atau brick.
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5

        # Jika bola bertabrakan dengan lebih dari satu objek (misalnya paddle + brick).
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1  # Bola memantul ke kanan.
            elif x < coords[0]:
                self.direction[0] = -1  # Bola memantul ke kiri.
            else:
                self.direction[1] *= -1  # Bola memantul ke atas/bawah.

        # Jika bertabrakan dengan brick, kurangi hit brick dan tambahkan skor.
        for game_object in game_objects:
            if isinstance(game_object, Brick):
                return game_object.hit()
        return 0


# Class Paddle untuk mengontrol paddle pemain.
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80  # Lebar paddle.
        self.height = 10  # Tinggi paddle.
        self.ball = None  # Bola yang terkait dengan paddle.
        item = canvas.create_rectangle(
            x - self.width / 2, y - self.height / 2,
            x + self.width / 2, y + self.height / 2,
            fill='#605678'  # Warna paddle.
        )
        super().__init__(canvas, item)

    def set_ball(self, ball):
        # Mengaitkan bola dengan paddle.
        self.ball = ball

    def move(self, offset):
        # Memindahkan paddle ke kiri/kanan berdasarkan offset.
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super().move(offset, 0)
            if self.ball is not None:
                # Jika bola belum dilepaskan, bola bergerak bersama paddle.
                self.ball.move(offset, 0)


# Class Brick untuk merepresentasikan batu bata dalam permainan.
class Brick(GameObject):
    COLORS = {1: '#257180', 2: '#00FF9C', 3: '#37AFE1'}  # Warna berdasarkan jumlah hit.
    POINTS = {1: 10, 2: 20, 3: 30}  # Poin berdasarkan jumlah hit.

    def __init__(self, canvas, x, y, hits):
        self.width = 75  # Lebar brick.
        self.height = 20  # Tinggi brick.
        self.hits = hits  # Jumlah hit yang diperlukan untuk menghancurkan brick.
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(
            x - self.width / 2, y - self.height / 2,
            x + self.width / 2, y + self.height / 2,
            fill=color, tags='brick'  # Warna dan tag untuk brick.
        )
        super().__init__(canvas, item)

    def hit(self):
        # Mengurangi hit brick. Jika habis, hapus brick dan tambahkan poin.
        self.hits -= 1
        if self.hits == 0:
            self.delete()
            return Brick.POINTS[1]
        else:
            # Ubah warna brick sesuai dengan jumlah hit yang tersisa.
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])
            return 5


# Class Game untuk mengontrol keseluruhan permainan.
class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.lives = 3  # Jumlah nyawa pemain.
        self.score = 0  # Skor awal.
        self.width = 610  # Lebar kanvas.
        self.height = 400  # Tinggi kanvas.
        self.canvas = tk.Canvas(
            self, bg='#FEEE91',  # Warna latar belakang.
            width=self.width, height=self.height
        )
        self.canvas.pack()
        self.pack()

        # Objek permainan.
        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle

        # Tambahkan brick ke dalam permainan.
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None  # Tampilan nyawa.
        self.score_text = None  # Tampilan skor.
        self.setup_game()  # Inisialisasi permainan.

        # Kontrol paddle dengan tombol panah.
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    def setup_game(self):
        # Atur ulang permainan dan tambahkan bola baru.
        self.add_ball()
        self.update_lives_text()
        self.update_score_text()
        self.text = self.draw_text(300, 200, 'Press Space to start')  # Petunjuk awal.
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        # Tambahkan bola baru ke paddle.
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        # Tambahkan brick ke lokasi tertentu.
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        # Gambar teks di kanvas.
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_lives_text(self):
        # Perbarui tampilan jumlah nyawa.
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def update_score_text(self):
        # Perbarui tampilan skor.
        text = 'Score: %s' % self.score
        if self.score_text is None:
            self.score_text = self.draw_text(150, 20, text, 15)
        else:
            self.canvas.itemconfig(self.score_text, text=text)

    def start_game(self):
        # Mulai permainan setelah menekan tombol spasi.
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        # Logika utama permainan.
        points = self.check_collisions()  # Periksa tabrakan.
        self.score += points  # Tambahkan skor.

        if self.ball.get_position()[3] >= self.height:
            # Bola jatuh ke bawah, kurangi nyawa.
            self.lives -= 1
            if self.lives < 0:
                # Permainan selesai jika nyawa habis.
                self.update_lives_text()
                self.game_over()
                return
            else:
                self.update_lives_text()
                self.canvas.after(1000, self.setup_game)
                return

        self.update_score_text()
        self.ball.update()
        self.canvas.after(50, self.game_loop)

    def check_collisions(self):
        # Periksa apakah bola bertabrakan dengan objek lain.
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(
            *ball_coords
        )
        objects = [self.items[x] for x in items if x in self.items]
        return self.ball.collide(objects)

    def game_over(self):
        # Tampilkan pesan permainan selesai.
        self.canvas.create_text(300, 200, text='Game Over', font=('Helvetica', 50))



if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()
