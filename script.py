import random
from flask import *

app = Flask(__name__)

num_rows, num_columns = 7, 8
max_moves = num_rows * num_columns
place_maker = "W"
tokens = ("R", "Y")
script_name = "/script.py"
app.secret_key = "sessionSecretKey"


# Dynamic matrix creation
def createMatrix():
    matrix = [place_maker] * num_rows
    for i in range(num_rows):
        matrix[i] = [place_maker] * num_columns
    return matrix


# 'R' => player1 turn
# 'Y' => player2 turn
def randomFirstPlayer():
    return random.choice([tokens[0], tokens[1]])


# Checking if the selected move is valid
def checkMove(matrix, col):
    for i in range(num_rows - 1, -1, -1):
        if (matrix[i][col] == place_maker):
            return i
    return -1


# Execution of the selected move
def moves(matrix, col, token):
    row = checkMove(matrix, col)
    if (row != -1):
        matrix[row][col] = token
        return row
    print("The selected move is not valid")
    return -1

# Check of all possibilities
def conditions(i, j, index):
    if (index == 0):
        return j >= 0
    elif (index == 1):
        return j < num_columns
    elif (index == 2):
        return i >= 0 and j >= 0
    elif (index == 3):
        return i < num_rows and j < num_columns
    elif (index == 4):
        return i >= 0 and j < num_columns
    return i < num_rows and j >= 0


def horizontalWinRule(matrix, i, j, cond, incrJ, token):
    count = 0
    while (conditions(i, j, cond)):
        if (matrix[i][j] == token):
            count += 1
            j += incrJ
        else:
            break
    return count


# I check if there is a horizontal streak of 4 between left and right
def horizontalWin(matrix, i, j, token):
    count = 1
    # I check if there is a horizontal streak of 4 to the left
    count += horizontalWinRule(matrix, i, j - 1, 0, -1, token)
    if (count == 4):
        return True
    # I check if there is a horizontal streak of 4 to the right
    count += horizontalWinRule(matrix, i, j + 1, 1, 1, token)
    return count == 4


# I check if there is a horizontal streak of 4 downward
def verticalWin(matrix, i, j, token):
    count = 0
    while (i < num_rows):
        if (matrix[i][j] == token):
            count += 1
            i += 1
        else:
            break
    return count == 4


def diagonalWinRule(matrix, i, j, cond, incrI, incrJ, token):
    count = 0
    while (conditions(i, j, cond)):
        if (matrix[i][j] == token):
            count += 1
            i += incrI
            j += incrJ
        else:
            break
    return count


# I check if there is a horizontal streak of 4 on a diagonal from left-upper to right-lower
def leftDiagonalWin(matrix, i, j, token):
    count = 1
    # I check if there is a horizontal streak of 4 toward the upper left diagonal
    count += diagonalWinRule(matrix, i - 1, j - 1, 2, -1, -1, token)
    if (count == 4):
        return True
    # I check if there is a horizontal streak of 4 toward the lower right diagonal
    count += diagonalWinRule(matrix, i + 1, j + 1, 3, 1, 1, token)
    return count == 4


# I check if there is a horizontal streak of 4 on a diagonal from right-upper to left-lower
def rightDiagonalWin(matrix, i, j, token):
    count = 1
    # I check if there is a horizontal streak of 4 toward the upper right diagonal
    count += diagonalWinRule(matrix, i - 1, j + 1, 4, -1, 1, token)
    if (count == 4):
        return True
    # I check if there is a horizontal streak of 4 toward the lower left diagonal
    count += diagonalWinRule(matrix, i + 1, j - 1, 5, 1, -1, token)
    return count == 4


# I check at each move whether the player who just made the move, made a winning move
def checkWin(matrix, row, col, token):
    return (verticalWin(matrix, row, col, token)
            or horizontalWin(matrix, row, col, token)
            or leftDiagonalWin(matrix, row, col, token)
            or rightDiagonalWin(matrix, row, col, token))


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    session.clear()
    session["matrix"] = createMatrix()
    return send_file("index.html")


@app.route(f"{script_name}/startGame", methods=["POST"])
def startGame():
    session["player1"] = request.form.get("player1")
    session["tokenPlayer1"] = tokens[0]
    session["player2"] = request.form.get("player2")
    session["tokenPlayer2"] = tokens[1]
    session["turn"] = randomFirstPlayer()
    session["message"] = ""
    session["moves"] = 0
    session["endGame"] = "N"
    session["num_rows"] = num_rows
    session["num_columns"] = num_columns
    return render_template("game.html", session=session)


@app.route(f"{script_name}/game", methods=["GET"])
def game():
    return render_template("game.html", session=session)


@app.route(f"{script_name}/move", methods=["POST"])
def move():
    col = int(request.form.get("move")) - 1
    row = moves(session["matrix"], col, session["turn"])
    if (row != -1):
        session["moves"] = int(session["moves"]) + 1
        if (checkWin(session["matrix"], row, col, session["turn"])):
            session["message"] = f"<h1>Congratulation {session.get('player1') if session.get('turn') ==  tokens[0] else session.get('player2')} for winnig</h1><form action='/' method='GET'><input type='submit' value='Homepage' id='button' /></form>"
            session["endGame"] = "Y"
        elif (int(session["moves"]) == max_moves):
            session["message"] = "<h2>The match ended in a tie</h2><form action='/' method='GET'><input type='submit' value='Homepage' id='homepage' /></form>"
            session["endGame"] = "Y"
        else:
            session["turn"] = tokens[1] if session["turn"] == tokens[0] else tokens[0]
        return redirect(f"{script_name}/game")
    else:
        return render_template("wrongMove.html")


if __name__ == "__main__":
    app.run(debug=True)