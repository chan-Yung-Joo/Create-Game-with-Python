from tkinter import *
from tkinter import messagebox
import random


class Game2048:
    # 숫자 배경 색 사전
    bg_color = {
        2: '#eee4da',
        4: '#ede0c8',
        8: '#edc850',
        16: '#edc53f',
        32: '#f67c5f',
        64: '#f65e3b',
        128: '#edcf72',
        256: '#edcc61',
        512: '#f2b179',
        1024: '#f59563',
        2048: '#edc22e',
    }
    # 숫자 색 사전
    color = {
        2: '#776e65',
        4: '#f9f6f2',
        8: '#f9f6f2',
        16: '#f9f6f2',
        32: '#f9f6f2',
        64: '#f9f6f2',
        128: '#f9f6f2',
        256: '#f9f6f2',
        512: '#776e65',
        1024: '#f9f6f2',
        2048: '#f9f6f2',
    }

    #nxn 격자(self.gridCell) 중에서 비어있는(숫자 0) cell들만 골라서
    #cells 리스트에 그 위치 (r,c)를 넣고 랜덤하게 골라서 숫자 2로 설정한다.
    def random_cell(self):
        cells = []

        for r in range(self.n):
            for c in range(self.n):
                if self.gridCell[r][c] == 0:    # 비어있는 공간(숫자)에만 cells에 넣는다.
                    cells.append((r,c))

        (r,c) = random.choice(cells)            # cells 리스트에서 random하게 선택함!

        self.gridCell[r][c] = 2                 # 랜덤하게 선택한 좌표에 숫자 2를 넣는다.


    #nxn 2D 라벨 격자 (self.board) 의 배경색과 숫자색 칠하기
    def paintGrid(self):
        for r in range(self.n):
            for c in range(self.n):
                if self.gridCell[r][c] == 0:    # 셀이 비어있으면(0)...
                    self.board[r][c].configure(text="",bg="azure4")
                else:
                    self.board[r][c].configure(text=str(self.gridCell[r][c]),bg=self.bg_color[self.gridCell[r][c]],fg=self.color[self.gridCell[r][c]])

    #행과 열을 바꿔서 전치 행렬로 만듦
    def transpose(self):
        #zip([[1,2,3],[4,5,6],[7,8,9]] : (1,4,7), (2,5,8), (3,6,9) 로 차례로 묶어서 튜플로 만듦
        self.gridCell =  [list(t) for t in zip(*self.gridCell)]
        # zip -> 첫번째 원소는 첫번째 원소끼리, 두번째 원소는 두번째 원소끼리 묶어 tuple을 만들어줌!!

    #모든 행에 대해서 reverse
    def reverse(self):
        for r in range(self.n):     # 모든 행에 대해서, (0,n-1), (1,n-2) 등을 값을 바꿈(swap)
            x = 0                   # x=0,1,.. -> 증가
            y = self.n - 1          # y=n-1,n-2,... -> 감소

            while x < y:            # gridCell[r][x] , gridCell[r][y] swap!
                # Python에서는 swap의 경우 temp라는 임시 변수 필요 없이 바로 가능
                (self.gridCell[r][x], self.gridCell[r][y]) = (self.gridCell[r][y], self.gridCell[r][x])

                x += 1              # x의 값 1 증가
                y -= 1              # y의 값 1 감소

    #nxn 격자의 모든 행에 대해서 left 방향으로 비어있는 셀이 있으면 끝까지 이동
    def compressGrid(self):
        self.compress = False   # 변수 초기화 -> 좌로 비어 있는 셀이 있어서 이동하게 되면, True로 변경!

        #nxn 비어 있는 2D 격자 셀 temp 생성
        #self.gridCell 의 숫자 셀(0이 아닌셀)은 temp의 좌측부터 비어 있는 셀(숫자 0)에 넣는다.
        temp = [[0] * self.n for _ in range(self.n)]   # nxn 행렬 (모두 0으로 채움)
        for r in range(self.n):
            cnt = 0             # 제일 좌측에 있는 셀의 인덱스를 0으로 초기화 설정
            for c in range(self.n):
                if self.gridCell[r][c] != 0:        # 숫자 셀(0이 아닌 셀)이라면...
                    # temp[r][cnt]에 비어 있는 좌측 셀로 이동 및 할당 받음
                    temp[r][cnt] = self.gridCell[r][c]
                    if cnt != c:        # 비어있는 셀로 밀착되었다면!
                        self.compress = True
                    cnt += 1            # 그 다음, 좌측 셀로 이동

        self.gridCell = temp

    #좌에서 우로 인접셀이 같으면 merge
    def mergeGrid(self):
        self.merge = False      # 변수 초기화
        for r in range(self.n):                 # 모든 행에 대해서
            for c in range(self.n - 1):         # c=0,1,2,...,n-2까지만
                # 0열부터 인접한 우측 셀의 숫자가 0이 아니면서 같으면, 숫자를 2배
                # 그리고 우측 셀은 0으로 변경
                if self.gridCell[r][c] == self.gridCell[r][c + 1] and self.gridCell[r][c] != 0 :
                    self.gridCell[r][c] *= 2
                    self.gridCell[r][c + 1] = 0
                    self.score += self.gridCell[r][c]       # 점수 획득
                    self.merge = True
                    # 왼쪽만 검사하는 이유: 밑에서, 이미 왼쪽으로 밀착 시키는 기준으로 잡았음. 즉, 상/하/우는 transpose, reverse가 일어나기 때문

    #셀이 꽉 찬경우에 merge 할 셀이 남아 있다면 True 리턴
    def can_merge(self):
        # 가로로 인접한 셀 merge 가능 유무 체크
        for r in range(self.n):             # 모든 행에 대해서
            for c in range(self.n - 1):     # c=0,1,2,...n-2까지만
                if self.gridCell[r][c] == self.gridCell[r][c + 1]:      # 0은 검사할 필요 없음. 꽉찬 경우이기 때문
                    return True

        # 세로로 인접한 셀 merge 가능 유무 체크
        for r in range(self.n - 1):     # r=0,1,2,...,n-2까지만
            for c in range(self.n):     # 모든 열에 대해서
                if self.gridCell[r][c] == self.gridCell[r + 1][c]:      # 0은 검사할 필요 없음. 꽉찬 경우이기 때문
                    return True

        return False


    #키 입력 Up, Down, Left, Right 이벤트 처리 함수
    def link_keys(self,event):
        if self.end or self.won:    # 게임 종료이면 키 입력 처리 안함
            return
        #변수 False 초기화
        self.compress = False   # nxn 격자 모든 행에 대해서 Left 방향으로 비어 있는 셀로 이동했으면 True
        self.merge = False      # 합치는 경우
        self.moved = False      # 움직이는 경우

        key = event.keysym

        # transpose, reverse 를 사용하는 이유: 왼쪽으로 이동하는 것을 기준으로 하기 위함
        # 즉, compressGrid -> mergeGrid -> moved -> compressGrid 구조를 재사용을 위함

        if key == 'Up':
            self.transpose()            # 행과 열 전치

            self.compressGrid()         # 좌로 비어있는 셀이 없도록 밀착
            self.mergeGrid()            # 좌우 인접셀 merge
            self.moved = self.compress or self.merge # compress 했거나 merge 했으면 moved = True 설정
            self.compressGrid()         # 다시 한번 좌로 비어있는 셀이 없도록 밀착

            self.transpose()            # 행과 열 다시한번 전치

        elif key == 'Down':
            self.transpose()
            self.reverse()

            self.compressGrid()  # 좌로 비어있는 셀이 없도록 밀착
            self.mergeGrid()  # 좌우 인접셀 merge
            self.moved = self.compress or self.merge  # compress 했거나 merge 했으면 moved = True 설정
            self.compressGrid()  # 다시 한번 좌로 비어있는 셀이 없도록 밀착

            self.reverse()
            self.transpose()

        elif key == 'Left':
            self.compressGrid()  # 좌로 비어있는 셀이 없도록 밀착
            self.mergeGrid()  # 좌우 인접셀 merge
            self.moved = self.compress or self.merge  # compress 했거나 merge 했으면 moved = True 설정
            self.compressGrid()  # 다시 한번 좌로 비어있는 셀이 없도록 밀착

        elif key == 'Right':
            self.reverse()       # 모든 행을 짝을 맞춰서 (0,3) swap , (1,2) swap

            self.compressGrid()  # 좌로 비어있는 셀이 없도록 밀착
            self.mergeGrid()  # 좌우 인접셀 merge
            self.moved = self.compress or self.merge  # compress 했거나 merge 했으면 moved = True 설정
            self.compressGrid()  # 다시 한번 좌로 비어있는 셀이 없도록 밀착

            self.reverse()  # 모든 행을 짝을 맞춰서 (0,3) swap , (1,2) swap
            # 결국, 오른쪽으로 이동!

        else:
            pass

        '''
        self.random_cell()
        self.paintGrid()        # 라벨 격자 다시 그리기
        '''

        # 2048 승리 검사
        flag = False
        for r in range(self.n):
            for c in range(self.n):
                if self.gridCell[r][c] == 2048:
                    flag = True
                    break

        if flag:        # 2048 승리했으면...
            self.won = True
            messagebox.showinfo("2048","You won!!!!")   # 메시지 출력
            return      # 게임 종료

        #2048 승리하지 않고 비어 있는 셀이 있다면 flag = True 로 설정
        for r in range(self.n):
            for c in range(self.n):
                if self.gridCell[r][c] == 0:
                    flag = True         # 비어 있는 셀이 하나라도 있다면 True!
                    break

        if not flag and not self.can_merge():      # 즉, 비어 있는 셀이 없고 merge 할 셀도 없다면...
            self.end = True         # 게임 종료
            messagebox.showinfo("2048","Game Over!!!")

        if self.moved:              # 움직였다면... -> self.compress or self.merge
            self.random_cell()      # 비어 있는 임의의 셀 위치에 2를 생성

        self.paintGrid()            # 다시 그린다


    def __init__(self,size):
        self.n = size       #size에 따라서 4x4, 5x5, 6x6 등으로 게임판 선택 가능
        self.window = Tk()
        self.window.title('2048 Game')
        self.window.resizable("False","False")
        self.gameArea = Frame(self.window, bg='azure3') #게임판 프레임 생성
        self.gridCell = [[0]*self.n for _ in range(self.n)]   # n x n 숫자 격자셀 0(비어있음) 으로 초기화

        self.compress = False   #좌로 비어 있는 셀로 이동 유무나타내는 변수
        self.merge = False      #좌우 인접셀 숫자가 같으면 merge 유무나타내는 변수
        self.moved = False      #compress 혹은 merge 유무나타내는 변수
        self.end = False        #게임 종료 변수
        self.won = False        #게임 승리 변수
        self.score = 0          #게임 점수

        self.board = [] #n x n 2D 격자 라벨 생성
        for r in range(self.n):
            rows = []
            for c in range(self.n):
                l = Label(self.gameArea, text='',bg='azure4',font=('G마켓 산스',22,'bold'),width=4,height=2)
                l.grid(row=r,column=c,padx=7,pady=7) #r행 c열 격자 라벨생성, padx=7, pady=7 좌,상 7포인트 간격
                rows.append(l)
            self.board.append(rows)
        self.gameArea.pack()

        self.random_cell()  #랜덤하게 숫자 2 위치 선택
        self.random_cell()  #랜덤하게 숫자 2 위치 선택
        self.paintGrid()    #self.board nxn 2D 라벨 배경과 숫자색 색칠
        self.window.bind('<Key>', self.link_keys)   #키입력 이벤트 함수 self.link_keys 연결
        self.window.mainloop()


Game2048(4)