import socket
import time

SERVER = "irc.hybridirc.com"
PORT = 6667
BOTNICK = "X-Bot"
IDENT = "rcbot"
REALNAME = "SECRET-BOT"
CHANNEL = "#chatterx"

NICKSERV_PASSWORD = "piyush!#1212"
VERIFY_PASSWORD = "chatter01"

verified_users = set()

HELP_TEXT = [
    "RC Bot Commands:",
    "!verify <password>  - Verify yourself (PM only)",
    "!k <nick>           - Kick user",
    "!b <nick>           - Ban + kick user",
    "!ub <nick>          - Unban user",
    "!inv <nick>         - Invite user",
    "!vc <nick>          - Give voice (+v)",
    "!help               - Show this help"
]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER, PORT))

def send(msg):
    print(">>", msg)
    sock.sendall((msg + "\r\n").encode())

send(f"NICK {BOTNICK}")
send(f"USER {IDENT} 0 * :{REALNAME}")

while True:
    data = sock.recv(4096).decode(errors="ignore")
    for line in data.split("\r\n"):
        if not line:
            continue

        print("<<", line)

        if line.startswith("PING"):
            send(f"PONG {line.split()[1]}")
            continue

        parts = line.split()
        if len(parts) < 2:
            continue

        if parts[1] == "001":
            send(f"PRIVMSG NickServ :IDENTIFY {NICKSERV_PASSWORD}")
            time.sleep(2)
            send(f"JOIN {CHANNEL}")
            continue

        if parts[1] == "QUIT":
            nick = line.split("!")[0][1:]
            verified_users.discard(nick)
            continue

        if parts[1] == "NICK":
            old = line.split("!")[0][1:]
            new = parts[2][1:]
            verified_users.discard(old)
            verified_users.discard(new)
            continue

        if parts[1] != "PRIVMSG":
            continue

        nick = line.split("!")[0][1:]
        target = parts[2]
        text = line.split(" :", 1)[1].strip()

        is_pm = (target == BOTNICK)

        if text.lower().startswith("!verify"):
            if not is_pm:
                send(f"PRIVMSG {nick} :Use !verify in PM only.")
                continue

            args = text.split()
            if len(args) != 2:
                send(f"PRIVMSG {nick} :Usage: !verify <password>")
                continue

            if args[1] == VERIFY_PASSWORD:
                verified_users.add(nick)
                send(f"PRIVMSG {nick} :Verification successful ✔")
                send(f"MODE {CHANNEL} +v {nick}")
            else:
                send(f"PRIVMSG {nick} :Incorrect password ❌")
            continue

        if text.lower() == "!help":
            for line in HELP_TEXT:
                send(f"PRIVMSG {nick} :{line}")
            continue

        if nick not in verified_users:
            send(f"PRIVMSG {nick} :You must verify first using !verify")
            continue

        cmd = text.split()
        if len(cmd) < 2:
            continue

        action = cmd[0].lower()
        user = cmd[1]

        if action == "!k":
            send(f"KICK {CHANNEL} {user} :Requested by {nick}")

        elif action == "!b":
            send(f"MODE {CHANNEL} +b {user}!*@*")
            send(f"KICK {CHANNEL} {user} :Banned by {nick}")

        elif action == "!ub":
            send(f"MODE {CHANNEL} -b {user}!*@*")

        elif action == "!inv":
            send(f"INVITE {user} {CHANNEL}")

        elif action == "!vc":
            send(f"MODE {CHANNEL} +v {user}")
